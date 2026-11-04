from src.data_loader import query_order


def test_valid_order():
    result = query_order(1, "pedro.oliveira@jmail.com")

    assert result is not None
    assert not result.empty
    assert result["order_id"].eq(1).all()
    assert "name" in result.columns
    assert "email" not in result.columns


def test_invalid_email():
    result = query_order(1, "incorreto@exemplo.com")

    assert result is None