import pandas as pd

def compute_inventory_table(products: pd.DataFrame, inventory: pd.DataFrame) -> pd.DataFrame:
    # Merge inventory snapshot with product metadata (keep it simple & tolerant)
    df = inventory.merge(
        products[["product_id", "product_name", "product_category", "drop_name", "launch_price_usd"]],
        on=["product_id", "product_name", "drop_name"],
        how="left",
    )

    # Build a reliable initial inventory column
    # Prefer products.initial_inventory if present, else compute from snapshot.
    if "initial_inventory" not in df.columns:
        df["initial_inventory"] = pd.NA

    # If initial_inventory came from products but merge didn't match, it'll be NaN -> fill from snapshot
    computed_initial = df["units_sold_estimate"].fillna(0) + df["units_remaining_estimate"].fillna(0)
    df["initial_inventory"] = df["initial_inventory"].fillna(computed_initial)

    # Avoid divide-by-zero
    denom = df["initial_inventory"].replace(0, pd.NA)

    df["sell_through_pct"] = (df["units_sold_estimate"].fillna(0) / denom).fillna(0) * 100

    def recommend(row):
        remaining = row.get("units_remaining_estimate", 0) or 0
        sell = row.get("sell_through_pct", 0) or 0
        init = row.get("initial_inventory", 0) or 0

        if remaining <= 0 and sell >= 95:
            return "Restock candidate"
        if sell >= 85 and remaining <= max(5, 0.08 * init):
            return "Consider restock"
        if sell <= 45 and remaining >= 0.4 * init:
            return "Discount / bundle"
        return "Monitor"

    df["recommendation"] = df.apply(recommend, axis=1)

    out = df[[
        "product_name",
        "product_category",
        "drop_name",
        "launch_price_usd",
        "initial_inventory",
        "units_sold_estimate",
        "units_remaining_estimate",
        "sell_through_pct",
        "recommendation",
    ]].copy()

    out["sell_through_pct"] = out["sell_through_pct"].round(1)
    out = out.sort_values(["recommendation", "sell_through_pct"], ascending=[True, False])

    return out
