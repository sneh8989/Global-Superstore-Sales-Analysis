# Power BI Dashboard Architecture & Verification Guide

This document provides a technical walkthrough of the **Global Superstore Sales Analytics** Power BI dashboard located at `dashboard/SuperstoreDashboard.pbix`.

---

## 1. Data Model Overview

The Power BI data model utilizes an efficient Star-Schema semantic structure:
- **Fact Table (`cleaned_superstore`):** 51,290 records tracking transactional orders across sales, profit, quantity, discount, customer, product, and geography.
- **Dimension Table (`DateTable`):** Dedicated calendar table providing continuous date hierarchies, month names, quarters, and YearMonth keys.
- **Relationship:** `cleaned_superstore[Order.Date]` connected $N:1$ with `DateTable[Date]`.

---

## 2. Core DAX Measures Specification

All business metrics are centralized as explicit DAX measures:

### Total Sales
```dax
Total Sales = SUM(cleaned_superstore[Sales])
```
- **Value:** \$12,642,905.00
- **Purpose:** Primary top-line revenue metric.

### Total Profit
```dax
Total Profit = SUM(cleaned_superstore[Profit])
```
- **Value:** \$1,467,457.29
- **Purpose:** Primary bottom-line profitability metric.

### Profit Margin %
```dax
Profit Margin % = DIVIDE([Total Profit], [Total Sales], 0)
```
- **Value:** 11.61%
- **Format:** Percentage (`0.00%`)

### Order Count
```dax
Order Count = DISTINCTCOUNT(cleaned_superstore[Order.ID])
```
- **Value:** 25,035
- **Purpose:** Unique customer transactions fulfilled.

### Average Order Value (AOV)
```dax
Avg Order Value = DIVIDE([Total Sales], [Order Count], 0)
```
- **Value:** \$505.01
- **Format:** Currency (`$#,##0.00`)

### Total Quantity
```dax
Total Quantity = SUM(cleaned_superstore[Quantity])
```
- **Value:** 178,312 units

---

## 3. Report Pages & Visual Hierarchy

The Power BI workbook consists of 5 specialized pages designed for executive decision-making:

### Page 1: Executive Overview (11 Visuals)
- **Top Metric Cards:** 5 KPI cards displaying `Total Sales`, `Total Profit`, `Profit Margin %`, `Order Count`, and `Avg Order Value`.
- **Monthly Trajectory:** Line & clustered column combo chart (`DateTable.YearMonth` on Category, `Total Sales` on Primary Y, `Profit Margin %` on Secondary Y).
- **Category Share:** Donut chart of `Total Sales` by `Category`.
- **Hierarchical Treemap:** `Category` and `Sub.Category` breakdown by `Total Sales`.
- **Interactive Multi-Filter Slicer:** Unified slicer across `Year`, `Category`, `Segment`, and `Region`.

### Page 2: Sales & Profit Analysis (5 Visuals)
- **Sub-Category Comparison:** Clustered bar chart of `Total Sales` and `Total Profit` by `Sub.Category`.
- **Product Profitability Scatter:** Scatter chart plotting `Total Sales` (X) vs. `Total Profit` (Y) with bubble size representing `Total Quantity`.
- **Regional Matrix Table:** Cross-tabulation matrix of `Region` (Rows) by `Category` (Columns) evaluating `Total Sales`, `Total Profit`, and `Profit Margin %`.
- **Discount Impact Curve:** Line chart plotting `Discount` rate vs. `Total Profit` illustrating margin erosion.
- **Fulfillment Matrix:** Bar chart of `Ship.Mode` vs. `Order Count` grouped by `Order.Priority`.

### Page 3: Customer & Product Insights (4 Visuals)
- **Top 10 Customers:** Ranked horizontal bar chart of the highest revenue-generating customers.
- **Top 10 Profitable Products:** Bar chart highlighting the most lucrative product SKUs.
- **Top 10 Loss-Making Products:** Bar chart displaying the SKUs incurring the highest net losses (identifying products needing immediate price revisions).
- **Segment Contribution:** Pie chart displaying revenue split across `Consumer`, `Corporate`, and `Home Office`.

### Page 4: Geographic Performance (2 Visuals)
- **Global Bubble Map:** Interactive world map plotting country-level sales volume with dynamic bubbles.
- **Market & Regional Hierarchy:** Clustered bar chart comparing revenue across the 7 global markets and 13 sales regions.

### Page 5: Map Tooltip (3 Visuals)
- Custom hover tooltip providing instant card KPIs (`Total Sales`, `Total Profit`, `Order Count`) upon hovering over any country on the Geographic Map.

---

## 4. How to Open and Refresh

1. Install **Microsoft Power BI Desktop** (Windows).
2. Open `dashboard/SuperstoreDashboard.pbix`.
3. The report immediately opens in interactive view mode with all pre-loaded visuals and calculations.
4. To refresh with new data: Ensure `data/processed/cleaned_superstore.csv` is updated, click **Home > Refresh** in Power BI Desktop.
