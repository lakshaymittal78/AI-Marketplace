from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from app.models.user import User
from app.database import SessionLocal
from app.utils.redis import redis_client  # use raw client for atomic ops


# ---------------------------
# DB Session Manager (safe)
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TokenTracker:
    def __init__(self, user_id: int):
        self.user_id = user_id

    # ---------------------------
    # Redis Key Generator
    # ---------------------------
    def _get_key(self):
        now = datetime.utcnow()
        return f"tokens:{self.user_id}:{now.year}:{now.month}"

    # ---------------------------
    # Expiry (end of month)
    # ---------------------------
    def _seconds_until_month_end(self):
        now = datetime.utcnow()
        next_month = (now.replace(day=28) + timedelta(days=4)).replace(day=1)
        return int((next_month - now).total_seconds())

    # ---------------------------
    # Get Token Limit (DB)
    # ---------------------------
    def get_tokens_limit(self):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == self.user_id).first()
            return user.tokens_limit if user else None
        finally:
            db.close()

    # ---------------------------
    # Get Current Usage (ASYNC)
    # ---------------------------
    async def get_current_usage(self):
        key = self._get_key()
        current = await redis_client.get(key)
        return int(current) if current else 0

    # ---------------------------
    # Atomic Increment (ASYNC SAFE ⚡)
    # ---------------------------
    async def increment_token(self, tokens_used: int):
        key = self._get_key()

        # Atomic increment
        new_total = await redis_client.incrby(key, tokens_used)

        # Set expiry only if key is new
        if new_total == tokens_used:
            await redis_client.expire(key, self._seconds_until_month_end())

        # Check limit AFTER increment (rollback if exceeded)
        limit = self.get_tokens_limit()
        if limit and new_total > limit:
            # rollback
            await redis_client.decrby(key, tokens_used)
            raise Exception("Token limit exceeded")

        return new_total

    # ---------------------------
    # Check Remaining Tokens (ASYNC)
    # ---------------------------
    async def get_remaining_tokens(self):
        limit = self.get_tokens_limit()
        if not limit:
            return None

        usage = await self.get_current_usage()
        return max(limit - usage, 0)

    # ---------------------------
    # Usage Warning (80%) (ASYNC)
    # ---------------------------
    async def check_warning(self):
        limit = self.get_tokens_limit()
        usage = await self.get_current_usage()

        if not limit:
            return None

        percent = usage / limit

        if percent >= 1:
            return "LIMIT_EXCEEDED"
        elif percent >= 0.8:
            return "WARNING_80_PERCENT"
        return "OK"