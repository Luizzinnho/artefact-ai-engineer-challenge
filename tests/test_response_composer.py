from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import src.response_composer as composer


@pytest.fixture
def mock_openai(monkeypatch):
    client = MagicMock()
    client.responses.create.return_value = SimpleNamespace(
        output_text="Olá! Como posso ajudar?"
    )

    monkeypatch.setattr(
        composer,
        "OpenAI",
        lambda: client,
    )

    return client


def test_composer_returns_text(mock_openai):
    answer = composer.compose_response(
        "Olá!",
        [],
    )

    assert answer == "Olá! Como posso ajudar?"
    mock_openai.responses.create.assert_called_once()


def test_composer_sends_original_message_and_results(mock_openai):
    results = [
        {
            "intent": "SEARCH_PRODUCTS",
            "query": "Quero um violão",
            "status": "ok",
            "data": [
                {
                    "product_id": 81,
                    "name": "Yamaha C40 Nylon Natural",
                    "price_brl": 599.90,
                }
            ],
        }
    ]

    composer.compose_response(
        "Vocês têm um violão Yamaha?",
        results,
    )

    kwargs = mock_openai.responses.create.call_args.kwargs

    assert kwargs["model"] == "gpt-5.6-luna"
    assert "Empório da Música" in kwargs["instructions"]
    assert "Vocês têm um violão Yamaha?" in kwargs["input"]
    assert "Yamaha C40 Nylon Natural" in kwargs["input"]
    assert '"product_id": 81' in kwargs["input"]


def test_composer_preserves_portuguese_characters(mock_openai):
    results = [
        {
            "intent": "QUERY_POLICY",
            "query": "Qual é a política de devolução?",
            "status": "ok",
            "data": "A devolução está sujeita às condições da loja.",
        }
    ]

    composer.compose_response(
        "Como funciona a devolução?",
        results,
    )

    user_input = mock_openai.responses.create.call_args.kwargs["input"]

    assert "devolução" in user_input
    assert "condições" in user_input


def test_composer_receives_multiple_results(mock_openai):
    results = [
        {
            "intent": "SEARCH_PRODUCTS",
            "query": "Quero violões",
            "status": "not_found",
            "data": [],
        },
        {
            "intent": "QUERY_ORDER",
            "query": "Onde está meu pedido?",
            "status": "missing_fields",
            "missing_fields": ["order_id"],
        },
    ]

    composer.compose_response(
        "Quero violões e consultar meu pedido.",
        results,
    )

    user_input = mock_openai.responses.create.call_args.kwargs["input"]

    assert '"intent": "SEARCH_PRODUCTS"' in user_input
    assert '"intent": "QUERY_ORDER"' in user_input
    assert '"status": "not_found"' in user_input
    assert '"status": "missing_fields"' in user_input


def test_composer_removes_extra_whitespace(mock_openai):
    mock_openai.responses.create.return_value = SimpleNamespace(
        output_text="  Olá! Seja bem-vindo!  \n"
    )

    answer = composer.compose_response("Olá!", [])

    assert answer == "Olá! Seja bem-vindo!"


@pytest.mark.parametrize(
    "invalid_answer",
    [None, "", "   \n   "],
)
def test_composer_rejects_empty_response(mock_openai, invalid_answer):
    mock_openai.responses.create.return_value = SimpleNamespace(
        output_text=invalid_answer
    )

    with pytest.raises(
        ValueError,
        match="A LLM não retornou uma resposta válida",
    ):
        composer.compose_response("Olá!", [])