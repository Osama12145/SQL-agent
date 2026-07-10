# Agentic SQL Dashboard

A small LangGraph project that converts a natural-language question into SQL,
runs it on SQLite, and returns an answer with a suitable dashboard element.
The code is intentionally compact so every node and decision can be explained.

## Stack

- Backend: FastAPI
- Agent workflow: LangGraph
- Database: SQLite
- Frontend: Streamlit
- LLM gateway: OpenRouter through `langchain-openai`
- Model: `openai/gpt-4o-mini-2024-07-18`

OpenRouter exposes an OpenAI-compatible API, so the project keeps the familiar
`ChatOpenAI` client and only changes the API key, base URL, and model name.

## Setup

From the project directory, create a virtual environment and install the
dependencies.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `OPENROUTER_API_KEY` in `.env`, then create the demo database:

```bash
python data/seed.py
```

Run the API:

```bash
uvicorn backend.main:app --reload
```

Run the dashboard in another terminal:

```bash
streamlit run frontend/app.py
```

Open `http://localhost:8501` in a browser.

## Sample Questions

| Question | Expected display |
| --- | --- |
| What is the total revenue for completed orders? | KPI |
| Show monthly revenue for completed orders. | Line chart |
| What are the top 5 products by revenue? | Bar chart |
| List each product with its category and price. | Table |

These display types are not hardcoded to the questions. `decide_display` checks
the returned columns and only accepts the LLM hint when it fits the real result.

## Agent Workflow

![LangGraph agent workflow](docs/agent-workflow.svg)

The diagram source is kept in `docs/agent-workflow.mmd` so it can be regenerated
when the graph changes.

The graph stops after `MAX_REPAIR_ATTEMPTS = 2`, so a bad query cannot create an
infinite repair loop.

## Project Structure

- `backend/state.py`: fields shared between graph nodes and the repair limit.
- `backend/graph.py`: nodes, conditional routes, and state transitions.
- `backend/llm.py`: OpenRouter model setup and structured LLM calls.
- `backend/prompts.py`: generation, repair, and summary instructions.
- `backend/validators.py`: SELECT-only checks and row limit.
- `backend/db.py`: schema loading and read-only SQL execution.
- `backend/display.py`: verifies the LLM display hint against actual rows.
- `backend/main.py`: FastAPI endpoints and request-level error handling.
- `frontend/app.py`: minimal Streamlit dashboard.
- `data/seed.py`: creates the retail demo database.
- `tests/`: focused validator, display, and graph-routing tests.
- `docs/demo-script.md`: live demo sequence, tools, and exact speaking prompts.
- `docs/interview-qa.md`: expected architecture, safety, and trade-off questions.
- `docs/demo-guide-ar.md`: Arabic demo guidance and speaking order.
- `docs/interview-qa-ar.md`: Arabic interview preparation notes.
- `outputs/agentic-sql-interview.pptx`: interview slide deck.

## Key Decisions

The state is a small `TypedDict`. Each node reads only the fields it needs and
returns only the fields it changes, which makes state flow easy to trace.

The LLM returns structured output containing SQL, an explanation, and a display
hint. The hint is checked after SQL execution because the actual rows are more
reliable than a prediction made before the query runs.

SQL execution has two safety layers. The validator allows one SELECT statement,
and SQLite is opened in read-only mode. Invalid SQL can be repaired twice before
the graph returns a controlled failure.

Streamlit was chosen because the assignment prioritizes agent behavior over UI
styling. It provides tables, charts, and KPI metrics with very little frontend
code.

## Tests

```bash
pytest
```

The tests cover SQL validation, display rules, the happy graph path, and the
repair route without making real LLM calls.
