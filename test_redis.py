import requests
import json

# Test the chat endpoint (correct path with router prefix)
url = "http://localhost:8000/chat/test"
payload = {
    "message": "Hello, Redis is working now!",
    "history": []
}

print("Sending request to", url)
try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Check Redis
import subprocess
redis_check = subprocess.run(
    ["docker", "exec", "redis", "redis-cli", "keys", "*"],
    capture_output=True,
    text=True
)
print("\nRedis Keys:")
print(redis_check.stdout)

# Get the actual content
redis_get = subprocess.run(
    ["docker", "exec", "redis", "redis-cli", "get", "chat_history:3"],
    capture_output=True,
    text=True
)
print("\nRedis Content (chat_history:3):")
print(redis_get.stdout[:500])  # First 500 chars

