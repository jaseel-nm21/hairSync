"""
HairSync Database Connection Helper
Provides secure parameterized queries and dictionary cursor support via PyMySQL.
"""

import pymysql
from pymysql.cursors import DictCursor
from flask import current_app, g
from config import Config


def get_db():
    """
    Open a new database connection if there is none yet for the
    current application context.
    """
    if 'db' not in g:
        try:
            g.db = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                charset='utf8mb4',
                cursorclass=DictCursor,
                autocommit=False
            )
        except pymysql.MySQLError as err:
            current_app.logger.error(f"Database connection error: {err}")
            raise err
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass


def query_db(query, args=(), one=False):
    """
    Executes a SELECT query with parameterized inputs to prevent SQL injection.
    
    :param query: SQL query string with %s placeholders
    :param args: Tuple or list of parameters
    :param one: If True, returns a single dictionary row or None
    :return: List of dicts or single dict
    """
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, args)
        result = cursor.fetchall()
        return (result[0] if result else None) if one else result


def execute_db(query, args=(), commit=True):
    """
    Executes an INSERT, UPDATE, or DELETE query with parameterized inputs.
    
    :param query: SQL statement with %s placeholders
    :param args: Tuple or list of parameters
    :param commit: If True, commits the transaction immediately
    :return: dict with 'lastrowid' and 'rowcount'
    """
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(query, args)
            last_id = cursor.lastrowid
            affected = cursor.rowcount
            if commit:
                db.commit()
            return {'lastrowid': last_id, 'rowcount': affected}
    except pymysql.MySQLError as err:
        db.rollback()
        current_app.logger.error(f"SQL execution error on [{query}]: {err}")
        raise err


def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)
