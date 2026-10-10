# 📦 Inventrack — Smart Inventory Management System
### Product-Wise Demand Prediction · FEFO Expiry Tracking · Valuation & Stock Controls

> A production-grade, full-stack inventory management web application built with **Python (Flask 3.0)** and **SQLite 3**, featuring an algorithmic **Min-Heap FEFO (First Expired, First Out)** dispatch engine, **product-wise 7-calendar-day demand forecasting**, **live pricing & inventory valuation**, and **instant stock quantity controls**.

---

## 📌 Table of Contents

- [Overview & What It Does](#-overview--what-it-does)
- [Key Features](#-key-features)
- [How It Works (Core Logic & DSA)](#-how-it-works-core-logic--dsa)
  - [1. Min-Heap FEFO Selling Algorithm](#1-min-heap-fefo-selling-algorithm)
  - [2. Explainable 7-Day Demand Forecasting & Smart Restock](#2-explainable-7-day-demand-forecasting--smart-restock)
  - [3. Stock Quantity & Price Adjustment Engine](#3-stock-quantity--price-adjustment-engine)
- [Tech Stack](#-tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Database Architecture & Schema](#-database-architecture--schema)
- [Quick Start / Local Setup Guide](#-quick-start--local-setup-guide)
- [Running Automated Tests](#-running-automated-tests)
- [Routes & API Endpoints](#-routes--api-endpoints)
- [Security & Backup Mechanism](#-security--backup-mechanism)
- [Author & Acknowledgments](#-author--acknowledgments)

---

## 🌟 Overview & What It Does

In retail businesses, pharmacies, FMCG distribution, and warehouses, stock loss happens due to two major bottlenecks:
1. **Expired Inventory Waste**: Newer batches are accidentally sold first while older stock quietly expires on the shelf.
2. **Poor Demand Visibility**: Businesses either over-order (capital lockup) or stock out on high-velocity items.

**Inventrack** completely automates and eliminates these issues:
- **Automatic Oldest-Stock Dispatch**: Automatically routes sales transactions to the earliest-expiring batch first using a Min-Heap.
- **Explainable Product Demand Forecasting**: Calculates a mathematically honest 7-calendar-day moving average to project stock shortages and recommend exact restock quantities.
- **Inventory Valuation (₹)**: Tracks unit prices, total stock value, and the exact investment capital required to fulfill restock needs.
- **Fast Stock Adjustments**: Allows instant quantity increment (`+`), decrement (`−`), price updates, and batch editing directly from the UI without navigating away.

---

## 🚀 Key Features

### 1. 📊 Product-Wise Demand Forecasting & Smart Restock
- **7-Calendar-Day Moving Average**: Accurately counts non-sales days across the calendar week (not just days with transactions).
- **Exact Restock Recommendation**: Proactively computes:
  $$\text{Projected Shortage} = \max(0, \text{7-Day Forecast} - \text{Current Active Stock})$$
- **Restock Investment Estimation (₹)**: Shows the exact budget needed to restock each product based on its unit price.
- **Honest "Insufficient Data" Handling**: Products with no recorded sales history clearly display *"Insufficient sales data"* instead of fabricating misleading predictions.

### 2. ⚡ Inline Stock & Price Management
- **Instant Stepper Controls (`+` / `−`)**: Rapidly increase or decrease batch stock with one click right on the dashboard table.
- **Quick Product Stock Adjustment Modal**: Adjust stock (`+ Add Units` or `− Deduct Units`) or update price by simply choosing the product from a dropdown — no need to remember complex batch IDs.
- **Batch Edit Modal (`✏️`)**: Edit exact quantities, unit prices (₹), and expiry dates in-place.
- **Live Inventory Valuation**: Real-time KPI metric card calculating total portfolio valuation across all warehouse batches.

### 3. 🛡️ Algorithmic Min-Heap FEFO Selling
- **O(log n) Dispatch**: Identifies and depletes the nearest-expiring batch in logarithmic time using an in-memory priority queue (`heapq`).
- **Multi-Batch Cascading**: If an order exceeds a single batch's quantity, the algorithm automatically consumes the earliest batch and cascades the remainder to the next earliest batch.
- **Automatic Depletion Cleanup**: Depleted batches ($Q \le 0$) are removed automatically from the active inventory.
- **Expired Stock Protection**: Expired batches are protected from customer dispatch and flagged with critical badges.

### 4. 🎨 Bespoke Obsidian & Indigo SaaS UI
- **Modern Theme**: Built with a dark slate palette (`#090d16` background, `#101728` card surfaces, subtle 1px hairline borders `#1e293b`, and electric indigo `#6366f1` accents).
- **Tabular Monospace Numerals**: Clean currency (₹) and quantity alignment using `JetBrains Mono` and `tabular-nums`.
- **Toast Notifications**: Responsive flash alert banners for all inventory actions.

---

## 🧠 How It Works (Core Logic & DSA)

### 1. Min-Heap FEFO Selling Algorithm
Inventrack maintains an in-memory Min-Heap for each user, stored as tuples:
```python
(expiry_date, id, product_name, batch_no, quantity, unit_price)
```
- Because Python compares tuples element-by-element, the primary comparison key is `expiry_date` (`YYYY-MM-DD`).
- When `sell_product(product, qty)` is invoked:
  1. Retrieves available non-expired stock. If total non-expired stock $< \text{qty}$, the transaction **rolls back completely** (no partial corrupt state).
  2. The Min-Heap pops the earliest-expiring batch in $O(\log n)$ time.
  3. Batches are deducted atomically within a database transaction, recording the units sold, unit price, and total sale amount in the `sales` ledger.

### 2. Explainable 7-Day Demand Forecasting & Smart Restock
The forecast engine ([`forecast.py`](file:///d:/inventery/forecast.py)) executes optimized, grouped SQL queries to prevent $N+1$ performance degradation:
1. Queries distinct active products and lifetime sales.
2. Sums total units sold during the previous 7 calendar days $[T-6, T]$.
3. Computes:
   $$\text{Avg Daily Demand} = \frac{\text{Units Sold in 7 Days}}{7.0}$$
   $$\text{Forecast Next 7 Days} = \lceil \text{Avg Daily Demand} \times 7 \rceil$$
   $$\text{Suggested Restock} = \max(0, \text{Forecast} - \text{Current Stock})$$
   $$\text{Restock Investment (₹)} = \text{Suggested Restock} \times \text{Unit Price}$$

### 3. Stock Quantity & Price Adjustment Engine
Stock can be adjusted through three intuitive workflows:
- **By Product Name** (`/adjust_product`): Automatically routes stock additions to the latest active batch, or deductions via FEFO.
- **By Batch Stepper** (`/adjust_batch/<batch_no>`): Increments or decrements a specific batch directly.
- **Batch Edit Modal** (`/edit_batch/<batch_no>`): Direct modification of batch attributes (Quantity, Unit Price, Expiry Date).

---

## 💻 Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Backend** | Python 3.12 / 3.14 | Core language |
| **Web Framework** | Flask 3.0.2 | Lightweight WSGI web framework |
| **Database** | SQLite 3 | Embedded ACID database with foreign keys and index optimization |
| **DSA / Caching** | Python `heapq` | In-memory per-user Min-Heap priority queues |
| **Frontend** | HTML5, CSS3, Vanilla JS | Bespoke dark Obsidian/Indigo UI design system |
| **Typography** | Plus Jakarta Sans & JetBrains Mono | Premium software typography |
| **Testing** | `pytest 9.1` | Automated test suite (13 comprehensive tests) |

---

## 📂 Project Directory Structure

```text
inventery/
├── app.py                      # Flask application entry point & route controllers
├── inventory_management.py     # Core business logic: batch CRUD, FEFO sell, stock adjustment
├── forecast.py                 # 7-day demand moving average & restock calculation engine
├── heap.py                     # Min-Heap priority queue implementation & heap sync
├── database_setup.py           # Safe schema migrations & online SQLite backups
├── auth.py                     # User registration, login, OTP verification logic
├── sms.py                      # Email alert dispatch (with local console OTP fallback)
├── view_db.py                  # CLI utility for inspecting database contents
├── database.db                 # Primary local SQLite database
├── backups/                    # Auto-generated verified database backups
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Shared layout, navigation, design tokens, toast alerts
│   ├── dashboard.html          # Main dashboard, KPI cards, forecast table, batch ledger
│   ├── add.html                # Add Batch & Quick Product Stock Adjustment tabs
│   ├── sell.html               # Dedicated FEFO selling interface with confirmation modal
│   ├── login.html              # Authentication login screen
│   ├── register.html           # User registration screen
│   └── verify_otp.html         # OTP verification screen
└── tests/
    └── test_inventrack.py      # Pytest test suite (13 automated unit & integration tests)
```

---

## 🗄️ Database Architecture & Schema

### `inventory` Table
Stores individual physical batches:
```sql
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    product_name TEXT NOT NULL,
    batch_no TEXT NOT NULL UNIQUE,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    expiry_date TEXT NOT NULL,
    unit_price REAL DEFAULT 0.0,
    FOREIGN KEY(user_email) REFERENCES user(email) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_inventory_lookup 
ON inventory(user_email, product_name, expiry_date);
```

### `sales` Table
Atomic transaction ledger tracking each sale:
```sql
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    sale_date TEXT NOT NULL,
    sale_timestamp TEXT NOT NULL,
    unit_price REAL DEFAULT 0.0,
    total_amount REAL DEFAULT 0.0,
    FOREIGN KEY(user_email) REFERENCES user(email) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_sales_query 
ON sales(user_email, product_name, sale_date);
```

### `user` Table
Stores user credentials and profile information:
```sql
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    mobile TEXT NOT NULL
);
```

---

## ⚡ Quick Start / Local Setup Guide

### 1. Prerequisites
- Python 3.10+ installed ([Download Python](https://www.python.org/downloads/))
- VS Code or your preferred code editor

### 2. Clone / Open the Project
```bash
git clone https://github.com/engineermayur-07/Inventrack-Inventory-Management-System.git
cd Inventrack-Inventory-Management-System
```

### 3. Install Dependencies
```bash
pip install flask python-dotenv pytest
```

### 4. Configure Environment (Optional)
Create a `.env` file in the root folder:
```ini
SECRET_KEY=inventrack-super-secret-key-2026
# Optional: SMTP email configuration for real email OTPs
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```
*(Note: If SMTP credentials are not configured, OTP codes will print directly to the terminal console during registration for seamless local testing).*

### 5. Launch the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### 6. Default Test Account
To test immediately without registering:
- **Email**: `demo@inventrack.com`
- **Password**: `password123`

---

## 🧪 Running Automated Tests

Inventrack includes a complete test suite covering database migrations, atomic rollbacks, Min-Heap synchronization, demand forecasting, stock adjustments, and price updates.

Run the test suite using `pytest`:
```bash
python -m pytest -v tests/test_inventrack.py
```

Expected Output:
```text
============================= test session starts =============================
tests/test_inventrack.py::test_database_init_and_backup PASSED           [  7%]
tests/test_inventrack.py::test_batch_management_and_validation PASSED    [ 15%]
tests/test_inventrack.py::test_fefo_selling_and_sales_recording PASSED   [ 23%]
tests/test_inventrack.py::test_atomic_rollback_on_insufficient_stock PASSED [ 30%]
tests/test_inventrack.py::test_zero_sales_calendar_days_average PASSED   [ 38%]
tests/test_inventrack.py::test_product_wise_demand_separation PASSED     [ 46%]
tests/test_inventrack.py::test_insufficient_sales_data_handling PASSED   [ 53%]
tests/test_inventrack.py::test_smart_restock_recommendations PASSED      [ 61%]
tests/test_inventrack.py::test_flask_dashboard_renders_forecast PASSED   [ 69%]
tests/test_inventrack.py::test_batch_quantity_adjustment_and_deletion PASSED [ 76%]
tests/test_inventrack.py::test_batch_edit_and_price_valuation PASSED     [ 84%]
tests/test_inventrack.py::test_product_level_stock_adjustment PASSED     [ 92%]
tests/test_inventrack.py::test_product_price_update PASSED               [100%]
============================= 13 passed in 1.03s ==============================
```

---

## 🔌 Routes & API Endpoints

| HTTP Method | Route | Description |
|---|---|---|
| `GET` | `/` | Dashboard displaying KPI cards, demand forecast, and batch ledger |
| `GET`, `POST` | `/login` | User authentication |
| `GET`, `POST` | `/register` | User account registration (with OTP verification) |
| `GET`, `POST` | `/add_batch` | Register a new batch or adjust existing product stock |
| `POST` | `/adjust_product` | Quick stock adjustment (`+ Add`, `− Deduct`, `🏷️ Price Only`) by product name |
| `POST` | `/adjust_batch/<batch_no>` | Increments (`+1`) or decrements (`−1`) a specific batch |
| `POST` | `/edit_batch/<batch_no>` | Updates quantity, unit price (₹), and expiry date for a batch |
| `POST` | `/delete_batch/<batch_no>` | Permanently deletes a specific batch from inventory |
| `GET`, `POST` | `/sell_product` | Performs atomic FEFO deduction and records transaction in `sales` |
| `GET` | `/get_expiring_stock` | Filtered view of batches expiring within 30 days |
| `GET` | `/logout` | Clears user session |

---

## 🔒 Security & Backup Mechanism

- **Online SQLite Backup API**: Before any schema modification, an automated verified backup is taken using `sqlite3.Connection.backup()`, avoiding Windows `WinError 32` file locks.
- **Foreign Key Constraints & Rollbacks**: SQLite is initialized with `PRAGMA foreign_keys = ON;`. Sales and stock adjustments use strict transaction blocks (`COMMIT` / `ROLLBACK`).
- **Cache Invalidation**: Custom `@app.after_request` handler enforces `Cache-Control: no-store, no-cache, must-revalidate` headers so browser snapshots never display stale inventory data.

---

## 👨‍💻 Author & Acknowledgments

**Mayur B Gund**  
B.Tech Computer Science & Engineering  

- **GitHub**: [@engineermayur-07](https://github.com/engineermayur-07)
- **LinkedIn**: [Mayur Gund](https://linkedin.com/in/mgund1920)
- **Email**: [mgund1920@gmail.com](mailto:mgund1920@gmail.com)

---

> *Inventrack — Where Data Structures meet Real-World Supply Chain Optimization.*
