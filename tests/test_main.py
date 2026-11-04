
from unittest.mock import Mock

import main


def test_process_message_integrates_pipeline(monkeypatch):
    message = "Quero um violão até R$ 1500."
    interpretation = object()
    results = [
        {
            "intent": "SEARCH_PRODUCTS",
            "query": message,
            "status": "ok",
            "data": [],
        }
    ]
    expected_answer = "Encontrei algumas opções para você!"

    interpreter = Mock(return_value=interpretation)
    executor = Mock(return_value=results)
    composer = Mock(return_value=expected_answer)

    monkeypatch.setattr(main, "interpret_message", interpreter)
    monkeypatch.setattr(main, "execute_commands", executor)
    monkeypatch.setattr(main, "compose_response", composer)

    answer = main.process_message(message)

    interpreter.assert_called_once_with(message)
    executor.assert_called_once_with(interpretation)
    composer.assert_called_once_with(message, results)

    assert answer == expected_answer
