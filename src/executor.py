import json
from src.schemas import SemanticInterpretation
from src.data_loader import (
    search_products,
    query_order,
    search_promotions,
)
from src.policy_loader import load_policies
from src.brand_normalizer import normalize_brand


def execute_commands(
    interpretation: SemanticInterpretation,
) -> list[dict]:

    results = []

    for command in interpretation.commands:
        if command.intent == "SEARCH_PRODUCTS":
            filters = (
                command.product_filters.model_dump(exclude_none=True)
                if command.product_filters
                else {}
            )

            brand = normalize_brand(filters.pop("brand", None))
            filters.setdefault("available_only", True)

            products = search_products(**filters)

            if command.missing_fields:
                results.append({
                "intent": command.intent,
                "query": command.query,
                "status": "missing_fields",
                "missing_fields": command.missing_fields,
                })
                continue

            if brand:
                products = products[
                    products["name"].str.contains(
                        brand,
                        case=False,
                        na=False,
                        regex=False,
                    )
                ]

            results.append({
                "intent": command.intent,
                "query": command.query,
                "status": "ok" if not products.empty else "not_found",
                "data": json.loads(
                    products.to_json(orient="records", force_ascii=False)
                ),
            })

           
        if command.intent == "QUERY_ORDER":
            filters = (
                command.order_lookup.model_dump(exclude_none=True)
                if command.order_lookup
                else {}
                )
                
            order_id = filters.get("order_id")
            customer_email = filters.get("customer_email")

                
            missing = []
            if not order_id or not order_id.strip():
                missing.append(
                    "order_id"
                    )
                    
            if not customer_email or not customer_email.strip():
                missing.append(
                "customer_email"
                )
            if missing: 
                results.append({
                    "intent": command.intent,
                    "query": command.query,
                    "status": "missing_fields",
                    "missing_fields": missing,
                })
                continue
            try:
                order_id = int(order_id.strip())

            except ValueError:
                results.append({
                "intent": command.intent,
                "query": command.query,
                "status": "invalid_input",
                "invalid_fields": ["order_id"],
                })
                continue
            order = query_order(order_id, customer_email.strip())
            if order is not None:
                results.append({
                    "intent": command.intent,
                    "query": command.query,
                    "status": "ok",
                    "data": json.loads(
                    order.to_json(orient="records", force_ascii=False)
                    ),
                    })
                continue
            else:
                results.append({
                    "intent": command.intent,
                    "query": command.query,
                    "status": "not_found",
                    "data": []
                    })
                continue
        
        if command.intent == "QUERY_POLICY":
            policy = load_policies()
            topic = command.policy_topic
            results.append({
                "intent": command.intent,
                "query": command.query,
                "status": "ok",
                "policy_topic": topic,
                "data": policy
                })
            continue 

        if command.intent == "QUERY_PROMOTIONS": 
            active_promotions = search_promotions()
            if active_promotions is None or active_promotions.empty:
                results.append({
                "intent": command.intent,
                "query": command.query,
                "status": "not_found",
                "data": []
                })
                continue 

            filters = (
                    command.product_filters.model_dump(exclude_none=True)
                    if command.product_filters
                    else {}
                )
            brand = normalize_brand(filters.pop("brand", None))
            min_price = filters.pop("min_price", None)
            max_price = filters.pop("max_price", None)
            filters.setdefault("available_only", True)
            products = search_products(**filters)
            if brand:
                products = products[
                products["name"].str.contains(
                brand,
                case=False,
                na=False,
                regex=False,
                )
                ]
            filtered_promotions = active_promotions[
                active_promotions["product_id"].isin(products["product_id"])
                ]
            if max_price is not None:
                filtered_promotions = filtered_promotions[
                    filtered_promotions["promotional_price_brl"] <= max_price
                ]
        
            if min_price is not None:
                filtered_promotions = filtered_promotions[
                    filtered_promotions["promotional_price_brl"] >= min_price
                ]
            results.append({
                "intent": command.intent,
                "query": command.query,
                "status": "ok" if not filtered_promotions.empty else "not_found",
                "data": json.loads(
                    filtered_promotions.to_json(
                    orient="records",
                    force_ascii=False
                    )
                    ),
                    })
            continue 
        if command.intent == "OUT_OF_SCOPE":
            results.append({
                "intent": command.intent,
                "query": command.query,
                "status":"out_of_scope",
                "data": []
            })
            continue 
        

    return results