"""
Pacifica Builder Code management.

Builder codes are registered with Pacifica and embedded in every order
placed by Zerova. Users must approve the builder code once before
the protocol can trade on their behalf.
"""

import time
import httpx
from solders.keypair import Keypair

from config import settings
from pacifica.signing import sign_message

ZEROVA_BUILDER_CODE = settings.pacifica_builder_code  # "ZEROVA01"
BUILDER_MAX_FEE_RATE = str(settings.vault_builder_fee_rate)  # "0.0005"


async def approve_builder_code(
    user_keypair: Keypair,
    builder_code: str = ZEROVA_BUILDER_CODE,
    max_fee_rate: str = BUILDER_MAX_FEE_RATE,
) -> dict:
    """
    Submit a signed builder code approval on behalf of a user.
    This allows Zerova to place orders with the builder code attached.
    """
    public_key = str(user_keypair.pubkey())
    timestamp = int(time.time() * 1000)

    header = {
        "type": "approve_builder_code",
        "timestamp": timestamp,
        "expiry_window": 5000,
    }
    payload = {
        "builder_code": builder_code,
        "max_fee_rate": max_fee_rate,
    }

    _, signature = sign_message(header, payload, user_keypair)

    request_body = {
        "account": public_key,
        "signature": signature,
        "timestamp": timestamp,
        "expiry_window": 5000,
        **payload,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.pacifica_api_url}/account/builder_codes/approve",
            json=request_body,
        )
        resp.raise_for_status()
        return resp.json()


async def revoke_builder_code(
    user_keypair: Keypair,
    builder_code: str = ZEROVA_BUILDER_CODE,
) -> dict:
    """Revoke builder code authorization for a user."""
    public_key = str(user_keypair.pubkey())
    timestamp = int(time.time() * 1000)

    header = {
        "type": "revoke_builder_code",
        "timestamp": timestamp,
        "expiry_window": 5000,
    }
    payload = {"builder_code": builder_code}

    _, signature = sign_message(header, payload, user_keypair)

    request_body = {
        "account": public_key,
        "signature": signature,
        "timestamp": timestamp,
        "expiry_window": 5000,
        **payload,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.pacifica_api_url}/account/builder_codes/revoke",
            json=request_body,
        )
        resp.raise_for_status()
        return resp.json()


async def check_approvals(wallet_address: str) -> dict:
    """Check which builder codes a wallet has approved."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.pacifica_api_url}/account/builder_codes/approvals",
            params={"account": wallet_address},
        )
        resp.raise_for_status()
        return resp.json()
