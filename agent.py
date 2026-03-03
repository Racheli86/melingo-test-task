import logging
import os
from typing import Any, Dict

from dotenv import load_dotenv

from graph import app

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Grocery Store Agent Module

This module contains the main agent function that processes customer orders
and returns structured order summaries.
"""

from typing import Any, Dict


def process_order(customer_order: str) -> Dict[str, Any]:
    """
    Process a natural language grocery order and return a structured summary.

    This function should:
    1. Parse the customer's free-text order to identify items and quantities
    2. Use the available tools (get_stock, get_item) to match items with the catalog
    3. Calculate quantities, prices, and totals
    4. Handle cases where items are out of stock, not found, or partially available
    5. Return a structured response matching the output_schema.json format

    Args:
        customer_order (str): Free-text order from the customer
            Example: "I want to buy 1kg of apples, 1 bag of juice"

    Returns:
        Dict[str, Any]: Structured order summary matching output_schema.json
            Contains:
            - customer_order: original order text
            - resolved_items: list of matched items with pricing
            - totals: subtotal, tax, and grand total
            - unresolved: list of items that couldn't be matched

    Example:
        >>> order = "2 dozen eggs and 1kg of apples"
        >>> result = process_order(order)
        >>> print(result['totals']['grand_total'])
    """

    initial_state = {
        "customer_order": customer_order,
        "extracted_items": [],
        "resolved_items": [],
        "unresolved": [],
        "final_response": {},
    }

    try:
        result = app.invoke(initial_state)

        final_output = result.get("final_response")
        if not final_output:
            raise ValueError("Graph execution finished but final_response is empty")

        return final_output

    except Exception as e:
        logger.error(f"Error processing order: {str(e)}")

        return {
            "customer_order": customer_order,
            "resolved_items": [],
            "totals": {
                "subtotal": 0.0,
                "tax_rate": 0.1,
                "tax": 0.0,
                "grand_total": 0.0,
                "currency": "USD",
            },
            "unresolved": [
                "System error: We couldn't process your order at this time."
            ],
            "error_log": str(e) if os.getenv("DEBUG") else "Internal processing error",
        }
