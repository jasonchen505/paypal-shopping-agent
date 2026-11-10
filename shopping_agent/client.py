"""Thin wrapper around the OpenAI API (gpt-6-luna).

gpt-6-luna is a reasoning model: for Chat Completions, reasoning effort is
set to "none" so the model answers directly (fast, deterministic, and JSON
mode works cleanly). It also takes max_completion_tokens, not max_tokens.
"""
import json
import os

from openai import OpenAI

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-6-luna"

ENV_API_KEY = "OPENAI_API_KEY"
ENV_BASE_URL = "OPENAI_BASE_URL"
ENV_MODEL = "OPENAI_MODEL"


def get_api_key(explicit=None):
    key = explicit or os.environ.get(ENV_API_KEY)
    if not key:
        raise RuntimeError(
            f"{ENV_API_KEY} is not set. Create a key at "
            f"https://platform.openai.com/api-keys and export {ENV_API_KEY}=<your-key>."
        )
    return key


def get_client(base_url=None, api_key=None):
    return OpenAI(
        base_url=base_url or os.environ.get(ENV_BASE_URL, DEFAULT_BASE_URL),
        api_key=get_api_key(api_key),
    )


def get_model(explicit=None):
    return explicit or os.environ.get(ENV_MODEL, DEFAULT_MODEL)


def parse_request(client, model, request_text):
    """Parse a plain-language shopping request into structured JSON.

    Returns {"budget_usd": float|null, "category": str|null,
             "keywords": [str, ...], "notes": str}.
    """
    system = (
        "You parse a shopping request into JSON. Extract the budget in USD "
        "(number, or null if none is stated), the most likely product "
        "category (one short phrase, or null), and 1-4 search keywords "
        "(lowercase, single words or short phrases). Also add a one-sentence "
        "notes field restating the request. Return ONLY valid JSON, no other text, "
        "with this exact shape: "
        '{"budget_usd": 50, "category": "birthday gift", '
        '"keywords": ["coffee", "mug"], "notes": "..."}'
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": request_text},
        ],
        response_format={"type": "json_object"},
        reasoning_effort="none",
        max_completion_tokens=512,
    )
    return json.loads(resp.choices[0].message.content)


def summarize_pick(client, model, request_text, product):
    """One-paragraph explanation of why this product fits the request."""
    system = (
        "You are a shopping assistant. In 2-3 sentences, explain why this "
        "product fits the shopper's request. Be concrete and honest; do not "
        "invent features that are not in the product description."
    )
    user = (
        f"Request: {request_text}\n\n"
        f"Product: {product['name']} (${product['price']:.2f})\n"
        f"Description: {product['description']}"
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        reasoning_effort="none",
        max_completion_tokens=256,
    )
    return resp.choices[0].message.content.strip()
