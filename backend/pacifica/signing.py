"""
Pacifica message signing utilities.

Mirrors the signing pattern from the official pacifica-fi/python-sdk:
- Recursive alphabetical JSON key sorting
- Compact JSON serialization (no spaces)
- Ed25519 signing via solders Keypair
- Base58-encoded signature output
"""

import json
import base58
from solders.keypair import Keypair


def sort_json_keys(value):
    """Recursively sort all dictionary keys alphabetically."""
    if isinstance(value, dict):
        return {key: sort_json_keys(value[key]) for key in sorted(value.keys())}
    elif isinstance(value, list):
        return [sort_json_keys(item) for item in value]
    return value


def prepare_message(header: dict, payload: dict) -> str:
    """Build the canonical message string for signing."""
    for key in ("type", "timestamp", "expiry_window"):
        if key not in header:
            raise ValueError(f"Header must contain '{key}'")

    data = {**header, "data": payload}
    sorted_data = sort_json_keys(data)
    return json.dumps(sorted_data, separators=(",", ":"))


def sign_message(header: dict, payload: dict, keypair: Keypair) -> tuple[str, str]:
    """
    Sign a Pacifica API message.

    Returns:
        (message_string, base58_signature)
    """
    message = prepare_message(header, payload)
    message_bytes = message.encode("utf-8")
    signature = keypair.sign_message(message_bytes)
    return message, base58.b58encode(bytes(signature)).decode("ascii")
