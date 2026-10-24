import hashlib
import secrets

def generate_api_key() -> tuple[str, str]:
    """
    Generates a secure API key and its SHA-256 hash.
    Returns (plaintext_key, hashed_key).
    Plaintext key must be shown to the user exactly once.
    """
    # 32 bytes of randomness, base64url encoded for safely passing in headers
    raw_key = secrets.token_urlsafe(32)
    api_key = f"asoc_{raw_key}"
    
    # Hash for storage
    key_hash = hashlib.sha256(api_key.encode('utf-8')).hexdigest()
    
    return api_key, key_hash

def verify_api_key(plaintext_key: str, hashed_key: str) -> bool:
    """
    Verifies a plaintext key against the stored hash.
    """
    candidate_hash = hashlib.sha256(plaintext_key.encode('utf-8')).hexdigest()
    return secrets.compare_digest(candidate_hash, hashed_key)
