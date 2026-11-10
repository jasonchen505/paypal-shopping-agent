"""CLI: shop-agent "birthday gift under 50 dollars for a coffee lover" """
import argparse
import json
import sys

from . import agent as agent_mod
from . import paypal as paypal_mod


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="shop-agent",
        description="Agentic commerce shopping agent: describe a need, it finds "
                    "the product and completes a real PayPal sandbox checkout.",
    )
    p.add_argument("request", help="plain-language shopping need, e.g. "
                   "'birthday gift under 50 dollars for a coffee lover'")
    p.add_argument("--pick", type=int, default=0,
                   help="which match to buy (0 = best match, default 0)")
    p.add_argument("--model", default=None, help="OpenAI model id (default: gpt-6-luna)")
    p.add_argument("--capture", action="store_true",
                   help="capture the order after you approve it (see the printed approval URL)")
    args = p.parse_args(argv)

    result = agent_mod.shop(args.request, model=args.model, pick_index=args.pick)
    print(f"Parsed: {json.dumps(result['parsed'])}")
    if not result["matches"]:
        print("No products matched your request (try a wider budget or different keywords).")
        return 1
    print("Matches:")
    for i, m in enumerate(result["matches"]):
        print(f"  [{i}] {m['name']} — ${m['price']:.2f}")
    print(f"Picked: {result['picked']['name']} — ${result['picked']['price']:.2f}")
    print(result.get("summary", ""))
    print(f"PayPal order: {result['order']['id']} (status: {result['order']['status']})")
    print(f"Approve it here: {result['approval_url']}")
    if args.capture:
        input("Press Enter after approving the order in your browser...")
        print(agent_mod.capture(result))
    else:
        print("To complete the payment, approve the order at the URL above, then "
              "re-run with --capture (or capture from the web UI).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
