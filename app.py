# app.py
import os
import psycopg2
from flask import Flask, jsonify, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests

app = Flask(__name__)
DATABASE_URL = os.getenv("postgresql://leetcode_db_user:vBTinZ7ZoiM6MbQZVlj4RiB0r6L5DWAL@dpg-cvsgd6i4d50c738ggsqg-a/leetcode_db")

def get_db_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                last_title TEXT,
                today_count INT
            )
        """)
        conn.commit()

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# --- Utility to get latest LeetCode submissions ---
def get_recent_submission_count(username):
    url = "https://leetcode.com/graphql"
    query = """
    query recentAcSubmissions($username: String!) {
      recentAcSubmissionList(username: $username, limit: 20) {
        title
        timestamp
      }
    }
    """
    response = requests.post(url, json={"query": query, "variables": {"username": username}})
    if response.status_code == 200:
        return response.json()["data"]["recentAcSubmissionList"]
    return []

# --- Init DB ---
def init_db():
    with get_db_conn(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, last_title TEXT, today_count INT)''')
        conn.commit()

@app.route("/api/users", methods=["GET"])
def get_users():
    with get_db_conn(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
    return jsonify(users)

def update_user_data():
    with get_db_conn(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT username, last_title FROM users")
        users = cur.fetchall()
        for username, last_title in users:
            subs = get_recent_submission_count(username)
            count = 0
            titles_seen = set()
            for sub in subs:
                if sub["title"] == last_title:
                    break
                if sub["title"] not in titles_seen:
                    count += 1
                    titles_seen.add(sub["title"])
            if subs:
                cur.execute("UPDATE users SET today_count = ?, last_title = ? WHERE username = ?",
                            (count, subs[0]["title"], username))
        conn.commit()

# --- Scheduler: Update at midnight ---
scheduler = BackgroundScheduler()
scheduler.add_job(update_user_data, 'cron', hour=0, minute=0)
scheduler.start()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
