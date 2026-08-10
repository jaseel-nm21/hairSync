"""
HairSync Database Initializer Script
Connects to MySQL server, creates `hairsync_db`, executes hairsync.sql,
and ensures admin and seed accounts are properly seeded.
Usage: python -m database.init_db OR python database/init_db.py
"""

import os
import sys
from pathlib import Path
import pymysql
from werkzeug.security import generate_password_hash

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import Config


def run_init():
    print("=" * 60)
    print("HairSync Database Initialization")
    print("=" * 60)
    print(f"Connecting to MySQL server at {Config.DB_HOST}:{Config.DB_PORT} as '{Config.DB_USER}'...")

    try:
        # Step 1: Connect to server without specific DB
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            charset='utf8mb4',
            autocommit=True
        )
        print("[+] Connected to MySQL successfully.")
    except pymysql.MySQLError as e:
        print(f"[-] ERROR: Unable to connect to MySQL server: {e}")
        print("    Please ensure MySQL/XAMPP is running and credentials in .env are correct.")
        sys.exit(1)

    sql_path = BASE_DIR / 'database' / 'hairsync.sql'
    if not sql_path.exists():
        print(f"[-] ERROR: SQL schema file not found at {sql_path}")
        sys.exit(1)

    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Split by semicolon statements (ignoring empty lines and comments)
    statements = []
    current_stmt = []
    for line in sql_content.splitlines():
        trimmed = line.strip()
        if trimmed.startswith('--') or trimmed.startswith('/*') or not trimmed:
            continue
        current_stmt.append(line)
        if trimmed.endswith(';'):
            statements.append("\n".join(current_stmt))
            current_stmt = []

    print(f"[*] Executing {len(statements)} SQL commands from {sql_path.name}...")

    with conn.cursor() as cursor:
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                except pymysql.MySQLError as err:
                    print(f"[-] Notice/Error on statement: {err}")

    conn.close()

    # Now verify default admin password hash with current Werkzeug installation
    print("[*] Reconnecting to hairsync_db to verify credentials...")
    try:
        db_conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset='utf8mb4',
            autocommit=True
        )
        admin_hash = generate_password_hash("Admin@123")
        sample_hash = generate_password_hash("Password@123")
        
        with db_conn.cursor() as cur:
            cur.execute("UPDATE users SET password_hash = %s WHERE email = 'admin@hairsync.com'", (admin_hash,))
            cur.execute("UPDATE users SET password_hash = %s WHERE email != 'admin@hairsync.com'", (sample_hash,))
        
        db_conn.close()
        print("[+] Passwords hashed and synced successfully.")
    except Exception as e:
        print(f"[*] Password sync note: {e}")

    print("\n" + "=" * 60)
    print("Database `hairsync_db` initialized successfully!")
    print("Default Test Accounts:")
    print("  1. Admin     : admin@hairsync.com      / Admin@123")
    print("  2. Approved NGO: contact@hopehair.org  / Password@123")
    print("  3. Pending NGO : info@gracecrown.org   / Password@123")
    print("  4. Donor     : donor@example.com       / Password@123")
    print("  5. Recipient : recipient@example.com   / Password@123")
    print("=" * 60)


if __name__ == '__main__':
    run_init()
