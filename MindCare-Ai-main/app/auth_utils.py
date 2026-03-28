# MindCare AI - Password hashing (Werkzeug). Security-critical: never log or expose hashes.

from werkzeug.security import generate_password_hash, check_password_hash

# Method and salt length; default 'pbkdf2:sha256' is fine for session-based auth
def hash_password(plain: str) -> str:
    return generate_password_hash(plain, method="pbkdf2:sha256")

def check_password(plain: str, hashed: str) -> bool:
    if not hashed:
        return False
    return check_password_hash(hashed, plain)
