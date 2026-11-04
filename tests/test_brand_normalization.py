from src.brand_normalizer import get_catalog_brands, normalize_brand
from src.executor import execute_commands
from src.schemas import SemanticInterpretation


def test_catalog_brands():
    brands = get_catalog_brands()

    assert "Tagima" in brands
    assert "Yamaha" in brands
    assert "Music Man" in brands
    assert "Korg" in brands
    assert "Pearl" in brands
    assert "Bateria" not in brands


def test_brand_typo():
    assert normalize_brand("tajima") == "Tagima"
    assert normalize_brand("Ymaha") == "Yamaha"


def test_brand_preserves_valid_names():
    assert normalize_brand("Kala") == "Kala"
    assert normalize_brand("Kalani") == "Kalani"
    assert normalize_brand("tagima") == "Tagima"


def test_brand_does_not_invent():
    assert normalize_brand("Sony") == "Sony"


def test_executor_corrects_brand_typo():
    interpretation = SemanticInterpretation.model_validate({
        "schema_version": "1.0",
        "commands": [
            {
                "intent": "SEARCH_PRODUCTS",
                "query": "quais violão tajima vocês têm?",
                "product_filters": {
                    "name": None,
                    "category": "violões",
                    "brand": "Tajima",
                    "min_price": None,
                    "max_price": None,
                    "available_only": True,
                },
                "order_lookup": None,
                "policy_topic": None,
                "missing_fields": [],
            }
        ],
    })

    results = execute_commands(interpretation)

    assert len(results) == 1
    assert results[0]["status"] == "ok"
    assert results[0]["data"]
    assert all(
        "tagima" in product["name"].casefold()
        for product in results[0]["data"]
    )
