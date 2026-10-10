import sqlite3
import datetime
import math

def calculate_product_forecasts(email, db_path='database.db', window_days=7):
    """
    Computes product-wise 7-day demand predictions and smart restock recommendations.
    
    Uses a 7-calendar-day moving average:
      Average Daily Demand = Total Units Sold During the Previous 7 Calendar Days / 7
      Forecast Demand for Next 7 Days = Average Daily Demand * 7
      Projected Shortage = max(0, Forecast Demand - Current Stock)
      Suggested Restock Quantity = Projected Shortage
      
    Accounts for zero-sales days accurately across the 7-day window.
    Retrieves all required data in grouped queries to avoid N+1 query patterns.
    """
    if not email:
        return {
            "generated_date": "",
            "history_period": "",
            "forecast_period": "",
            "items": [],
            "products": [],
            "summary": {
                "total_products": 0,
                "restock_suggested_count": 0,
                "low_stock_count": 0,
                "sufficient_stock_count": 0,
                "insufficient_data_count": 0
            }
        }

    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=window_days - 1)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = today.strftime('%Y-%m-%d')
    forecast_start_str = (today + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    forecast_end_str = (today + datetime.timedelta(days=window_days)).strftime('%Y-%m-%d')
    generated_date_str = today.strftime('%Y-%m-%d')

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. Get all distinct products belonging to the user
        cursor.execute('''
            SELECT DISTINCT product_name FROM inventory WHERE user_email = ?
            UNION
            SELECT DISTINCT product_name FROM sales WHERE user_email = ?
            ORDER BY product_name ASC
        ''', (email, email))
        all_products = [row[0] for row in cursor.fetchall() if row[0]]

        # 2. Get current active (non-expired) stock and unit price per product
        cursor.execute('''
            SELECT product_name, SUM(quantity), COALESCE(MAX(unit_price), 0.0)
            FROM inventory 
            WHERE user_email = ? AND expiry_date >= ?
            GROUP BY product_name
        ''', (email, end_date_str))
        stock_price_rows = cursor.fetchall()
        stock_map = {row[0]: int(row[1]) for row in stock_price_rows}
        price_map = {row[0]: float(row[2]) for row in stock_price_rows}

        # Also get any fallback unit_price from inventory if stock is currently 0 or expired
        cursor.execute('''
            SELECT product_name, COALESCE(MAX(unit_price), 0.0)
            FROM inventory
            WHERE user_email = ?
            GROUP BY product_name
        ''', (email,))
        for p_row in cursor.fetchall():
            if p_row[0] not in price_map or price_map[p_row[0]] == 0.0:
                price_map[p_row[0]] = float(p_row[1])

        # 3. Check lifetime sales presence per product
        cursor.execute('''
            SELECT product_name, COUNT(*), SUM(quantity)
            FROM sales
            WHERE user_email = ?
            GROUP BY product_name
        ''', (email,))
        lifetime_sales = {row[0]: {'txn_count': row[1], 'total_qty': row[2]} for row in cursor.fetchall()}

        # 4. Grouped query: units sold per product per date within the 7-calendar-day window
        cursor.execute('''
            SELECT product_name, sale_date, SUM(quantity)
            FROM sales
            WHERE user_email = ? AND sale_date >= ? AND sale_date <= ?
            GROUP BY product_name, sale_date
        ''', (email, start_date_str, end_date_str))
        
        window_sales_map = {}
        for row in cursor.fetchall():
            prod, sdate, sqty = row[0], row[1], int(row[2])
            if prod not in window_sales_map:
                window_sales_map[prod] = {}
            window_sales_map[prod][sdate] = sqty

        conn.close()

        items = []
        restock_suggested_count = 0
        low_stock_count = 0
        sufficient_stock_count = 0
        insufficient_data_count = 0

        for product in all_products:
            current_stock = stock_map.get(product, 0)
            unit_price = round(price_map.get(product, 0.0), 2)
            inventory_value = round(current_stock * unit_price, 2)
            has_lifetime_sales = (product in lifetime_sales and lifetime_sales[product]['total_qty'] > 0)

            if not has_lifetime_sales:
                # Honest handling for products with no recorded sales history
                status = "Insufficient Data"
                status_label = "Insufficient sales data"
                insufficient_data_count += 1
                items.append({
                    "product_name": product,
                    "unit_price": unit_price,
                    "current_stock": current_stock,
                    "inventory_value": inventory_value,
                    "avg_daily_demand": None,
                    "forecast_7_days": None,
                    "projected_shortage": 0,
                    "suggested_restock": 0,
                    "estimated_restock_cost": 0.0,
                    "status": status,
                    "status_label": status_label,
                    "has_data": False,
                    "days_with_sales": 0
                })
            else:
                # Sum daily sales over the 7-calendar-day window (zero-sales days naturally sum to 0)
                product_window_sales = window_sales_map.get(product, {})
                units_sold_window = sum(product_window_sales.values())
                days_with_sales = len(product_window_sales)

                # Exactly 7 calendar days in the window divisor
                avg_daily_demand = round(units_sold_window / float(window_days), 2)
                forecast_demand = int(math.ceil(avg_daily_demand * window_days))
                projected_shortage = max(0, forecast_demand - current_stock)
                suggested_restock = projected_shortage
                estimated_restock_cost = round(suggested_restock * unit_price, 2)

                # Status determination
                if projected_shortage > 0 or (current_stock == 0 and forecast_demand > 0):
                    status = "Restock Suggested"
                    status_label = f"Restock +{suggested_restock}"
                    restock_suggested_count += 1
                elif current_stock <= max(2, int(math.ceil(avg_daily_demand * 2))):
                    status = "Low Stock"
                    status_label = "Low Stock"
                    low_stock_count += 1
                else:
                    status = "Sufficient Stock"
                    status_label = "Sufficient Stock"
                    sufficient_stock_count += 1

                items.append({
                    "product_name": product,
                    "unit_price": unit_price,
                    "current_stock": current_stock,
                    "inventory_value": inventory_value,
                    "avg_daily_demand": avg_daily_demand,
                    "forecast_7_days": forecast_demand,
                    "projected_shortage": projected_shortage,
                    "suggested_restock": suggested_restock,
                    "estimated_restock_cost": estimated_restock_cost,
                    "status": status,
                    "status_label": status_label,
                    "has_data": True,
                    "days_with_sales": days_with_sales
                })

        total_inventory_valuation = round(sum(it.get("inventory_value", 0.0) for it in items), 2)
        total_restock_investment = round(sum(it.get("estimated_restock_cost", 0.0) for it in items), 2)

        return {
            "generated_date": generated_date_str,
            "history_period": f"{start_date_str} to {end_date_str}",
            "forecast_period": f"{forecast_start_str} to {forecast_end_str}",
            "items": items,
            "products": items,
            "summary": {
                "total_products": len(items),
                "total_inventory_valuation": total_inventory_valuation,
                "total_restock_investment": total_restock_investment,
                "restock_suggested_count": restock_suggested_count,
                "low_stock_count": low_stock_count,
                "sufficient_stock_count": sufficient_stock_count,
                "insufficient_data_count": insufficient_data_count
            }
        }
    except Exception as e:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        print(f"Error in calculate_product_forecasts: {e}")
        return {
            "generated_date": generated_date_str,
            "history_period": f"{start_date_str} to {end_date_str}",
            "forecast_period": f"{forecast_start_str} to {forecast_end_str}",
            "items": [],
            "products": [],
            "summary": {
                "total_products": 0,
                "restock_suggested_count": 0,
                "low_stock_count": 0,
                "sufficient_stock_count": 0,
                "insufficient_data_count": 0
            }
        }
