import os

os.environ.setdefault("MONGO_URL", "mongodb://127.0.0.1:1")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:1")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
import database as db


@pytest.fixture(autouse=True)
def reset_memory_store():
    db._use_memory = True
    db._db = "memory"
    db._memory_store = {"users": [], "messages": [], "groups": [], "reset_tokens": []}
    yield
