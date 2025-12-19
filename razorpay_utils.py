import hmac
import hashlib

def verify_signature(order_id, payment_id, signature, secret):
    body = f"{order_id}|{payment_id}"
    expected_signature = hmac.new(
        bytes(secret, 'utf-8'),
        bytes(body, 'utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)
