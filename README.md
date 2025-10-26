# 🧠 Cardivore AI (Demo Version)

**Cardivore AI** is an eBay Pokémon card analysis demo designed to show how a data pipeline can extract, normalize, and analyze graded vs. raw card sales to identify potential grading ROI opportunities.

This **demo version** runs entirely in SQLite — no MySQL setup required — and includes Jupyter Notebooks for both building and exploring the dataset.

---

## 🚀 Quick Start

### 1. Build the Demo Data
Open the notebook:
notebooks/01_pipeline_builder.ipynb

markdown
Copy code

Run all cells.  
This will:
- Load data from `/data/raw/`
- Normalize and clean it
- Create tables in `/data/database/card_demo.db`
- Generate a `card_summary` table for analysis

### 2. Launch the Viewer
Open the notebook:
notebooks/02_demo_launcher.ipynb

yaml
Copy code

If the database already exists, this notebook launches the ROI Dashboard directly.  
If not, you’ll see a message prompting you to run the builder first.

---

## 📂 Project Structure

cardivore_ai_demo/
│
├── data/
│ ├── raw/ # Input CSVs from MarketMovers
│ └── database/ # SQLite database lives here
│ └── card_demo.db
│
├── cardivore_ai/
│ ├── utils/ # Core helper modules
│ └── init.py
│
└── notebooks/
├── 01_pipeline_builder.ipynb
└── 02_demo_launcher.ipynb

markdown
Copy code

---

## 🔄 Updating Data Files

1. Go to **[MarketMoversApp.com](https://marketmoversapp.com)** → **Movements**
2. Set filters for the card set(s) you want
3. Under **Grade**, select:
   - **“Graded Only”**
   - **“PSA 10”**
   - Click **Download**
4. Save that file to:
/data/raw/psa10_historic_sales.csv

kotlin
Copy code
5. Repeat the same process, but this time set **Grade = Raw**, and save that file as:
/data/raw/psa10_raw_sales.csv

yaml
Copy code

> ⚠️ **Note:**  
> This demo is not optimized for massive datasets.  
> It runs smoothly with roughly 30 days of data for a single Pokémon set, but performance beyond that is not guaranteed.

---

## 🧩 What’s Next

- **Phase 2:** Add automated photo quality evaluation  
- **Phase 3:** Train an ML model to predict grading potential  

---

## 📜 License

The **demo version** is released under a **freeware license** for non-commercial use.  
The underlying production application is proprietary.

---

**Made with 🧠 + 🐍 + ❤️ in Pittsburgh**
