import sqlite3

def display_table(cursor, title, query, headers):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)
    cursor.execute(query)
    rows = cursor.fetchall()
    if not rows:
        print("  (No records found)")
        return

    # Print headers
    header_str = " | ".join(f"{h:<18}" for h in headers)
    print(header_str)
    print("-" * len(header_str))

    # Print rows
    for row in rows:
        print(" | ".join(f"{str(col):<18}" for col in row))

def main():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    display_table(
        cursor,
        "REGISTERED USERS (user table)",
        "SELECT id, email, name, mobile FROM user",
        ["ID", "Email", "Name", "Mobile"]
    )

    display_table(
        cursor,
        "CURRENT INVENTORY BATCHES (inventory table)",
        "SELECT id, product_name, batch_no, quantity, expiry_date, user_email FROM inventory ORDER BY expiry_date ASC",
        ["ID", "Product", "Batch No", "Quantity", "Expiry Date", "User Email"]
    )

    display_table(
        cursor,
        "RECORDED SALES TRANSACTIONS (sales table)",
        "SELECT id, product_name, quantity, sale_date, sale_timestamp, user_email FROM sales ORDER BY id DESC",
        ["ID", "Product", "Qty Sold", "Sale Date", "Timestamp", "User Email"]
    )

    print("\n" + "=" * 70 + "\n")
    conn.close()

if __name__ == '__main__':
    main()
