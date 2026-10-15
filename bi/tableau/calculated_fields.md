# Tableau calculated fields: Toy Store KPI Report

Create each one with **Analysis → Create Calculated Field**, name it exactly as shown, and paste the formula.
Tableau shows CSV columns in title case (`new_cases` becomes *New Cases*). If yours show the raw names, use those in the formulas.

## Connect the data

Connect to `sales.csv` in the repo root. Double-click it to open the physical layer and add `bi/data/dim_product.csv` with a **left join** on `Product_ID = Product_ID`, then `bi/data/dim_date.csv` with a **left join** on `Date = date`. Joins (not relationships) are needed because revenue is units × price on every row. If Tableau reads `Date` as text, change its type to Date first.

## Fields

### Revenue

```
SUM([Units] * [Price])
```

### Profit

```
SUM([Units] * [Unit Margin])
```

### Profit Margin

```
[Profit] / [Revenue]
```

Format as percentage.

### Revenue LFL

```
SUM(IF [Like For Like] = 1 THEN [Units] * [Price] END)
```

Revenue in the months both years have (Jan-Sep).

### LFL Growth

```
SUM(IF [Like For Like] = 1 AND YEAR([Date]) = 2023 THEN [Units] * [Price] END)
/ SUM(IF [Like For Like] = 1 AND YEAR([Date]) = 2022 THEN [Units] * [Price] END) - 1
```

Fair year-on-year growth. Matches the 'Like-for-like' figure below.

### Profit Running Share

```
RUNNING_SUM(SUM([Units] * [Unit Margin])) / TOTAL(SUM([Units] * [Unit Margin]))
```

Table calc for the Pareto chart: products sorted by Profit descending, compute using Product.

### Store

```
"Store " + STR([Store Id])
```

stores.csv only lists location names with no ID, so stores are shown by ID.
