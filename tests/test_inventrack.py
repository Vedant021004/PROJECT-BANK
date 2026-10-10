import os
import sys
import sqlite3
import datetime
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database_setup import init_db, backup_db
from heap import load_from_db, clear_heap, get_nearest_expiry, user_heaps
from inventory_management import (
    add_batch, sell_product, get_all_inventory, get_expiring_stocks,
    delete_batch, adjust_batch_quantity, edit_batch,
    adjust_product_stock, get_user_products_summary, update_product_price
)
from forecast import calculate_product_forecasts

TEST_DB = "test_inventory.db"
TEST_BACKUP_DIR = "test_backups"
TEST_EMAIL = "testuser@example.com"

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Setup fresh temporary test database
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    clear_heap(TEST_EMAIL)
    init_db(db_path=TEST_DB)
    
    # Insert test user
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user (email, password, name, mobile) VALUES (?, ?, ?, ?)",
        (TEST_EMAIL, "hashed_or_plain_pw", "Test Manager", "9876543210")
    )
    conn.commit()
    conn.close()

    yield

    # Teardown
    clear_heap(TEST_EMAIL)
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass
    if os.path.exists(TEST_BACKUP_DIR):
        import shutil
        try:
            shutil.rmtree(TEST_BACKUP_DIR)
        except Exception:
            pass


def test_database_init_and_backup():
    """Verify tables, indexes, and verified backup mechanism."""
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    assert "user" in tables
    assert "inventory" in tables
    assert "sales" in tables
    conn.close()

    # Test verified backup
    backup_path = backup_db(db_path=TEST_DB, backup_dir=TEST_BACKUP_DIR)
    assert backup_path is not None
    assert os.path.exists(backup_path)

    # Verify backup integrity
    b_conn = sqlite3.connect(backup_path)
    b_cursor = b_conn.cursor()
    b_cursor.execute("PRAGMA integrity_check;")
    assert b_cursor.fetchone()[0] == "ok"
    b_conn.close()


def test_batch_management_and_validation():
    """Verify adding batches, duplicate prevention, and input validation."""
    future_date = (datetime.date.today() + datetime.timedelta(days=60)).strftime('%Y-%m-%d')

    # Successful batch add
    success = add_batch(
        email=TEST_EMAIL,
        product_name="Amoxicillin",
        batch_no="AMX-001",
        quantity=50,
        expiry_date=future_date,
        db_path=TEST_DB
    )
    assert success is True

    # Duplicate batch_no must fail
    duplicate = add_batch(
        email=TEST_EMAIL,
        product_name="Amoxicillin",
        batch_no="AMX-001",
        quantity=20,
        expiry_date=future_date,
        db_path=TEST_DB
    )
    assert duplicate is False

    # Negative / zero quantity must fail
    neg = add_batch(
        email=TEST_EMAIL,
        product_name="Amoxicillin",
        batch_no="AMX-002",
        quantity=-10,
        expiry_date=future_date,
        db_path=TEST_DB
    )
    assert neg is False

    # Verify inventory fetch
    items = get_all_inventory(email=TEST_EMAIL, db_path=TEST_DB)
    assert len(items) == 1
    assert items[0][2] == "AMOXICILLIN"
    assert items[0][3] == "AMX-001"
    assert items[0][4] == 50

    # Delete batch
    del_success = delete_batch(email=TEST_EMAIL, batch_no="AMX-001", db_path=TEST_DB)
    assert del_success is True
    assert len(get_all_inventory(email=TEST_EMAIL, db_path=TEST_DB)) == 0


def test_fefo_selling_and_sales_recording():
    """
    Verify FEFO algorithm with Min-Heap:
    Earlier expiring batch must be sold first, and atomic sales record must be written.
    """
    today = datetime.date.today()
    exp_early = (today + datetime.timedelta(days=10)).strftime('%Y-%m-%d')
    exp_late = (today + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    exp_expired = (today - datetime.timedelta(days=2)).strftime('%Y-%m-%d')

    # Add expired batch (5 units)
    add_batch(email=TEST_EMAIL, product_name="Paracetamol", batch_no="PCM-EXPIRED", quantity=5, expiry_date=exp_expired, db_path=TEST_DB)
    # Add early-expiry batch (10 units)
    add_batch(email=TEST_EMAIL, product_name="Paracetamol", batch_no="PCM-EARLY", quantity=10, expiry_date=exp_early, db_path=TEST_DB)
    # Add late-expiry batch (20 units)
    add_batch(email=TEST_EMAIL, product_name="Paracetamol", batch_no="PCM-LATE", quantity=20, expiry_date=exp_late, db_path=TEST_DB)

    # Sell 15 units
    sold = sell_product(email=TEST_EMAIL, product_name="Paracetamol", quantity=15, db_path=TEST_DB)
    assert sold is True

    # Check remaining inventory in DB
    items = get_all_inventory(email=TEST_EMAIL, db_path=TEST_DB)
    # PCM-EXPIRED should be pruned/deleted because it was expired
    # PCM-EARLY (10 units) should be completely depleted and deleted
    # PCM-LATE (20 - 5 = 15 units) should remain
    assert len(items) == 1
    assert items[0][3] == "PCM-LATE"
    assert items[0][4] == 15

    # Check sales history record
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, quantity, sale_date FROM sales WHERE user_email = ?", (TEST_EMAIL,))
    sales_rows = cursor.fetchall()
    conn.close()

    assert len(sales_rows) == 1
    assert sales_rows[0][0] == "PARACETAMOL"
    assert sales_rows[0][1] == 15
    assert sales_rows[0][2] == today.strftime('%Y-%m-%d')


def test_atomic_rollback_on_insufficient_stock():
    """
    If requested quantity > available non-expired stock, sell_product must fail
    and leave existing batches completely untouched (no partial deletions).
    """
    today = datetime.date.today()
    exp_date = (today + datetime.timedelta(days=20)).strftime('%Y-%m-%d')

    add_batch(email=TEST_EMAIL, product_name="Ibuprofen", batch_no="IBU-001", quantity=10, expiry_date=exp_date, db_path=TEST_DB)

    # Attempt to sell 50 units (only 10 exist)
    sold = sell_product(email=TEST_EMAIL, product_name="Ibuprofen", quantity=50, db_path=TEST_DB)
    assert sold is False

    # Verify inventory is intact: 10 units still there
    items = get_all_inventory(email=TEST_EMAIL, db_path=TEST_DB)
    assert len(items) == 1
    assert items[0][4] == 10

    # Verify NO sales record was inserted
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales WHERE user_email = ?", (TEST_EMAIL,))
    assert cursor.fetchone()[0] == 0
    conn.close()


def test_zero_sales_calendar_days_average():
    """
    Verify demand forecast:
    14 units sold on 1 day across a 7-day window must give average daily demand = 14 / 7 = 2.0
    (NOT 14 / 1 = 14).
    """
    today = datetime.date.today()
    future_exp = (today + datetime.timedelta(days=60)).strftime('%Y-%m-%d')
    
    # Add inventory
    add_batch(email=TEST_EMAIL, product_name="Vitamin C", batch_no="VTC-001", quantity=50, expiry_date=future_exp, db_path=TEST_DB)

    # Sell 14 units today (only 1 sale day in the 7-day window)
    sell_product(email=TEST_EMAIL, product_name="Vitamin C", quantity=14, db_path=TEST_DB)

    # Run forecast
    result = calculate_product_forecasts(email=TEST_EMAIL, db_path=TEST_DB, window_days=7)
    items = {item["product_name"]: item for item in result["items"]}
    
    vtc = items.get("VITAMIN C")
    assert vtc is not None
    assert vtc["has_data"] is True
    # 14 units / 7 calendar days = 2.0 units/day
    assert vtc["avg_daily_demand"] == 2.0
    # Next 7 days forecast = 2.0 * 7 = 14 units
    assert vtc["forecast_7_days"] == 14
    # Current stock = 50 - 14 = 36 units
    assert vtc["current_stock"] == 36
    # Shortage = max(0, 14 - 36) = 0
    assert vtc["projected_shortage"] == 0
    assert vtc["suggested_restock"] == 0
    assert vtc["status"] == "Sufficient Stock"


def test_product_wise_demand_separation():
    """
    Verify demand calculations are strictly separated per product.
    Sales of Product A must not bleed into Product B.
    """
    today = datetime.date.today()
    future_exp = (today + datetime.timedelta(days=60)).strftime('%Y-%m-%d')

    add_batch(email=TEST_EMAIL, product_name="Aspirin", batch_no="ASP-001", quantity=100, expiry_date=future_exp, db_path=TEST_DB)
    add_batch(email=TEST_EMAIL, product_name="Cetirizine", batch_no="CET-001", quantity=100, expiry_date=future_exp, db_path=TEST_DB)

    # Aspirin: 28 units sold -> 4.0 / day, forecast = 28
    sell_product(email=TEST_EMAIL, product_name="Aspirin", quantity=28, db_path=TEST_DB)
    # Cetirizine: 7 units sold -> 1.0 / day, forecast = 7
    sell_product(email=TEST_EMAIL, product_name="Cetirizine", quantity=7, db_path=TEST_DB)

    result = calculate_product_forecasts(email=TEST_EMAIL, db_path=TEST_DB, window_days=7)
    items = {item["product_name"]: item for item in result["items"]}

    assert items["ASPIRIN"]["avg_daily_demand"] == 4.0
    assert items["ASPIRIN"]["forecast_7_days"] == 28

    assert items["CETIRIZINE"]["avg_daily_demand"] == 1.0
    assert items["CETIRIZINE"]["forecast_7_days"] == 7


def test_insufficient_sales_data_handling():
    """
    New product with no sales history must display 'Insufficient Data'
    and 'Insufficient sales data' without misleading calculations.
    """
    today = datetime.date.today()
    future_exp = (today + datetime.timedelta(days=60)).strftime('%Y-%m-%d')

    add_batch(email=TEST_EMAIL, product_name="New Drug X", batch_no="NDX-001", quantity=25, expiry_date=future_exp, db_path=TEST_DB)

    result = calculate_product_forecasts(email=TEST_EMAIL, db_path=TEST_DB, window_days=7)
    items = {item["product_name"]: item for item in result["items"]}

    ndx = items.get("NEW DRUG X")
    assert ndx is not None
    assert ndx["has_data"] is False
    assert ndx["avg_daily_demand"] is None
    assert ndx["forecast_7_days"] is None
    assert ndx["status"] == "Insufficient Data"
    assert ndx["status_label"] == "Insufficient sales data"


def test_smart_restock_recommendations():
    """
    Verify restock calculations:
    If Forecast Demand > Current Stock:
      Projected Shortage = Forecast Demand - Current Stock
      Suggested Restock = Projected Shortage
      Status = 'Restock Suggested'
    """
    today = datetime.date.today()
    future_exp = (today + datetime.timedelta(days=60)).strftime('%Y-%m-%d')

    # Add 25 units, sell 21 units -> Remaining = 4 units
    add_batch(email=TEST_EMAIL, product_name="Omeprazole", batch_no="OMP-001", quantity=25, expiry_date=future_exp, db_path=TEST_DB)
    sell_product(email=TEST_EMAIL, product_name="Omeprazole", quantity=21, db_path=TEST_DB)

    result = calculate_product_forecasts(email=TEST_EMAIL, db_path=TEST_DB, window_days=7)
    items = {item["product_name"]: item for item in result["items"]}

    omp = items["OMEPRAZOLE"]
    assert omp["current_stock"] == 4
    # 21 sold in 7 days -> 3.0 / day -> forecast = 21
    assert omp["forecast_7_days"] == 21
    # Shortage = 21 - 4 = 17
    assert omp["projected_shortage"] == 17
    assert omp["suggested_restock"] == 17
    assert omp["status"] == "Restock Suggested"
    assert "Restock +17" in omp["status_label"]


def test_flask_dashboard_renders_forecast():
    """
    Verify Flask web application starts, sets session, and renders the dashboard
    including the Demand Forecast & Restock Recommendations table.
    """
    from app import app
    app.config["TESTING"] = True

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["email"] = TEST_EMAIL

    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Demand Forecast & Smart Restock" in html
    assert "Inventory Batches & Quantity Management" in html or "Batches" in html


def test_batch_quantity_adjustment_and_deletion():
    """Verify incrementing, decrementing, and auto-deleting batches via adjust_batch_quantity."""
    today = datetime.date.today()
    exp = (today + datetime.timedelta(days=90)).strftime('%Y-%m-%d')

    # Add initial batch of 10 units at ₹150.00
    add_batch(email=TEST_EMAIL, product_name="IBUPROFEN", batch_no="IBU-001", quantity=10, expiry_date=exp, unit_price=150.0, db_path=TEST_DB)

    # Increment +5
    new_qty = adjust_batch_quantity(email=TEST_EMAIL, batch_no="IBU-001", delta_qty=5, db_path=TEST_DB)
    assert new_qty == 15

    # Decrement -7
    new_qty = adjust_batch_quantity(email=TEST_EMAIL, batch_no="IBU-001", delta_qty=-7, db_path=TEST_DB)
    assert new_qty == 8

    # Decrement by 8 -> reaching 0 -> should delete the batch
    final_qty = adjust_batch_quantity(email=TEST_EMAIL, batch_no="IBU-001", delta_qty=-8, db_path=TEST_DB)
    assert final_qty == 0

    # Verify batch is gone from inventory
    inv = get_all_inventory(email=TEST_EMAIL, db_path=TEST_DB)
    assert len(inv) == 0


def test_batch_edit_and_price_valuation():
    """Verify editing batch quantity, price, expiry date and forecast valuation metrics."""
    today = datetime.date.today()
    exp1 = (today + datetime.timedelta(days=45)).strftime('%Y-%m-%d')
    exp2 = (today + datetime.timedelta(days=120)).strftime('%Y-%m-%d')

    # Add batch
    add_batch(email=TEST_EMAIL, product_name="METFORMIN", batch_no="MET-101", quantity=20, expiry_date=exp1, unit_price=25.50, db_path=TEST_DB)

    # Edit batch: change quantity to 50, price to 30.00, expiry to exp2
    updated = edit_batch(email=TEST_EMAIL, batch_no="MET-101", quantity=50, unit_price=30.00, expiry_date=exp2, db_path=TEST_DB)
    assert updated is True

    # Check inventory
    rows = get_all_inventory(email=TEST_EMAIL, db_path=TEST_DB)
    assert len(rows) == 1
    # row: id, user_email, product_name, batch_no, quantity, expiry_date, unit_price
    assert rows[0][4] == 50
    assert rows[0][5] == exp2
    assert rows[0][6] == 30.00

    # Sell 14 units at 30.00
    sold = sell_product(email=TEST_EMAIL, product_name="METFORMIN", quantity=14, db_path=TEST_DB)
    assert sold is True

    # Check forecast calculations and valuation
    fc = calculate_product_forecasts(email=TEST_EMAIL, db_path=TEST_DB, window_days=7)
    assert fc["summary"]["total_products"] == 1
    item = fc["items"][0]
    assert item["product_name"] == "METFORMIN"
    assert item["unit_price"] == 30.00
    assert item["current_stock"] == 36
    assert item["inventory_value"] == 36 * 30.00
    assert fc["summary"]["total_inventory_valuation"] == 36 * 30.00


def test_product_level_stock_adjustment():
    """Verify increasing and decreasing stock at the product level without requiring batch IDs."""
    today = datetime.date.today()
    exp = (today + datetime.timedelta(days=60)).strftime('%Y-%m-%d')

    # Add initial batch of PEPSI
    add_batch(email=TEST_EMAIL, product_name="PEPSI", batch_no="PEP-001", quantity=10, expiry_date=exp, unit_price=40.0, db_path=TEST_DB)

    # 1. Increase stock (+15)
    success, msg, new_qty = adjust_product_stock(email=TEST_EMAIL, product_name="PEPSI", delta_qty=15, db_path=TEST_DB)
    assert success is True
    assert new_qty == 25

    # 2. Check summary
    prods = get_user_products_summary(email=TEST_EMAIL, db_path=TEST_DB)
    assert len(prods) == 1
    assert prods[0]["product_name"] == "PEPSI"
    assert prods[0]["total_quantity"] == 25

    # 3. Decrease stock (-10)
    success, msg, _ = adjust_product_stock(email=TEST_EMAIL, product_name="PEPSI", delta_qty=-10, db_path=TEST_DB)
    assert success is True

    prods = get_user_products_summary(email=TEST_EMAIL, db_path=TEST_DB)
    assert prods[0]["total_quantity"] == 15


def test_product_price_update():
    """Verify updating unit price of an existing product."""
    today = datetime.date.today()
    exp = (today + datetime.timedelta(days=90)).strftime('%Y-%m-%d')

    # Add batch with initial price 20.00
    add_batch(email=TEST_EMAIL, product_name="ASPIRIN", batch_no="ASP-001", quantity=100, expiry_date=exp, unit_price=20.0, db_path=TEST_DB)

    # 1. Update price directly via update_product_price
    success = update_product_price(email=TEST_EMAIL, product_name="ASPIRIN", unit_price=28.50, db_path=TEST_DB)
    assert success is True

    # Check inventory rows
    rows = get_all_inventory(email=TEST_EMAIL, db_path=TEST_DB)
    assert rows[0][6] == 28.50

    # 2. Update price via adjust_product_stock with price_only (delta_qty=0)
    success, msg, _ = adjust_product_stock(email=TEST_EMAIL, product_name="ASPIRIN", delta_qty=0, unit_price=35.00, db_path=TEST_DB)
    assert success is True
    assert "35.00" in msg

    rows = get_all_inventory(email=TEST_EMAIL, db_path=TEST_DB)
    assert rows[0][6] == 35.00
    assert rows[0][4] == 100  # Quantity unchanged
