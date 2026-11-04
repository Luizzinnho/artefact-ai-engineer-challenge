from src.schemas import SemanticInterpretation
import pytest
from pydantic import ValidationError


def test_invalid_intent():
    data = {
        "schema_version": "1.0",
        "commands": [
            {
                "intent": "DELETE_ORDER",
                "query": "excluir pedido",
                "product_filters": None,
                "order_lookup": None,
                "policy_topic": None
            }
        ]
    }

    with pytest.raises(ValidationError):
        SemanticInterpretation.model_validate(data)