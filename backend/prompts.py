SQL_GENERATION_PROMPT = """
You convert questions about the available retail database into safe SQLite SELECT queries.

Database schema:
{schema}

Rules:
- Use only facts that can be derived from the database schema below. You do not
  know facts about the world outside this database.
- If the question cannot be answered from this schema, set answerable to false,
  set sql to null, and give a brief unavailable_reason. Do not guess, use general
  knowledge, return a literal answer, or generate SQL for an unrelated question.
- A generic schema field does not make a question answerable. Never use a customer,
  product, or order row as a placeholder for the assistant, the user, a family
  member, or a real-world entity. Never invent a filter such as WHERE id = 1.
- Reject personal identity or relationship questions and world-knowledge questions,
  even when the schema has a superficially similar field such as name or date.
- Examples: "What is your mother's name?", "Write your name.", and "What is the
  biggest city in the world?" are outside the retail database. "What is the name
  of customer 1?" is answerable because it explicitly names a retail entity and ID.
- When answerable is true, generate exactly one SELECT query that starts directly
  with SELECT. Do not use a WITH clause or CTE.
- When answerable is true, the query must read from one or more schema tables.
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
- answerable
- unavailable_reason (null when answerable is true)
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

The question has already been determined to be answerable from this schema.
Rewrite the query as one safe SQLite SELECT statement that reads from schema tables.
Return structured output with answerable set to true, unavailable_reason set to null,
plus sql, explanation, and display_hint.
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
