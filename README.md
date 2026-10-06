# 🧸 Toy Store KPI Report

A **Power BI** report tracking the key performance indicators of a toy store chain across 50 stores — orders, revenue and profit — with trends over time and breakdowns by product category.

![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=flat-square&logo=powerbi&logoColor=black)
![DAX](https://img.shields.io/badge/DAX-F2C811?style=flat-square)

## 📋 Overview

Management wants a single page that answers: *How much are we selling, how profitable is it, and which product categories drive the business?* This report brings together over **829,000 sales transactions** from January 2022 to September 2023 into one interactive view.

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
