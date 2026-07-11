from typing import Any, Literal, Optional, TypedDict


# Two retries demonstrate self-correction without unbounded API cost or latency.
MAX_REPAIR_ATTEMPTS = 2

ChartType = Literal["table", "kpi", "bar", "line"]


class DisplayHint(TypedDict, total=False):
    chart_type: ChartType
    x: str
    y: str
    title: str
    reason: str


class DisplaySpec(TypedDict, total=False):
    chart_type: ChartType
    x: Optional[str]
    y: Optional[str]
    title: str
    reason: str


class AgentState(TypedDict, total=False):
    question: str
    schema: str
    out_of_scope: bool
    unavailable_reason: Optional[str]
    sql: Optional[str]
    sql_explanation: Optional[str]
    display_hint: Optional[DisplayHint]
    rows: list[dict[str, Any]]
    columns: list[str]
    answer: Optional[str]
    display: Optional[DisplaySpec]
    error: Optional[str]
    attempts: int
