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
    headers = {
        'Authorization': f'token {token}'
    }
    
    url = f'https://api.github.com/repos/{owner}/{repo}/git/refs/tags'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        tags = response.json()
        last_tag = tags[0]["ref"].split("/")[-1]
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
        "body": body
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
        print(f"Error: {response.status_code} - {response.text}")


def get_body(token, owner, repo, pull_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"

    response = requests.get(url, headers={"Authorization": f"token {token}"})

    if response.status_code == 200:
        response = response.json()
        return response["body"]
    else:
        print(f"Error: {response.status_code} - {response.text}")

version = get_version(GITHUB_TOKEN, owner, REPO)
pr_number = get_pull_request(GITHUB_TOKEN, owner, REPO, COMMIT)
body = get_body(GITHUB_TOKEN, owner, REPO, pr_number)
create_release(GITHUB_TOKEN, owner, REPO, branch, version, body)