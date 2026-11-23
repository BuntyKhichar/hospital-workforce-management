import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "hospital.db"

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL, department TEXT NOT NULL,
            patient_count INTEGER NOT NULL, avg_wait_minutes REAL,
            peak_hour INTEGER)""")
        c.execute("""CREATE TABLE IF NOT EXISTS staff (
            staff_id TEXT PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL,
            department TEXT NOT NULL, available INTEGER DEFAULT 1,
            max_shifts_per_week INTEGER DEFAULT 5)""")
        c.execute("""CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT, schedule_date TEXT,
            shift TEXT, department TEXT, staff_id TEXT, staff_name TEXT,
            role TEXT, UNIQUE(schedule_date, shift, staff_id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, prediction_date TEXT,
            department TEXT, predicted_patients INTEGER, model_name TEXT)""")

def save_dataframe(table, df):
    if df.empty:
        return
    with connect() as c:
        df.to_sql(table, c, if_exists="append", index=False)

def read_table(table):
    with connect() as c:
        return pd.read_sql_query(f"SELECT * FROM {table}", c)

def replace_table(table, df):
    with connect() as c:
        df.to_sql(table, c, if_exists="replace", index=False)

def clear_schedules():
    with connect() as c:
        c.execute("DELETE FROM schedules")

def save_schedules(df):
    if df.empty:
        return
    with connect() as c:
        df.to_sql("schedules", c, if_exists="append", index=False)
