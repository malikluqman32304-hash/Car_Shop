import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Dataset Viewer", layout="wide")
st.title("📊 Streamlit SQLite / SQL Dataset Explorer")

st.write(
    "Upload a **SQLite .db file** or a **.sql script** containing table definitions/data."
)

uploaded_file = st.file_uploader("Upload dataset file", type=["db", "sqlite", "sql"])

@st.cache_data
def load_from_sql_script(sql_bytes):
    script = sql_bytes.decode("utf-8")
    conn = sqlite3.connect(":memory:")
    conn.executescript(script)
    return conn

@st.cache_data
def load_from_sqlite_db(db_bytes):
    temp_path = Path("/mnt/data/temp.db")
    temp_path.write_bytes(db_bytes)
    return sqlite3.connect(str(temp_path))

if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()

    if file_ext == "sql":
        st.info("Detected SQL script — loading into an in-memory database…")
        conn = load_from_sql_script(uploaded_file.read())
    else:
        st.info("Detected SQLite database file — opening database…")
        conn = load_from_sqlite_db(uploaded_file.read())

    # Fetch available tables
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;", conn
    )

    if tables.empty:
        st.warning("No tables found in the database.")
    else:
        table_names = tables["name"].tolist()
        table = st.selectbox("Select a table to view", table_names)

        df = pd.read_sql(f"SELECT * FROM {table};", conn)

        st.subheader(f"📁 Table: {table}")
        st.write(f"Rows: **{len(df)}**, Columns: **{len(df.columns)}**")

        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇️ Download as CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"{table}.csv",
            mime="text/csv",
        )

else:
    st.info("Upload your dataset file to begin.")
