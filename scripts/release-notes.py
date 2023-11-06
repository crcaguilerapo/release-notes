import os
import requests
import utils

REPO = os.getenv("CIRCLE_PROJECT_REPONAME")

if REPO is None:
    raise Exception("CIRCLE_PROJECT_REPONAME not found")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if GITHUB_TOKEN is None:
    raise Exception("GITHUB_TOKEN not found ")

COMMIT = os.getenv("CIRCLE_SHA1")
if COMMIT is None:
    raise Exception("CIRCLE_SHA1 not found")

owner = "crcaguilerapo"
branch = "main"


def create_release(token, owner, repo, branch, version_number, body):
    payload = {
        "owner": owner,
        "repo": repo,
        "tag_name": f"{version_number}",
        "target_commitish": branch,
        "name": f"{version_number}",
        "body": body,
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


def get_body(token, owner, repo, pull_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"

    response = requests.get(url, headers={"Authorization": f"token {token}"})

    if response.status_code == 200:
        response = response.json()
        return response["body"]
    else:
        print(f"Error obtaining the PR body: {response.status_code} - {response.text}")


def get_commits_by_folder(token, owner, repo, pull_request_number, folder):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_request_number}/commits"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    commits = response.json()

    modified_commits = []

    for commit in commits:
        sha = commit["sha"]
        commit_details_url = (
            f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
        )
        commit_details_response = requests.get(commit_details_url, headers=headers)
        commit_details = commit_details_response.json()

        modified_files = commit_details["files"]
        for file in modified_files:
            if folder in file["filename"]:
                modified_commits.append(sha)

    return modified_commits


version = utils.get_version(GITHUB_TOKEN, owner, REPO)
pr_number = utils.get_pull_request(GITHUB_TOKEN, owner, REPO, COMMIT)
body = get_body(GITHUB_TOKEN, owner, REPO, pr_number)

changelog_text = "\n\n### Changelog \n\n"
for folder in ["services/demo1", "services/demo2"]:
    commits = get_commits_by_folder(GITHUB_TOKEN, owner, REPO, pr_number, folder)
    changelog_text += f"- {folder}:\n"
    for commit in commits:
        changelog_text += f"  - {commit}\n"

create_release(GITHUB_TOKEN, owner, REPO, branch, version, body + changelog_text)
