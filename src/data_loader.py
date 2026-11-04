from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_products() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "desafio_tecnico_ai_eng - products.csv")

def load_category() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "desafio_tecnico_ai_eng - categories.csv")


def search_products(
    name: str | None = None,
    max_price: float | None = None,
    min_price: float | None = None, 
    category: str | None = None, 
    available_only: bool | None = None

) -> pd.DataFrame:
    filtered = load_products()
    if name is not None: 
        filtered = filtered[
        filtered["name"].str.contains(
            name,
            case=False,
            na=False,
            regex=False
        )
        ]
    if max_price is not None: 
        filtered = filtered[filtered["price_brl"] <= max_price]

    if min_price is not None: 
        filtered = filtered[filtered["price_brl"] >= min_price]

    if category is not None: 
        CATEGORY_ALIASES = {
        "violão": "Violões",
        "violões": "Violões",
        "violao": "Violões",
        "violoes": "Violões", 
        "baixo": "Baixos",
        "guitarra eletrica": "Guitarras",
        "guitarra": "Guitarras",
        "guitarra elétrica": "Guitarras",
        }
        normalized_category = CATEGORY_ALIASES.get(
        category.lower(),
        category.lower()
        )

        df_category = load_category()
        df_category = df_category.rename(
            columns={"name": "category_name", }
        )
        filtered = pd.merge(
        left=filtered,
        right=df_category[["category_id", "category_name"]],
        on="category_id",
        how="left"
        )
        filtered = filtered[
                filtered["category_name"].str.contains(
                    normalized_category,
                    case=False,
                    na=False,
                    regex=False
                )
                ]

    if available_only is True: 
        filtered = filtered[
        (filtered["status"] == "active") &
        (filtered["stock_quantity"] > 0)
            ]

    return filtered

#QUERY LOADER:


def load_orders() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "desafio_tecnico_ai_eng - orders.csv")

def load_customers() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "desafio_tecnico_ai_eng - customers.csv")

def load_order_items() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "desafio_tecnico_ai_eng - order_items.csv")

def query_order(order_id: int, customer_email: str):
    orders = load_orders()
    customers = load_customers()
    merged = pd.merge(
        left=orders,
        right=customers[["customer_id", "email"]],
        on="customer_id",
        how="inner"
    )
    filtered = merged[
        (merged["order_id"] == order_id) &
        (merged["email"].str.lower() == customer_email.strip().lower())               
        ]
    if filtered.empty:
        return None

    items = load_order_items()

    order_with_items = pd.merge(
        left=filtered,
        right=items,
        on="order_id",
        how="left"
    )

    products = load_products()
    merged = pd.merge(
        left=order_with_items,
        right=products[["product_id", "name"]],
        on="product_id",
        how="left"
    )

    return merged[[
        "order_id",
        "order_date",
        "status",
        "total_brl",
        "payment_method",
        "tracking_code",
        "estimated_delivery",
        "name",
        "quantity"
    ]].copy()






















if __name__ == "__main__":
    result = query_order(1, "pedro.oliveira@jmail.com")
    assert query_order(1, "email.incorreto@exemplo.com") is None
    if result is not None:
        print(result[["order_id", "status", "name", "quantity", "total_brl"]])
    else:
        print("Pedido não encontrado.")