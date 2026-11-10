"""End-to-end smoke test with mocked OpenAI + PayPal (no keys needed)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shopping_agent import agent as agent_mod
from shopping_agent import catalog as catalog_mod


class _Msg:
    def __init__(self, content):
        self.content = content


class _Choice:
    def __init__(self, content):
        self.message = _Msg(content)


class _Resp:
    def __init__(self, content):
        self.choices = [_Choice(content)]
        self.usage = None


class _Completions:
    def create(self, **kwargs):
        if kwargs.get("response_format"):
            return _Resp(
                '{"budget_usd": 50, "category": "birthday gift", '
                '"keywords": ["coffee", "mug"], "notes": "mock"}'
            )
        return _Resp("A ceramic mug is a warm, personal gift for a coffee lover.")


class _Chat:
    completions = _Completions()


class FakeClient:
    chat = _Chat()


agent_mod.client_mod.get_client = lambda **kw: FakeClient()
agent_mod.client_mod.get_model = lambda explicit=None: "mock-model"
agent_mod.paypal_mod.get_access_token = lambda *a, **k: "mock-token"
agent_mod.paypal_mod.create_order = lambda token, product: {
    "id": "MOCK-ORDER-1", "status": "CREATED",
    "links": [{"rel": "approve", "href": "https://example.com/approve"}],
}
agent_mod.paypal_mod.capture_order = lambda token, oid: {
    "status": "COMPLETED",
    "purchase_units": [{"payments": {"captures": [{"id": "MOCK-TXN-1"}]}}],
}

result = agent_mod.shop("birthday gift under 50 dollars for a coffee lover")
assert result["parsed"]["budget_usd"] == 50
assert result["matches"], "no matches"
assert result["picked"]["price"] <= 50
assert result["order"]["id"] == "MOCK-ORDER-1"
assert result["approval_url"] == "https://example.com/approve"
receipt = agent_mod.capture(result)
assert "MOCK-TXN-1" in receipt
assert "COMPLETED" in receipt
print("SMOKE OK")
print("picked:", result["picked"]["name"], result["picked"]["price"])
print(receipt)
