"""
Database configuration and connection management
"""
import os
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")


def get_connection():
    """Get a new database connection"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute_query(query: str, params: Optional[tuple] = None, fetch: bool = True):
    """
    Execute a query and return results
    
    Args:
        query: SQL query string
        params: Query parameters
        fetch: Whether to fetch results (SELECT) or not (INSERT/UPDATE/DELETE)
    
    Returns:
        List of dict rows if fetch=True, None otherwise
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if fetch:
                return cur.fetchall()
            return None


def execute_many(query: str, params_list: list):
    """Execute a query multiple times with different parameters"""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.executemany(query, params_list)


def init_db():
    """Initialize database with schema"""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
    
    print("✅ Database schema initialized successfully")


def create_default_users():
    """Create default users for canchas and public access"""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    users = [
        ("cancha1", "cancha1", "cancha1"),
        ("cancha2", "cancha2", "cancha2"),
        ("cancha3", "cancha3", "cancha3"),
        ("publico", "publico", "publico"),
        ("admin", "admin123", "admin"),
    ]
    
    with get_db() as conn:
        with conn.cursor() as cur:
            for username, password, tipo in users:
                password_hash = pwd_context.hash(password)
                cur.execute(
                    """
                    INSERT INTO usuarios (username, password_hash, tipo)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (username) DO NOTHING
                    """,
                    (username, password_hash, tipo)
                )
    
    print("✅ Default users created")
