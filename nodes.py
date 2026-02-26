from typing import List

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from state import AgentState, ParsedItem
from tools import check_availability, get_item

load_dotenv()


class ParsedOrder(BaseModel):
    items: List[ParsedItem]


def extraction_node(state: AgentState):
    """
    Node 1: NLP Extraction.
    Deconstructs free-text into structured objects with initial normalization.
    """

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    parser = PydanticOutputParser(pydantic_object=ParsedOrder)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are an expert grocery order parser.\n"
                    "Extract items and quantities from the user's order.\n\n"
                    "Normalization Rules:\n"
                    "- Item names: Convert to lowercase and use singular form (e.g., 'apples' -> 'apple').\n"
                    "- Quantities: Convert textual numbers to digits (e.g., 'three' -> 3).\n"
                    "- Units: Standardize to 'kg', 'dozen', 'unit', 'bottle', 'carton', etc.\n\n"
                    "{format_instructions}"
                ),
            ),
            ("human", "{customer_order}"),
        ]
    )

    chain = prompt | llm | parser
    response = chain.invoke(
        {
            "customer_order": state["customer_order"],
            "format_instructions": parser.get_format_instructions(),
        }
    )

    return {"extracted_items": response.items}


def fulfillment_node(state: AgentState):
    """
    Node 2: Fulfillment & Inventory logic.
    Iterates through extracted items, performs catalog matching, and checks inventory levels.
    """

    resolved_items = []
    unresolved = []

    for item in state["extracted_items"]:
        # 1. Attempt to find the item in the catalog (Initial Fuzzy Matching via get_item)
        catalog_item = get_item(item.item_search_name)

        if not catalog_item:
            # If the item is not found in the catalog at all
            unresolved.append(item.requested)
            continue

        # 2. Check stock availability
        stock_info = check_availability(catalog_item["id"], item.quantity)

        # 3. calculate the line_total based on what can actually be fulfilled (can_fulfill)
        billable_quantity = stock_info["can_fulfill"]
        line_total = round(billable_quantity * catalog_item["unit_price"], 2)

        # Build the item object according to the output_schema
        resolved_entry = {
            "requested": item.requested,
            "matched_item": catalog_item["name"],
            "item_id": catalog_item["id"],
            "quantity": item.quantity,
            "unit": catalog_item["unit"],
            "unit_price": catalog_item["unit_price"],
            "currency": catalog_item["currency"],
            "status": stock_info["status"],
            "line_total": line_total,
        }

        # Add a note in case of partial stock 
        if stock_info["status"] == "partial":
            resolved_entry["notes"] = (
                f"Only {stock_info['in_stock']} units available in stock."
            )

        resolved_items.append(resolved_entry)

    return {"resolved_items": resolved_items, "unresolved": unresolved}


def calculation_node(state: AgentState):
    """
    Node 3: Financial Calculations.
    Calculates sub-totals, taxes, and the final grand total.
    """
    # 1. Calculate subtotal from resolved_items
    subtotal = sum(item["line_total"] for item in state["resolved_items"])

    # 2. Calculate tax (10% according to requirements)
    tax_rate = 0.1
    tax = subtotal * tax_rate

    # 3. Calculate final grand total
    grand_total = subtotal + tax

    # 4. Build final response according to output_schema.json
    final_response = {
        "customer_order": state["customer_order"],
        "resolved_items": state["resolved_items"],
        "totals": {
            "subtotal": round(subtotal, 2),
            "tax_rate": tax_rate,
            "tax": round(tax, 2),
            "grand_total": round(grand_total, 2),
            "currency": "USD",  # Assumption based on output example
        },
        "unresolved": state["unresolved"],
    }

    return {"final_response": final_response}
