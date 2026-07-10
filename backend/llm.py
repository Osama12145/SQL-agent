import os
from typing import Literal

from pydantic import BaseModel, Field

from backend.prompts import SQL_GENERATION_PROMPT, SQL_REPAIR_PROMPT, SUMMARY_PROMPT


class DisplayHintModel(BaseModel):
    chart_type: Literal["table", "kpi", "bar", "line"] = Field(
        default="table",
        description="Suggested chart type based on the user's intent.",
    )
    x: str | None = None
    y: str | None = None
    title: str | None = None
    reason: str | None = None


class SQLGenerationModel(BaseModel):
    sql: str
    explanation: str
    display_hint: DisplayHintModel = Field(default_factory=DisplayHintModel)


def _chat_model():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing.")

    from langchain_openai import ChatOpenAI

    # OpenRouter is OpenAI-compatible, so provider configuration stays in one place.
    return ChatOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        model=os.getenv(
            "OPENROUTER_MODEL",
            "openai/gpt-4o-mini-2024-07-18",
        ),
        temperature=0,
        timeout=30,
        max_retries=2,
    )


def generate_sql(question: str, schema: str) -> SQLGenerationModel:
    # Structured output removes fragile JSON parsing from the rest of the graph.
    model = _chat_model().with_structured_output(SQLGenerationModel)
    prompt = SQL_GENERATION_PROMPT.format(schema=schema)
    return model.invoke(
        [
            ("system", prompt),
            ("human", question),
        ]
    )


def repair_sql(
    question: str,
    schema: str,
    sql: str,
    error: str,
) -> SQLGenerationModel:
    model = _chat_model().with_structured_output(SQLGenerationModel)
    prompt = SQL_REPAIR_PROMPT.format(
        schema=schema,
        question=question,
        sql=sql,
        error=error,
    )
    return model.invoke(
        [
            ("system", prompt),
            ("human", "Return the corrected structured output."),
        ]
    )


def summarize_answer(question: str, sql: str, rows: list[dict]) -> str:
    if not rows:
        return "No matching rows were found for this question."

    try:
        model = _chat_model()
        prompt = SUMMARY_PROMPT.format(question=question, sql=sql, rows=rows[:20])
        response = model.invoke([("human", prompt)])
        return str(response.content)
    except Exception:
        # SQL results are still useful when the optional summary call fails.
        return _fallback_summary(rows)


def _fallback_summary(rows: list[dict]) -> str:
    first_row = rows[0]
    if len(rows) == 1:
        values = ", ".join(f"{key}: {value}" for key, value in first_row.items())
        return f"The result is {values}."

    return f"The query returned {len(rows)} rows. The first row is {first_row}."
