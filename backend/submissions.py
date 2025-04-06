import requests

def get_recent_submissions(username):
    url = f"https://leetcode.com/graphql"
    headers = {
        "Content-Type": "application/json",
    }
    query = {
        "query": """
        query recentAcSubmissions($username: String!) {
            recentAcSubmissionList(username: $username) {
                title
                timestamp
            }
        }
        """,
        "variables": {
            "username": username
        }
    }

    res = requests.post(url, json=query, headers=headers)
    if res.status_code == 200:
        data = res.json()
        return data['data']['recentAcSubmissionList']
    return []
