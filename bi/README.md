# 📊 Toy Store KPI Report: Tableau & Power BI kit

Everything needed to rebuild this project as a Tableau dashboard in under an hour: model-ready data, ready-to-paste Tableau calculated fields, a matching colour theme, a page-by-page layout, and the exact numbers your finished dashboard should show.

> **Interactive web version:** [scarface96.github.io/Toy-Store-KPI-Report](https://scarface96.github.io/Toy-Store-KPI-Report/). The kit uses the same cleaned data, so the numbers will match.

> **Power BI version:** already built, see [`Toy Store KPI Report.pbix`](../Toy%20Store%20KPI%20Report.pbix). This kit adds the Tableau version.

## What's in this folder

| File | What it is |
|---|---|
| `sales.csv (repo root)` | one row per sale (829,262): date, store ID, product ID, units; used as-is, not copied |
| `data/dim_product.csv` | one row per product: numeric cost, price and margin (the source stores "$15.99 " as text), category, ABC class by profit |
| `data/dim_date.csv` | one row per day: year, month, weekday, `like_for_like` flag for Jan-Sep (2023 data stops in September) |
| `tableau/calculated_fields.md` | Every calculated field, plus how to connect the tables |
| `tableau/Preferences.tps` | The same colours as Tableau palettes |
| `kpis.json` | Headline numbers, for checking your build |
| `build_bi.py` | Regenerates everything here from the repo's own cleaning code: `python -m bi.build_bi` |

## Dashboard design

Canvas 1280 × 720. Light page background, white cards, teal for the main series, amber to highlight, red only for bad news.

### Page 1: KPI overview
*How is the business doing?*

- BANs: Revenue · Profit · Profit Margin · LFL Growth
- Line chart: Revenue by MONTH([Date]), colour YEAR([Date])
- Bar chart: Revenue and Profit Margin by Category
- Filter: Category (applied to all sheets)

### Page 2: Products
*Which products carry the business?*

- Pareto: bars = Profit by Product (sorted), line = Profit Running Share on dual axis, colour by ABC Class
- Scatter: Units vs Unit Margin by Product, size Revenue

### Page 3: Stores and seasonality
*Where and when do we sell?*

- Bar chart: Revenue by Store, sorted, colour by LFL Growth (diverging palette)
- Highlight table: Weekday × Month, average daily revenue (AVG of a FIXED daily revenue LOD)

## Build it in Tableau

1. Copy `tableau/Preferences.tps` to `Documents/My Tableau Repository/` (or merge its palettes into the one there) and restart Tableau.
2. Connect the data as described at the top of `tableau/calculated_fields.md`.
3. Create the calculated fields in that file.
4. Build one sheet per chart above, then a dashboard per page at 1280 × 720 (Fixed size). Use the *Tony Mulunda* palettes for colour.
5. Check your BANs against **Check your numbers** below.
6. **File → Save to Tableau Public**, then save the packaged workbook (`.twbx`) in the repo root.

## Check your numbers

Your finished dashboard (no filters applied) should show:

| Measure | Value |
|---|---|
| Revenue | 14,444,572.35 |
| Profit | 4,014,029 |
| Profit margin | 27.8% |
| Sales transactions | 829,262 |
| Units sold | 1,090,565 |
| Like-for-like revenue growth (Jan-Sep 2022 to 2023) | 30.9% |
| Top store by revenue | Store 31 (554,553) |
| Class A products (top 70% of profit) | 12 |
| Date range | 2022-01-01 to 2023-09-30 |

If a number is off, the usual causes are a relationship pointing the wrong way, a date column loaded as text, or a missing join.

## Notes on the data

- The Power BI version already exists in the repo root (`Toy Store KPI Report.pbix`). This kit adds a matching Tableau version.

## Publish and show it off

- **Tableau Public:** after saving, copy the share link and add it to the main README next to the live web report.
- Take a 1280 × 720 screenshot of page 1 and put it at the top of the main README, so it's the first thing a recruiter sees.
