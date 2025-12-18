import pandas as pd
from pathlib import Path

def load_all_data(data_path: str = "data/mock") -> dict:
    # Always resolve paths relative to the project root (folder containing app.py)
    project_root = Path(__file__).resolve().parents[1]
    base = (project_root / data_path).resolve()

    required = [
        "products.csv",
        "orders.csv",
        "inventory_snapshot.csv",
        "instagram_posts.csv",
        "instagram_daily.csv",
    ]
    missing = [f for f in required if not (base / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing files in {base}:\n"
            + "\n".join([f"- {m}" for m in missing])
            + "\n\nExpected structure: data/mock/<csv files>"
        )

    products = pd.read_csv(base / "products.csv")
    orders = pd.read_csv(base / "orders.csv")
    inventory = pd.read_csv(base / "inventory_snapshot.csv")
    ig_posts = pd.read_csv(base / "instagram_posts.csv")
    ig_daily = pd.read_csv(base / "instagram_daily.csv")

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
