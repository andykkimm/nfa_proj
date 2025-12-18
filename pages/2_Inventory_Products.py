import streamlit as st
from utils.load_data import load_all_data
from utils.filters import sidebar_filters
from utils.inventory import compute_inventory_table

st.set_page_config(page_title="Inventory & Products — Non-Foya", layout="wide")

st.title("Inventory & Products")
st.caption("Restock vs discontinue signals using sell-through + remaining inventory.")

# --- Load once ---
data = load_all_data(data_path="data/mock")
filters = sidebar_filters(data)

products_raw = data["products"].copy()
inventory_raw = data["inventory"].copy()

# --- Compute the full lifecycle table FIRST (best practice) ---
# This avoids "filtering yourself into zero rows" before metrics exist.
table = compute_inventory_table(products_raw, inventory_raw)

# --- Apply filters to the computed table (display-layer filtering) ---
filtered = table.copy()

# Brand filter (only apply if the column exists in the computed table)
# Note: our compute_inventory_table may not include brand; this keeps things robust.
if filters.get("brand") and filters["brand"] != "All" and "brand" in filtered.columns:
    filtered = filtered[filtered["brand"] == filters["brand"]]

if filters.get("drop_name") and filters["drop_name"] != "All" and "drop_name" in filtered.columns:
    filtered = filtered[filtered["drop_name"] == filters["drop_name"]]

if filters.get("category") and filters["category"] != "All" and "product_category" in filtered.columns:
    filtered = filtered[filtered["product_category"] == filters["category"]]

if filters.get("product_name") and filters["product_name"] != "All" and "product_name" in filtered.columns:
    filtered = filtered[filtered["product_name"] == filters["product_name"]]

# --- UI ---
st.subheader("Product lifecycle table")

if filtered.empty:
    st.info(
        "No products match your current filters.\n\n"
        "Try setting **Drop / Category / Product** back to **All**."
    )
else:
    # Streamlit deprecating use_container_width; use width="stretch"
    st.dataframe(filtered, width="stretch", hide_index=True)

st.markdown(
    """
**How to use this page**
- **Sell-through** near 100% + **low remaining** = strong restock candidate.
- **High remaining** + **low sell-through** = discount, bundle, or consider discontinuing.
"""
)
