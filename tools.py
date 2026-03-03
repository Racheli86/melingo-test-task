"""
Tools for the Grocery Store Agent

This module provides utility functions that can be used as tools
by the agent to interact with the store's inventory system.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_stock() -> List[Dict[str, Any]]:
    """
    Retrieve the complete stock catalog from the store.

    Returns:
        List[Dict[str, Any]]: Complete list of all items in stock with their details
            Each item contains:
            - id: unique identifier
            - name: item name
            - aliases: list of alternative names
            - unit: unit of measurement
            - currency: price currency
            - unit_price: price per unit
            - stock_qty: available quantity

    Example:
        >>> stock = get_stock()
        >>> print(len(stock))
        12
    """
    stock_path = Path(__file__).parent / "stock.json"

    with open(stock_path, "r", encoding="utf-8") as f:
        stock_data = json.load(f)

    return stock_data


def get_item(query: str) -> Optional[Dict[str, Any]]:
    """
    Search for an item in the catalog by name or alias.

    This function performs a case-insensitive search across item names and aliases.
    It returns the first matching item found.

    Args:
        query (str): Search term (item name or alias)
            Example: "eggs", "sourdough", "banana"

    Returns:
        Optional[Dict[str, Any]]: Item details if found, None otherwise
            Item structure same as in get_stock()

    Example:
        >>> item = get_item("eggs")
        >>> print(item['name'])
        'Organic Eggs (dozen)'
        >>> print(item['unit_price'])
        5.49

        >>> item = get_item("nonexistent")
        >>> print(item)
        None
    """
    stock = get_stock()
    query_lower = query.lower().strip()

    for item in stock:
        if query_lower in item["name"].lower():
            return item

        for alias in item["aliases"]:
            if query_lower in alias.lower() or alias.lower() in query_lower:
                return item

    return None


def search_items(query: str) -> List[Dict[str, Any]]:
    """
    Search for all items matching a query string.

    Unlike get_item which returns the first match, this function returns
    all items that match the query in their name or aliases.

    Args:
        query (str): Search term

    Returns:
        List[Dict[str, Any]]: List of all matching items (empty list if none found)

    Example:
        >>> items = search_items("milk")
        >>> print(len(items))
        2
        >>> print([item['name'] for item in items])
        ['Almond Milk (1L carton)', 'Whole Milk (1L)']
    """
    stock = get_stock()
    query_lower = query.lower().strip()
    matches = []

    for item in stock:
        if query_lower in item["name"].lower():
            matches.append(item)
            continue

        for alias in item["aliases"]:
            if query_lower in alias.lower() or alias.lower() in query_lower:
                matches.append(item)
                break

    return matches


def check_availability(item_id: str, requested_qty: float) -> Dict[str, Any]:
    """
    Check if requested quantity of an item is available in stock.

    Args:
        item_id (str): Item identifier (e.g., "EGG001")
        requested_qty (float): Requested quantity

    Returns:
        Dict[str, Any]: Availability information
            - available: bool - whether item is available
            - in_stock: float - current stock quantity
            - can_fulfill: float - quantity that can be fulfilled
            - status: str - "available", "partial", or "out_of_stock"

    Example:
        >>> availability = check_availability("EGG001", 3)
        >>> print(availability['status'])
        'available'

        >>> availability = check_availability("YOG001", 1)
        >>> print(availability['status'])
        'out_of_stock'
    """
    stock = get_stock()

    item = None
    for stock_item in stock:
        if stock_item["id"] == item_id:
            item = stock_item
            break

    if not item:
        return {
            "available": False,
            "in_stock": 0,
            "can_fulfill": 0,
            "status": "not_found",
        }

    stock_qty = item["stock_qty"]

    if stock_qty == 0:
        return {
            "available": False,
            "in_stock": 0,
            "can_fulfill": 0,
            "status": "out_of_stock",
        }
    elif stock_qty >= requested_qty:
        return {
            "available": True,
            "in_stock": stock_qty,
            "can_fulfill": requested_qty,
            "status": "available",
        }
    else:
        return {
            "available": True,
            "in_stock": stock_qty,
            "can_fulfill": stock_qty,
            "status": "partial",
        }
