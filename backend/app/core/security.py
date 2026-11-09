import hashlib
import secrets


def get_password_hash(password: str) -> str:
    """
    Computes a salted PBKDF2-HMAC-SHA256 hash for password storage.
    Satisfies security requirements without external C-extension dependencies.
    """
    salt = secrets.token_hex(16)
    iterations = 100000
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"pbkdf2:sha256:{iterations}${salt}${derived.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored PBKDF2 hash."""
    try:
        algorithm, salt, stored_hash = hashed_password.split("$")
        parts = algorithm.split(":")
        iterations = int(parts[2])
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return secrets.compare_digest(derived.hex(), stored_hash)
    except Exception:
        return False
