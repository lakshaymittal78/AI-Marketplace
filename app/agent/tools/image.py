from app.utils.redis import save_to_redis, get_from_redis, delete_from_redis
async def handle_image(prompt: str) -> str:
    cached = await get_from_redis(prompt)
    if cached:
        return cached.decode("utf-8")
    clean_prompt = prompt.replace(" ", "%20")
    image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}"
    await save_to_redis(prompt, image_url)
    return f"Here is your image: {image_url}"