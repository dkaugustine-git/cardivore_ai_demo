import os
import mysql.connector
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

load_dotenv()

def get_mysql_connection():
    """Return a live MySQL connection using .env credentials."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )

def insert_dataframe(df, table_name):
    """
    Insert a pandas DataFrame into a MySQL table.

    - Escapes column names with backticks to handle spaces/special chars.
    - Uses executemany() for speed.
    - Commits and closes connection automatically.
    """
    import mysql.connector
    from cardivore_ai.utils.db_utils import get_mysql_connection

    if df.empty:
        print(f"[insert_dataframe] DataFrame is empty — nothing to insert into '{table_name}'.")
        return

    conn = get_mysql_connection()
    cursor = conn.cursor()

    # ✅ Escape column names with backticks
    cols = ", ".join(f"`{col}`" for col in df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    query = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"

    data = [tuple(row) for _, row in df.iterrows()]

    try:
        cursor.executemany(query, data)
        conn.commit()
        print(f"[insert_dataframe] Inserted {cursor.rowcount} rows into '{table_name}'.")
    except mysql.connector.Error as e:
        print(f"[insert_dataframe] MySQL error: {e}")
        print("SQL:", query)
    finally:
        cursor.close()
        conn.close()

def execute_sql(statement: str):
    """Execute a single SQL statement."""
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute(statement)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Executed SQL successfully.")

def execute_sql_file(sql_file_path: str):
    """Execute the contents of a .sql file, supporting multiple statements."""
    conn = get_mysql_connection()
    cursor = conn.cursor()

    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Split the SQL file by semicolon, safely ignoring empty lines
    for statement in sql_script.strip().split(";"):
        stmt = statement.strip()
        if stmt:
            cursor.execute(stmt)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Executed SQL file: {os.path.basename(sql_file_path)}")

def get_engine_from_env():
    """
    Create a SQLAlchemy engine using the .env file variables.
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "")

    url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url)


MYSQL_TYPE_MAP = {
    "object": "TEXT",
    "float64": "DOUBLE",
    "int64": "INT",
    "Int64": "INT",
}

def create_table_if_not_exists(engine, df: pd.DataFrame, table_name: str):
    """
    Create a MySQL table if it doesn't exist, with inferred column types.
    """
    with engine.connect() as conn:
        existing = engine.dialect.has_table(conn, table_name)
        if existing:
            print(f"ℹ️ Table '{table_name}' already exists.")
            return

        # Infer column types
        cols = []
        for col, dtype in df.dtypes.items():
            sql_type = MYSQL_TYPE_MAP.get(str(dtype), "TEXT")
            cols.append(f"`{col}` {sql_type}")
        ddl = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n  {', '.join(cols)}\n);"
        conn.execute(text(ddl))
        print(f"✅ Table '{table_name}' created.")

def create_or_replace_view(engine, view_name: str, select_sql: str):
    ddl = f"CREATE OR REPLACE VIEW {view_name} AS {select_sql}"
    with engine.connect() as conn:
        conn.execute(text(ddl))
        conn.commit()


def get_engine(demo_mode=True):
    """
    Returns a SQLAlchemy engine.
    - demo_mode=True: uses SQLite for the demo
    - demo_mode=False: reads MySQL credentials from .env
    """
    if demo_mode:
        # --- FIXED PATH ---
        # Base project root (two levels above utils/)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        db_path = os.path.join(project_root, "data", "database", "card_demo.db")

        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        print(f"📦 Using SQLite database at: {db_path}")

        engine = create_engine(f"sqlite:///{db_path}")
    else:
        load_dotenv()
        host = os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("MYSQL_PORT", "3306")
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", "")
        database = os.getenv("MYSQL_DATABASE", "cardivore_ai")
        url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        engine = create_engine(url)

    return engine