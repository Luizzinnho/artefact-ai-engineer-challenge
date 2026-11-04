import pytest

from src.data_loader import search_promotions


def test_valid_promotion():
    result = search_promotions(127)

    assert result is not None
    assert not result.empty
    assert (result["is_active"] == 1).all()
    assert (result["status"] == "active").all()
    assert (result["stock_quantity"] > 0).all()


def test_promotion_prices():
    result = search_promotions(127)

    assert result is not None

    promotion = result.iloc[0]

    assert promotion["price_brl"] == pytest.approx(359.00)
    assert promotion["promotional_price_brl"] == pytest.approx(323.10)
    assert promotion["pix_price_brl"] == pytest.approx(341.05)


def test_product_without_promotion():
    result = search_promotions(-1)

    assert result is None


def test_list_all_promotions():
    result = search_promotions()

    assert result is not None
    assert not result.empty
    assert result["product_id"].is_unique
    assert (result["is_active"] == 1).all()
    assert (result["status"] == "active").all()
    assert (result["stock_quantity"] > 0).all()