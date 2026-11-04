from difflib import SequenceMatcher

from src.data_loader import load_products


def get_catalog_brands() -> list[str]:
    products = load_products()
    brands = set()

    for name in products["name"].dropna():
        parts = name.split()

        if name.startswith("Music Man "):
            brand = "Music Man"
        elif name.startswith(("Bateria Acústica ", "Teclado Sintetizador ")):
            brand = parts[2]
        else:
            brand = parts[0]

        brands.add(brand)

    return sorted(brands, key=str.casefold)


def normalize_brand(brand: str | None) -> str | None:
    if not brand:
        return brand

    candidate = brand.strip()
    known_brands = get_catalog_brands()

    for known in known_brands:
        if candidate.casefold() == known.casefold():
            return known

    matches = sorted(
        (
            (
                SequenceMatcher(
                    None,
                    candidate.casefold(),
                    known.casefold(),
                ).ratio(),
                known,
            )
            for known in known_brands
        ),
        reverse=True,
    )

    if not matches:
        return candidate

    best_score, best_brand = matches[0]
    second_score = matches[1][0] if len(matches) > 1 else 0

    if best_score >= 0.82 and best_score - second_score >= 0.12:
        return best_brand

    return candidate