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