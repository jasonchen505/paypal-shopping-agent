"""Gradio web UI for the PayPal AI Hackathon demo.

Run: python app.py  (needs OPENAI_API_KEY, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
Flow: describe a need -> pick a product -> create a PayPal sandbox order ->
approve it in your browser -> capture -> receipt with a transaction ID.
"""
import os

from shopping_agent import agent as agent_mod
from shopping_agent import catalog as catalog_mod
from shopping_agent import client as client_mod
from shopping_agent import paypal as paypal_mod


def find_products(request_text, state):
    if not request_text.strip():
        return "Type a shopping need first.", [], None, state
    try:
        cli = client_mod.get_client()
        model_id = client_mod.get_model()
        parsed = client_mod.parse_request(cli, model_id, request_text)
        products = catalog_mod.load_catalog()
        matches = catalog_mod.search(products, parsed, limit=3)
    except Exception as e:
        return f"Error: {e}", [], None, state
    if not matches:
        return "No products matched (try a wider budget or different keywords).", [], None, state
    state = {"request": request_text, "parsed": parsed, "matches": matches,
             "model": model_id}
    labels = [f"{m['name']} — ${m['price']:.2f}" for m in matches]
    info = (f"Understood: budget "
            f"{'$' + str(parsed.get('budget_usd')) if parsed.get('budget_usd') else 'any'}, "
            f"keywords {', '.join(parsed.get('keywords') or [])}.")
    return info, labels, labels[0], state


def create_order(selected_label, state):
    if not state or not state.get("matches"):
        return "Find products first.", state
    picked = next((m for m in state["matches"]
                   if f"{m['name']} — ${m['price']:.2f}" == selected_label),
                  state["matches"][0])
    try:
        cli = client_mod.get_client()
        summary = client_mod.summarize_pick(cli, state["model"], state["request"], picked)
        token = paypal_mod.get_access_token()
        order = paypal_mod.create_order(token, picked)
    except Exception as e:
        return f"Error: {e}", state
    state["picked"] = picked
    state["summary"] = summary
    state["order"] = order
    state["approval_url"] = paypal_mod.approval_url(order)
    return (
        f"**{picked['name']}** — ${picked['price']:.2f}\n\n"
        f"{summary}\n\n"
        f"PayPal order: `{order['id']}` (status: {order['status']})\n\n"
        f"**Approve the payment here:** [{state['approval_url']}]"
        f"({state['approval_url']})\n\n"
        f"Open the link, log in with your PayPal **sandbox buyer** account, "
        f"approve, then come back and click Capture payment.",
        state,
    )


def capture_payment(state):
    if not state or not state.get("order"):
        return "Create a PayPal order first.", state
    try:
        receipt = agent_mod.capture(state)
    except Exception as e:
        return (f"Capture failed: {e}\n\n"
                f"Make sure you approved the order first (open the approval "
                f"link and approve with your sandbox buyer account)."), state
    return receipt, state


def main():
    import gradio as gr

    with gr.Blocks(title="Agentic Commerce Shopping Agent") as demo:
        gr.Markdown(
            "# Agentic Commerce Shopping Agent\n"
            "Describe a need in plain language. The agent (GPT-6 Luna) finds the "
            "product, creates a real PayPal **sandbox** order, and completes the "
            "checkout after you approve it. Every payment is a real PayPal "
            "sandbox transaction with a transaction ID."
        )
        state = gr.State({})
        request = gr.Textbox(
            label="What do you need?",
            placeholder="birthday gift under 50 dollars for a coffee lover",
            lines=2,
        )
        find_btn = gr.Button("Find products", variant="primary")
        parsed_out = gr.Markdown()
        choices = gr.Radio(label="Matches (pick one)", choices=[], value=None)
        order_btn = gr.Button("Create PayPal order", variant="primary")
        order_out = gr.Markdown()
        capture_btn = gr.Button("Capture payment", variant="primary")
        receipt_out = gr.Markdown()

        find_btn.click(find_products, inputs=[request, state],
                       outputs=[parsed_out, choices, choices, state])
        order_btn.click(create_order, inputs=[choices, state],
                        outputs=[order_out, state])
        capture_btn.click(capture_payment, inputs=[state],
                          outputs=[receipt_out, state])
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))


if __name__ == "__main__":
    main()
