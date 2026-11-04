from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CATEGORY_ALIASES = {
    "violão": "Violões",
    "violões": "Violões",
    "violao": "Violões",
    "violoes": "Violões",
    "baixo": "Baixos",
    "baixos": "Baixos",
    "guitarra": "Guitarras",
    "guitarras": "Guitarras",
    "guitarra eletrica": "Guitarras",
    "guitarra elétrica": "Guitarras",
}


# 1. DATA LOADERS

def load_products() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "desafio_tecnico_ai_eng - products.csv")


def load_category() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "desafio_tecnico_ai_eng - categories.csv")


def load_orders() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "desafio_tecnico_ai_eng - orders.csv")


def load_customers() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "desafio_tecnico_ai_eng - customers.csv")


def load_order_items() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "desafio_tecnico_ai_eng - order_items.csv")


def load_promotions() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "desafio_tecnico_ai_eng - promotions.csv")


# 2. PRODUCT SEARCH



def search_products(
    name: str | None = None,
    max_price: float | None = None,
    min_price: float | None = None,
    category: str | None = None,
    available_only: bool | None = None,
    product_id: int | None = None,
    style: str | None = None,
) -> pd.DataFrame:

    products = load_products()
    categories = load_category().rename(
        columns={"name": "category_name"}
    )

    filtered = pd.merge(
        left=products,
        right=categories[["category_id", "category_name"]],
        on="category_id",
        how="left",
    )

    if product_id is not None:
        filtered = filtered[
            filtered["product_id"] == product_id
        ]

    if name is not None:
        filtered = filtered[
            filtered["name"].str.contains(
                name.strip(),
                case=False,
                na=False,
                regex=False,
            )
        ]

    if style is not None and style.strip():
        term = style.strip()

        name_matches = filtered["name"].str.contains(
            term,
            case=False,
            na=False,
            regex=False,
        )

        description_matches = filtered["description"].str.contains(
            term,
            case=False,
            na=False,
            regex=False,
        )

        filtered = filtered[
            name_matches | description_matches
        ]

    if max_price is not None:
        filtered = filtered[
            filtered["price_brl"] <= max_price
        ]

    if min_price is not None:
        filtered = filtered[
            filtered["price_brl"] >= min_price
        ]

    if category is not None:
        category_key = category.strip().lower()

        normalized_category = CATEGORY_ALIASES.get(
            category_key,
            category_key,
        )

        filtered = filtered[
            filtered["category_name"].str.contains(
                normalized_category,
                case=False,
                na=False,
                regex=False,
            )
        ]

    if available_only is True:
        filtered = filtered[
            (filtered["status"] == "active")
            & (filtered["stock_quantity"] > 0)
        ]

    return filtered.copy()



# 3. ORDER LOOKUP

def query_order(
    order_id: int,
    customer_email: str,
) -> pd.DataFrame | None:

    orders = load_orders()
    customers = load_customers()

    merged = pd.merge(
        left=orders,
        right=customers[["customer_id", "email"]],
        on="customer_id",
        how="inner",
    )

    filtered = merged[
        (merged["order_id"] == order_id)
        & (
            merged["email"].str.lower()
            == customer_email.strip().lower()
        )
    ]

    if filtered.empty:
        return None

    items = load_order_items()

    order_with_items = pd.merge(
        left=filtered,
        right=items,
        on="order_id",
        how="left",
    )

    products = load_products()

    merged = pd.merge(
        left=order_with_items,
        right=products[["product_id", "name"]],
        on="product_id",
        how="left",
    )

    return merged[
        [
            "order_id",
            "order_date",
            "status",
            "total_brl",
            "payment_method",
            "tracking_code",
            "estimated_delivery",
            "name",
            "quantity",
        ]
    ].copy()


# 4. PROMOTION SEARCH


def search_promotions(
    product_id: int | None = None,
) -> pd.DataFrame | None:

    promotions = load_promotions()

    active = promotions[
        promotions["is_active"] == 1
    ]

    if product_id is not None:
        active = active[
            active["product_id"] == product_id
        ]

    if active.empty:
        return None

    products = load_products()

    merged = pd.merge(
        left=active,
        right=products[[
            "product_id",
            "name",
            "price_brl",
            "status",
            "stock_quantity",
        ]],
        on="product_id",
        how="inner",
    )

    available = merged[
        (merged["status"] == "active")
        & (merged["stock_quantity"] > 0)
    ]

    if available.empty:
        return None

    best_promotions = (
        available.sort_values(
            by=["product_id", "discount_percent", "promotion_id"],
            ascending=[True, False, True],
        )
        .drop_duplicates(
            subset="product_id",
            keep="first",
        )
        .copy()
    )

    best_promotions["promotional_price_brl"] = (
        best_promotions["price_brl"]
        * (1 - best_promotions["discount_percent"] / 100)
    ).round(2)

    best_promotions["pix_price_brl"] = (
        best_promotions["price_brl"] * 0.95
    ).round(2)

    return best_promotions.reset_index(drop=True)








# 5. MANUAL CHECK

if __name__ == "__main__":

    print(search_products(product_id=127)[["product_id", "name"]])

    result = search_promotions()

    if result is not None:
        print(result[[
        "product_id",
        "name",
        "discount_percent",
        "promotional_price_brl",
        "pix_price_brl",
        ]].to_string(index=False))

        assert result["product_id"].is_unique
