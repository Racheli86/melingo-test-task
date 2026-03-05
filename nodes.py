from typing import List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from state import (
    AgentState, 
    ResolvedItem, 
    OrderTotals, 
    SmartOrderSummary
)
from tools import check_availability, get_item

load_dotenv()

class ExtractionItem(BaseModel):
    requested: str = Field(description="The raw text of the item")
    item_search_name: str = Field(description="Simplified name for search")
    quantity: float
    unit: str

class ExtractionResponse(BaseModel):
    items: List[ExtractionItem]

def extraction_node(state: AgentState):
    """
    NLP Extraction Node:
    Utilizes a Large Language Model (LLM) to transform unstructured natural language 
    into validated Pydantic objects. 
    
    This node performs Named Entity Recognition (NER) to isolate items, quantities, 
    and units, applying normalization rules (singularization, lowercase conversion) 
    to prepare data for downstream catalog reconciliation.

    Args:
        state (AgentState): The current graph state containing the raw customer_order.

    Returns:
        dict: A state update containing the list of extracted 'items' as ResolvedItem objects.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    parser = PydanticOutputParser(pydantic_object=ExtractionResponse)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert grocery order parser. Extract items and quantities.\n"
            "Normalization Rules:\n"
            "- Item names: lowercase, singular form.\n"
            "- Quantities: convert to digits.\n"
            "- Units: standardize to 'kg', 'bottle', 'unit', etc.\n"
            "- Collective Units: When a user uses terms like 'dozen', 'pack', 'case', or 'loaf', "
            "treat the term as the 'unit' and set the quantity to the number of those units "
            "(e.g., '1 dozen eggs' -> quantity: 1, unit: 'dozen'; '2 dozen' -> quantity: 2, unit: 'dozen'). "
            "Do not multiply the internal count into the quantity field.\n\n"
            "{format_instructions}"
        )),
        ("human", "{customer_order}"),
    ])

    chain = prompt | llm | parser
    response = chain.invoke({
        "customer_order": state["customer_order"],
        "format_instructions": parser.get_format_instructions(),
    })
    resolved_items = [
        ResolvedItem(
            requested=item.requested,
            quantity=item.quantity,
            unit=item.unit,
            unit_price=0.0,  
            line_total = 0.0,    
            status="pending"    
        ) 
        for item in response.items
    ]

    return {"resolved_items": resolved_items}

def fulfillment_node(state: AgentState):
    """
    Fulfillment & Inventory Node:
    Reconciles extracted items with the product catalog and performs real-time 
    inventory availability checks.
    
    Implements 'Consistent Fulfillment' logic (Option A): if stock is insufficient, 
    the 'quantity' field is programmatically updated to match the available stock. 
    This ensures strict mathematical consistency (quantity * unit_price = line_total) 
    as mandated by the output schema contract. Discrepancies are documented in the 
    'notes' field for transparency.

    Args:
        state (AgentState): The current state containing extracted items.

    Returns:
        dict: A state update with enriched 'items' (prices, IDs, status) and a 
              list of 'unresolved' strings for items not found in the catalog.
    """
    updated_items = []
    unresolved = []

    items_to_process = state.get("resolved_items", [])

    for item in items_to_process:
        catalog_item = get_item(item.requested)

        if not catalog_item:
            unresolved.append(f"Could not find '{item.requested}' in catalog.")
            continue

        stock_info = check_availability(catalog_item["id"], item.quantity)
        
        final_qty = item.quantity
        status = stock_info["status"]
        notes = None

        if status == "partial":
            final_qty = stock_info["in_stock"]
            notes = f"Requested {item.quantity}, but only {final_qty} available. Order updated."
        elif status == "out_of_stock":
            final_qty = 0
            notes = "Item is currently out of stock."

        line_total = round(final_qty * catalog_item["unit_price"], 2)


        updated_items.append(ResolvedItem(
            requested=item.requested,
            matched_item=catalog_item["name"],
            item_id=catalog_item["id"],
            quantity=final_qty,
            unit=catalog_item["unit"],
            unit_price=catalog_item["unit_price"],
            currency=catalog_item["currency"],
            status=status,
            line_total=line_total,
            notes=notes
        ))

    return {
        "resolved_items": updated_items, 
        "unresolved": unresolved
    }

def calculation_node(state: AgentState):
    """
    Financial Calculation Node:
    Aggregates line items and performs deterministic financial computations 
    to finalize the transaction state.
    
    This node calculates the subtotal, applies a fixed tax rate (10%), and 
    computes the grand total with precision rounding (2 decimal places). 
    The final output is encapsulated in a 'SmartOrderSummary' object, 
    enforcing 100% adherence to the mandated JSON output schema.

    Args:
        state (AgentState): The current state containing resolved and priced items.

    Returns:
        dict: A state update containing the 'final_response' object ready for delivery.
    """
    TAX_RATE = 0.1
    
    resolved_items = state.get("resolved_items", [])

    subtotal = sum(item.line_total for item in resolved_items)
    tax = round(subtotal * TAX_RATE, 2)
    grand_total = round(subtotal + tax, 2)

    totals = OrderTotals(
        subtotal=round(subtotal, 2),
        tax_rate=TAX_RATE,
        tax=tax,
        grand_total=grand_total,
        currency="USD"
    )

    final_response_obj = SmartOrderSummary(
        customer_order=state["customer_order"],
        resolved_items=resolved_items,
        totals=totals,
        unresolved=state.get("unresolved", [])
    )

    return {"final_response": final_response_obj.model_dump()}