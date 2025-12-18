import streamlit as st
from utils.load_data import load_all_data
from utils.filters import sidebar_filters
from utils.inventory import compute_inventory_table

st.set_page_config(page_title="Inventory & Products — Non-Foya", layout="wide")

st.title("Inventory & Products")
st.caption("Restock vs discontinue signals using sell-through + remaining inventory.")

data = load_all_data(data_path="data/mock")
filters = sidebar_filters(data)

products = data["products"]
inventory = data["inventory"]

if filters["brand"] != "All":
    products = products[products["brand"] == filters["brand"]]
    inventory = inventory[inventory["brand"] == filters["brand"]]

if filters["drop_name"] != "All":
    products = products[products["drop_name"] == filters["drop_name"]]
    inventory = inventory[inventory["drop_name"] == filters["drop_name"]]

if filters["category"] != "All":
    products = products[products["product_category"] == filters["category"]]
    inventory = inventory[inventory["product_name"].isin(products["product_name"])]

if filters["product_name"] != "All":
    products = products[products["product_name"] == filters["product_name"]]
    inventory = inventory[inventory["product_name"] == filters["product_name"]]

table = compute_inventory_table(products, inventory)

st.subheader("Product lifecycle table")
st.dataframe(table, use_container_width=True, hide_index=True)

st.markdown("""
**How to use this page**
- **Sell-through** near 100% + low remaining = strong restock candidate.
- High remaining + low sell-through = discount, bundle, or consider discontinuing.
""")
