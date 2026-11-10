"""PayPal sandbox, Orders v2 (create -> buyer approves -> capture).

Sandbox only. Credentials come from the environment (PAYPAL_CLIENT_ID,
PAYPAL_CLIENT_SECRET) or explicit arguments; they are never written to disk.
"""
import base64
import json
import os
import urllib.error
import urllib.request

SANDBOX_BASE = "https://api-m.sandbox.paypal.com"
ENV_CLIENT_ID = "PAYPAL_CLIENT_ID"
ENV_CLIENT_SECRET = "PAYPAL_CLIENT_SECRET"


class PayPalError(RuntimeError):
    pass


def _request(method, url, token=None, payload=None, basic=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if basic:
        headers["Authorization"] = f"Basic {basic}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise PayPalError(f"PayPal {method} {url} failed ({e.code}): {body}")


def get_access_token(client_id=None, client_secret=None):
    cid = client_id or os.environ.get(ENV_CLIENT_ID)
    sec = client_secret or os.environ.get(ENV_CLIENT_SECRET)
    if not cid or not sec:
        raise PayPalError(
            f"{ENV_CLIENT_ID} and {ENV_CLIENT_SECRET} are not set. Create a "
            f"sandbox app at https://developer.paypal.com/dashboard/applications/sandbox"
        )
    basic = base64.b64encode(f"{cid}:{sec}".encode()).decode()
    # Token endpoint takes form-encoded body, not JSON.
    req = urllib.request.Request(
        f"{SANDBOX_BASE}/v1/oauth2/token",
        data=b"grant_type=client_credentials",
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)["access_token"]
    except urllib.error.HTTPError as e:
        raise PayPalError(f"PayPal token request failed ({e.code}): {e.read().decode(errors='replace')}")


def create_order(token, product):
    """Create a sandbox order for one product. Returns the order JSON."""
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": f"{product['price']:.2f}",
            },
            "description": f"{product['name']} ({product['id']})",
        }],
        "application_context": {
            "brand_name": "Agentic Commerce Shopping Agent",
            "user_action": "PAY_NOW",
            "return_url": "https://example.com/return",
            "cancel_url": "https://example.com/cancel",
        },
    }
    return _request("POST", f"{SANDBOX_BASE}/v2/checkout/orders", token=token, payload=payload)


def get_order(token, order_id):
    return _request("GET", f"{SANDBOX_BASE}/v2/checkout/orders/{order_id}", token=token)


def capture_order(token, order_id):
    """Capture an approved order. Returns the capture JSON.

    Raises PayPalError if the order has not been approved yet
    (ORDER_NOT_APPROVED) or is already captured.
    """
    return _request("POST", f"{SANDBOX_BASE}/v2/checkout/orders/{order_id}/capture",
                    token=token, payload={})


def approval_url(order):
    for link in order.get("links", []):
        if link.get("rel") == "approve":
            return link["href"]
    return None


def capture_id(capture):
    """Extract the PayPal transaction id from a capture response."""
    try:
        units = capture["purchase_units"]
        payments = units[0]["payments"]["captures"]
        return payments[0]["id"]
    except (KeyError, IndexError, TypeError):
        return None
