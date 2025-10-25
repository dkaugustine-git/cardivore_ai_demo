# Cardivore_AI

## 🎯 Project Overview  
**Cardivore_AI** is a research/automation tool for analyzing trading-card market data (initially focused on Pokémon cards) in the context of eBay sourcing & grading.  
It ingests raw and graded sales data (e.g., from MarketMoversApp), stores it in a MySQL backend, applies filters and logic to identify high-ROI opportunities (raw card purchase → PSA10 resale), and provides systems for automation, search link generation, and future image-recognition workflows.

## 📂 Project Structure  
/cardivore_ai
D:\dev\cardivore_ai\
│
├── .env                          ← environment variables (MySQL, etc.)
├── docker-compose.yml            ← Docker config (MySQL container)
├── README.md                     ← your evolving project snapshot
├── requirements.txt              ← pip dependencies
│
├── data/
│   ├── raw/                      ← incoming CSVs (unmodified)
│   ├── processed/                ← generated CSVs/exports
│   └── staging/                  ← optional temporary cleaning outputs
│
├── mysql/
│   ├── init/
│   │   ├── 01_create_raw_historic_sales.sql
│   │   ├── 02_create_psa10_historic_sales.sql
│   │   └── seed_data.sql         ← optional future seeds/tests
│   └── Dockerfile (optional)
│
├── notebooks/
│   ├── 00_db_init.ipynb          ← runs CREATE TABLE scripts
│   ├── 01_file_imports.ipynb     ← loads CSV → MySQL
│   ├── 02_merge_filter.ipynb     ← runs ROI logic
│   ├── 03_pipeline_builder.ipynb ← (future) widget-based mapping
│   └── playground.ipynb          ← scratchpad
│
└── cardivore_ai/
    ├── __init__.py
    │
    ├── core/                     ← main logic modules
    │   ├── merge_filter.py
    │   ├── ebay_scraper.py
    │   ├── image_evaluator.py
    │   ├── price_model.py
    │   └── __init__.py
    │
    ├── utils/                    ← shared helper utilities
    │   ├── io_utils.py           ← CSV cleaning, column normalization
    │   ├── db_utils.py           ← connection, insert, create-table
    │   ├── cards.py              ← string builders, URL creation
    │   ├── fe_helpers.py         ← notebook/UI helpers
    │   ├── timers.py             ← timeit decorator, etc.
    │   └── __init__.py
    │
    ├── frontend/                 ← (future) Flask/FastAPI or Streamlit app
    │   ├── __init__.py
    │   ├── routes.py
    │   ├── templates/
    │   └── static/
    │
    └── tests/                    ← unit tests
        ├── test_io_utils.py
        ├── test_db_utils.py
        └── __init__.py


markdown
Copy code

## 🛠 Key Capabilities  
- Dockerized MySQL instance, isolated from other data-projects.  
- CSV ingestion and normalization pipelines for raw and PSA10 data.  
- Helper modules:
  - `io_utils.py` → column header normalization, data cleaning  
  - `db_utils.py` → DB connection management, dynamic CREATE/INSERT operations  
  - `cards.py` → card-specific logic (search string builders, URL generation)  
- Notebook workflows for:
  1. Creating tables if not already exists  
  2. Loading raw/PSA10 data into the database  
  3. Merging, filtering and exporting high-ROI card opportunities  
- Generated eBay search URLs for raw card sourcing (e.g., ungraded, English, near-mint) based on mapping logic.

## ✅ Current Status  
- Directory & package structure established.  
- MySQL Docker container configured and accessible.  
- Two key tables created: `raw_historic_sales` and `psa10_historic_sales`.  
- Column normalization and insertion logic drafted.  
- Basic merge/filter notebook built, though filtering currently yields zero results → awaiting threshold tuning and column naming fixes.

## 📅 Short-Term Roadmap  
1. Finalize `normalize_column_headers()` helper in `io_utils.py`.  
2. Build `create_table_if_not_exists(df, table_name)` in `db_utils.py`.  
3. Re-run import pipelines and verify data loads, then merge/filter workflows begin producing viable opportunities.  
4. Save export results (e.g., `profitable_cards.csv`) and version them.  
5. Integrate image-recognition and eBay API automation (next phase).

## 🔮 Long-Term Objectives  
- Expand beyond Pokémon to other trading-card markets (e.g., Magic, Yu-Gi-Oh).  
- Build a web or mobile front-end (e.g., with FastAPI + React) to monitor live opportunities on your phone.  
- Incorporate machine-learning models for price prediction and card grading/image quality recognition.

## 📋 Contributing / Next Steps for Me  
- All development tracked in this repo under `cardivore_ai`.  
- Use the virtual-environment & `requirements.txt` to install dependencies.  
- For any change in helpers or notebooks, update this README: _“Last updated: YYYY-MM-DD”._  
- Backup raw CSVs and processed exports; database volume may grow quickly.

🧱 Universal Notebook Bootstrap

Purpose: guarantee consistent imports and environment loading across all notebooks (no matter where they’re located).

%load_ext autoreload
%autoreload 2
# --- Cell 0: Universal Notebook Bootstrap ---
import os, sys
from dotenv import load_dotenv

# Dynamically set project root so imports always work
NOTEBOOK_DIR = os.getcwd()
PROJECT_ROOT = os.path.dirname(NOTEBOOK_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Load environment variables (for MySQL, etc.)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

print(f"✅ Environment ready. Project root: {PROJECT_ROOT}")


_Last updated: 2025-10-24_
