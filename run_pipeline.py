import subprocess
from pathlib import Path

# Get the directory where this script lives
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
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)

if __name__ == "__main__":
    try:
        run_script("espn_scrape.py")
        run_script("Sports_Data_IO.py")
        run_script("MLB_Model_Success.py")

        git_commit_push(
            ["comparison.csv", "app.py"],
            "Automated update: comparison + app"
        )

        print("✅ Automation complete!")

    except subprocess.CalledProcessError as e:
        print("❌ An error occurred during automation:")
        print(e)
