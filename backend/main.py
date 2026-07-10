from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.graph import build_graph

load_dotenv()


app = FastAPI(title="Agentic SQL Dashboard")
agent = build_graph()


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query")
def query(request: QueryRequest) -> dict:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Provider failures are not repairable SQL errors, so handle them at the API edge.
    try:
        final_state = agent.invoke({"question": question, "attempts": 0})
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="The query could not be completed. Please try again.",
        ) from exc

    return {
        "answer": final_state.get("answer"),
        "sql": final_state.get("sql"),
        "sql_explanation": final_state.get("sql_explanation"),
        "rows": final_state.get("rows", []),
        "columns": final_state.get("columns", []),
        "display": final_state.get("display"),
        "error": final_state.get("error"),
    }
