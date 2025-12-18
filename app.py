import streamlit as st
from utils.load_data import load_all_data
from utils.filters import sidebar_filters
from utils.kpis import compute_kpis

st.set_page_config(
    page_title="Non-Foya Archive Dashboard",
    page_icon="🧵",
    layout="wide",
)

st.title("Non-Foya Archive — Business Dashboard")
st.caption("Decision support for drops, inventory, products, customers, and Instagram impact.")

with st.spinner("Loading data..."):
    data = load_all_data(data_path="data/mock")

filters = sidebar_filters(data)

orders = data["orders"]
products = data["products"]
inventory = data["inventory"]
ig_posts = data["ig_posts"]
ig_daily = data["ig_daily"]

# Brand filter (kept for future extensibility)
if filters["brand"] != "All":
    orders = orders[orders["brand"] == filters["brand"]]
    products = products[products["brand"] == filters["brand"]]
    inventory = inventory[inventory["brand"] == filters["brand"]]
    ig_posts = ig_posts[ig_posts["brand"] == filters["brand"]]
    ig_daily = ig_daily[ig_daily["brand"] == filters["brand"]]

# Date filter
if filters["date_range"] is not None:
    start, end = filters["date_range"]
    orders = orders[(orders["order_datetime"].dt.date >= start) & (orders["order_datetime"].dt.date <= end)]
    ig_posts = ig_posts[(ig_posts["post_datetime"].dt.date >= start) & (ig_posts["post_datetime"].dt.date <= end)]
    ig_daily = ig_daily[(ig_daily["date"].dt.date >= start) & (ig_daily["date"].dt.date <= end)]

# Drop filter
if filters["drop_name"] != "All":
    orders = orders[orders["drop_name"] == filters["drop_name"]]
    products = products[products["drop_name"] == filters["drop_name"]]
    inventory = inventory[inventory["drop_name"] == filters["drop_name"]]

# Category filter
if filters["category"] != "All":
    orders = orders[orders["product_category"] == filters["category"]]
    products = products[products["product_category"] == filters["category"]]
    inventory = inventory[inventory["product_name"].isin(products["product_name"])]

# Product filter
if filters["product_name"] != "All":
    orders = orders[orders["product_name"] == filters["product_name"]]
    products = products[products["product_name"] == filters["product_name"]]
    inventory = inventory[inventory["product_name"] == filters["product_name"]]

kpis = compute_kpis(orders, products, inventory)

st.subheader("Quick Snapshot")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Revenue", f"${kpis['revenue']:,.0f}")
c2.metric("Orders", f"{kpis['orders']:,}")
c3.metric("Avg Order Value", f"${kpis['aov']:,.2f}")
c4.metric("Repeat Customer Rate", f"{kpis['repeat_rate']*100:,.1f}%")
c5.metric("Sold Out Products", f"{kpis['sold_out_pct']*100:,.1f}%")

st.divider()
st.markdown(
    """
### Where to go next
Use the left sidebar to filter by **date**, **drop**, **category**, or **product**.

Then open the pages on the left:
- **Overview** — trendlines and breakdowns
- **Inventory & Products** — restock vs discontinue signals
- **Drop Performance** — what worked and why
- **Instagram → Sales** — marketing impact
- **Customers** — retention and repeat behavior
"""
)

st.info("Tip: This starter app uses mock data. When you receive real exports, replace the CSVs in `data/mock/` with your real files (same column names).")
