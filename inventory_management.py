import sqlite3
import datetime
from heap import *
from auth import *

def add_batch(email=None, product_name=None, batch_no=None, quantity=None, expiry_date=None, unit_price=0.0, allow_increment=False, db_path='database.db'):
    """
    Adds a product batch to the database. Validates input and ensures unique batch Id per user.
    If allow_increment is True and batch exists, increments existing batch quantity.
    """
    if not email or not product_name or not batch_no or quantity is None or not expiry_date:
        return False

    try:
        quantity = int(quantity)
        if quantity <= 0:
            return False
    except (ValueError, TypeError):
        return False

    try:
        price = float(unit_price) if unit_price is not None else 0.0
        if price < 0:
            price = 0.0
    except (ValueError, TypeError):
        price = 0.0

    conn = None
    try:
        product_name = str(product_name).upper().strip()
        batch_no = str(batch_no).strip()
        expiry_date_obj = datetime.datetime.strptime(str(expiry_date).strip(), '%Y-%m-%d').date()
        expiry_date_str = expiry_date_obj.strftime('%Y-%m-%d')

        conn = sqlite3.connect(db_path)
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor = conn.cursor()

        cursor.execute("SELECT id, quantity, unit_price FROM inventory WHERE batch_no = ? AND user_email = ?", (batch_no, email))
        existing = cursor.fetchone()
        if existing:
            if allow_increment:
                new_qty = existing[1] + quantity
                new_price = price if price > 0 else (existing[2] or 0.0)
                cursor.execute(
                    "UPDATE inventory SET quantity=?, expiry_date=?, unit_price=? WHERE id=?",
                    (new_qty, expiry_date_str, new_price, existing[0])
                )
                conn.commit()
                conn.close()
                load_from_db(email, db_path=db_path)
                return True
            else:
                conn.close()
                return False

        cursor.execute(
            "INSERT INTO inventory(user_email, product_name, batch_no, quantity, expiry_date, unit_price) VALUES(?,?,?,?,?,?)",
            (email, product_name, batch_no, quantity, expiry_date_str, price)
        )
        conn.commit()
        conn.close()
        load_from_db(email, db_path=db_path)
        return True
    except Exception as e:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        print(f"Error in add_batch: {e}")
        return False


def adjust_batch_quantity(email=None, batch_no=None, delta_qty=0, db_path='database.db'):
    """
    Safely adjusts quantity of an existing batch (e.g. +1, +5, -1).
    If remaining quantity becomes <= 0, deletes the batch safely.
    Returns the new quantity, or None on failure.
    """
    if not email or not batch_no or delta_qty == 0:
        return None

    try:
        delta = int(delta_qty)
    except (ValueError, TypeError):
        return None

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, quantity, product_name FROM inventory WHERE user_email=? AND batch_no=?",
            (email, str(batch_no).strip())
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        batch_id, current_qty, prod_name = row[0], row[1], row[2]
        new_qty = current_qty + delta

        if new_qty <= 0:
            cursor.execute("DELETE FROM inventory WHERE id=?", (batch_id,))
            conn.commit()
            conn.close()
            remove_batch_from_heap(email, batch_no, prod_name)
            load_from_db(email, db_path=db_path)
            return 0
        else:
            cursor.execute("UPDATE inventory SET quantity=? WHERE id=?", (new_qty, batch_id))
            conn.commit()
            conn.close()
            update_batch_quantity_in_heap(email, batch_no, prod_name, new_qty)
            load_from_db(email, db_path=db_path)
            return new_qty
    except Exception as e:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        print(f"Error in adjust_batch_quantity: {e}")
        return None


def sell_product(email=None, product_name=None, quantity=None, db_path='database.db'):
    """
    Sells a product using Min-Heap powered FEFO (First Expired, First Out) algorithm.
    Atomically depletes batches and records the transaction in the 'sales' table.
    Rolls back completely if the requested quantity exceeds available non-expired stock.
    """
    if not email or not product_name or quantity is None:
        return False

    try:
        quantity = int(quantity)
        if quantity <= 0:
            return False
    except (ValueError, TypeError):
        return False

    product_name = str(product_name).upper().strip()
    load_from_db(email, db_path=db_path)

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor = conn.cursor()

        # Begin atomic transaction
        cursor.execute("BEGIN TRANSACTION;")

        remaining = quantity
        today = datetime.date.today()
        depleted_batches_price = []

        while remaining > 0:
            batch = get_nearest_expiry(email, product_name)
            if not batch:
                # Insufficient non-expired stock: rollback entire operation
                cursor.execute("ROLLBACK;")
                conn.close()
                load_from_db(email, db_path=db_path)
                return False

            batch_expiry_date = batch[0]
            batch_no = batch[3]
            batch_qty = batch[4]
            batch_price = batch[5] if len(batch) > 5 else 0.0

            # Prune expired batches
            if batch_expiry_date < today:
                cursor.execute(
                    "DELETE FROM inventory WHERE user_email=? AND batch_no=? AND product_name=?",
                    (email, batch_no, product_name)
                )
                remove_batch_from_heap(email, batch_no, product_name)
                continue

            if batch_qty <= remaining:
                remaining -= batch_qty
                depleted_batches_price.append((batch_qty, batch_price))
                cursor.execute(
                    "DELETE FROM inventory WHERE user_email=? AND batch_no=? AND product_name=?",
                    (email, batch_no, product_name)
                )
                remove_batch_from_heap(email, batch_no, product_name)
            else:
                depleted_batches_price.append((remaining, batch_price))
                cursor.execute(
                    "UPDATE inventory SET quantity=quantity-? WHERE user_email=? AND batch_no=? AND product_name=?",
                    (remaining, email, batch_no, product_name)
                )
                update_batch_quantity_in_heap(email, batch_no, product_name, batch_qty - remaining)
                remaining = 0

        # Calculate weighted average unit price and total sale value
        total_sale_amount = sum(qty * pr for qty, pr in depleted_batches_price)
        avg_unit_price = round(total_sale_amount / float(quantity), 2) if quantity > 0 else 0.0

        # Record atomic sales transaction
        sale_date = today.strftime('%Y-%m-%d')
        sale_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            """INSERT INTO sales (user_email, product_name, quantity, sale_date, sale_timestamp, unit_price, total_amount) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (email, product_name, quantity, sale_date, sale_timestamp, avg_unit_price, round(total_sale_amount, 2))
        )

        cursor.execute("COMMIT;")
        conn.close()
        load_from_db(email, db_path=db_path)
        return True
    except Exception as e:
        if conn:
            try:
                cursor.execute("ROLLBACK;")
                conn.close()
            except Exception:
                pass
        load_from_db(email, db_path=db_path)
        print(f"Error in sell_product: {e}")
        return False


def get_all_inventory(email=None, db_path='database.db'):
    """Returns all inventory rows for the user, ordered by expiry date ascending."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, user_email, product_name, batch_no, quantity, expiry_date, COALESCE(unit_price, 0.0) 
               FROM inventory WHERE user_email=? ORDER BY expiry_date ASC""",
            (email,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error in get_all_inventory: {e}")
        return []


def get_expiring_stocks(email=None, db_path='database.db'):
    """Returns inventory items expiring within 30 days."""
    try:
        today = datetime.date.today()
        thirty_days = today + datetime.timedelta(days=30)
        max_date_str = thirty_days.strftime('%Y-%m-%d')

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, user_email, product_name, batch_no, quantity, expiry_date, COALESCE(unit_price, 0.0) 
               FROM inventory WHERE user_email=? AND expiry_date <= ? ORDER BY expiry_date ASC""",
            (email, max_date_str)
        )
        stocks = cursor.fetchall()
        conn.close()
        return stocks
    except Exception as e:
        print(f"Error in get_expiring_stocks: {e}")
        return []


def delete_batch(email=None, batch_no=None, db_path='database.db'):
    """Safely deletes an individual batch belonging to the user."""
    if not email or not batch_no:
        return False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT product_name FROM inventory WHERE user_email=? AND batch_no=?",
            (email, str(batch_no).strip())
        )
        row = cursor.fetchone()
        prod_name = row[0] if row else ""

        cursor.execute("DELETE FROM inventory WHERE user_email=? AND batch_no=?", (email, str(batch_no).strip()))
        conn.commit()
        conn.close()
        if prod_name:
            remove_batch_from_heap(email, batch_no, prod_name)
        load_from_db(email, db_path=db_path)
        return True
    except Exception as e:
        print(f"Error in delete_batch: {e}")
        return False


def edit_batch(email=None, batch_no=None, quantity=None, unit_price=None, expiry_date=None, db_path='database.db'):
    """Safely updates quantity, price, and/or expiry date of an existing batch."""
    if not email or not batch_no:
        return False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT quantity, expiry_date, unit_price, product_name FROM inventory WHERE user_email=? AND batch_no=?", (email, str(batch_no).strip()))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        cur_qty, cur_exp, cur_pr, prod_name = row[0], row[1], row[2], row[3]
        new_qty = int(quantity) if quantity is not None else cur_qty
        if new_qty <= 0:
            conn.close()
            return False

        new_pr = float(unit_price) if unit_price is not None else cur_pr
        if new_pr < 0:
            new_pr = 0.0

        new_exp = str(expiry_date).strip() if expiry_date else cur_exp

        cursor.execute(
            "UPDATE inventory SET quantity=?, unit_price=?, expiry_date=? WHERE user_email=? AND batch_no=?",
            (new_qty, new_pr, new_exp, email, str(batch_no).strip())
        )
        conn.commit()
        conn.close()
        load_from_db(email, db_path=db_path)
        return True
    except Exception as e:
        print(f"Error in edit_batch: {e}")
        return False


def get_user_products_summary(email=None, db_path='database.db'):
    """
    Returns grouped list of products with total stock and individual batches
    for quick selection in UI forms and stock adjustment.
    """
    if not email:
        return []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT product_name, batch_no, quantity, expiry_date, COALESCE(unit_price, 0.0) 
               FROM inventory WHERE user_email=? ORDER BY product_name ASC, expiry_date ASC""",
            (email,)
        )
        rows = cursor.fetchall()
        conn.close()

        prod_map = {}
        for row in rows:
            pname, bno, qty, exp, pr = row[0], row[1], int(row[2]), row[3], float(row[4])
            if pname not in prod_map:
                prod_map[pname] = {
                    "product_name": pname,
                    "total_quantity": 0,
                    "unit_price": pr,
                    "batches": []
                }
            prod_map[pname]["total_quantity"] += qty
            if pr > 0 and prod_map[pname]["unit_price"] == 0:
                prod_map[pname]["unit_price"] = pr
            prod_map[pname]["batches"].append({
                "batch_no": bno,
                "quantity": qty,
                "expiry_date": exp,
                "unit_price": pr
            })
        return list(prod_map.values())
    except Exception as e:
        print(f"Error in get_user_products_summary: {e}")
        return []


def update_product_price(email=None, product_name=None, unit_price=0.0, db_path='database.db'):
    """
    Updates the unit price of a product across all active inventory batches.
    """
    if not email or not product_name or unit_price is None:
        return False
    try:
        price = float(unit_price)
        if price < 0:
            price = 0.0
    except (ValueError, TypeError):
        return False

    product_name = str(product_name).upper().strip()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE inventory SET unit_price=? WHERE user_email=? AND product_name=?",
            (price, email, product_name)
        )
        conn.commit()
        conn.close()
        load_from_db(email, db_path=db_path)
        return True
    except Exception as e:
        print(f"Error in update_product_price: {e}")
        return False


def adjust_product_stock(email=None, product_name=None, delta_qty=0, batch_no=None, unit_price=None, db_path='database.db'):
    """
    Adjusts stock quantity and/or unit price of an existing product.
    If delta_qty == 0 and unit_price is provided, updates the unit price only.
    If unit_price is provided, updates unit price in addition to quantity adjustments.
    Returns (success: bool, message: str, new_quantity: int)
    """
    if not email or not product_name:
        return False, "Invalid product specified.", None

    product_name = str(product_name).upper().strip()

    # Parse price if provided
    new_price = None
    if unit_price is not None and str(unit_price).strip() != "":
        try:
            parsed_price = float(unit_price)
            if parsed_price >= 0:
                new_price = parsed_price
        except (ValueError, TypeError):
            pass

    # If only updating price without quantity delta
    if delta_qty == 0:
        if new_price is not None:
            updated = update_product_price(email=email, product_name=product_name, unit_price=new_price, db_path=db_path)
            if updated:
                return True, f"Updated price for {product_name} to ₹{new_price:.2f}.", None
            return False, f"Failed to update price for {product_name}.", None
        return False, "No quantity or price change specified.", None

    try:
        delta = int(delta_qty)
    except (ValueError, TypeError):
        return False, "Quantity must be an integer.", None

    # If price is also specified, update product price
    if new_price is not None:
        update_product_price(email=email, product_name=product_name, unit_price=new_price, db_path=db_path)

    if batch_no and str(batch_no).strip() != "" and str(batch_no).strip() != "AUTO":
        res = adjust_batch_quantity(email=email, batch_no=str(batch_no).strip(), delta_qty=delta, db_path=db_path)
        if res is not None:
            price_msg = f" (Price set to ₹{new_price:.2f})" if new_price is not None else ""
            return True, f"Batch {batch_no} quantity updated to {res}{price_msg}.", res
        return False, f"Failed to update batch {batch_no}.", None

    # No specific batch chosen:
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, batch_no, quantity FROM inventory WHERE user_email=? AND product_name=? ORDER BY expiry_date DESC",
            (email, product_name)
        )
        batches = cursor.fetchall()
        conn.close()

        if not batches:
            return False, f"No existing batches found for product {product_name}.", None

        price_msg = f" and updated price to ₹{new_price:.2f}" if new_price is not None else ""

        if delta > 0:
            target_batch_no = batches[0][1]
            new_qty = adjust_batch_quantity(email=email, batch_no=target_batch_no, delta_qty=delta, db_path=db_path)
            return True, f"Added {delta} units to {product_name} (Batch {target_batch_no}){price_msg}. New batch qty: {new_qty}.", new_qty
        else:
            success = sell_product(email=email, product_name=product_name, quantity=abs(delta), db_path=db_path)
            if success:
                return True, f"Reduced {abs(delta)} units from {product_name} using FEFO{price_msg}.", None
            return False, f"Insufficient stock to reduce {abs(delta)} units of {product_name}.", None
    except Exception as e:
        print(f"Error in adjust_product_stock: {e}")
        return False, str(e), None



 
