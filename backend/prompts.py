SQL_GENERATION_PROMPT = """
You convert natural language questions into safe SQLite SELECT queries.

Database schema:
{schema}

Rules:
- Generate exactly one SELECT query.
- Start directly with SELECT. Do not use a WITH clause or CTE.
- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, or VACUUM.
- Select only columns needed to answer the question.
- Prefer explicit JOINs when a question needs multiple tables.
- Use readable aliases for calculated columns.
- Return time groups as YYYY-MM or YYYY-MM-DD so they stay sortable.
- If the user does not request a limit, keep the result compact.
- Also suggest a display_hint. The hint is not final; another node will verify it.
- Suggest kpi for one number, line for time series, bar for one category plus
  one number, and table for detailed results with three or more columns.

Return structured output with:
- sql
- explanation
- display_hint
"""


SQL_REPAIR_PROMPT = """
The previous SQLite SELECT query failed or did not pass validation.

Database schema:
{schema}

User question:
{question}

Previous SQL:
{sql}

Error:
{error}

Rewrite the query as one safe SQLite SELECT statement.
Return structured output with sql, explanation, and display_hint.
"""


SUMMARY_PROMPT = """
Answer the user's question using the SQL result.
Keep the answer short and direct. Do not invent facts outside the rows.

Question:
{question}

SQL:
{sql}

Rows:
{rows}
"""
