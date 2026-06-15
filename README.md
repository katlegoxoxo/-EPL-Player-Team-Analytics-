#  EPL Player & Team Analytics — Databricks SQL Project

 English Premier League data analysis project built on **Databricks**, combining player and team statistics from the **2024/25 season**. The project covers data cleaning, transformation, and SQL-based analytical views covering goal contributions, assist providers, team rankings, and player usage patterns.

---



##  Tech Stack

| Tool | Purpose |
|------|---------|
| **Databricks** | SQL workspace, dataset management, Lakeview dashboards |
| **Apache Spark SQL** | Query engine for all analytical views |
| **Python (Pandas)** | Data cleaning, season concatenation, ETL pipeline |
| **Google Colab** | Preprocessing notebook environment |
| **FBref** | Primary stats source (goals, assists, minutes, cards) |
| **Transfermarkt** | Player metadata (nationality, preferred foot, market value) |

---

## 🔄 Data Pipeline

```
FBref / Transfermarkt
        │
        ▼
  Google Colab (Python)
  - Clean nulls & zero-minute rows
  - Normalize column names
  - Add season column (2024/25 | 2025/26)
  - Concat into single CSV
        │
        ▼
  Databricks (Upload)
  - Register as Delta table
  - Run SQL cleaning view (≥90 min filter)
        │
        ▼
  SQL Analytical Views
  - Team rankings, top scorers, assist leaders
  - Age-group breakdowns, productivity rankings
        │
        ▼
  Lakeview Dashboard
```

---

## 🧹 Data Cleaning Notes

- Players with **fewer than 90 minutes** played are excluded from all views — this is standard practice to avoid skewing per-90 statistics
- The 2024/25 CSV had **397 rows with entirely null stats** (no minutes, goals, or assists) — these were dropped during preprocessing
- The `minutes` column in the 2024/25 dataset contained comma-formatted strings (e.g. `"2,825"`) — converted to integers before loading


---

##  Key Analysis Areas

- **Goals excl. penalties** — separating genuine scorers from penalty takers
- **Team output distribution** — squads that rely on one player vs spread contribution
- **Positional productivity** — G+A rates by FW / MF / DF
- **Age group trends** — which age bands contribute most to goal output
- **Preferred foot analysis** — performance patterns by dominant foot

---

## Getting Started

### Prerequisites
- Databricks workspace (Community Edition works)


### Steps

1. **Clone this repo**
   ```bash
   git clone https://github.com/katlegoxoxo/-EPL-Player-Team-Analytics-.git
   cd epl-databricks-analytics
   ```

2. **Run the cleaning notebook**
   Open `notebooks/epl_data_cleaning.ipynb` in Google Colab or Jupyter, upload both raw data files, and run all cells. This outputs `epl_combined_2024_25.csv`.

3. **Upload to Databricks**
   - Go to your Databricks workspace → **Data** → **Add data**
   - Upload `epl_combined_2024_25.csv` as a Delta table

4. **Run SQL views in order**
   Execute the SQL scripts in the `sql/` folder in numerical order (01 → 08), each view builds on the cleaned base table.

---

##  Data Sources

- [FBref — Football Reference](https://fbref.com) — match stats, per-90 metrics, positional data
- [Transfermarkt](https://www.transfermarkt.com) — player profiles, nationalities, preferred foot

> **Note:** Data was scraped and compiled for educational and research purposes only.

---

##  Author

**Katlego** — Junior Data Analyst  
Diploma in IT (Software Development) — IIE Rosebank College  

---

## 📄 License

This project is for educational and portfolio purposes. All football statistics belong to their respective data providers.
