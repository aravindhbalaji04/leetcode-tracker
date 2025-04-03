import sqlite3
from datetime import datetime
from leetcode_scraper import get_all_user_stats
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

def update_data():
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

            # ✅ **Only update yesterday_solved if today is a new day**
            if last_updated != today_date:
                print(f"🌙 Midnight update for {username} → Yesterday's count is now {previous_solved}")
                yesterday_solved = previous_solved  # Correctly store yesterday's count

            # 🔥 **Daily solved calculation**
            daily_solved = max(0, solved_count - yesterday_solved)

            # Update database **without touching yesterday_solved during the day**
            cursor.execute(
                """
                UPDATE leetcode_stats
                SET solved_problems = ?, daily_solved = ?, last_updated = ?
                WHERE username = ?
                """,
                (solved_count, daily_solved, today_date, username),
            )

            # ✅ **At 12:00 AM, update yesterday_solved**
            if last_updated != today_date:
                cursor.execute(
                    """
                    UPDATE leetcode_stats
                    SET yesterday_solved = ?
                    WHERE username = ?
                    """,
                    (yesterday_solved, username),
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