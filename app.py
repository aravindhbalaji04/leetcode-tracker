from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from submissions import get_recent_submissions
from apscheduler.schedulers.background import BackgroundScheduler
import csv
from datetime import datetime
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_FILE = 'users.json'
CSV_FILE = 'daily_data.csv'

def log_daily_submission(username, count):
    today = datetime.now().strftime("%Y-%m-%d")

    # If file doesn't exist, create with header
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Username", "ProblemsSolved"])
        writer.writerow([today, username, count])


def load_users():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    users = load_users()
    submissions = get_recent_submissions(username)

    if submissions:
        users[username] = {
            "lastSubmission": submissions[0]["title"],
            "lastCheck": str(datetime.now().date()),
            "problemsSolvedToday": 0
        }
        save_users(users)
        return jsonify({"success": True, "message": "User added"})
    return jsonify({"success": False, "message": "Error fetching user submissions"})

@app.route('/get_users')
def get_users():
    users = load_users()
    results = []

    for username, data in users.items():
        submissions = get_recent_submissions(username)
        count = 0
        for sub in submissions:
            if sub["title"] == data["lastSubmission"]:
                break
            count += 1

        results.append({
            "username": username,
            "solvedToday": count
        })
        users[username]["problemsSolvedToday"] = count

    save_users(users)
    return jsonify(results)

# Daily Reset at 12AM
def reset_daily_submissions():
    users = load_users()
    for username in users:
        submissions = get_recent_submissions(username)
        if submissions:
            users[username]["lastSubmission"] = submissions[0]["title"]
            users[username]["lastCheck"] = str(datetime.now().date())
            users[username]["problemsSolvedToday"] = 0
    save_users(users)
    print("Daily reset done.")

# Scheduler Setup
scheduler = BackgroundScheduler()
scheduler.add_job(reset_daily_submissions, 'cron', hour=0, minute=0)  # Every day at 12AM
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
