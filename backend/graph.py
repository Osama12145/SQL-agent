from langgraph.graph import END, START, StateGraph

from backend.db import execute_select, load_schema
from backend.display import decide_display
from backend.llm import generate_sql, repair_sql, summarize_answer
from backend.state import MAX_REPAIR_ATTEMPTS, AgentState
from backend.validators import validate_select_sql


def load_schema_node(state: AgentState) -> AgentState:
    return {
        "schema": load_schema(),
        "attempts": state.get("attempts", 0),
        "error": None,
    }


def generate_sql_node(state: AgentState) -> AgentState:
    result = generate_sql(state["question"], state["schema"])
    if not result.answerable:
        return {
            "out_of_scope": True,
            "unavailable_reason": result.unavailable_reason,
            "error": None,
        }

    return {
        "out_of_scope": False,
        "sql": result.sql,
        "sql_explanation": result.explanation,
        "display_hint": result.display_hint.model_dump(exclude_none=True),
        "error": None,
    }


def out_of_scope_node(state: AgentState) -> AgentState:
    # A schema mismatch is a valid refusal, not malformed SQL to repair. Return a
    # clear answer without asking the model again or touching the database.
    reason = state.get("unavailable_reason") or (
        "The available retail database does not contain that information."
    )
    return {
        "answer": "I can only answer questions using the available retail database. "
        + reason,
        "rows": [],
        "columns": [],
        "error": None,
    }


def route_after_generation(state: AgentState) -> str:
    if state.get("out_of_scope"):
        return "out_of_scope"
    return "validate_sql"


def validate_sql_node(state: AgentState) -> AgentState:
    is_valid, reason, safe_sql = validate_select_sql(state.get("sql") or "")
    if not is_valid:
        # Keep validation failures in state so the graph, not this node, decides
        # whether to repair the SQL or return a controlled failure.
        return {"error": reason}
    return {"sql": safe_sql, "error": None}


def repair_sql_node(state: AgentState) -> AgentState:
    # Count correction calls, not the initial generation, so the limit is explicit.
    attempts = state.get("attempts", 0) + 1
    result = repair_sql(
        question=state["question"],
        schema=state["schema"],
        sql=state.get("sql") or "",
        error=state.get("error") or "Unknown error",
    )
    return {
        "sql": result.sql,
        "sql_explanation": result.explanation,
        "display_hint": result.display_hint.model_dump(exclude_none=True),
        "attempts": attempts,
        "error": None,
    }


def execute_sql_node(state: AgentState) -> AgentState:
    try:
        rows, columns = execute_select(state["sql"] or "")
    except Exception as exc:
        # Convert database failures into state so they follow the same bounded repair
        # policy and user-feedback path as validation failures.
        return {"error": str(exc)}

    return {
        "rows": rows,
        "columns": columns,
        "error": None,
    }


def decide_display_node(state: AgentState) -> AgentState:
    display = decide_display(
        rows=state.get("rows", []),
        columns=state.get("columns", []),
        hint=state.get("display_hint"),
    )
    return {"display": display}


def summarize_answer_node(state: AgentState) -> AgentState:
    answer = summarize_answer(
        question=state["question"],
        sql=state.get("sql") or "",
        rows=state.get("rows", []),
    )
    return {"answer": answer}


def fail_node(state: AgentState) -> AgentState:
    return {
        "answer": state.get("error") or "The query could not be completed.",
        "rows": state.get("rows", []),
        "columns": state.get("columns", []),
    }


def route_after_validation(state: AgentState) -> str:
    # Validation and execution have different success destinations, but share one
    # error policy: repair while attempts remain, otherwise end with a clear failure.
    if not state.get("error"):
        return "execute_sql"
    if state.get("attempts", 0) < MAX_REPAIR_ATTEMPTS:
        return "repair_sql"
    return "fail"


def route_after_execution(state: AgentState) -> str:
    if not state.get("error"):
        return "decide_display"
    if state.get("attempts", 0) < MAX_REPAIR_ATTEMPTS:
        return "repair_sql"
    return "fail"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("load_schema", load_schema_node)
    graph.add_node("generate_sql", generate_sql_node)
    graph.add_node("out_of_scope", out_of_scope_node)
    graph.add_node("validate_sql", validate_sql_node)
    graph.add_node("repair_sql", repair_sql_node)
    graph.add_node("execute_sql", execute_sql_node)
    graph.add_node("decide_display", decide_display_node)
    graph.add_node("summarize_answer", summarize_answer_node)
    graph.add_node("fail", fail_node)

    # Schema stays in AgentState instead of hidden process configuration, so each
    # graph run shows exactly what database context the LLM used.
    graph.add_edge(START, "load_schema")
    graph.add_edge("load_schema", "generate_sql")
    # Retrying cannot create data that is absent from the schema, so out-of-scope
    # questions end clearly before SQL validation or execution.
    graph.add_conditional_edges(
        "generate_sql",
        route_after_generation,
        {
            "out_of_scope": "out_of_scope",
            "validate_sql": "validate_sql",
        },
    )
    graph.add_edge("out_of_scope", END)

    # Validation and execution fail for different reasons, but both failures can
    # reuse one repair node before returning to the same safety check.
    graph.add_conditional_edges(
        "validate_sql",
        route_after_validation,
        {
            "execute_sql": "execute_sql",
            "repair_sql": "repair_sql",
            "fail": "fail",
        },
    )
    # Repair produces new LLM output, not trusted SQL. Route it through validation
    # again rather than directly to execution, so every query crosses the same safety gate.
    graph.add_edge("repair_sql", "validate_sql")
    graph.add_conditional_edges(
        "execute_sql",
        route_after_execution,
        {
            "decide_display": "decide_display",
            "repair_sql": "repair_sql",
            "fail": "fail",
        },
    )

    # Display is decided after execution so the LLM hint is checked against real rows.
    graph.add_edge("decide_display", "summarize_answer")
    graph.add_edge("summarize_answer", END)
    graph.add_edge("fail", END)

    return graph.compile()
