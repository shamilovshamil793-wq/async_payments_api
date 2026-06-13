import hashlib
import os

WEBHOOK_SECRET_KEY = os.getenv("WEBHOOK_SECRET_KEY", "gfdmhghif38yrf9ew0jkf32")

def generate_signature(data: dict, secret_key: str = WEBHOOK_SECRET_KEY) -> str:
    sorted_keys = sorted([k for k in data.keys() if k != "signature"])
    parts = [str(data[key]) for key in sorted_keys]
    parts.append(secret_key)
    raw_string = "".join(parts)
    return hashlib.sha256(raw_string.encode()).hexdigest()

def verify_signature(data: dict) -> bool:
    received_signature = data.pop("signature", None)
    if not received_signature:
        return False
    expected_signature = generate_signature(data)
    # Возвращаем signature обратно в data (чтобы не менять исходный объект)
    data["signature"] = received_signature
    return expected_signature == received_signature
