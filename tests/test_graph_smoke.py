from backend import graph as graph_module
from backend.llm import SQLGenerationModel


def _generation(
    sql: str | None,
    *,
    answerable: bool = True,
    unavailable_reason: str | None = None,
) -> SQLGenerationModel:
    return SQLGenerationModel(
        answerable=answerable,
        unavailable_reason=unavailable_reason,
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
        lambda question, schema: _generation("SELECT 42 AS total FROM products"),
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
        lambda question, schema, sql, error: _generation(
            "SELECT 42 AS total FROM products"
        ),
    )

    result = graph_module.build_graph().invoke(
        {"question": "What is the total?", "attempts": 0}
    )

    assert result["answer"] == "The result is 42."
    assert result["attempts"] == 1
    assert result["error"] is None


def test_graph_stops_questions_outside_the_database(monkeypatch):
    _mock_shared_nodes(monkeypatch)
    monkeypatch.setattr(
        graph_module,
        "generate_sql",
        lambda question, schema: _generation(
            None,
            answerable=False,
            unavailable_reason="The database contains retail sales data, not global city data.",
        ),
    )
    monkeypatch.setattr(
        graph_module,
        "execute_select",
        lambda sql: (_ for _ in ()).throw(AssertionError("SQL should not execute.")),
    )

    result = graph_module.build_graph().invoke(
        {"question": "What is the biggest city in the world?", "attempts": 0}
    )

    assert result["out_of_scope"] is True
    assert "retail database" in result["answer"]
    assert result["attempts"] == 0


def test_repaired_sql_is_validated_before_execution(monkeypatch):
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
    monkeypatch.setattr(
        graph_module,
        "execute_select",
        lambda sql: (_ for _ in ()).throw(AssertionError("Invalid repaired SQL executed.")),
    )

    result = graph_module.build_graph().invoke(
        {"question": "What is the total?", "attempts": 0}
    )

    assert result["attempts"] == 2
    assert "must read from" in result["answer"]
