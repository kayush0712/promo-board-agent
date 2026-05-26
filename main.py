

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enum import Enum
from pydantic import BaseModel, Field
import json
import asyncio
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models import ReviewSession
from orchestrator import run_full_review, apply_human_decision
from dotenv import load_dotenv
from database import save_human_decision, load_review, get_all_reviews

load_dotenv()


app = FastAPI(title="Promotion Review Board")

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = False,
    allow_methods     = ["*"],
    allow_headers     = ["*"]
)

API_KEY        = os.environ.get("INTERNAL_API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)  

async def verify_api_key(key: str = Security(api_key_header)):

    if key is None:
        raise HTTPException(status_code=403, detail="API key is missing from headers")
    if not API_KEY:
        raise RuntimeError("INTERNAL_API_KEY is not set in environment")
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")

sessions: dict[str, ReviewSession] = {}

async def get_or_restore_session(employee_id: str) -> ReviewSession | None:
    """
    Checks RAM for a session. If missing (e.g. server restarted),
    fetches from MongoDB and restores it to RAM.
    """
    
    if employee_id in sessions:
        return sessions[employee_id]
        
    
    db_review = await load_review(employee_id)
    if not db_review:
        return None 
        
    
    session = ReviewSession(employee_id)
    session.final_packet   = db_review.get("final_packet")
    session.human_decision = db_review.get("human_decision", "pending")
    session.human_comment  = db_review.get("human_comment", "")
    saved_tokens           = db_review.get("token_usage")
    
    if saved_tokens:
        session.tokens.summary = lambda: saved_tokens
    
    sessions[employee_id] = session
    return session

@app.post("/review/{employee_id}", dependencies=[Depends(verify_api_key)])
async def start_review(employee_id: str):
    
    if employee_id in sessions:
        existing = sessions[employee_id]
        if not existing.is_complete():
            raise HTTPException(
                status_code = 409,
                detail      = (
                    f"A review is already in progress for {employee_id}. "
                    f"Wait for it to complete or check /status/{employee_id}"
                )
            )
        # If previous review is complete, allow starting a new one
        # (manager wants to re-review after time has passed)

    # Create new session — safe to do now
    session = ReviewSession(employee_id)
    sessions[employee_id] = session

    async def event_generator():

        async def stream_callback(agent, status, message, data=None):
            
            payload = {
                "agent":   agent,
                "status":  status,
                "message": message,
                "data":    data
            }
            yield f"data: {json.dumps(payload)}\n\n"

        queue = asyncio.Queue(maxsize=50)

        async def queued_callback(agent, status, message, data=None):
            payload = {
                "agent":   agent,
                "status":  status,
                "message": message,
                "data":    data
            }
            try:
            # put_nowait raises QueueFull instead of waiting forever
                queue.put_nowait(f"data: {json.dumps(payload)}\n\n")
            except asyncio.QueueFull:
            # Client is too slow or disconnected — drop this update
            # The review still continues running — we just don't buffer
                print(f"SSE queue full for {employee_id} — dropping update from {agent}")

        # Run review in background task
        async def run_review():
            try:
                await run_full_review(employee_id, session, queued_callback)
            except Exception as e:
                await queue.put(
                    f"data: {json.dumps({'agent': 'system', 'status': 'error', 'message': str(e)})}\n\n"
                )
            finally:
                # Signal stream is done
                await queue.put(None)

        # Start review in background
        asyncio.create_task(run_review())

        # Stream queue items to frontend
        while True:
            item = await queue.get()
            if item is None:
                break
            yield item

    return StreamingResponse(
        event_generator(),
        media_type = "text/event-stream",
        headers    = {
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering":"no"
        }
    )


class DecisionEnum(str, Enum):

    approved = "approved"
    rejected = "rejected"

class DecisionRequest(BaseModel):
    decision: DecisionEnum          
    comment:  str = Field(
        default    = "",
        max_length = 2000         
    )


@app.post("/decide/{employee_id}", dependencies=[Depends(verify_api_key)])
async def make_decision(employee_id: str, body: DecisionRequest):

    # ⬇️ THE FIX: Use our new lazy-loader
    session = await get_or_restore_session(employee_id)
    
    if not session:
        raise HTTPException(status_code=404, detail=f"No active review for {employee_id}")

    if session.final_packet is None:
        raise HTTPException(status_code=400, detail="Review not complete yet")

    if session.is_complete():
        raise HTTPException(status_code=409, detail=f"Decision already recorded as '{session.human_decision}'")

    # Save to RAM
    result = apply_human_decision(session, body.decision.value, body.comment)

    # Save to MongoDB
    await save_human_decision(employee_id, body.decision.value, body.comment)

    # 🧹 PREVENT RAM LEAK: Since it's done, clear it from RAM
    sessions.pop(employee_id, None)

    return result



@app.get("/status/{employee_id}", dependencies=[Depends(verify_api_key)])
async def get_status(employee_id: str):
    
    # ⬇️ THE FIX: Use our new lazy-loader
    session = await get_or_restore_session(employee_id)
    
    if not session:
        raise HTTPException(
            status_code = 404,
            detail      = f"No review found for {employee_id}"
        )

    return session.summary()

@app.get("/history", dependencies=[Depends(verify_api_key)])
async def get_history():
    """
    Returns all past reviews.
    Useful for building a dashboard.
    Survives server restarts.
    """
    reviews = await get_all_reviews(limit=50)
    return {"reviews": reviews, "count": len(reviews)}

@app.get("/history/{employee_id}", dependencies=[Depends(verify_api_key)])
async def get_review_history(employee_id: str):
    """
    Returns the full saved review for one employee.
    Works even after server restart.
    """
    review = await load_review(employee_id)
    if not review:
        raise HTTPException(status_code=404, detail=f"No review history found for {employee_id}")
    return review
# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "status":  "running",
        "message": "Promotion Review Board API",
        "docs":    "http://localhost:8000/docs"
    }