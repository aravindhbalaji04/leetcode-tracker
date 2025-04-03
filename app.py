from flask import Flask, render_template, request
import pandas as pd
from leetcode_scraper import get_leetcode_stats, get_all_user_stats  # Import scraper function

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = get_all_user_stats()  # Fetch stats for predefined usernames

    if request.method == "POST":
        usernames = request.form.get("usernames").split(",")
        for username in usernames:
            username = username.strip()
            if username:
                results.append(get_leetcode_stats(username))  # Add new users dynamically

    return render_template("index.html", results=results)

@app.route("/export", methods=["POST"])
def export():
    data = get_all_user_stats()
    df = pd.DataFrame(data)
    df.to_excel("leetcode_stats.xlsx", index=False)
    return "Excel file exported successfully!", 200

if __name__ == "__main__":
    app.run(debug=True)
