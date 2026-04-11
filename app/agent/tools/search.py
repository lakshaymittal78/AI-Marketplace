from ddgs import DDGS
from app.utils.redis import save_to_redis, get_from_redis, delete_from_redis
import asyncio
import time

async def search_web(query: str) -> str:
    # Check Redis cache first
    cached = await get_from_redis(query)
    print(f"Cache check for query: '{query}' - {'HIT' if cached else 'MISS'}")
    if cached:
        return cached.decode("utf-8")
    
    try:
        # Run DDGS in thread pool to avoid blocking
        results = await asyncio.to_thread(
            lambda: list(DDGS(timeout=10).text(query, max_results=5))
        )
        
        if not results:
            return f"No search results found for: {query}"
        
        formatted = []
        for r in results:
            formatted.append(
                f"Title: {r['title']}\n"
                f"URL: {r['href']}\n" 
                f"Summary: {r['body']}"
            )
        
        result = "\n\n".join(formatted)
        await save_to_redis(query, result)
        return result
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return f"Search failed for query: {query}. Error: {str(e)}"

