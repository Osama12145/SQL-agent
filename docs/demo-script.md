# Demo Script For The Updated Deck

## Communication Goal

Show that the project is small by design, but architecturally complete: the LLM
proposes SQL, while LangGraph makes validation, repair, execution, and display
decisions explicit and bounded.

Remember this sentence:

> The LLM proposes structured SQL and a display hint, while LangGraph controls
> validation, repair, execution, and the final data-driven display decision.

## Important Accuracy Fix

Before presenting, replace the Slide 3 subtitle with:

> The graph is defined in code; this diagram makes its nodes and routes easy to review.

The project keeps its workflow diagram as Mermaid/SVG documentation alongside
backend/graph.py. It is not automatically exported at runtime, so this wording
is accurate and easy to defend in the interview.

## Before The Interview

Run the API in one PowerShell window:

~~~powershell
cd C:\tmp\agentic_sql_dashboard
.\.venv\Scripts\python.exe data\seed.py
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
~~~

Run the dashboard in a second window:

~~~powershell
cd C:\tmp\agentic_sql_dashboard
.\.venv\Scripts\streamlit.exe run frontend\app.py
~~~

Check http://127.0.0.1:8000/health, then open http://127.0.0.1:8501. Keep
terminals open but do not share them. Test the four sample questions before the
meeting.

## Slide-By-Slide Speaking Script

### Slide 1: Opening

> Good morning. This is an Agentic SQL Dashboard built with LangGraph. A user
> asks a business question in natural language, the system generates safe SQL,
> executes it against a read-only SQLite database, and returns both an answer
> and a dashboard view that fits the result.

> I intentionally kept the interface small. For this assignment, the important
> part is making the agent workflow and its engineering decisions easy to see
> and explain.

### Slide 2: The End-To-End Contract

> This slide shows the complete contract. The user asks a natural-language
> question. The LLM returns structured SQL, an explanation, and a display hint.
> The SQL is validated, row-limited, and executed through a read-only
> connection. Finally, the system returns a written answer and a display chosen
> from the actual rows.

> The UI is intentionally minimal because the engineering decisions are the
> product being evaluated here.

### Slide 3: Why LangGraph

> I used LangGraph because this is not a single prompt followed by one database
> call. It has state and meaningful branches. Validation can fail, execution can
> fail, and both failures can be repaired before the workflow continues.

> Each node has one responsibility: load the schema, generate SQL, validate it,
> execute it, decide the display, and summarize the result. The conditional
> routes make the recovery path visible instead of hiding it inside one large
> function.

> The repair loop is bounded by two attempts. That demonstrates self-correction
> without allowing unlimited latency or API cost.

### Slide 4: State

> The shared state is deliberately small. It contains the user question and
> schema, the SQL work, the returned rows and display result, and two control
> fields: attempts and error.

> Each node reads only the fields it needs and returns only the fields it owns.
> LangGraph merges those partial updates, which makes the flow traceable and
> keeps hidden memory out of the design.

### Slide 5: SQL Safety

> LLM-generated SQL should never be trusted directly, so I used defense in
> depth. The first layer is readable application policy: one SELECT statement,
> blocked write keywords, and a LIMIT of 100 rows.

> The second layer is enforced by SQLite itself. The database is opened with
> read-only mode, so it cannot be modified even if the validator misses an edge
> case. EXPLAIN QUERY PLAN also lets execution planning errors enter the same
> controlled repair route.

### Slide 6: Display Decision

> The LLM suggests a display type because it understands intent. For example,
> compare suggests a bar chart, trend suggests a line chart, and total suggests
> a KPI.

> But the suggestion is not the final authority. After execution, the
> decide_display node checks the real result shape. One numeric value becomes a
> KPI, date plus number becomes a line chart, category plus number becomes a bar
> chart, and detailed rows become a table. The Streamlit frontend only renders
> that backend decision.

### Slide 7: Transition To The Live Demo

> The slides explain the decisions. I will now use these four questions to show
> that the dashboard changes its primary display from the returned data.

## Live Dashboard

### KPI

Question:

~~~text
What is the total revenue for completed orders?
~~~

Say:

> This returns one numeric value, so the backend selects a KPI. The frontend did
> not choose this from the words in the question; it received a display
> specification after the SQL result was inspected.

### Line

Question:

~~~text
Show monthly revenue for completed orders.
~~~

Say:

> This result has a month column and a numeric revenue column, so it becomes a
> line chart. This is where the actual result confirms the LLM's trend hint.

### Bar

Question:

~~~text
What are the top 5 products by revenue?
~~~

Say:

> Here the data compares product categories with a numeric revenue value, so a
> bar chart is the most useful view. I will open Generated SQL once to show that
> the executed query is visible for transparency and debugging.

### Table

Question:

~~~text
List each product with its category and price.
~~~

Say:

> This is a detailed multi-column result. A table preserves the useful detail,
> whereas a chart would hide it.

Do not force an error live. Say instead:

> If validation or execution failed, the graph would route through repair_sql,
> return to validation, and stop with a clear failure after two repair attempts.

### Slide 8: Technology Choices

> Each technology was selected for the evaluation scope. FastAPI creates a small
> typed boundary between the UI and graph. SQLite keeps the demo self-contained.
> Streamlit provides input, KPIs, charts, and tables without a large frontend.
> OpenRouter is OpenAI-compatible, so provider settings stay isolated in one
> module while the project retains the standard ChatOpenAI client.

### Slide 9: Honest Scope

> This project is deliberately small, not presented as production-complete. The
> current validator is a readable demo guard rather than a full SQL parser. For
> production, I would add database permissions, a proper parser, resource
> limits, authentication, auditing, schema caching, evaluations, and tracing.

> The important point is that these are explicit next steps, not hidden gaps in
> the current design.

### Slide 10: Closing

> To summarize: the LLM proposes structured SQL and a display hint, while
> LangGraph controls validation, repair, execution, and the final data-driven
> display decision. I kept every current node small enough to explain, test, and
> improve independently.

## If A Reviewer Asks For Code

Open only the file that answers the question:

1. backend/graph.py: nodes and conditional routes.
2. backend/state.py: shared fields and repair limit.
3. backend/validators.py: SELECT-only policy and LIMIT.
4. backend/db.py: read-only connection and schema loading.
5. backend/display.py: result-shape rules.
6. README.md: setup and architectural decisions.

## Presentation Rules

- Present Slides 1 to 7, then the dashboard, then Slides 8 to 10.
- Keep the live demo under two minutes.
- Open Generated SQL once only.
- Do not show .env, terminals, or every source file.
- If a provider error occurs, explain it as a service failure rather than a
  repairable SQL error, then continue with the prepared architecture explanation.
