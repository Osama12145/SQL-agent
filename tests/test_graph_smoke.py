from backend import graph as graph_module
from backend.llm import SQLGenerationModel


def _generation(sql: str) -> SQLGenerationModel:
    return SQLGenerationModel(
        sql=sql,
        explanation="Test query",
        display_hint={"chart_type": "kpi", "y": "total"},
    )


def _mock_shared_nodes(monkeypatch) -> None:
    monkeypatch.setattr(graph_module, "load_schema", lambda: "Table: products")
    monkeypatch.setattr(
        graph_module,
        "execute_select",
        lambda sql: ([{"total": 42}], ["total"]),
    )
    monkeypatch.setattr(
        graph_module,
        "summarize_answer",
        lambda question, sql, rows: "The result is 42.",
    )


def test_graph_happy_path(monkeypatch):
    _mock_shared_nodes(monkeypatch)
    monkeypatch.setattr(
        graph_module,
        "generate_sql",
        lambda question, schema: _generation("SELECT 42 AS total"),
    )

    result = graph_module.build_graph().invoke(
        {"question": "What is the total?", "attempts": 0}
    )

    assert result["answer"] == "The result is 42."
    assert result["display"]["chart_type"] == "kpi"
    assert result["attempts"] == 0


def test_graph_repairs_invalid_sql(monkeypatch):
    _mock_shared_nodes(monkeypatch)
    monkeypatch.setattr(
        graph_module,
        "generate_sql",
        lambda question, schema: _generation("DELETE FROM products"),
    )
    monkeypatch.setattr(
        graph_module,
        "repair_sql",
        lambda question, schema, sql, error: _generation("SELECT 42 AS total"),
    )

    result = graph_module.build_graph().invoke(
        {"question": "What is the total?", "attempts": 0}
    )

    assert result["answer"] == "The result is 42."
    assert result["attempts"] == 1
    assert result["error"] is None
