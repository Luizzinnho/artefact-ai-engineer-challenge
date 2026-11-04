from src.data_loader import search_products


def test_available_products():
    result = search_products(available_only=True)

    assert not result.empty
    assert (result["status"] == "active").all()
    assert (result["stock_quantity"] > 0).all()


def test_product_price_range():
    result = search_products(min_price=1500, max_price=3000)

    assert not result.empty
    assert (result["price_brl"] >= 1500).all()
    assert (result["price_brl"] <= 3000).all()

def test_category_aliases():
    result1 = search_products(category="violão")
    result2 = search_products(category="violao")

    assert not result1.empty
    assert set(result1["product_id"]) == set(result2["product_id"])

def test_name_aliases():
    result1 = search_products(name="Yamaha")
    result2 = search_products(name="yamaha")
    assert not result1.empty
    assert set(result1["product_id"]) == set(result2["product_id"])
    assert result1["name"].str.contains(
    "yamaha", case=False, na=False, regex=False
    ).all()
