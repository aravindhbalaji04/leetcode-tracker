from celery import Celery
from apscheduler.schedulers.background import BackgroundScheduler
from leetcode_scraper import get_all_user_stats
import sqlite3
from datetime import datetime
import time

# Configure Celery
celery = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery.task
def update_leetcode_data():
    """Fetch latest LeetCode stats and update database correctly."""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    users = get_all_user_stats()  # Get latest stats
    today_date = datetime.now().strftime("%Y-%m-%d")

    for user in users:
        username, solved_count = user["username"], user["solved"]

        # Fetch existing data
        cursor.execute("SELECT solved_problems, yesterday_solved, last_updated FROM leetcode_stats WHERE username = ?", (username,))
        row = cursor.fetchone()

        if row:
            previous_solved, yesterday_solved, last_updated = row

            # Only update yesterday_solved at 12:00 AM
            if last_updated != today_date:
                yesterday_solved = previous_solved  # Correctly store yesterday's count

            # Ensure daily solved count is always correct
            daily_solved = max(0, solved_count - yesterday_solved)

            # Update database
            cursor.execute(
                """
                UPDATE leetcode_stats
                SET solved_problems = ?, yesterday_solved = ?, daily_solved = ?, last_updated = ?
                WHERE username = ?
                """,
                (solved_count, yesterday_solved, daily_solved, today_date, username),
            )
        else:
            # Insert new user data
            cursor.execute(
                """
                INSERT INTO leetcode_stats (username, solved_problems, yesterday_solved, daily_solved, last_updated)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, solved_count, solved_count, 0, today_date),
            )

    conn.commit()
    conn.close()
    print(f"✅ LeetCode stats updated correctly at {datetime.now()}!")

# APScheduler: Run task daily at 12:00 AM
scheduler = BackgroundScheduler()

def schedule_updates():
    scheduler.add_job(update_leetcode_data, "cron", hour=0, minute=0)  # Runs every day at 12:00 AM
    scheduler.start()
    print("🔄 Scheduled daily updates for LeetCode stats at 12:00 AM.")

if __name__ == "__main__":
    schedule_updates()
    while True:
        time.sleep(1)  # Keeps the script running
