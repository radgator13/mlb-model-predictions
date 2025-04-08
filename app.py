import streamlit as st
import pandas as pd
import subprocess
from pathlib import Path

st.set_page_config(page_title="MLB Model Predictions", layout="wide")

st.title("⚾ MLB Model Predictions")
st.caption("DraftKings lines vs model picks with 🔥 fireball confidence")

if st.button("🔄 Run Model & Update Predictions"):
    subprocess.run(["python", "predict_today.py"], check=True)

files = sorted(Path().glob("mlb_predictions_*.csv"), reverse=True)
if not files:
    st.error("No prediction file found.")
    st.stop()

latest_file = files[0]
df = pd.read_csv(latest_file)
st.markdown(f"📂 **Using:** `{latest_file.name}`")

min_conf = st.selectbox(
    "🔥 Minimum Confidence (Fireballs)",
    ["All", "🔥", "🔥🔥", "🔥🔥🔥", "🔥🔥🔥🔥", "🔥🔥🔥🔥🔥"],
    index=0
)

if min_conf != "All":
    df = df[
        (df["model_spread_conf"] >= min_conf) |
        (df["model_total_conf"] >= min_conf)
    ]

columns_to_display = [
    "timestamp", "home_team", "away_team",
    "spread_line", "model_spread_pick", "model_spread_conf",
    "total_line", "model_total_pick", "model_total_conf"
]


st.dataframe(df[columns_to_display], use_container_width=True)
