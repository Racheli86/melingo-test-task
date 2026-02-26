from typing import Annotated, Any, Dict, List, TypedDict

from pydantic import BaseModel, Field


class ParsedItem(BaseModel):
    requested: str = Field(description="The raw text of the item requested")
    item_search_name: str = Field(description="The simplified name for catalog search")
    quantity: float
    unit: str


class AgentState(TypedDict):
    customer_order: str
    extracted_items: List[ParsedItem]
    resolved_items: List[Dict]
    unresolved: List[str]
    final_response: Dict[str, Any]
