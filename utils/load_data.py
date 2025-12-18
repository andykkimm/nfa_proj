import pandas as pd
from pathlib import Path

def load_all_data(data_path: str = "data/mock") -> dict:
    base = Path(data_path)

    products = pd.read_csv(base / "products.csv")
    orders = pd.read_csv(base / "orders.csv")
    inventory = pd.read_csv(base / "inventory_snapshot.csv")
    ig_posts = pd.read_csv(base / "instagram_posts.csv")
    ig_daily = pd.read_csv(base / "instagram_daily.csv")

    # Parse datetimes
    orders["order_datetime"] = pd.to_datetime(orders["order_datetime"])
    ig_posts["post_datetime"] = pd.to_datetime(ig_posts["post_datetime"])
    ig_daily["date"] = pd.to_datetime(ig_daily["date"])

    return {
        "products": products,
        "orders": orders,
        "inventory": inventory,
        "ig_posts": ig_posts,
        "ig_daily": ig_daily,
    }
