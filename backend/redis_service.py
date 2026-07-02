import os
import json
from datetime import datetime

_redis = None
_use_memory = True
_memory_cache = {"presence": {}, "messages": {}, "typing": {}}


async def init_redis():
    global _redis, _use_memory
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    try:
        import redis.asyncio as aioredis
        _redis = aioredis.from_url(redis_url, decode_responses=True)
        await _redis.ping()
        _use_memory = False
        print(f"Redis connected: {redis_url}")
    except Exception as e:
        print(f"[WARNING] Redis unavailable ({e}), using in-memory cache")
        print("[WARNING] WARNING: Rate limiting will NOT persist across restarts!")
        _use_memory = True


async def set_user_presence(username: str, online: bool):
    data = json.dumps({"online": online, "last_seen": datetime.utcnow().isoformat()})
    if _use_memory:
        _memory_cache["presence"][username] = data
    else:
        await _redis.set(f"presence:{username}", data, ex=86400)


async def get_user_presence(username: str) -> dict:
    if _use_memory:
        raw = _memory_cache["presence"].get(username)
    else:
        raw = await _redis.get(f"presence:{username}")
    return json.loads(raw) if raw else {"online": False, "last_seen": None}


async def cache_message(chat_key: str, message: dict, max_cache: int = 100):
    data = json.dumps(message)
    if _use_memory:
        if chat_key not in _memory_cache["messages"]:
            _memory_cache["messages"][chat_key] = []
        _memory_cache["messages"][chat_key].append(data)
        _memory_cache["messages"][chat_key] = _memory_cache["messages"][chat_key][-max_cache:]
    else:
        await _redis.rpush(f"chat:{chat_key}", data)
        await _redis.ltrim(f"chat:{chat_key}", -max_cache, -1)
        await _redis.expire(f"chat:{chat_key}", 3600)


async def get_cached_messages(chat_key: str) -> list:
    if _use_memory:
        return [json.loads(m) for m in _memory_cache["messages"].get(chat_key, [])]
    raw = await _redis.lrange(f"chat:{chat_key}", 0, -1)
    return [json.loads(m) for m in raw] if raw else []


async def set_typing(username: str, receiver: str):
    if _use_memory:
        _memory_cache["typing"][f"{username}:{receiver}"] = datetime.utcnow().isoformat()
    else:
        await _redis.set(f"typing:{username}:{receiver}", "1", ex=5)


async def increment_rate(key: str, window: int = 60) -> int:
    if _use_memory:
        now = datetime.utcnow().timestamp()
        cache_key = f"rate:{key}"
        if cache_key not in _memory_cache:
            _memory_cache[cache_key] = []
        _memory_cache[cache_key] = [t for t in _memory_cache[cache_key] if now - t < window]
        _memory_cache[cache_key].append(now)
        return len(_memory_cache[cache_key])
    pipe = _redis.pipeline()
    pipe.incr(f"rate:{key}")
    pipe.expire(f"rate:{key}", window)
    results = await pipe.execute()
    return results[0]

async def record_failed_login(username: str, window: int = 900) -> int:
    if _use_memory:
        now = datetime.utcnow().timestamp()
        cache_key = f"failed_login:{username}"
        if cache_key not in _memory_cache:
            _memory_cache[cache_key] = []
        # Keep only failures within the window
        _memory_cache[cache_key] = [t for t in _memory_cache[cache_key] if now - t < window]
        _memory_cache[cache_key].append(now)
        return len(_memory_cache[cache_key])
    
    pipe = _redis.pipeline()
    pipe.incr(f"failed_login:{username}")
    pipe.expire(f"failed_login:{username}", window)
    results = await pipe.execute()
    return results[0]

async def check_lockout(username: str, threshold: int = 5) -> bool:
    if _use_memory:
        cache_key = f"failed_login:{username}"
        fails = len(_memory_cache.get(cache_key, []))
        return fails >= threshold
        
    val = await _redis.get(f"failed_login:{username}")
    if val and int(val) >= threshold:
        return True
    return False

async def clear_failed_logins(username: str):
    if _use_memory:
        cache_key = f"failed_login:{username}"
        if cache_key in _memory_cache:
            _memory_cache[cache_key] = []
    else:
        await _redis.delete(f"failed_login:{username}")
