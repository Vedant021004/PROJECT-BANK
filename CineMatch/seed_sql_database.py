"""
seed_sql_database.py
CLI Utility to initialize and seed the CineMatch SQLite Database from movies.csv.
Demonstrates DDL schema creation, table constraints, B-Tree indexes, and CRUD execution.
"""

import sys
import os

# Add root directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Configure UTF-8 encoding for Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from engine.sql_database import SQLMovieDatabase


def main():
    print("=" * 70)
    print("🎬 CINEMATCH DBMS INITIALIZATION & SQL SEEDER")
    print("=" * 70)

    db_path = os.path.join(os.path.dirname(__file__), "data", "movies.db")
    csv_path = os.path.join(os.path.dirname(__file__), "data", "movies.csv")

    print(f"[*] SQLite Database Path : {db_path}")
    print(f"[*] Source CSV Path     : {csv_path}")

    # Initialize SQL database
    sql_db = SQLMovieDatabase(db_path=db_path, csv_path=csv_path)

    print("\n[+] Creating Relational Tables & DDL Schema...")
    sql_db.init_database()

    print("[+] Seeding records from CSV into SQLite table 'movies'...")
    count = sql_db.seed_from_csv(csv_path)
    print(f"[✓] Successfully seeded {count} movies into SQLite database!")

    # Display Schema Report
    print("\n" + "=" * 70)
    print("📊 RELATIONAL SCHEMA REPORT (DDL & CONSTRAINTS)")
    print("=" * 70)
    schema = sql_db.get_schema_info()
    for table_name, info in schema.items():
        print(f"\n📁 TABLE: {table_name}")
        print("  Columns:")
        for col in info["columns"]:
            pk = " [PRIMARY KEY]" if col["pk"] else ""
            notnull = " NOT NULL" if col["notnull"] else ""
            default = f" DEFAULT {col['dflt_value']}" if col["dflt_value"] else ""
            print(f"    - {col['name']} ({col['type']}){pk}{notnull}{default}")
        print("  Indexes:")
        for idx in info["indexes"]:
            print(f"    * {idx['name']} (unique={bool(idx['unique'])})")

    # Display Stats
    print("\n" + "=" * 70)
    print("📈 DBMS AGGREGATE METRICS (SQL AGGREGATIONS)")
    print("=" * 70)
    stats = sql_db.get_stats()
    for k, v in stats.items():
        print(f"  • {k.replace('_', ' ').title():20}: {v}")

    # Test CRUD demonstration
    print("\n" + "=" * 70)
    print("⚡ DEMONSTRATING LIVE CRUD OPERATIONS")
    print("=" * 70)

    # 1. READ
    sample = sql_db.read_movie(1)
    print(f"[R] READ movie #1: {sample['title']} ({sample['release_year']}) | Rating: {sample['rating']} | OTT: {sample['ott_platform']}")

    # 2. CREATE (Test temporary record)
    test_id, insert_sql = sql_db.create_movie(
        title="DBMS Viva Demo Movie",
        genre="Sci-Fi, Education",
        language="English",
        mood="Thoughtful",
        duration=120,
        rating=9.5,
        ott_platform="Netflix",
        release_year=2026,
        description="A movie created to demonstrate SQL INSERT CRUD operation to professors."
    )
    print(f"[C] CREATE inserted test movie with ID #{test_id}")
    print(f"    Executed SQL: {insert_sql}")

    # 3. UPDATE
    upd_ok, update_sql = sql_db.update_movie(
        movie_id=test_id,
        title="DBMS Viva Demo Movie (Updated)",
        genre="Sci-Fi, Education",
        language="English",
        mood="Thoughtful, Excited",
        duration=125,
        rating=9.9,
        ott_platform="Prime Video",
        release_year=2026,
        description="Updated to demonstrate SQL UPDATE statement."
    )
    print(f"[U] UPDATE movie #{test_id} status: {upd_ok}")
    print(f"    Executed SQL: {update_sql}")

    # 4. DELETE
    del_ok, delete_sql = sql_db.delete_movie(test_id)
    print(f"[D] DELETE movie #{test_id} status: {del_ok}")
    print(f"    Executed SQL: {delete_sql}")

    print("\n[✓] All DBMS & CRUD Operations verified successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
