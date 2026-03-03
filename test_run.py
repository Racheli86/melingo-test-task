import json

from agent import process_order

with open("test_orders.json", encoding="utf-8") as f:
    test_orders = json.load(f)

for order in test_orders:
    print(f"\n--- Processing Order {order['id']} ---")
    try:
        result = process_order(order["text"])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error processing order {order['id']}: {str(e)}")