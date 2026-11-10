# Demo script — Agentic Commerce Shopping Agent (target ~2:30, hard limit 3:00)

Record the Gradio web UI in the browser. Talk through each step in one
continuous take; do not edit out the PayPal approval, it is the proof the
checkout is real. Keep the terminal out of frame except where noted.

## Setup (before recording)

- `pip install -r requirements.txt`
- `export OPENAI_API_KEY=... PAYPAL_CLIENT_ID=... PAYPAL_CLIENT_SECRET=...`
- `python app.py` (Gradio on :7860). Open the app in the browser.
- Have the PayPal sandbox buyer account ready (Dashboard -> Sandbox ->
  Accounts, the personal account). You will log in with it at the approval step.

## Script

### 0:00-0:15 — The need
Show the Gradio UI. Say: "I need a birthday gift under 50 dollars for a
coffee lover." Type exactly that into the box and click Find products.
Point at the parsed line: budget $50, keywords coffee.

### 0:15-0:45 — The pick
Three matches appear. Say: "Three coffee products under budget." Click the
top match (Ethiopia Yirgacheffe whole-bean coffee, $18.50). Click
Create PayPal order.

### 0:45-1:15 — The order
The order panel shows the product, the one-paragraph explanation, the PayPal
order ID, and the approval link. Say: "This is a real PayPal sandbox order,
not a mock." Click the approval link (opens PayPal sandbox checkout).

### 1:15-1:50 — The approval
On the PayPal sandbox page, log in with the sandbox buyer account and click
the approve/complete button. Say: "Approving as the sandbox buyer." Return
to the app tab.

### 1:50-2:20 — The capture and receipt
Click Capture payment. The receipt appears: product, price, PayPal order ID,
transaction ID, status COMPLETED. Say: "Captured. The transaction ID is a
real PayPal sandbox transaction."

### 2:20-2:30 — Close
Say: "One sentence in, one paid order out. GPT-6 Luna parses, PayPal
sandbox moves the money." Stop recording.

## Notes

- If the approval page asks to log in, use the sandbox buyer account, never
  a real PayPal account. Sandbox URLs always contain sandbox.paypal.com.
- If capture fails with ORDER_NOT_APPROVED, the approval did not go through;
  go back to the approval link and approve again.
- Total cost of the demo: a few cents of GPT-6 Luna tokens; the PayPal
  payment is sandbox test money.
