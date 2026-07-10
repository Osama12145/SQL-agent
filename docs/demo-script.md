# Demo Script

## Communication Goal

Show that the project is a small, explainable agentic workflow, not just an
LLM call that happens to return SQL.

The main sentence to remember:

> The LLM proposes structured SQL and a display hint, while LangGraph controls
> validation, repair, execution, and the final data-driven display decision.

## Tools

- VS Code: keep the repository and README open.
- PowerShell: run the API and Streamlit in separate terminals.
- Browser: show the dashboard at `http://127.0.0.1:8501`.
- GitHub: show the README and architecture image only after the live demo.
- OpenRouter: configured through `.env`; never display the key while sharing the screen.

Do not add LangSmith, Postman, or extra tools to the live demo. The browser and
two terminals are enough to prove the assignment.

## Before The Interview

From the project directory:

```powershell
.\.venv\Scripts\Activate.ps1
python data\seed.py
uvicorn backend.main:app --reload
```

In a second terminal:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend\app.py
```

Check `http://127.0.0.1:8000/health`, then open the Streamlit URL. Make sure
`.env` contains the OpenRouter key but do not open the file during screen share.

## 90-Second Demo

### Opening: 10 seconds

Say:

> I kept the UI intentionally minimal because the assignment prioritizes the
> agent workflow. The system receives a natural-language question, generates
> structured SQL, validates and executes it safely, then chooses a display based
> on the actual result shape.

### Query 1: KPI, 15 seconds

Use:

```text
What is the total revenue for completed orders?
```

Say:

> This returns one numeric cell, so the backend selects a KPI. The important
> point is that the frontend does not decide this from the question text; it
> renders the display specification returned by the graph.

Open Generated SQL once and point out that the query is a SELECT with the
expected joins and aggregation.

### Query 2: Line chart, 15 seconds

Use:

```text
Show monthly revenue for completed orders.
```

Say:

> This result has a month column and a numeric revenue column, so it is a time
> series and becomes a line chart. The LLM can suggest line, but the
> `decide_display` node verifies that the returned columns really support it.

### Query 3: Bar chart, 15 seconds

Use:

```text
What are the top 5 products by revenue?
```

Say:

> This is a category-to-number comparison, so a bar chart is more useful than a
> table. The result is limited to five rows, which also keeps the dashboard
> readable.

### Query 4: Table, 15 seconds

Use:

```text
List each product with its category and price.
```

Say:

> This is a detailed multi-column result. A table preserves all fields instead
> of hiding useful information inside a chart.

### Architecture close: 20 seconds

Say:

> If SQL validation or execution fails, the graph routes to `repair_sql` and
> then returns to validation. The repair count is bounded at two attempts, so
> the workflow cannot loop forever or spend unlimited API calls. SQL is also
> protected by a SELECT-only validator and a read-only SQLite connection.

Finish with:

> I chose this architecture because every node has one clear responsibility and
> every important decision is visible in the state.

## What To Show In The Repository

Open these files only when the reviewer asks:

1. `backend/graph.py`: node registration and conditional routes.
2. `backend/state.py`: the shared state and repair limit.
3. `backend/validators.py`: SELECT-only validation and row limit.
4. `backend/db.py`: read-only connection and schema loading.
5. `backend/display.py`: actual result-shape rules.
6. `README.md`: setup, workflow, and decisions.

## If Something Fails

Do not improvise a complex recovery during the interview. Say:

> The API boundary reports provider or configuration failures separately from
> SQL failures. SQL failures are repairable inside the graph; provider failures
> are returned as a clear service error.

Then check `/health`, the API terminal, and that `OPENROUTER_API_KEY` exists in
`.env`. Never reveal the key on screen.

## Presentation Rules

- Start with the working dashboard, not the code.
- Use four questions to show four display types.
- Expand Generated SQL only once; do not read every line aloud.
- Explain one architectural decision after the result it affects.
- Let the reviewer ask for deeper code details instead of opening every file.
- Keep the live demo under two minutes, then move to architecture questions.
