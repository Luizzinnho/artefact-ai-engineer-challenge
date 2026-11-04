from src.policy_loader import load_policies


def test_policies_extraction():
    text = load_policies()

    assert isinstance(text, str)
    assert len(text.strip()) > 5000
    assert "EMPÓRIO" in text
    assert "POLÍTICAS" in text


def test_policies_last_page():
    text = load_policies()
    normalized = " ".join(text.split())

    assert "Versão 2.1 Página 8" in normalized