import streamlit as st

def sidebar_filters(data: dict) -> dict:
    st.sidebar.header("Filters")

    brands = ["All"] + sorted(data["orders"]["brand"].dropna().unique().tolist())
    brand = st.sidebar.selectbox("Brand", brands, index=0)

    min_date = data["orders"]["order_datetime"].dt.date.min()
    max_date = data["orders"]["order_datetime"].dt.date.max()
    date_range = st.sidebar.date_input("Date range", (min_date, max_date))
    if isinstance(date_range, tuple) and len(date_range) == 2:
        date_range = (date_range[0], date_range[1])
    else:
        date_range = None

    drops = ["All"] + sorted(data["products"]["drop_name"].dropna().unique().tolist())
    drop_name = st.sidebar.selectbox("Drop", drops, index=0)

    cats = ["All"] + sorted(data["products"]["product_category"].dropna().unique().tolist())
    category = st.sidebar.selectbox("Category", cats, index=0)

    prods = ["All"] + sorted(data["products"]["product_name"].dropna().unique().tolist())
    product_name = st.sidebar.selectbox("Product", prods, index=0)

    return {
        "brand": brand,
        "date_range": date_range,
        "drop_name": drop_name,
        "category": category,
        "product_name": product_name,
    }
