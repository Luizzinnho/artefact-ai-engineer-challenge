from typing import Literal
from pydantic import BaseModel


class ProductFilters(BaseModel):
    name: str | None
    category: str | None
    brand: str | None
    min_price: float | None
    max_price: float | None
    available_only: bool | None
    


class OrderLookup(BaseModel):
    order_id: str | None
    customer_email: str | None
    


class Command(BaseModel):
    intent: Literal[
        "SEARCH_PRODUCTS",
        "QUERY_ORDER",
        "QUERY_POLICY",
        "OUT_OF_SCOPE",
    ]

    query: str
    product_filters: ProductFilters | None
    order_lookup: OrderLookup | None
    policy_topic: str | None


class SemanticInterpretation(BaseModel):
    schema_version: Literal["1.0"]
    commands: list[Command]

