from src.executor import execute_commands
from src.schemas import SemanticInterpretation


def make_order_interpretation(order_id, customer_email):
    return SemanticInterpretation.model_validate({
        "schema_version": "1.0",
        "commands": [
            {
                "intent": "QUERY_ORDER",
                "query": "Quero consultar meu pedido",
                "product_filters": None,
                "order_lookup": {
                    "order_id": order_id,
                    "customer_email": customer_email,
                },
                "policy_topic": None,
                "missing_fields": [],
            }
        ],
    })


def test_executor_valid_order():
    interpretation = make_order_interpretation(
        "1", "pedro.oliveira@jmail.com"
    )

    results = execute_commands(interpretation)

    assert len(results) == 1
    assert results[0]["status"] == "ok"
    assert results[0]["data"][0]["order_id"] == 1
    assert "email" not in results[0]["data"][0]


def test_executor_order_not_found():
    interpretation = make_order_interpretation(
        "999999", "pedro.oliveira@jmail.com"
    )

    results = execute_commands(interpretation)

    assert results[0]["status"] == "not_found"
    assert results[0]["data"] == []


def test_executor_missing_fields():
    interpretation = make_order_interpretation(None, None)

    results = execute_commands(interpretation)

    assert results[0]["status"] == "missing_fields"
    assert set(results[0]["missing_fields"]) == {
        "order_id",
        "customer_email",
    }


def test_executor_invalid_order_id():
    interpretation = make_order_interpretation(
        "ABC123", "pedro.oliveira@jmail.com"
    )

    results = execute_commands(interpretation)

    assert results[0]["status"] == "invalid_input"
    assert "order_id" in results[0]["invalid_fields"]

def test_executor_multiple_commands():
    interpretation = SemanticInterpretation.model_validate({
        "schema_version": "1.0",
        "commands": [
            {
                "intent": "QUERY_ORDER",
                "query": "Quero consultar meu pedido",
                "product_filters": None,
                "order_lookup": {
                    "order_id": None,
                    "customer_email": "pedro.oliveira@jmail.com",
                },
                "policy_topic": None,
                "missing_fields": [],
            },
            {
                "intent": "SEARCH_PRODUCTS",
                "query": "Quero violões até 1500 reais",
                "product_filters": {
                    "name": None,
                    "category": "violões",
                    "brand": None,
                    "min_price": None,
                    "max_price": 1500.0,
                    "available_only": True,
                },
                "order_lookup": None,
                "policy_topic": None,
                "missing_fields": [],
            },
        ],
    })

    results = execute_commands(interpretation)

    assert len(results) == 2

    assert results[0]["intent"] == "QUERY_ORDER"
    assert results[0]["status"] == "missing_fields"
    assert results[0]["missing_fields"] == ["order_id"]

    assert results[1]["intent"] == "SEARCH_PRODUCTS"
    assert results[1]["status"] == "ok"
    assert len(results[1]["data"]) > 0

    assert all(
        product["price_brl"] <= 1500
        for product in results[1]["data"]
    )

def test_executor_policy():
    interpretation = SemanticInterpretation.model_validate({
        "schema_version": "1.0",
        "commands": [
            {
                "intent": "QUERY_POLICY",
                "query": "Qual é a política de devolução?",
                "product_filters": None,
                "order_lookup": None,
                "policy_topic": "devolução",
                "missing_fields": [],
            }
        ],
    })

    results = execute_commands(interpretation)

    assert len(results) == 1
    assert results[0]["intent"] == "QUERY_POLICY"
    assert results[0]["status"] == "ok"
    assert results[0]["policy_topic"] == "devolução"
    assert isinstance(results[0]["data"], str)
    assert len(results[0]["data"]) > 5000
    assert "POLÍTICAS" in results[0]["data"]

def make_promotion_interpretation(**overrides):
    filters = {
        "name": None,
        "category": None,
        "brand": None,
        "min_price": None,
        "max_price": None,
        "available_only": True,
    }

    filters.update(overrides)

    return SemanticInterpretation.model_validate({
        "schema_version": "1.0",
        "commands": [
            {
                "intent": "QUERY_PROMOTIONS",
                "query": "Consultar promoções",
                "product_filters": filters if overrides else None,
                "order_lookup": None,
                "policy_topic": None,
                "missing_fields": [],
            }
        ],
    })


def test_executor_all_promotions():
    interpretation = make_promotion_interpretation()
    results = execute_commands(interpretation)

    assert len(results) == 1
    assert results[0]["status"] == "ok"

    product_ids = {
        product["product_id"]
        for product in results[0]["data"]
    }

    assert product_ids == {90, 94, 121, 127}


def test_executor_promotions_by_category():
    interpretation = make_promotion_interpretation(
        category="violões"
    )

    results = execute_commands(interpretation)
    data = results[0]["data"]

    assert results[0]["status"] == "ok"
    assert {product["product_id"] for product in data} == {90, 94}


def test_executor_promotions_by_brand():
    interpretation = make_promotion_interpretation(
        brand="Kalani"
    )

    results = execute_commands(interpretation)
    data = results[0]["data"]

    assert results[0]["status"] == "ok"
    assert len(data) == 1
    assert data[0]["product_id"] == 127
    assert "Kalani" in data[0]["name"]


def test_executor_promotions_max_price():
    interpretation = make_promotion_interpretation(
        max_price=400
    )

    results = execute_commands(interpretation)
    data = results[0]["data"]

    assert results[0]["status"] == "ok"
    assert {product["product_id"] for product in data} == {127}

    assert all(
        product["promotional_price_brl"] <= 400
        for product in data
    )


def test_executor_promotions_min_price():
    interpretation = make_promotion_interpretation(
        min_price=5000
    )

    results = execute_commands(interpretation)
    data = results[0]["data"]

    assert results[0]["status"] == "ok"
    assert {product["product_id"] for product in data} == {94}

    assert all(
        product["promotional_price_brl"] >= 5000
        for product in data
    )


def test_executor_promotions_combined_filters():
    interpretation = make_promotion_interpretation(
        category="violões",
        brand="Crafter",
        min_price=1900,
        max_price=2000,
    )

    results = execute_commands(interpretation)
    data = results[0]["data"]

    assert results[0]["status"] == "ok"
    assert len(data) == 1
    assert data[0]["product_id"] == 90

    assert data[0]["price_brl"] > 2000
    assert 1900 <= data[0]["promotional_price_brl"] <= 2000


def test_executor_promotions_not_found():
    interpretation = make_promotion_interpretation(
        category="baixos"
    )

    results = execute_commands(interpretation)

    assert len(results) == 1
    assert results[0]["status"] == "not_found"
    assert results[0]["data"] == []

def make_out_of_scope_command(query):
    return {
        "intent": "OUT_OF_SCOPE",
        "query": query,
        "product_filters": None,
        "order_lookup": None,
        "policy_topic": None,
        "missing_fields": [],
    }


def test_executor_out_of_scope():
    interpretation = SemanticInterpretation.model_validate({
        "schema_version": "1.0",
        "commands": [
            make_out_of_scope_command(
                "Qual é a previsão do tempo amanhã?"
            )
        ],
    })

    results = execute_commands(interpretation)

    assert len(results) == 1
    assert results[0]["intent"] == "OUT_OF_SCOPE"
    assert results[0]["status"] == "out_of_scope"
    assert results[0]["data"] == []
    assert results[0]["query"] == "Qual é a previsão do tempo amanhã?"


def test_executor_out_of_scope_with_valid_command():
    interpretation = SemanticInterpretation.model_validate({
        "schema_version": "1.0",
        "commands": [
            {
                "intent": "SEARCH_PRODUCTS",
                "query": "Quero violões até R$ 1500",
                "product_filters": {
                    "name": None,
                    "category": "violões",
                    "brand": None,
                    "min_price": None,
                    "max_price": 1500,
                    "available_only": True,
                },
                "order_lookup": None,
                "policy_topic": None,
                "missing_fields": [],
            },
            make_out_of_scope_command(
                "Quanto está a temperatura em São Paulo?"
            ),
        ],
    })

    results = execute_commands(interpretation)

    assert len(results) == 2
    assert results[0]["intent"] == "SEARCH_PRODUCTS"
    assert results[0]["status"] == "ok"
    assert len(results[0]["data"]) > 0

    assert results[1]["intent"] == "OUT_OF_SCOPE"
    assert results[1]["status"] == "out_of_scope"


def test_executor_out_of_scope_preserves_order():
    interpretation = SemanticInterpretation.model_validate({
        "schema_version": "1.0",
        "commands": [
            make_out_of_scope_command("Conte uma piada"),
            {
                "intent": "QUERY_POLICY",
                "query": "Qual é a política de devolução?",
                "product_filters": None,
                "order_lookup": None,
                "policy_topic": "devolução",
                "missing_fields": [],
            },
            make_out_of_scope_command("Qual é a capital da Alemanha?"),
        ],
    })

    results = execute_commands(interpretation)

    assert len(results) == 3
    assert [result["intent"] for result in results] == [
        "OUT_OF_SCOPE",
        "QUERY_POLICY",
        "OUT_OF_SCOPE",
    ]
    assert [result["status"] for result in results] == [
        "out_of_scope",
        "ok",
        "out_of_scope",
    ]