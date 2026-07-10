# Interview Questions And Answers

## Architecture

### Why did you use LangGraph instead of a simple chain?

LangGraph makes state and conditional control flow explicit. This workflow has
two meaningful branches: SQL validation can fail, and SQL execution can fail;
both can route to a bounded repair step before returning to validation.

### Is this really an agentic workflow?

Yes, within the scope of the assignment. The model generates and repairs SQL,
while the graph decides whether to execute, repair, choose a display, or fail.
It is intentionally bounded rather than an open-ended autonomous agent.

### Why does every node have one responsibility?

It makes the state transitions easy to test and explain. It also prevents SQL
validation, database access, display policy, and answer generation from becoming
one large function with hidden side effects.

### Why is `load_schema` a node instead of a startup operation?

Keeping it in the graph makes the schema part of the visible agent context and
allows the workflow to reflect schema changes without restarting the server. For
a larger production database, I would cache it with migration-based invalidation.

### Why do you not use memory or a checkpointer?

Each question is independent, so conversation memory is not required. Adding a
checkpointer would introduce persistence and session behavior that the assignment
does not ask for.

### Why is the state a `TypedDict`?

The state is a small collection of named fields, not a complex domain object.
`TypedDict` keeps it lightweight while documenting what nodes can read and write.

## SQL And Safety

### Why do you validate SQL before execution?

The LLM is probabilistic, so its output must pass a deterministic boundary. The
validator allows one SELECT statement, rejects write-oriented keywords, and adds
a row limit before the database sees the query.

### Why do you use a read-only SQLite connection if validation already exists?

They protect different layers. The validator is readable policy code; `mode=ro`
is a database-enforced second boundary if validation misses an edge case.

### Why do you use `EXPLAIN QUERY PLAN`?

It forces SQLite to plan the query before rows are fetched, so schema and SQL
planning errors are handled by the same execution error route. It is not treated
as a complete performance guard.

### Why do you add `LIMIT 100`?

The dashboard is a demo UI, so an unbounded detail query could create a very
large response. The limit keeps response size and rendering predictable.

### Why are there only two repair attempts?

Two attempts are enough to demonstrate self-correction while keeping latency and
API cost bounded. The constant lives in one place so the code and README cannot
drift apart.

### What happens if the model returns invalid SQL?

`validate_sql` stores an error in state. The route sends the query, schema, and
error to `repair_sql`, then sends the repaired SQL through validation again. If
the attempts are exhausted, `fail` returns a controlled response.

### What happens if OpenRouter is unavailable?

That is not a repairable SQL error. The API catches provider/configuration
failures at the boundary and returns a clear service error, while the summary
call has a deterministic fallback so successful SQL results remain useful.

## Display And Frontend

### Why does the LLM return a `display_hint`?

The model understands user intent. For example, "compare" often implies a bar
chart and "trend" implies a line chart. The hint is only a proposal; it cannot
override the actual result shape.

### Why do you decide the final display after execution?

Before execution, the model does not know whether the result will contain one
row, a date column, or several detail columns. After execution, deterministic
rules can prevent an empty or misleading chart.

### Why not let the frontend choose the chart?

Chart policy belongs to the backend because it is part of the agent decision. The
frontend only renders the `DisplaySpec`, which keeps Streamlit simple and avoids
duplicating business logic.

### Why is this called a dashboard if it shows one primary result?

It is a query-driven minimal dashboard, not a fixed BI dashboard. Each question
changes the primary dashboard element to the most useful KPI, chart, or table,
which matches the requirement to adjust elements dynamically.

### Why did you choose Streamlit?

The assignment says styling is not a priority. Streamlit provides input, tables,
KPI metrics, and charts with very little frontend code, so more time stays on the
agent workflow.

### Why did you choose FastAPI?

FastAPI gives a small typed HTTP boundary between the UI and the graph. It also
makes health checks, request validation, and error responses straightforward.

## LLM And Testing

### Why use OpenRouter?

OpenRouter exposes an OpenAI-compatible API, so the project can keep the
`ChatOpenAI` integration and isolate provider settings in `llm.py`. The selected
model is OpenAI GPT-4o-mini accessed through OpenRouter.

### Why use structured output?

The graph needs predictable fields: `sql`, `explanation`, and `display_hint`.
Pydantic structured output avoids fragile string splitting and manual JSON parsing.

### Why is answer summarization a separate LLM call?

SQL generation and natural-language explanation have different responsibilities.
Keeping them separate means SQL can be tested and displayed independently, and a
summary failure does not erase valid query results.

### How did you test the project?

There are focused tests for SQL validation, display rules, the graph happy path,
and the repair route. I also tested the four sample questions through the running
API and verified KPI, line, bar, and table results.

### What would you improve for production?

I would add schema caching with invalidation, stronger query timeouts and cost
guards, authentication, audit logging, an evaluation dataset, and tracing. I
left those out of the assignment demo so every current node remains explainable.

## One Honest Limitation To Mention

The validator is deliberately a small demo guard, not a full SQL parser or a
production security system. The read-only connection is the important second
boundary, and a production version would use a real SQL parser plus database
permissions and query resource limits.
