import httpx
import os
from typing import AsyncGenerator
import json

async def handle_code(topic: str, code_plan: str = "") -> AsyncGenerator[str, None]:
    prompt = topic
    if code_plan:   
        prompt = f"Problem: {topic}\n\nFollow this plan:\n{code_plan}\n\nNow write the code."
    
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 1024,
                "stream": True,
                "messages": [
                    {"role": "system", "content": "You are an expert programmer. Help with code"},
                    {"role": "user", "content": prompt}
                ]
            }
        ) as response:
            async for line in response.aiter_lines():
                if not line:
                    continue
                if line == "data: [DONE]":
                    break
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta",{})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue