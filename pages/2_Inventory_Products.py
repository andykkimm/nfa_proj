import pandas as pd

def compute_inventory_table(products: pd.DataFrame, inventory: pd.DataFrame) -> pd.DataFrame:
    """
    Builds a product lifecycle table from:
      - inventory snapshot (must include product_name, units_sold_estimate, units_remaining_estimate)
      - products metadata (optional: product_category, drop_name, launch_price_usd, initial_inventory)

    Robust to missing initial_inventory in products: derives it as sold + remaining.
    """

    # --- Validate required inventory columns ---
    required_inv = {"product_name", "units_sold_estimate", "units_remaining_estimate"}
    missing = required_inv - set(inventory.columns)
    if missing:
        raise KeyError(f"inventory_snapshot missing columns: {sorted(missing)}")

    # --- Merge product metadata (only take what exists) ---
    prod_cols = [c for c in [
        "product_name",
        "product_category",
        "drop_name",
        "launch_price_usd",
        "initial_inventory",
    ] if c in products.columns]

    # Merge on product_name (most stable with your current filtering)
    df = inventory.merge(
        products[prod_cols].drop_duplicates("product_name"),
        on="product_name",
        how="left",
    )

    # --- ALWAYS define initial_inventory (this fixes your KeyError) ---
    computed_initial = df["units_sold_estimate"].fillna(0) + df["units_remaining_estimate"].fillna(0)

    if "initial_inventory" not in df.columns:
        df["initial_inventory"] = computed_initial
    else:
        df["initial_inventory"] = df["initial_inventory"].fillna(computed_initial)

    # --- Sell-through ---
    denom = df["initial_inventory"].replace(0, pd.NA)
    df["sell_through_pct"] = (df["units_sold_estimate"].fillna(0) / denom).fillna(0) * 100

    # --- Simple recommendation rules ---
    def recommend(row):
        remaining = float(row.get("units_remaining_estimate", 0) or 0)
        sell = float(row.get("sell_through_pct", 0) or 0)
        init = float(row.get("initial_inventory", 0) or 0)

        if remaining <= 0 and sell >= 95:
            return "Restock candidate"
        if sell >= 85 and remaining <= max(5, 0.08 * init):
            return "Consider restock"
        if sell <= 45 and remaining >= 0.4 * init:
            return "Discount / bundle"
        return "Monitor"

    df["recommendation"] = df.apply(recommend, axis=1)

    # --- Output columns (only include what exists) ---
    out_cols = [
        "product_name",
        "product_category",
        "drop_name",
        "launch_price_usd",
        "initial_inventory",
        "units_sold_estimate",
        "units_remaining_estimate",
        "sell_through_pct",
        "recommendation",
    ]
    out_cols = [c for c in out_cols if c in df.columns]

    out = df[out_cols].copy()
    out["sell_through_pct"] = out["sell_through_pct"].round(1)
    out = out.sort_values(["recommendation", "sell_through_pct"], ascending=[True, False])

    return out
