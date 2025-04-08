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
st.markdown("---")
st.header("🔥 Top 5 Best Spread Picks (by Edge)")

top_spread = df.sort_values("spread_edge", ascending=False).head(5)
st.dataframe(top_spread[[
    "home_team", "away_team", "spread_line",
    "model_spread_pick", "spread_edge", "model_spread_conf"
]])

st.markdown("### ")

st.header("🔥 Top 5 Best Total Picks (by Confidence)")

top_total = df.sort_values("model_total_conf", ascending=False).head(5)
st.dataframe(top_total[[
    "home_team", "away_team", "total_line",
    "model_total_pick", "model_total_conf"
]])

st.markdown("---")
st.header("📊 Best Bets Log (Top 5 Daily Picks)")

log_path = Path("best_bets_log.csv")
if log_path.exists():
    log_df = pd.read_csv(log_path)

    # Display full log table
    st.dataframe(log_df, use_container_width=True)

    # === Daily Summary (basic count only)
    st.markdown("### 🔢 Daily Summary: Wins & Losses")

    # Count daily picks
    daily_counts = log_df.groupby(["date", "type"]).size().unstack(fill_value=0)

    st.dataframe(daily_counts)

    # === Optional: calculate win/loss if you add outcome tracking later
    # For now, we just show how many spread/total picks were made per day

else:
    st.warning("No best_bets_log.csv found yet. Run the pipeline to generate top 5 picks.")
