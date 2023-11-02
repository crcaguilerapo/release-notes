import os
import requests
import json

REPO = os.getenv("CIRCLE_PROJECT_REPONAME")

if REPO is None:
    raise Exception("Not found CIRCLE_PROJECT_REPONAME")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if GITHUB_TOKEN is None:
    raise Exception("Not found GITHUB_TOKEN")

OWNER = "crcaguilerapo"
BRANCH = "main"

try:
    # Open the JSON file in read mode
    with open("file.json", "r") as file:
        # Load JSON content into a dictionary
        semantic_versioning = json.load(file)

    version_number = semantic_versioning["version"]
    module_name = semantic_versioning["module"]

except FileNotFoundError:
    print("JSON file not found.")


def create_release(token, owner, repo, branch, module_name, version_number):
    payload = {
        "owner": owner,
        "repo": repo,
        "tag_name": f"{module_name}/{version_number}",
        "target_commitish": branch,
        "name": f"Release {module_name}/{version_number}",
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    respuesta = requests.post(
        url, json=payload, headers={"Authorization": f"token {token}"}
    )

    if respuesta.status_code == 201:
        print(f"Tag created successfully in the '{repo}' repository.")
    else:
        print(f"Error creating the tag. Status code: {respuesta.status_code}")
        print(respuesta.text)


def get_pull_request(token, owner, repo, commit):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit}/pulls"

    response = requests.get(url, headers={"Authorization": f"token {token}"})

    if response.status_code == 200:
        pull_requests = response.json()
        print(pull_requests)
    else:
        print(f"Error: {response.status_code} - {response.text}")


def get_comments(token, owner, repo, pull_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/comments"

    response = requests.get(url, headers={"Authorization": f"token {token}"})

    if response.status_code == 200:
        comments = response.json()
        print(comments)
    else:
        print(f"Error: {response.status_code} - {response.text}")
