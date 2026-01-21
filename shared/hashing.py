import hashlib

def compute_bucket(feature_flag, user_id):
    """
    Computes a hash bucket for a given user and feature flag.
    Function is deterministic and will always return the same bucket for the same inputs.
    
    Args:
        user_id (str): The unique identifier for the user.
        feature_flag (str): The name of the feature flag.
    Returns:
        int: A hash bucket value between 0 and 9999.
    """
    if not user_id or not feature_flag:
        raise ValueError("Both user_id and feature_flag must be provided and non-empty.")
    key = f"{user_id}.{feature_flag}".encode('utf-8')
    hash_digest = hashlib.sha256(key).hexdigest()
    hash_int = int(hash_digest, 16)
    normalized = hash_int / (2**256)
    return normalized * 100.0
