from typing import Any, Dict, List, Optional, TypedDict
from pydantic import BaseModel, Field

class ResolvedItem(BaseModel):
    requested: str = Field(description="Raw parsed item phrase from customer order")
    matched_item: Optional[str] = Field(default=None, description="Catalog item name if matched, null if not found")
    item_id: Optional[str] = Field(default=None, description="Catalog item ID if matched")
    quantity: float = Field(description="Quantity normalized to the item's unit of measurement")
    unit: str = Field(description="Unit of measurement (kg, dozen, piece, bottle, etc.)")
    unit_price: float = Field(description="Price per unit")
    currency: str = Field(default="USD", description="Currency code")
    status: str = Field(description="Availability status: available, out_of_stock, not_found, partial")
    line_total: float = Field(description="Total price for this line item (quantity * unit_price)")
    notes: Optional[str] = Field(default=None, description="Additional notes about the item")

class OrderTotals(BaseModel):
    subtotal: float = Field(description="Sum of all line_total values")
    tax_rate: float = Field(default=0.1, description="Applied tax rate (e.g., 0.1 for 10%)")
    tax: float = Field(description="Calculated tax amount")
    grand_total: float = Field(description="Final total including tax")
    currency: str = Field(default="USD")

class SmartOrderSummary(BaseModel):
    customer_order: str
    resolved_items: List[ResolvedItem]
    totals: OrderTotals
    unresolved: List[str]

class AgentState(TypedDict):
    customer_order: str
    resolved_items: List[ResolvedItem] 
    unresolved: List[str]
    final_response: SmartOrderSummary