"""The agent loop: parse a need -> find products -> create a PayPal order -> receipt."""
from . import catalog as catalog_mod
from . import client as client_mod
from . import paypal as paypal_mod


def shop(request_text, catalog_path=None, model=None, api_key=None,
         paypal_client_id=None, paypal_client_secret=None, pick_index=0):
    """Run one shopping trip. Returns a dict with the parsed request, matches,
    the chosen product, the PayPal order and (after capture) the receipt."""
    cli = client_mod.get_client(api_key=api_key)
    model_id = client_mod.get_model(model)

    parsed = client_mod.parse_request(cli, model_id, request_text)
    products = catalog_mod.load_catalog(catalog_path)
    matches = catalog_mod.search(products, parsed, limit=3)
    if not matches:
        return {
            "model": model_id, "parsed": parsed, "matches": [],
            "picked": None, "order": None, "receipt": None,
        }
    picked = matches[min(pick_index, len(matches) - 1)]
    summary = client_mod.summarize_pick(cli, model_id, request_text, picked)

    token = paypal_mod.get_access_token(paypal_client_id, paypal_client_secret)
    order = paypal_mod.create_order(token, picked)
    return {
        "model": model_id,
        "parsed": parsed,
        "matches": matches,
        "picked": picked,
        "summary": summary,
        "order": order,
        "approval_url": paypal_mod.approval_url(order),
        "receipt": None,
    }


def capture(result, paypal_client_id=None, paypal_client_secret=None):
    """Capture the order in `result` (buyer must have approved it first).
    Returns the receipt markdown, and stores the capture on the result."""
    order = result["order"]
    token = paypal_mod.get_access_token(paypal_client_id, paypal_client_secret)
    cap = paypal_mod.capture_order(token, order["id"])
    result["capture"] = cap
    result["receipt"] = receipt_markdown(result, cap)
    return result["receipt"]


def receipt_markdown(result, capture):
    picked = result["picked"]
    txn = paypal_mod.capture_id(capture) or "(capture id not returned)"
    status = capture.get("status", "COMPLETED")
    return (
        "# Receipt\n\n"
        f"**Product:** {picked['name']}\n\n"
        f"**Price:** ${picked['price']:.2f} USD\n\n"
        f"**PayPal order:** {result['order']['id']}\n\n"
        f"**Transaction ID:** {txn}\n\n"
        f"**Status:** {status} (PayPal sandbox)\n\n"
        f"**Why this pick:** {result.get('summary', '')}\n"
    )
