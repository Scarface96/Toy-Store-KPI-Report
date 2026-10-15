"""Export model-ready tables for Tableau (the Power BI file already lives in the repo root).

    python -m bi.build_bi

The 829k-row sales.csv in the repo root is already clean and is used as the fact table
as-is, so it is not copied. This writes the small lookup tables it needs:

  bi/data/dim_product.csv   numeric cost, price and margin (products.csv stores "$15.99 "
                            as text) plus each product's ABC class by profit
  bi/data/dim_date.csv      every calendar day with a like-for-like flag, because 2023
                            data stops in September
  bi/kpis.json              the headline numbers your dashboard should show
"""

import json
from pathlib import Path

import pandas as pd

from analysis import data as d

OUT = Path(__file__).resolve().parent


def tables(products: pd.DataFrame, sales: pd.DataFrame) -> dict:
    abc = d.abc(sales)[["product", "class"]].rename(columns={"class": "abc_class"})
    dim_product = products.merge(abc, on="product", how="left")
    dim_product["unit_margin_pct"] = (dim_product["unit_margin"] / dim_product["price"]).round(4)

    cal = pd.to_datetime(pd.read_csv(d.ROOT / "calendar.csv")["Date"], format="%m/%d/%Y")
    last_month = sales.loc[sales["year"] == sales["year"].max(), "Date"].dt.month.max()
    dim_date = pd.DataFrame({"date": cal})
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["month_no"] = dim_date["date"].dt.month
    dim_date["month"] = dim_date["date"].dt.strftime("%b")
    dim_date["weekday"] = dim_date["date"].dt.strftime("%a")
    dim_date["weekday_no"] = dim_date["date"].dt.isocalendar().day.astype(int)
    dim_date["like_for_like"] = (dim_date["month_no"] <= last_month).astype(int)
    return {"dim_product": dim_product, "dim_date": dim_date}


def kpis(sales: pd.DataFrame) -> dict:
    t = d.totals(sales)
    lfl = d.like_for_like(sales)
    y0, y1 = lfl.attrs["years"]
    top_store = d.by_store(sales).iloc[0]
    a = d.abc(sales)
    return {
        "Revenue": round(float(t["revenue"]), 2),
        "Profit": round(float(t["profit"]), 2),
        "Profit margin": round(float(t["margin"]), 4),
        "Sales transactions": int(t["orders"]),
        "Units sold": int(t["units"]),
        f"Like-for-like revenue growth (Jan-Sep {y0} to {y1})": round(float(lfl["revenue_growth"].iloc[0]), 4),
        "Top store by revenue": f"Store {int(top_store['Store_ID'])} ({top_store['revenue']:,.0f})",
        "Class A products (top 70% of profit)": int((a["class"] == "A").sum()),
        "Date range": f"{sales['Date'].min():%Y-%m-%d} to {sales['Date'].max():%Y-%m-%d}",
    }


def build(out: Path = OUT) -> dict:
    products = d.load_products()
    sales = d.load_sales(products=products)
    t = tables(products, sales)
    (out / "data").mkdir(parents=True, exist_ok=True)
    for name, frame in t.items():
        frame.to_csv(out / "data" / f"{name}.csv", index=False, date_format="%Y-%m-%d")
    k = kpis(sales)
    (out / "kpis.json").write_text(json.dumps(k, indent=2) + "\n")
    return {"tables": t, "kpis": k}


if __name__ == "__main__":
    res = build()
    for name, frame in res["tables"].items():
        print(f"{name}: {len(frame):,} rows")
    print(json.dumps(res["kpis"], indent=2))
