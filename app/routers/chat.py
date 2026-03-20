from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from pydantic import BaseModel
from app.agent.graph import build_graph

router = APIRouter(prefix="/chat", tags=["chat"])
agent = build_graph()

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    
@router.post("")
async def chat(request: ChatRequest,current_user = Depends(get_current_user)):
    result = await agent.ainvoke({"message": request.message,"history": request.history})
    return {"response": result["response"], "history": result["history"],"agent_used":result["tool"]}
