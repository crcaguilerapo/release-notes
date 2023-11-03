import os
import requests
import json

REPO = os.getenv("CIRCLE_PROJECT_REPONAME")

if REPO is None:
    raise Exception("Not found CIRCLE_PROJECT_REPONAME")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if GITHUB_TOKEN is None:
    raise Exception("Not found GITHUB_TOKEN")

COMMIT = os.getenv("CIRCLE_SHA1")
if COMMIT is None:
    raise Exception("Not found CIRCLE_SHA1")

owner = "crcaguilerapo"
branch = "main"


def get_version(token, owner, repo):
    headers = {"Authorization": f"token {token}"}

    url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/tags"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        tags = response.json()
        last_tag = tags[-1]["ref"].split("/")[-1]
        return last_tag
    elif response.status_code == 404:
        return "0"
    else:
        print(f"Error getting tags: {response.status_code}")


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


def get_pull_request(token, owner, repo, commit):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit}/pulls"

    response = requests.get(url, headers={"Authorization": f"token {token}"})

    if response.status_code == 200:
        pull_requests = response.json()
        return pull_requests[0]["number"]
    else:
        print(f"Error getting PR number: {response.status_code} - {response.text}")


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


version = get_version(GITHUB_TOKEN, owner, REPO)
pr_number = get_pull_request(GITHUB_TOKEN, owner, REPO, COMMIT)
body = get_body(GITHUB_TOKEN, owner, REPO, pr_number)

changelog_text = "Changelog\n\n"
for folder in ["services/demo1", "services/demo2"]:
    commits = get_commits_by_folder(GITHUB_TOKEN, owner, REPO, pr_number, folder)
    changelog_text += f"- {folder}:\n"
    for commit in commits:
        changelog_text += f"  - {commit}\n"

create_release(GITHUB_TOKEN, owner, REPO, branch, version, body + changelog)
