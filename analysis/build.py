"""Run the toy store analysis and write the website to site/index.html.

    python -m analysis.build
"""

import warnings

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from . import data, forecast
from .report import AQUA, AXIS, BLUE, GRID, INK_2, MUTED, ORANGE, SEQUENTIAL, SERIES, Report, money, pct, style

warnings.filterwarnings("ignore", module="statsmodels")
REPO = "Scarface96/Toy-Store-KPI-Report"
CATS = ["Toys", "Art & Crafts", "Games", "Sports & Outdoors", "Electronics"]  # fixed colour order


def trend_figure(s: pd.DataFrame) -> go.Figure:
    """Monthly revenue and profit, with a menu to show one category at a time."""
    groups = [("All categories", s)] + [(c, s[s["category"] == c]) for c in CATS]
    fig = go.Figure()
    for i, (name, g) in enumerate(groups):
        m = data.monthly(g)
        vis = i == 0
        fig.add_scatter(x=m["month"], y=m["revenue"], name="Revenue", mode="lines", line=dict(color=BLUE, width=2), visible=vis,
                        hovertemplate="%{x|%b %Y}<br>Revenue %{y:$,.0f}<extra></extra>")
        fig.add_scatter(x=m["month"], y=m["profit"], name="Profit", mode="lines", line=dict(color=ORANGE, width=2), visible=vis,
                        hovertemplate="%{x|%b %Y}<br>Profit %{y:$,.0f}<extra></extra>")
    buttons = []
    for i, (name, _) in enumerate(groups):
        vis = [False] * (2 * len(groups))
        vis[2 * i] = vis[2 * i + 1] = True
        buttons.append(dict(label=name, method="update", args=[{"visible": vis}]))
    style(fig, height=420)
    fig.update_layout(
        updatemenus=[dict(buttons=buttons, direction="down", x=1, xanchor="right", y=1.14, yanchor="top", bgcolor="white", bordercolor=AXIS, font=dict(size=13))],
        legend=dict(x=0, y=1.08),
        margin=dict(t=48),
    )
    fig.update_yaxes(tickprefix="$", rangemode="tozero")
    return fig


def margin_figure(m: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(x=m["month"], y=m["margin"], mode="lines+markers", line=dict(color=BLUE, width=2), marker=dict(size=8, line=dict(color="#fcfcfb", width=2)),
                               hovertemplate="%{x|%b %Y}<br>Profit margin %{y:.1%}<extra></extra>"))
    for year, g in m.groupby(m["month"].dt.year):
        avg = g["profit"].sum() / g["revenue"].sum()
        fig.add_scatter(x=[g["month"].min(), g["month"].max()], y=[avg, avg], mode="lines", line=dict(color=MUTED, dash="dot", width=1), hoverinfo="skip", showlegend=False)
        fig.add_annotation(x=g["month"].max(), y=avg, text=f"{year} average {avg:.1%}", showarrow=False, yshift=12, xanchor="right", font=dict(size=12, color=MUTED))
    style(fig, height=320, legend=False)
    fig.update_yaxes(tickformat=".0%")
    return fig


def category_figure(cat: pd.DataFrame) -> go.Figure:
    t = cat.set_index("category").loc[CATS[::-1]].reset_index()
    fig = go.Figure()
    fig.add_bar(y=t["category"], x=t["revenue_growth"], name="Revenue growth", orientation="h", marker_color=BLUE, hovertemplate="%{y}<br>Revenue %{x:+.0%}<extra></extra>")
    fig.add_bar(y=t["category"], x=t["profit_growth"], name="Profit growth", orientation="h", marker_color=ORANGE, hovertemplate="%{y}<br>Profit %{x:+.0%}<extra></extra>")
    style(fig, height=380)
    fig.update_layout(barmode="group", bargroupgap=0.08)
    fig.update_xaxes(tickformat="+.0%", showgrid=True, gridcolor=GRID, zeroline=True, zerolinecolor=AXIS, title="Jan–Sep 2023 vs Jan–Sep 2022")
    fig.update_yaxes(showgrid=False)
    return fig


def portfolio_figure(p: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for i, cls in enumerate(["A", "B", "C"]):
        g = p[p["class"] == cls]
        fig.add_scatter(
            x=g["units"], y=g["margin"], mode="markers", name=f"Class {cls}",
            marker=dict(color=SERIES[i], size=np.sqrt(g["profit"]) / 18 + 8, line=dict(color="#fcfcfb", width=2), opacity=0.9),
            customdata=np.stack([g["product"], g["category"], g["profit"]], axis=1),
            hovertemplate="<b>%{customdata[0]}</b> (%{customdata[1]})<br>%{x:,} units, margin %{y:.0%}<br>Profit %{customdata[2]:$,.0f}<extra></extra>",
        )
    # Label a few products, each with its own offset so labels never collide.
    labels = {p.iloc[0]["product"]: (0, -40), "Action Figure": (-60, 30), "Lego Bricks": (-70, -10), "Glass Marbles": (-40, -36)}
    for name, (ax, ay) in labels.items():
        row = p[p["product"] == name]
        if row.empty:
            continue
        r = row.iloc[0]
        fig.add_annotation(x=np.log10(r["units"]), y=r["margin"], text=name, ax=ax, ay=ay, showarrow=True, arrowcolor=AXIS, arrowwidth=1, arrowhead=0, font=dict(size=12, color=INK_2), bgcolor="rgba(252,252,251,.85)")
    style(fig, height=480)
    fig.update_xaxes(type="log", title="Units sold (log scale)", showgrid=True, gridcolor=GRID)
    fig.update_yaxes(title="Profit margin", tickformat=".0%")
    return fig


def pareto_figure(p: pd.DataFrame) -> go.Figure:
    colors = {"A": SERIES[0], "B": SERIES[1], "C": SERIES[2]}
    fig = go.Figure()
    fig.add_bar(x=p["product"], y=p["share"], marker_color=[colors[c] for c in p["class"]], name="Share of profit", showlegend=False,
                customdata=p["class"], hovertemplate="%{x}<br>%{y:.1%} of profit, class %{customdata}<extra></extra>")
    fig.add_scatter(x=p["product"], y=p["cumulative_share"], mode="lines", name="Cumulative share", line=dict(color=INK_2, width=2),
                    hovertemplate="Top products up to %{x}: %{y:.0%} of profit<extra></extra>")
    style(fig, height=420)
    fig.update_yaxes(tickformat=".0%", range=[0, 1.02])
    fig.update_xaxes(tickangle=-50, tickfont=dict(size=11))
    return fig


def store_figure(st: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=st["revenue"], y=st["revenue_growth"], mode="markers",
        marker=dict(color=BLUE, size=11, line=dict(color="#fcfcfb", width=2)),
        customdata=np.stack([st["Store_ID"], st["margin"]], axis=1),
        hovertemplate="Store %{customdata[0]}<br>Revenue %{x:$,.0f}<br>Like-for-like growth %{y:+.0%}<br>Margin %{customdata[1]:.0%}<extra></extra>",
    ))
    med = st["revenue_growth"].median()
    fig.add_hline(y=med, line=dict(color=MUTED, width=1, dash="dot"), annotation_text=f"Median store {med:+.0%}", annotation_position="top left", annotation_font_color=MUTED)
    style(fig, height=420, legend=False)
    fig.update_xaxes(title="Total revenue, Jan 2022 – Sep 2023", tickprefix="$", showgrid=True, gridcolor=GRID)
    fig.update_yaxes(title="Revenue growth, Jan–Sep 2023 vs 2022", tickformat="+.0%", zeroline=True, zerolinecolor=AXIS)
    return fig


def heatmap_figure(h: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=h.values, x=h.columns, y=h.index, colorscale=[[i / (len(SEQUENTIAL) - 1), c] for i, c in enumerate(SEQUENTIAL)],
        xgap=2, ygap=2, colorbar=dict(title=dict(text="Avg daily<br>revenue"), tickprefix="$", thickness=12, outlinewidth=0),
        hovertemplate="%{y}, %{x}<br>Average day %{z:$,.0f}<extra></extra>",
    ))
    style(fig, height=440, legend=False)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(side="top")
    return fig


def forecast_figure(f: dict) -> go.Figure:
    h, best = f["history"], f["best"]
    fig = go.Figure()
    fig.add_scatter(x=h.index, y=h.values, mode="lines", name="Actual", line=dict(color=BLUE, width=2), hovertemplate="%{x|%b %Y}<br>Actual %{y:$,.0f}<extra></extra>")
    idx = f["forecast"].index
    fig.add_scatter(x=list(idx) + list(idx[::-1]), y=list(f["high"]) + list(f["low"][::-1]), fill="toself", fillcolor="rgba(235,104,52,0.15)", mode="lines", line=dict(width=0), hoverinfo="skip", name="Typical error range")
    names = {"seasonal_naive": "Seasonal method", "holt": "Trend method", "blend": "Average of both"}
    colors = {"seasonal_naive": AQUA, "holt": ORANGE, "blend": SERIES[6]}
    for key, path in f["paths"].items():
        x = [h.index[-1]] + list(path.index)
        y = [h.values[-1]] + list(path.values)
        fig.add_scatter(x=x, y=y, mode="lines+markers", name=names[key] + (" (chosen)" if key == best else ""),
                        line=dict(color=colors[key], width=2 if key == best else 1.5, dash="solid" if key == best else "dot"),
                        marker=dict(size=8 if key == best else 6), hovertemplate=f"%{{x|%b %Y}}<br>{names[key]} %{{y:$,.0f}}<extra></extra>")
    style(fig, height=440)
    fig.update_yaxes(tickprefix="$", rangemode="tozero")
    return fig


def main(out="site/index.html"):
    products = data.load_products()
    s = data.load_sales(products=products)
    cal = data.check_calendar(s)
    t = data.totals(s)
    lfl = data.like_for_like(s)
    y0, y1 = lfl.attrs["years"]
    g_rev, g_prof = lfl.loc[0, "revenue_growth"], lfl.loc[0, "profit_growth"]
    cat = data.like_for_like(s, by="category")
    prod_lfl = data.like_for_like(s, by="product").set_index("product")
    port = data.abc(s)
    st = data.by_store(s)
    m = data.monthly(s)
    f = forecast.forecast(m)
    margin = {y: g["profit"].sum() / g["revenue"].sum() for y, g in m.groupby(m["month"].dt.year)}
    top = port.iloc[0]
    top_drop = prod_lfl.loc[top["product"], "revenue_growth"]
    a_count = int((port["class"] == "A").sum())
    a_share = port.loc[port["class"] == "A", "share"].sum()
    elec = cat.set_index("category").loc["Electronics"]
    art = cat.set_index("category").loc["Art & Crafts"]
    q4 = f["forecast"].sum()
    sn_q4 = f["paths"]["seasonal_naive"].sum()

    r = Report(
        title=f"Sales grew {g_rev:.0%} this year, but profit grew only {g_prof:.0%}",
        project="Toy Store KPI Report",
        summary=(
            f"Across 50 stores and {t['orders']:,} sales, the chain earned {money(t['revenue'])} in revenue and {money(t['profit'])} in profit. "
            f"Comparing January–September {y1} with the same months of {y0}, growth came mostly from lower-margin lines, while the most "
            f"profitable product, {top['product']}, lost {abs(top_drop):.0%} of its sales. Profit margin slipped from {margin[y0]:.1%} to {margin[y1]:.1%}."
        ),
        repo=REPO,
        accent=ORANGE,
        source="sales.csv (829,262 transactions), products.csv (35 products with cost and price), stores.csv and calendar.csv, January 2022 to September 2023.",
        method=(
            "pandas joins the star schema and computes revenue (units × price) and profit (units × (price − cost)). Growth compares the same "
            "nine months in both years. Products are classed A/B/C by share of profit. The forecast compares three methods in a "
            "six-month backtest using statsmodels, and the one with the lowest error is chosen."
        ),
    )
    r.kpis([
        (money(t["revenue"]), "revenue", f"{t['units']:,} units sold"),
        (money(t["profit"]), "profit", f"{t['margin']:.1%} margin"),
        (f"{g_rev:+.0%}", "revenue growth", f"Jan–Sep {y1} vs {y0}"),
        (f"{g_prof:+.0%}", "profit growth", "same months"),
    ])

    r.section(
        "How are revenue and profit moving?",
        "<p>Both lines climb through 2022 and into 2023, but the gap between them widens: revenue rises faster than profit. "
        "Use the menu to see each category on its own.</p>",
        fig=trend_figure(s),
        table=m.assign(margin=(m["margin"] * 100).round(1), month=m["month"].dt.strftime("%b %Y")).round(0).rename(columns={"margin": "margin %"}),
    )
    r.section(
        "Is the business getting less profitable?",
        f"<p>Yes. Profit margin averaged <b>{margin[y0]:.1%}</b> in {y0} and <b>{margin[y1]:.1%}</b> in {y1}. Each product has one fixed price in the data, so the "
        "slide comes entirely from the sales mix: customers are buying more of the products that earn less per sale.</p>",
        fig=margin_figure(m),
    )
    cat_t = cat.copy()
    for c in ["revenue_growth", "profit_growth"]:
        cat_t[c] = (cat_t[c] * 100).round(1)
    r.section(
        "Which categories are driving the change?",
        f"<p><b>Art &amp; Crafts</b> more than tripled ({art['revenue_growth']:+.0%}), and Games, Toys and Sports grew steadily. "
        f"<b>Electronics fell {abs(elec['revenue_growth']):.0%}</b>, and its profit fell further ({elec['profit_growth']:+.0%}), because "
        "it holds the chain's highest-margin products.</p>",
        fig=category_figure(cat),
        table=cat_t.round(0).rename(columns={"revenue_growth": "revenue growth %", "profit_growth": "profit growth %"}),
    )
    r.section(
        "Which products earn the money?",
        f"<p>Every product, placed by how many units it sells and how much of each sale is profit. Bubble size is total profit. "
        f"<b>{top['product']}</b> stands alone: a {top['margin']:.0%} margin and {top['share']:.0%} of all profit. "
        "Lego Bricks sells in volume but keeps only about an eighth of each sale.</p>",
        fig=portfolio_figure(port),
        note="Classes: A = products making up the first 70% of profit, B = the next 20%, C = the last 10%.",
    )
    port_t = port[["product", "category", "units", "revenue", "profit", "margin", "share", "class"]].copy()
    port_t["margin"] = (port_t["margin"] * 100).round(1)
    port_t["share"] = (port_t["share"] * 100).round(2)
    r.section(
        "How concentrated is profit?",
        f"<p>Just <b>{a_count} of 35 products earn {a_share:.0%} of the profit</b>. Those A-class lines are the ones to keep in stock, "
        "promote and protect. The 14 C-class products together earn less than a tenth, which makes them candidates for review.</p>",
        fig=pareto_figure(port),
        table=port_t.round(0).rename(columns={"margin": "margin %", "share": "share of profit %"}),
    )
    st_t = st.copy()
    st_t["revenue_growth"] = (st_t["revenue_growth"] * 100).round(1)
    st_t["margin"] = (st_t["margin"] * 100).round(1)
    shrinking = int((st["revenue_growth"] < 0).sum())
    r.section(
        "Are all stores growing?",
        f"<p>Most are: the median store grew <b>{st['revenue_growth'].median():+.0%}</b>. But growth varies widely, from "
        f"{st['revenue_growth'].min():+.0%} to {st['revenue_growth'].max():+.0%}, and <b>{shrinking} stores shrank</b>. "
        "Hover a dot to see which store it is.</p>",
        fig=store_figure(st),
        table=st_t.round(0).rename(columns={"Store_ID": "store", "revenue_growth": "growth %", "margin": "margin %"}),
        note="The store table in this dataset only lists location types, not which store is which, so stores are shown by ID.",
    )
    h = data.weekday_month(s)
    r.section(
        "When do customers buy?",
        "<p>Average revenue for each weekday in each month. <b>Fridays and Saturdays</b> are the busiest days all year, nearly double a "
        "typical Monday, and December lifts every day of the week. Staffing and promotions should follow the same rhythm.</p>",
        fig=heatmap_figure(h),
        table=h.round(0).reset_index(),
    )
    bt = f["backtest"].copy()
    bt["month"] = bt["month"].dt.strftime("%b %Y")
    for c in ["seasonal_naive_error", "holt_error", "blend_error"]:
        bt[c] = (bt[c] * 100).round(1)
    names = {"seasonal_naive": "seasonal method", "holt": "trend method", "blend": "average of both"}
    err = f["errors"]
    r.section(
        "What should the chain expect for October to December?",
        f"<p>Three simple methods were tested on the last six months of known data. The <b>{names[f['best']]}</b> was closest, off by "
        f"{err[f['best']]:.0%} a month on average (seasonal {err['seasonal_naive']:.0%}, trend {err['holt']:.0%}, average {err['blend']:.0%}). "
        f"It projects about <b>{money(q4)}</b> for the quarter.</p>"
        f"<p>Treat that as a floor. The backtest contained no holiday months, and the seasonal method, which copies last year's "
        f"December spike, points to about <b>{money(sn_q4)}</b>. Planning stock between those two numbers is the prudent call.</p>",
        fig=forecast_figure(f),
        table=bt.round(0).rename(columns={"seasonal_naive": "seasonal", "holt": "trend", "blend": "average", "seasonal_naive_error": "seasonal error %", "holt_error": "trend error %", "blend_error": "average error %"}),
        table_caption="Show the backtest",
    )

    path = r.write(out)
    print(f"Wrote {path} ({path.stat().st_size / 1024:.0f} KB). Calendar check: {cal}")
    return r


if __name__ == "__main__":
    main()
