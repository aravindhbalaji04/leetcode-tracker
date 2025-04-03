import requests
import sqlite3
from datetime import datetime

USERNAMES = ["aravindhbalaji04", "Naveen-1212", "dhanush__27", "Dineshram_005", "ArjanVailly"]  # Predefined usernames

def get_leetcode_stats(username):
    url = "https://leetcode.com/graphql"
    query = {
        "query": """
        query userProfile($username: String!) {
            matchedUser(username: $username) {
                submitStatsGlobal {
                    acSubmissionNum {
                        count
                    }
                }
            }
        }
        """,
        "variables": {"username": username},
    }
    
    response = requests.post(url, json=query)
    data = response.json()

    if "errors" in data:
        return {"username": username, "solved": "Not Found", "solved_today": 0}
    
    solved_count = data["data"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"][0]["count"]
    solved_today = update_database(username, solved_count)  # Store in DB and get daily count
    return {"username": username, "solved": solved_count, "solved_today": solved_today}

def update_database(username, solved_count):
    """Update database with the latest solved problems and calculate daily solved problems."""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT solved_problems FROM leetcode_stats WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row:
        prev_solved = row[0]
        solved_today = max(solved_count - prev_solved, 0)  # Prevent negative values

        # Update database
        cursor.execute("UPDATE leetcode_stats SET solved_problems = ?, last_updated = ? WHERE username = ?",
                       (solved_count, datetime.now().strftime("%Y-%m-%d"), username))
    else:
        solved_today = 0  # First-time entry, no previous data

        # Insert new user into the database
        cursor.execute("INSERT INTO leetcode_stats (username, solved_problems, last_updated) VALUES (?, ?, ?)",
                       (username, solved_count, datetime.now().strftime("%Y-%m-%d")))

    conn.commit()
    conn.close()
    return solved_today  # Return today's solved problems

def get_all_user_stats():
    return [get_leetcode_stats(username) for username in USERNAMES]
[]