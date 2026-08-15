"""
HairSync Database Initializer Script
Creates SQLite database, executes hairsync.sql schema,
and ensures admin and seed accounts are properly seeded.
Usage: python -m database.init_db OR python database/init_db.py OR flask init-db
"""

import os
import sys
from pathlib import Path
import sqlite3
from werkzeug.security import generate_password_hash

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import Config


def run_init(db_path=None):
    """Initializes the SQLite database with tables and seed data."""
    if db_path is None:
        db_path = Config.DATABASE

    print("=" * 60)
    print("HairSync Database Initialization (SQLite)")
    print("=" * 60)
    print(f"[*] Target database file: {db_path}")

    # Ensure target directory exists
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    sql_path = BASE_DIR / 'database' / 'hairsync.sql'
    if not sql_path.exists():
        print(f"[-] ERROR: SQL schema file not found at {sql_path}")
        sys.exit(1)

    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        print("[*] Executing database schema...")
        conn.executescript(sql_content)

        # Update initial user seeds with live Werkzeug password hashes
        print("[*] Generating secure password hashes for seed accounts...")
        admin_hash = generate_password_hash("Admin@123")
        sample_hash = generate_password_hash("Password@123")

        cur = conn.cursor()
        cur.execute("UPDATE users SET password_hash = ? WHERE email = 'admin@hairsync.com'", (admin_hash,))
        cur.execute("UPDATE users SET password_hash = ? WHERE email != 'admin@hairsync.com'", (sample_hash,))
        conn.commit()
        conn.close()

        print("[+] SQLite database initialized and synced successfully.")
    except sqlite3.Error as e:
        print(f"[-] ERROR during database initialization: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Database `hairsync.db` initialized successfully!")
    print("Default Test Accounts:")
    print("  1. Admin        : admin@hairsync.com      / Admin@123")
    print("  2. Approved NGO : contact@hopehair.org  / Password@123")
    print("  3. Pending NGO  : info@gracecrown.org   / Password@123")
    print("  4. Donor        : donor@example.com       / Password@123")
    print("  5. Recipient    : recipient@example.com   / Password@123")
    print("=" * 60)


def init_db_if_needed(db_path=None):
    """Automatically initialize the database if the file does not exist or is empty."""
    if db_path is None:
        db_path = Config.DATABASE
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        run_init(db_path)


if __name__ == '__main__':
    run_init()
