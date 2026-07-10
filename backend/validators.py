import re


BLOCKED_SQL_WORDS = {
    "alter",
    "attach",
    "create",
    "delete",
    "detach",
    "drop",
    "insert",
    "pragma",
    "replace",
    "update",
    "vacuum",
}


def clean_sql(sql: str) -> str:
    """Remove common LLM formatting without changing the query meaning."""
    sql = sql.strip()
    sql = re.sub(r"^```sql\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"^```\s*", "", sql)
    sql = re.sub(r"\s*```$", "", sql)
    return sql.strip().rstrip(";")


def validate_select_sql(sql: str) -> tuple[bool, str | None, str | None]:
    cleaned = clean_sql(sql)
    lowered = cleaned.lower()

    if not cleaned:
        return False, "The SQL query is empty.", None

    # A SELECT allowlist is easier to audit than trying to enumerate every write form.
    if not re.match(r"^select\b", lowered):
        return False, "Only SELECT queries are allowed in this demo.", None

    if ";" in cleaned:
        return False, "Only one SQL statement is allowed.", None

    words = set(re.findall(r"[a-z_]+", lowered))
    blocked = sorted(words.intersection(BLOCKED_SQL_WORDS))
    if blocked:
        return False, f"Blocked SQL keyword found: {blocked[0]}.", None

    return True, None, ensure_limit(cleaned)


def ensure_limit(sql: str, limit: int = 100) -> str:
    if re.search(r"\blimit\s+\d+\b", sql, flags=re.IGNORECASE):
        return sql
    # Bounding returned rows keeps the API response and dashboard predictable.
    return f"{sql} LIMIT {limit}"
