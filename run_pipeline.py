import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

def run_script(script_name):
    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return
    print(f"▶️ Running {script_path.name}...")
    subprocess.run(["python", str(script_path)], check=True)

def git_commit_push(files, message):
    print("📦 Committing and pushing to GitHub...")
    subprocess.run(["git", "add"] + files, check=True)

    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode == 0:
        print("✅ No changes to commit.")
        return

    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)

if __name__ == "__main__":
    try:
        # === Run fresh prediction
        run_script("predict_today.py")

        # === Find the latest prediction file
        predictions = sorted(SCRIPT_DIR.glob("mlb_predictions_*.csv"), reverse=True)
        latest_prediction = predictions[0].name if predictions else None

        if latest_prediction:
            # === Only commit necessary files
            git_commit_push(
                [
                    latest_prediction,
                    "app.py",
                    "predict_today.py",
                    "run_pipeline.py",
                    "win_model.pkl",
                    "ou_model.pkl"
                ],
                f"🔁 Daily model update: {latest_prediction}"
            )
        else:
            print("⚠️ No predictions found to commit.")

        print("✅ Pipeline complete!")

    except subprocess.CalledProcessError as e:
        print("❌ An error occurred during automation:")
        print(e)
