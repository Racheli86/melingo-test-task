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
    NLP Extraction Node:
    Converts unstructured natural language input into validated Pydantic objects.
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
    Fulfillment Node:
    Handles catalog matching and real-time inventory verification.
    """
    resolved_items = []
    unresolved = []

    for item in state["extracted_items"]:
        catalog_item = get_item(item.item_search_name)

        if not catalog_item:
            unresolved.append(item.requested)
            continue

        stock_info = check_availability(catalog_item["id"], item.quantity)
        
        billable_quantity = stock_info["can_fulfill"]
        line_total = round(billable_quantity * catalog_item["unit_price"], 2)

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

        if stock_info["status"] == "partial":
            resolved_entry["notes"] = f"Only {stock_info['in_stock']} units available in stock."

        resolved_items.append(resolved_entry)

    return {"resolved_items": resolved_items, "unresolved": unresolved}

def calculation_node(state: AgentState):
    """
    Financial Calculation Node:
    Finalizes the transaction by calculating taxes and rounding totals.
    """
    TAX_RATE = 0.1
    DEFAULT_CURRENCY = "USD"

    subtotal = sum(item["line_total"] for item in state["resolved_items"])
    tax = subtotal * TAX_RATE
    grand_total = subtotal + tax

    final_response = {
        "customer_order": state["customer_order"],
        "resolved_items": state["resolved_items"],
        "totals": {
            "subtotal": round(subtotal, 2),
            "tax_rate": TAX_RATE,
            "tax": round(tax, 2),
            "grand_total": round(grand_total, 2),
            "currency": DEFAULT_CURRENCY,
        },
        "unresolved": state["unresolved"],
    }

    return {"final_response": final_response}