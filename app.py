import streamlit as st
import pandas as pd
import subprocess
from pathlib import Path

st.set_page_config(page_title="MLB Model Predictions", layout="wide")

st.title("⚾ MLB Model Predictions")
st.caption("DraftKings lines vs model picks with 🔥 fireball confidence")

# === Run model manually
if st.button("🔄 Run Model & Update Predictions"):
    subprocess.run(["python", "predict_today.py"], check=True)

# === Load latest prediction file
files = sorted(Path().glob("mlb_predictions_*.csv"), reverse=True)
if not files:
    st.error("No prediction file found.")
    st.stop()

latest_file = files[0]
df = pd.read_csv(latest_file)
st.markdown(f"📂 **Using:** `{latest_file.name}`")

# === Filter by minimum confidence
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

# === Main predictions table
columns_to_display = [
    "timestamp", "home_team", "away_team",
    "spread_line", "model_spread_pick", "model_spread_conf",
    "total_line", "model_total_pick", "model_total_conf"
]
st.dataframe(df[columns_to_display], use_container_width=True)

# === Top 5 Picks
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

# === Best Bets Log & Summary
st.markdown("---")
st.header("📊 Best Bets Log (Top 5 Daily Picks)")

log_path = Path("best_bets_log.csv")
if log_path.exists():
    log_df = pd.read_csv(log_path)
    st.dataframe(log_df, use_container_width=True)

    # === Pick count summary + status
    st.markdown("### 📅 Daily Pick Summary + Results")

    if "correct" in log_df.columns:
        # Total picks per day/type
        total_counts = log_df.groupby(["date", "type"]).size().rename("total")

        # Results filled
        completed = log_df[log_df["correct"].isin([0, 1])]
        result_summary = (
            completed.groupby(["date", "type"])["correct"]
            .agg(["count", "sum"])
            .rename(columns={"count": "results_filled", "sum": "wins"})
        )
        result_summary["losses"] = result_summary["results_filled"] - result_summary["wins"]
        result_summary["win_rate"] = (result_summary["wins"] / result_summary["results_filled"]).round(2)

        # Merge total and result summary
        summary = total_counts.to_frame().join(result_summary, how="left")
        summary["results_filled"] = summary["results_filled"].fillna(0).astype(int)
        summary["wins"] = summary["wins"].fillna("")
        summary["losses"] = summary["losses"].fillna("")
        summary["win_rate"] = summary["win_rate"].fillna("")

        # Add result status
        summary["result_status"] = summary.apply(
            lambda row: "✅ Completed" if row["results_filled"] == row["total"] and row["total"] > 0
            else "⏳ Pending", axis=1
        )

        st.dataframe(summary[[
            "total", "wins", "losses", "win_rate", "result_status"
        ]])
    else:
        st.info("Results not yet added to the log. Update 'result' and 'correct' columns to enable win/loss tracking.")

else:
    st.warning("No best_bets_log.csv found yet. Run the pipeline to generate top 5 picks.")
