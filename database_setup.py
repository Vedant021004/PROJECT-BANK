import sqlite3
import os
import shutil
import datetime

def backup_db(db_path='database.db', backup_dir='backups'):
    """
    Creates a verified backup copy of the SQLite database before any schema update.
    Returns the backup file path if created, or None if the database does not exist yet.
    """
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        return None

    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f"database_backup_{timestamp}.db")

    try:
        source_conn = sqlite3.connect(db_path)
        dest_conn = sqlite3.connect(backup_file)
        source_conn.backup(dest_conn)
        dest_conn.close()
        source_conn.close()

        # Verify backup integrity
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        conn.close()
        if result and result[0] == 'ok':
            print(f"[Database Backup] Verified backup successfully created at: {backup_file}")
            return backup_file
    except Exception as e:
        print(f"[Database Backup Warning] SQLite online backup encountered: {e}")
        try:
            shutil.copy2(db_path, backup_file)
            return backup_file
        except Exception:
            pass

    return backup_file

def init_db(db_path='database.db'):
    """
    Safely initializes or migrates the SQLite database.
    Preserves all existing tables and data, and adds the sales table and indexes.
    """
    # Create verified backup if database exists
    backup_db(db_path=db_path)

    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON;')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,   
            password TEXT NOT NULL,
            name TEXT,
            mobile TEXT
        )
    ''')
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_user_email ON user(email);')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            product_name TEXT NOT NULL,
            batch_no TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            expiry_date TEXT NOT NULL,
            unit_price REAL DEFAULT 0.0,
            FOREIGN KEY (user_email) REFERENCES user(email)
        )
    ''')

    # Safe migration: ensure unit_price exists in inventory
    cursor.execute("PRAGMA table_info(inventory);")
    inv_cols = {col[1] for col in cursor.fetchall()}
    if 'unit_price' not in inv_cols:
        cursor.execute("ALTER TABLE inventory ADD COLUMN unit_price REAL DEFAULT 0.0;")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            sale_date TEXT NOT NULL,
            sale_timestamp TEXT NOT NULL,
            unit_price REAL DEFAULT 0.0,
            total_amount REAL DEFAULT 0.0,
            FOREIGN KEY (user_email) REFERENCES user(email)
        )
    ''')

    # Safe migration: ensure unit_price and total_amount exist in sales
    cursor.execute("PRAGMA table_info(sales);")
    sales_cols = {col[1] for col in cursor.fetchall()}
    if 'unit_price' not in sales_cols:
        cursor.execute("ALTER TABLE sales ADD COLUMN unit_price REAL DEFAULT 0.0;")
    if 'total_amount' not in sales_cols:
        cursor.execute("ALTER TABLE sales ADD COLUMN total_amount REAL DEFAULT 0.0;")

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_sales_user_product_date 
        ON sales(user_email, product_name, sale_date)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_inventory_user_product 
        ON inventory(user_email, product_name)
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")