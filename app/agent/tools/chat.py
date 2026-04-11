import httpx
import os

async def handle_chat(message: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": message}]
            }
        )
    return response.json()["choices"][0]["message"]["content"]

async def handle_chat_with_history(messages: list[dict]) -> str:
    last_message = messages[-1]["content"] if messages else ""
    has_rag_context = "Document context:" in last_message
    system_prompt = (
        "You are a helpful assistant that can use tools to answer questions. "
        "Answer using ONLY the provided Document context"
        if has_rag_context else
        "You are a helpful assistant that can use tools to answer questions."
    )
    final_messages = [{"role": "system", "content": system_prompt}] + messages
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 1024,
                "messages": final_messages
            }
        )
    return response.json()["choices"][0]["message"]["content"]