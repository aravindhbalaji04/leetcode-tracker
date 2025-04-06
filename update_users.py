import json
from datetime import datetime
from submissions import get_recent_submissions
import csv
import os

USERS_FILE = "users.json"
CSV_FILE = "daily_data.csv"

def log_to_csv(username, count):
    today = datetime.now().strftime("%Y-%m-%d")
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Date", "Username", "ProblemsSolved"])
        writer.writerow([today, username, count])

def update_user_data():
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_date = datetime.now().date()

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    for username, data in users.items():
        last_submission = data.get("lastSubmission")
        last_check = data.get("lastCheck")

        # Skip if already checked today
        if last_check == today_str:
            continue

        recent_subs = get_recent_submissions(username)
        count = 0

        for sub in recent_subs:
            sub_date = datetime.fromtimestamp(int(sub["timestamp"])).date()
            if sub_date != today_date:
                break
            if sub["title"] == last_submission:
                break
            count += 1

        # ✅ If no submissions today, still reset and log 0
        if recent_subs:
            users[username]["lastSubmission"] = recent_subs[0]["title"]

        users[username]["lastCheck"] = today_str
        users[username]["problemsSolvedToday"] = count

        # ✅ Log daily count (even if 0)
        log_to_csv(username, count)

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

    print("✅ Daily update done and logged.")
