import json

from agent import process_order

# Load test orders
with open("test_orders.json", encoding="utf-8") as f:
    test_orders = json.load(f)

# Test each order
for order in test_orders:
    result = process_order(order["text"])
    print(f"\nOrder {order['id']}:")
    print(json.dumps(result, indent=2))
