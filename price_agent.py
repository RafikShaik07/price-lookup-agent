"""
Your first tool-using AI (Gemini version).

The AI model can call ONE function, get_product_price(), which looks up a
product's price in a local file (prices.json). This script shows the full
tool-use loop: ask -> model requests a tool -> we run it -> send result back
-> model writes the final answer.

Setup:
    pip install google-genai
    set GEMINI_API_KEY=your-key        (Mac/Linux: export GEMINI_API_KEY="your-key")
Run:
    python price_agent.py "How much is a keyboard?"
"""

import json
import os
import sys

from google import genai
from google.genai import types

MODEL = os.environ.get("MODEL", "gemini-2.5-flash")
PRICES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.json")


# ---------------------------------------------------------------------------
# The ONE function the AI is allowed to call
# ---------------------------------------------------------------------------
def get_product_price(product_name: str) -> dict:
    """Look up a product's price (in INR) in the local prices.json file."""
    with open(PRICES_FILE, "r", encoding="utf-8") as f:
        prices = json.load(f)

    key = product_name.strip().lower()
    if key in prices:
        return {"product": key, "price_inr": prices[key]}
    return {"error": f"'{product_name}' not found", "available_products": list(prices)}


# ---------------------------------------------------------------------------
# Tool description: this is how the model learns the function exists
# ---------------------------------------------------------------------------
price_tool = types.Tool(
    function_declarations=[
        {
            "name": "get_product_price",
            "description": (
                "Look up the price of a product in the local price list. "
                "Use this whenever the user asks how much a product costs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Name of the product, e.g. 'laptop' or 'keyboard'",
                    }
                },
                "required": ["product_name"],
            },
        }
    ]
)

# We turn off automatic calling so YOU can see and control every step of the loop
config = types.GenerateContentConfig(
    tools=[price_tool],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)


def run_agent(user_question: str) -> str:
    client = genai.Client()  # reads GEMINI_API_KEY from the environment
    contents = [types.Content(role="user", parts=[types.Part(text=user_question)])]

    while True:
        # STEP 1 & 4: send the conversation + tool list to the model
        response = client.models.generate_content(
            model=MODEL, contents=contents, config=config
        )

        # STEP 2: did the model ask to call a tool?
        if not response.function_calls:
            # No tool requested -> this is the final answer
            return response.text

        # Keep the model's tool request in the conversation history
        contents.append(response.candidates[0].content)

        # STEP 3: run the requested function ourselves and collect results
        result_parts = []
        for call in response.function_calls:
            print(f"[tool call] {call.name}({dict(call.args)})")
            result = get_product_price(**call.args)
            print(f"[tool result] {result}")
            result_parts.append(
                types.Part.from_function_response(name=call.name, response={"result": result})
            )

        # Send the results back; the loop repeats so the model can answer
        contents.append(types.Content(role="user", parts=result_parts))


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How much does a laptop cost?"
    print(f"Question: {question}\n")
    print("Answer:", run_agent(question))
