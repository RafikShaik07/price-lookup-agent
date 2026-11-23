# Your First Tool-Using AI

A simple Python script where an AI model can call **one function**, `get_product_price()`, to look up a product's price in a local file (`prices.json`). The README explains each step of the **tool-use loop**.

## What is tool use?

An AI model can only generate text. It can't read your files or run your code. **Tool use** (function calling) lets the model *ask* your program to run a function and then use the result in its answer. The model never runs the function itself. Your code does.

## Project files

| File | Purpose |
|---|---|
| `price_agent.py` | The script containing the tool and the tool-use loop |
| `prices.json` | Local "database" of product prices (INR) |
| `requirements.txt` | Python dependency (`google-genai`) |

## How to run

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-here"      # Windows CMD: set GEMINI_API_KEY=your-key-here
python price_agent.py "How much is a keyboard?"
```

## Example output

```
Question: How much is a keyboard?

[tool call] get_product_price({'product_name': 'keyboard'})
[tool result] {'product': 'keyboard', 'price_inr': 1299}
Answer: A keyboard costs ₹1,299.
```

## The tool-use loop, step by step

```
User question
     |
     v
[1] Send question + tool description to the model
     |
     v
[2] Model replies with a TOOL REQUEST (a function_call)
     |
     v
[3] Our code runs get_product_price() and gets a result
     |
     v
[4] Send the tool RESULT back to the model
     |
     v
[5] Model writes the FINAL ANSWER (plain text, no function_call)
```

### Step 1: Describe the tool and ask the question
We send the user's question along with a tool list (`function_declarations`). Each tool has a name, a description and `parameters` (the arguments it takes). This is how the model learns that `get_product_price` exists and when to use it.

### Step 2: The model decides to call the tool
For "How much is a keyboard?" the model replies with a `function_call`, for example `get_product_price(product_name="keyboard")`, instead of a normal answer.

### Step 3: Our code runs the function
The script reads the tool name and arguments from the model's request and runs the real Python function, which reads `prices.json` and returns `{"product": "keyboard", "price_inr": 1299}`. The model can't see or run our files, so this step has to happen in our code.

### Step 4: Return the result to the model
We append the model's tool request and our function response (via `Part.from_function_response`) to the conversation and call the model again.

### Step 5: The model gives the final answer
Now the model has the real price, so it writes a natural-language reply. There is no `function_call` this time, so the `while` loop ends and the script prints the answer.

The `while True` loop also lets the model call a tool more than once if it needs to, for example when asked to compare two products.

## Handling unknown products
If the product isn't in `prices.json`, the function returns an error plus a list of available products, and the model uses that to tell the user politely.

## Ideas to extend
- Add a second tool, such as `check_stock`
- Read prices from a CSV or database instead of JSON
- Add a currency conversion tool
