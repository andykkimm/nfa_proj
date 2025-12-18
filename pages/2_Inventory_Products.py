import pandas as pd

def _require_cols(df: pd.DataFrame, required: list[str], df_name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(
            f"[{df_name}] Missing required columns: {missing}\n"
            f"[{df_name}] Available columns: {list(df.columns)}"
        )

def compute_inventory_table(products: pd.DataFrame, inventory: pd.DataFrame) -> pd.DataFrame:
    # --- Required columns for inventory snapshot ---
    inv_required = ["product_name", "units_sold_estimate", "units_remaining_estimate"]
    _require_cols(inventory, inv_required, "inventory_snapshot")

    # --- Required columns for products (we'll be flexible on what we use) ---
    prod_required = ["product_name"]
    _require_cols(products, prod_required, "products")

    # Merge on product_name (most robust). If you have product_id later, you can upgrade this.
    # Keep only columns we might need; ignore if missing.
    prod_cols = [c for c in [
        "product_name",
        "product_category",
        "drop_name",
        "launch_price_usd",
        "initial_inventory",
    ] if c in products.columns]

    df = inventory.merge(products[prod_cols].drop_duplicates("product_name"), on="product_name", how="left")

    # Build initial inventory:
    # Prefer products.initial_inventory if present; otherwise derive from snapshot.
    computed_initial = df["units_sold_estimate"].fillna(0) + df["units_remaining_estimate"].fillna(0)

    if "initial_inventory" not in df.columns:
        df["initial_inventory"] = computed_initial
    else:
        df["initial_inventory"] = df["initial_inventory"].fillna(computed_initial)

    # Avoid divide-by-zero
    denom = df["initial_inventory"].replace(0, pd.NA)

    df["sell_through_pct"] = (df["units_sold_estimate"].fillna(0) / denom).fillna(0) * 100

    # Recommendation heuristic
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

    # Build output table (only include columns that exist)
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
    if "sell_through_pct" in out.columns:
        out["sell_through_pct"] = out["sell_through_pct"].round(1)

    if "recommendation" in out.columns and "sell_through_pct" in out.columns:
        out = out.sort_values(["recommendation", "sell_through_pct"], ascending=[True, False])

    return out
