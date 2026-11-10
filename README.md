# Agentic Commerce Shopping Agent

An AI shopping agent for the **PayPal AI Hackathon**. Describe a need in plain
language and the agent closes the loop to a paid order: it parses the request
with GPT-6 Luna, finds the product in a built-in catalog, creates a real
**PayPal sandbox** order (Orders v2), and captures the payment after you
approve it — ending with a receipt that carries a real PayPal transaction ID.

## How it uses PayPal and AI

| Layer | What | Why |
|---|---|---|
| AI | **GPT-6 Luna** (`gpt-6-luna`) via the OpenAI API, reasoning effort `none` | Parses the request into structured JSON (budget, category, keywords) and explains each pick |
| Payments | **PayPal sandbox, Orders v2** (`api-m.sandbox.paypal.com`) | Every checkout is a real sandbox transaction: create order -> buyer approves -> capture -> transaction ID |
| Catalog | Built-in `data/catalog.json` (18 products) | The agent searches and ranks real products by budget and keyword match |

## Quickstart

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=<your OpenAI key>
export PAYPAL_CLIENT_ID=<your sandbox app client id>
export PAYPAL_CLIENT_SECRET=<your sandbox app secret>

# One shopping trip from the command line:
python -m shopping_agent.cli "birthday gift under 50 dollars for a coffee lover"

# Approve the printed URL in your browser (sandbox buyer account), then capture:
python -m shopping_agent.cli "birthday gift under 50 dollars for a coffee lover" --capture
```

## Web UI (the hosted demo)

```bash
python app.py   # Gradio UI on :7860
```

Flow: type a need -> pick a product -> Create PayPal order -> approve the
order at the printed link (log in with your PayPal **sandbox buyer** account)
-> Capture payment -> receipt with a transaction ID.

## How it works

1. **Parse**: the request goes to GPT-6 Luna with a JSON-mode prompt; it
   returns budget, category, and keywords.
2. **Search**: the catalog is filtered by budget and ranked by keyword
   overlap (name/keywords weigh more than description).
3. **Order**: the agent creates a PayPal sandbox order for the picked product
   and returns the approval URL.
4. **Approve + capture**: you approve in the browser with a sandbox buyer
   account; the agent captures the order and prints a receipt with the
   PayPal transaction ID.

## Setup notes

- PayPal sandbox app: create one at
  https://developer.paypal.com/dashboard/applications/sandbox (type
  Merchant, sandbox business account). Copy its Client ID and Secret.
- Sandbox buyer account: the developer dashboard auto-creates a sandbox
  personal account (Dashboard -> Sandbox -> Accounts). Use it to approve
  orders at the approval URL.
- OpenAI model: `gpt-6-luna` by default (override with `OPENAI_MODEL`).
  Note it takes `max_completion_tokens`, not `max_tokens`.

## License

MIT, see [LICENSE](LICENSE).
