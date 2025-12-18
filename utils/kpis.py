import pandas as pd

def compute_kpis(orders: pd.DataFrame, products: pd.DataFrame, inventory: pd.DataFrame) -> dict:
    if orders is None or len(orders) == 0:
        return {"revenue": 0.0, "orders": 0, "aov": 0.0, "repeat_rate": 0.0, "sold_out_pct": 0.0}

    unique_orders = orders.drop_duplicates("order_id")
    revenue = float(unique_orders["order_total_usd"].sum())
    n_orders = int(unique_orders["order_id"].nunique())
    aov = revenue / n_orders if n_orders else 0.0

    cust = unique_orders.groupby("customer_id")["order_id"].nunique()
    repeat_rate = float((cust >= 2).mean()) if len(cust) else 0.0

    sold_out_pct = 0.0
    if inventory is not None and len(inventory) > 0 and "units_remaining_estimate" in inventory.columns:
        sold_out_pct = float((inventory["units_remaining_estimate"] <= 0).mean())

    return {
        "revenue": revenue,
        "orders": n_orders,
        "aov": aov,
        "repeat_rate": repeat_rate,
        "sold_out_pct": sold_out_pct,
    }
