import pandas as pd

def compute_inventory_table(products: pd.DataFrame, inventory: pd.DataFrame) -> pd.DataFrame:
    df = inventory.merge(
        products[["product_id","product_name","product_category","drop_name","drop_date","launch_price_usd","initial_inventory"]],
        on=["product_id","product_name","drop_name","drop_date"],
        how="left",
    )

    df["sell_through_pct"] = (df["units_sold_estimate"] / df["initial_inventory"]).replace([float("inf")], 0).fillna(0) * 100

    def recommend(row):
        if row["units_remaining_estimate"] <= 0 and row["sell_through_pct"] >= 95:
            return "Restock candidate"
        if row["sell_through_pct"] >= 85 and row["units_remaining_estimate"] <= max(5, 0.08*row["initial_inventory"]):
            return "Consider restock"
        if row["sell_through_pct"] <= 45 and row["units_remaining_estimate"] >= 0.4*row["initial_inventory"]:
            return "Discount / bundle"
        return "Monitor"

    df["recommendation"] = df.apply(recommend, axis=1)

    out = df[[
        "product_name","product_category","drop_name","launch_price_usd",
        "initial_inventory","units_sold_estimate","units_remaining_estimate",
        "sell_through_pct","recommendation"
    ]].copy()

    out["sell_through_pct"] = out["sell_through_pct"].round(1)
    out = out.sort_values(["recommendation","sell_through_pct"], ascending=[True, False])
    return out
