
from src.data_loader import search_products
from src.executor import execute_commands
from src.schemas import SemanticInterpretation


def make_style_interpretation(
    intent: str,
    style: str,
    max_price: float | None = None,
) -> SemanticInterpretation:
    return SemanticInterpretation.model_validate({
        "schema_version": "1.0",
        "commands": [
            {
                "intent": intent,
                "query": f"Consultar instrumentos {style}",
                "product_filters": {
                    "name": None,
                    "category": "violão",
                    "brand": None,
                    "style": style,
                    "min_price": None,
                    "max_price": max_price,
                    "available_only": True,
                },
                "order_lookup": None,
                "policy_topic": None,
                "missing_fields": [],
            }
        ],
    })


def test_folk_search_in_name_and_description():
    products = search_products(
        category="violão",
        style="folk",
        max_price=1000,
        available_only=True,
    )

    assert set(products["product_id"]) == {
        86, 87, 88, 89
    }


def test_executor_folk_search():
    interpretation = make_style_interpretation(
        intent="SEARCH_PRODUCTS",
        style="folk",
        max_price=1000,
    )

    results = execute_commands(interpretation)

    assert len(results) == 1
    assert results[0]["status"] == "ok"

    product_ids = {
        product["product_id"]
        for product in results[0]["data"]
    }

    assert product_ids == {86, 87, 88, 89}


def test_executor_folk_promotions():
    interpretation = make_style_interpretation(
        intent="QUERY_PROMOTIONS",
        style="folk",
    )

    results = execute_commands(interpretation)

    assert len(results) == 1
    assert results[0]["status"] == "ok"

    product_ids = {
        product["product_id"]
        for product in results[0]["data"]
    }

    assert product_ids == {90}


def test_executor_unknown_style():
    interpretation = make_style_interpretation(
        intent="SEARCH_PRODUCTS",
        style="banjo",
    )

    results = execute_commands(interpretation)

    assert results[0]["status"] == "not_found"
    assert results[0]["data"] == []
