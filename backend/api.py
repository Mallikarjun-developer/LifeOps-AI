
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from agent import respond, call_tool

load_dotenv(Path(__file__).with_name(".env"))
log = logging.getLogger(__name__)

app = FastAPI(title="LifeOps AI", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001", "http://127.0.0.1:8001"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class Chat(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

class NewTask(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    due: str = ""
    duration: int = Field(default=30, ge=5, le=480)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")

class EditTask(BaseModel):
    title: str | None = None
    due: str | None = None
    duration: int | None = None
    priority: str | None = None
    status: str | None = None

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "mcp_endpoint": os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp"),
        "ai_configured": bool(os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"))
    }

@app.post("/api/chat")
async def chat(payload: Chat):
    try:
        return await respond(payload.message)
    except Exception:
        log.exception("Chat failed")
        raise HTTPException(500, "Chat failed. Check backend terminal for details.")

@app.get("/api/tasks")
async def tasks():
    try:
        return await call_tool("list_tasks")
    except Exception:
        log.exception("List tasks failed")
        raise HTTPException(503, "MCP task service unavailable")

@app.post("/api/tasks")
async def create(payload: NewTask):
    try:
        return await call_tool("create_task", payload.model_dump())
    except Exception as e:
        raise HTTPException(400, str(e))

@app.patch("/api/tasks/{task_id}")
async def edit(task_id: int, payload: EditTask):
    try:
        return await call_tool("edit_task", {
            "task_id": task_id,
            **payload.model_dump(exclude_none=True)
        })
    except Exception as e:
        raise HTTPException(400, str(e))

@app.delete("/api/tasks/{task_id}")
async def delete(task_id: int):
    try:
        return await call_tool("remove_task", {"task_id": task_id})
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/api/plan")
async def replan():
    try:
        return await call_tool("replan_schedule")
    except Exception as e:
        raise HTTPException(400, str(e))

FRONT = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/assets", StaticFiles(directory=FRONT), name="assets")

@app.get("/")
async def index():
    return FileResponse(FRONT / "index.html")
