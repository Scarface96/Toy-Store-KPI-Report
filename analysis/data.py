"""Load the toy store star schema and build an enriched sales table."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _money(col: pd.Series) -> pd.Series:
    """'$15.99 ' -> 15.99"""
    return col.astype(str).str.replace(r"[$,\s]", "", regex=True).astype(float)


def load_products(path: Path = ROOT / "products.csv") -> pd.DataFrame:
    p = pd.read_csv(path)
    p["cost"] = _money(p["Product_Cost"])
    p["price"] = _money(p["Product_Price"])
    p["unit_margin"] = p["price"] - p["cost"]
    p = p.rename(columns={"Product_Name": "product", "Product_Category": "category"})
    return p[["Product_ID", "product", "category", "cost", "price", "unit_margin"]]


def load_sales(path: Path = ROOT / "sales.csv", products: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per sale with revenue, cost and profit attached."""
    products = load_products() if products is None else products
    s = pd.read_csv(path, parse_dates=["Date"])
    unknown = set(s["Product_ID"]) - set(products["Product_ID"])
    assert not unknown, f"sales reference unknown products: {sorted(unknown)[:5]}"
    s = s.merge(products, on="Product_ID", how="left", validate="many_to_one")
    s["revenue"] = s["Units"] * s["price"]
    s["profit"] = s["Units"] * s["unit_margin"]
    s["month"] = s["Date"].dt.to_period("M").dt.to_timestamp()
    s["year"] = s["Date"].dt.year
    return s


def check_calendar(sales: pd.DataFrame, path: Path = ROOT / "calendar.csv") -> dict:
    cal = pd.to_datetime(pd.read_csv(path)["Date"], format="%m/%d/%Y")
    missing_days = sorted(set(cal.dt.normalize()) - set(sales["Date"].dt.normalize()))
    return {"calendar_days": len(cal), "days_without_sales": len(missing_days), "first": cal.min(), "last": cal.max()}


# ------------------------------------------------------------------ measures --
def totals(s: pd.DataFrame) -> dict:
    rev, prof = s["revenue"].sum(), s["profit"].sum()
    return {"revenue": rev, "profit": prof, "margin": prof / rev, "orders": len(s), "units": int(s["Units"].sum())}


def monthly(s: pd.DataFrame, by: str | None = None) -> pd.DataFrame:
    keys = ["month"] + ([by] if by else [])
    m = s.groupby(keys).agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("Sale_ID", "size"), units=("Units", "sum")).reset_index()
    m["margin"] = m["profit"] / m["revenue"]
    return m


def like_for_like(s: pd.DataFrame, by: str | None = None) -> pd.DataFrame:
    """Compare the same months in both years (2023 data stops in September)."""
    last_month = s.loc[s["year"] == s["year"].max(), "Date"].dt.month.max()
    window = s[s["Date"].dt.month <= last_month]
    keys = (["year"] + ([by] if by else []))
    t = window.groupby(keys).agg(revenue=("revenue", "sum"), profit=("profit", "sum")).reset_index()
    wide = t.pivot_table(index=by if by else None, columns="year", values=["revenue", "profit"], aggfunc="sum") if by else None
    years = sorted(window["year"].unique())
    y0, y1 = years[0], years[-1]
    if by:
        out = pd.DataFrame({
            by: wide.index,
            f"revenue_{y0}": wide[("revenue", y0)].values,
            f"revenue_{y1}": wide[("revenue", y1)].values,
            f"profit_{y0}": wide[("profit", y0)].values,
            f"profit_{y1}": wide[("profit", y1)].values,
        })
    else:
        r = t.set_index("year")
        out = pd.DataFrame([{f"revenue_{y0}": r.loc[y0, "revenue"], f"revenue_{y1}": r.loc[y1, "revenue"], f"profit_{y0}": r.loc[y0, "profit"], f"profit_{y1}": r.loc[y1, "profit"]}])
    out["revenue_growth"] = out[f"revenue_{y1}"] / out[f"revenue_{y0}"] - 1
    out["profit_growth"] = out[f"profit_{y1}"] / out[f"profit_{y0}"] - 1
    out.attrs.update(months=int(last_month), years=(int(y0), int(y1)))
    return out


def abc(s: pd.DataFrame, measure: str = "profit") -> pd.DataFrame:
    """Pareto / ABC classification: A = top 70% of the measure, B = next 20%, C = last 10%."""
    p = s.groupby(["product", "category"]).agg(revenue=("revenue", "sum"), profit=("profit", "sum"), units=("Units", "sum")).reset_index()
    p = p.sort_values(measure, ascending=False).reset_index(drop=True)
    p["share"] = p[measure] / p[measure].sum()
    p["cumulative_share"] = p["share"].cumsum()
    prev = p["cumulative_share"].shift(fill_value=0)
    p["class"] = pd.cut(prev, [-0.01, 0.70, 0.90, 1.01], labels=["A", "B", "C"]).astype(str)
    p["margin"] = p["profit"] / p["revenue"]
    return p


def by_store(s: pd.DataFrame) -> pd.DataFrame:
    lfl = like_for_like(s, by="Store_ID")
    y0, y1 = lfl.attrs["years"]
    t = s.groupby("Store_ID").agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("Sale_ID", "size")).reset_index()
    t = t.merge(lfl[["Store_ID", "revenue_growth"]], on="Store_ID")
    t["margin"] = t["profit"] / t["revenue"]
    return t.sort_values("revenue", ascending=False).reset_index(drop=True)


def weekday_month(s: pd.DataFrame) -> pd.DataFrame:
    """Average daily revenue for each weekday in each calendar month."""
    d = s.groupby(s["Date"].dt.normalize())["revenue"].sum().rename("revenue").reset_index()
    d["weekday"] = d["Date"].dt.day_name().str[:3]
    d["month"] = d["Date"].dt.month_name().str[:3]
    t = d.groupby(["month", "weekday"])["revenue"].mean().unstack()
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    return t.reindex(index=[m for m in months if m in t.index], columns=days)
