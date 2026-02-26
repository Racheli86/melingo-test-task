# Gen AI Developer with Agents - Test Task

## Overview

Build an intelligent grocery store agent that can process natural language orders from customers and return structured order summaries with pricing, availability, and item matching.

## Objective

Your task is to implement the `process_order()` function in `agent.py` that takes a free-text customer order and returns a structured JSON response following the provided schema.

## What You Need to Implement

### Core Function

Implement the `process_order(customer_order: str) -> Dict[str, Any]` function in `agent.py`.

The agent should:

1. **Parse Natural Language**: Extract items and quantities from free-text orders
   - Handle various phrasings (e.g., "2kg apples", "apples 2 kg", "two kilograms of apples")
   - Recognize different units (kg, dozen, piece, bottle, carton, etc.)
   - Handle numerical and textual quantities (e.g., "2" vs "two")

2. **Match Items to Catalog**: Use the provided tools to find items
   - Use fuzzy matching to handle variations in item names
   - Match against item names and aliases
   - Handle cases where items are not in the catalog

3. **Check Availability**: Verify stock levels
   - Determine if items are available, out of stock, or partially available
   - Provide appropriate status codes

4. **Calculate Pricing**: Compute totals
   - Calculate line totals (quantity × unit_price)
   - Calculate subtotal (sum of all line totals)
   - Apply tax rate (10%) to compute tax amount
   - Calculate grand total (subtotal + tax)

5. **Return Structured Output**: Format response according to `output_schema.json`

## Provided Resources

### Files

- **`agent.py`**: Contains the stub function you need to implement
- **`tools.py`**: Utility functions for accessing inventory
  - `get_stock()`: Returns complete catalog
  - `get_item(query)`: Searches for a single item
  - `search_items(query)`: Returns all matching items
  - `check_availability(item_id, quantity)`: Checks stock levels
- **`stock.json`**: Store inventory with 12 items
- **`output_schema.json`**: JSON schema for the required output format
- **`test_orders.json`**: Sample orders for testing

### Available Tools

```python
from tools import get_stock, get_item, search_items, check_availability

# Get all items
stock = get_stock()

# Find a specific item
item = get_item("eggs")

# Search for items
items = search_items("milk")

# Check availability
availability = check_availability("EGG001", 5)
```

## Requirements

### Technical Requirements

1. **Use an LLM/Agent Framework**: 
   - Use any LLM API (OpenAI, Anthropic, etc.) or agent framework (LangChain, LlamaIndex, etc.)
   - The agent should intelligently parse orders and match items

2. **Error Handling**:
   - Handle items not found in catalog (add to `unresolved` list)
   - Handle out-of-stock items (set status to "out_of_stock", line_total = 0)
   - Handle partial availability (set status to "partial", add notes)

3. **Output Format**:
   - Must strictly follow `output_schema.json`
   - All monetary values should be rounded to 2 decimal places
   - Tax rate: 10% (0.1)

### Example Output

For order: "2 dozen eggs and 1 kg apples"

```json
{
  "customer_order": "2 dozen eggs and 1 kg apples",
  "resolved_items": [
    {
      "requested": "2 dozen eggs",
      "matched_item": "Organic Eggs (dozen)",
      "item_id": "EGG001",
      "quantity": 2,
      "unit": "dozen",
      "unit_price": 5.49,
      "currency": "USD",
      "status": "available",
      "line_total": 10.98
    },
    {
      "requested": "1 kg apples",
      "matched_item": "Gala Apples",
      "item_id": "FRT003",
      "quantity": 1,
      "unit": "kg",
      "unit_price": 3.99,
      "currency": "USD",
      "status": "available",
      "line_total": 3.99
    }
  ],
  "totals": {
    "subtotal": 14.97,
    "tax_rate": 0.1,
    "tax": 1.50,
    "grand_total": 16.47,
    "currency": "USD"
  },
  "unresolved": []
}
```

## Testing

Test your implementation with the orders in `test_orders.json`:

```python
import json
from agent import process_order

# Load test orders
with open('test_orders.json') as f:
    test_orders = json.load(f)

# Test each order
for order in test_orders:
    result = process_order(order['text'])
    print(f"\nOrder {order['id']}:")
    print(json.dumps(result, indent=2))
```

### Edge Cases to Handle

1. **ORD02**: Greek yogurt is out of stock (stock_qty = 0)
2. **ORD07**: Items not in catalog (strawberries, blueberries, raspberries)
3. **ORD08**: Quantities exceed stock (10 loaves, 5 dozen eggs, 20kg apples)

## Evaluation Criteria

Your solution will be evaluated on:

1. **Correctness**: Does it produce valid output according to the schema?
2. **Robustness**: Does it handle edge cases (out of stock, not found, partial availability)?
3. **Natural Language Understanding**: How well does it parse different order formats?
4. **Code Quality**: Is the code clean, documented, and maintainable?
5. **Agent Design**: Appropriate use of LLM capabilities and tool integration

## Setup Instructions

1. Install required dependencies:
```bash
pip install openai  # or anthropic, langchain, llamaindex, etc.
```

2. Set up your API key:
```bash
export OPENAI_API_KEY="your-key-here"
# or use a .env file
```

3. Implement the `process_order()` function in `agent.py`

4. Test with provided test orders

## Submission

Submit:
1. Your completed `agent.py` file
2. A `requirements.txt` with dependencies
3. A brief `README.md` explaining:
   - Your approach and design decisions
   - Which LLM/framework you used
   - Any assumptions made
   - How to run your code

## Time Estimate

This task should take approximately 2-4 hours to complete.

## Questions?

If you have any questions or need clarification, please don't hesitate to reach out.

Good luck! 🚀

