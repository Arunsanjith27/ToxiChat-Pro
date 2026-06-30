import re
import html
import hashlib
import secrets
from datetime import datetime, timedelta

try:
    import bcrypt
    _bcrypt_available = True
except ImportError:
    _bcrypt_available = False


def hash_password(password: str) -> str:
    if _bcrypt_available:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password: str, stored: str) -> bool:
    if _bcrypt_available and stored.startswith("$2"):
        return bcrypt.checkpw(password.encode(), stored.encode())
    if "$" in stored:
        salt, hashed = stored.split("$", 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    return False


def migrate_password(password: str, stored: str) -> str | None:
    if _bcrypt_available and not stored.startswith("$2") and verify_password(password, stored):
        return hash_password(password)
    return None


def sanitize_input(text: str) -> str:
    text = html.escape(text.strip())
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    return text[:5000]


ALLOWED_FILE_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_file(content_type: str, size: int) -> bool:
    return content_type in ALLOWED_FILE_TYPES and size <= MAX_FILE_SIZE
