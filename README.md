# 🧸 Toy Store KPI Report

**Retail Business Intelligence | Power BI • DAX • Data Modeling • Revenue & Profit KPIs**

A **Power BI** report tracking the key performance indicators of a toy store chain across 50 stores — orders, revenue and profit — with trends over time and breakdowns by product category.

![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=flat-square&logo=powerbi&logoColor=black)
![DAX](https://img.shields.io/badge/DAX-F2C811?style=flat-square)

## Business value

Bring sales, products and calendar data into an interactive retail performance report. KPI cards, category comparisons and time drill-down help stakeholders examine revenue, profitability and sales activity.

### Questions this project addresses

- How do revenue and profit change over time?
- Which product categories contribute the most sales?
- What happens to the KPIs when a category filter is applied?


## 📋 Overview

Management wants a single page that answers: *How much are we selling, how profitable is it, and which product categories drive the business?* This report brings together over **829,000 sales transactions** from January 2022 to September 2023 into one interactive view.

## 📈 Results at a Glance

Charts built with Python (pandas + matplotlib) from the data files in this repo.

<p align="center"><img src="docs/images/monthly_revenue.png" alt="Monthly revenue line chart, January 2022 to September 2023" width="85%"></p>

<p align="center"><img src="docs/images/category_revenue.png" alt="Revenue by product category" width="85%"></p>

## 🗂️ Data Model

Star schema with one fact table and three dimension tables:

| Table | Rows | Description |
|-------|------|-------------|
| `sales.csv` *(fact)* | 829,262 | Sale ID, date, store ID, product ID, units |
| `products.csv` | 35 | Product name, category, cost, price |
| `stores.csv` | 4 | Store location types: Airport, Commercial, Downtown, Residential |
| `calendar.csv` | 638 | Date table, 1 Jan 2022 – 30 Sep 2023 |

**Product categories:** Toys, Art & Crafts, Games, Sports & Outdoors, Electronics

## 📊 Report Page

- **3 KPI cards** — **Total Orders**, **Revenue (M)** and **Profit (M)**, each with a monthly trend
- **Clustered bar chart** — total orders by product category
- **Line chart** — revenue over time, with drill-down from month to week to day
- **Product category slicer** — filters the whole page

## 💡 Key Figures (from the data)

- **Total revenue:** ~$14.4M · **Total profit:** ~$4.0M · **Units sold:** ~1.09M
- **Toys** is by far the largest category (~$5.1M revenue), followed by Art & Crafts (~$2.7M)

## 📁 Repository Contents

```
├── Toy Store KPI Report.pbix   # Power BI report
├── sales.csv
├── products.csv
├── stores.csv
├── calendar.csv
└── README.md
```

## 🚀 How to Use

Download `Toy Store KPI Report.pbix` and open it in **[Power BI Desktop](https://powerbi.microsoft.com/desktop/)** (free, Windows). The data is already loaded in the file; the CSVs are included so you can rebuild or extend the model.

## 🛠️ Skills Demonstrated

Data modelling (star schema) · DAX measures · KPI visuals · date hierarchies & drill-down · interactive report design

---

👤 **Tony Mulunda** — [GitHub @Scarface96](https://github.com/Scarface96)

## Interpretation & limitations

Transaction count and units sold are different measures. Reconcile report totals with the source files before reuse, and verify the grain and keys of the store dimension before extending store-level analysis.

## Explore the analytics portfolio

- [sql_retail_sales_p1](https://github.com/Scarface96/sql_retail_sales_p1)
- [HR-Analysis-Dashboard](https://github.com/Scarface96/HR-Analysis-Dashboard)
- [Global-CO2-Emissions-Dashboard](https://github.com/Scarface96/Global-CO2-Emissions-Dashboard)
- [B2B-Sales-Pipeline-CRM-Dashboard-for-TechSolutions-Inc.](https://github.com/Scarface96/B2B-Sales-Pipeline-CRM-Dashboard-for-TechSolutions-Inc.)

## About This Project

A Power BI business-intelligence project designed to give retail stakeholders a concise view of orders, revenue and profitability. It demonstrates star-schema data modelling, DAX measures, KPI design, interactive filtering and management-focused dashboard storytelling.
