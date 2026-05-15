#!/usr/bin/env python3
"""Push CF IP results to GitHub"""

import requests
import json
import base64

GITHUB_TOKEN = ""  # Set via environment or config
GITHUB_OWNER = "chanriver"
GITHUB_REPO = "claude-cfip"
BRANCH = "main"
FILE_PATH = "cf-best-ips.json"

def main():
    # Read local file
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get current file SHA (if exists)
    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{FILE_PATH}"
    get_resp = requests.get(api_url, headers=headers)
    sha = None
    if get_resp.status_code == 200:
        sha = get_resp.json().get("sha")
        print(f"File exists, SHA: {sha}")
    elif get_resp.status_code == 404:
        print("File does not exist, will create new")
    else:
        print(f"Error checking file: {get_resp.status_code} {get_resp.text}")

    # Create or update file
    data = {
        "message": f"Update CF best IPs - {json.loads(content)['update_time']}",
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": BRANCH
    }
    if sha:
        data["sha"] = sha

    resp = requests.put(api_url, headers=headers, json=data)
    if resp.status_code in [200, 201]:
        print(f"Success! File pushed to https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/blob/{BRANCH}/{FILE_PATH}")
    else:
        print(f"Failed: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    main()