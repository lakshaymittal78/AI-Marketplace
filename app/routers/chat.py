from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from pydantic import BaseModel
from app.agent.graph import build_graph
from fastapi import WebSocket
from app.utils.jwt import decode_access_token
from app.utils.redis import save_to_redis, get_from_redis
from starlette.websockets import WebSocketState
from app.database import SessionLocal, get_db
from sqlalchemy.orm import Session
import json
import traceback
import asyncio
from main import limiter
router = APIRouter(prefix="/chat", tags=["chat"])
agent = build_graph()

NODE_STATUS = {
    "decide":        "Routing to the right agent...",
    "code_plan":     "Planning the solution...",
    "code_execute":  "Writing the code...",
    "code_reflect":  "Reviewing the output...",
    "code_finalize": "Finalizing the solution...",
    "search":        "Searching the web...",
    "chat":          "Thinking...",
    "image":         "Generating image...",
    "ppt":           "Building presentation...",
    "email":         "Preparing email...",
    "rag":           "Retrieving relevant information from your documents..."
}

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

@router.post("")
@limiter.limit("30/minute")
async def chat(request: ChatRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    redis_key = f"chat_history:{current_user.id}"
    stored_history = await get_from_redis(redis_key)
    history = json.loads(stored_history) if stored_history else request.history

    initial_state = {
        "message": request.message,
        "tool": "",
        "response": "",
        "search_result": "",
        "history": history,
        "ppt_path": "",
        "code_plan": "",
        "code_output": "",
        "reflection": "",
        "retry_count": 0,
        "email_details": {},
        "user_id": current_user.id,
        "db": db
    }

    result = await agent.ainvoke(initial_state)
    await save_to_redis(redis_key, json.dumps(result.get("history", [])))
    return {"response": result.get("response", ""), "history": result.get("history", []), "agent_used": result.get("tool", "")}

@router.get("/history")
async def get_history(current_user = Depends(get_current_user)):
    redis_key = f"chat_history:{current_user.id}"
    stored_history = await get_from_redis(redis_key)
    return {"history": json.loads(stored_history) if stored_history else []}

@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    query_params = dict(websocket.query_params)
    token = query_params.get("token")
    data = query_params.get("data")

    if not token or not data:
        await websocket.close(code=4002, reason="Missing token or data")
        return

    user = decode_access_token(token)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await websocket.accept()

    db = SessionLocal()
    heartbeat_task = None
    stream_task = None

    try:
        # Load history from Redis
        redis_key = f"chat_history:{user.get('user_id')}"
        stored_history = await get_from_redis(redis_key)
        history = json.loads(stored_history) if stored_history else []

        initial_state = {
            "message": data,
            "tool": "",
            "response": "",
            "search_result": "",
            "history": history,
            "ppt_path": "",
            "code_plan": "",
            "code_output": "",
            "reflection": "",
            "retry_count": 0,
            "email_details": {},
            "user_id": user.get("user_id"),
            "db": db
        }

        async def send_heartbeat():
            while True:
                try:
                    await asyncio.sleep(3)
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await websocket.send_text("__heartbeat__")
                except Exception as e:
                    print(f"Heartbeat error: {e}")
                    break

        heartbeat_task = asyncio.create_task(send_heartbeat())

        async def process_stream():
            final_history = history.copy()
            try:
                async for chunk in agent.astream(initial_state):
                    for node_name, node_output in chunk.items():
                        status = NODE_STATUS.get(node_name)
                        if status:
                            if websocket.client_state == WebSocketState.CONNECTED:
                                await websocket.send_text(f"__status__{status}")

                        if isinstance(node_output, dict):
                            if "history" in node_output:
                                final_history = node_output["history"]
                            if "response" in node_output:
                                if websocket.client_state == WebSocketState.CONNECTED:
                                    await websocket.send_text(node_output["response"])

                # Save history to Redis
                await save_to_redis(redis_key, json.dumps(final_history))

                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text("[DONE]")

            except asyncio.TimeoutError:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text("__error__Operation timed out")
            except Exception as e:
                error_msg = f"Stream error: {str(e)}"
                print(error_msg)
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(f"__error__{error_msg}")

        stream_task = asyncio.create_task(process_stream())
        await asyncio.wait_for(stream_task, timeout=120)

    except Exception as e:
        error_msg = f"WebSocket error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_text(f"__error__{error_msg}")
            except:
                pass
    finally:
        db.close()
        if heartbeat_task:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
        if stream_task and not stream_task.done():
            stream_task.cancel()
            try:
                await stream_task
            except asyncio.CancelledError:
                pass