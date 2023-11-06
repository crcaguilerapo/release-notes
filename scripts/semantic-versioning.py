import json
import requests
import os
import re
import utils

REPO = os.getenv("CIRCLE_PROJECT_REPONAME")

if REPO is None:
    raise Exception("CIRCLE_PROJECT_REPONAME not found")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if GITHUB_TOKEN is None:
    raise Exception("GITHUB_TOKEN not found")

COMMIT = os.getenv("CIRCLE_SHA1")
if COMMIT is None:
    raise Exception("CIRCLE_SHA1 not found")


def create_tag(token, owner, repo, commit, tag_name):
    # URL for the endpoint to create a tag on GitHub
    url = f"https://api.github.com/repos/{owner}/{repo}/git/tags"

    # Create a tag object
    tag_object = {
        "tag": tag_name,
        "message": f"Version {tag_name}",
        "object": commit,
        "type": "commit",
    }

    # Create the tag using the GitHub API
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers, json=tag_object)

    if response.status_code == 201:
        print(f"Tag created on GitHub: {tag_name}")
        return json.loads(response.text)["sha"]
    else:
        print(f"Error creating tag on GitHub. Status code: {response.status_code}")


def create_ref(token, owner, repo, tag_name, tag_sha):
    ref_data = {"ref": f"refs/tags/{tag_name}", "sha": tag_sha}

    response = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs",
        headers={"Authorization": f"Bearer {token}"},
        json=ref_data,
    )

    if response.status_code == 201:
        print(f"Tag {tag_name} adn ref created successfully")
    else:
        print(
            f"Error creating ref. State Code: {response.status_code}"
        )
        print(response.text)

def get_title(token, owner, repo, pull_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"

    response = requests.get(url, headers={"Authorization": f"token {token}"})

    if response.status_code == 200:
        response = response.json()
        return response["title"]
    else:
        print(f"Error obtaining the PR body: {response.status_code} - {response.text}")

def get_type(message):
    pattern = r'^(BREAKING CHANGE|feat|fix|chore|docs|style|refactor|perf|test)(\(.+\))?:\s(.+)$'
    match = re.match(pattern, message)
    if match:
        return match.group(1)
    return None

def generate_new_version(old_version, message):
    major, minor, patch = old_version.split(".")

    major = int(major)
    minor = int(minor)
    patch = int(patch)

    commit_type = get_type(message)
    if commit_type == 'BREAKING CHANGE':
        major += 1
    elif commit_type == 'feat':
        minor += 1
    elif commit_type == 'fix':
        patch += 1

    version = f"{major}.{minor}.{patch}"
    return version

owner = "crcaguilerapo"
old_version = utils.get_version(GITHUB_TOKEN, owner, REPO)
pr_number = utils.get_pull_request(GITHUB_TOKEN, owner, REPO, COMMIT)
title = get_title(GITHUB_TOKEN, owner, REPO, pr_number)
new_version = generate_new_version(old_version, title)
tag = create_tag(GITHUB_TOKEN, owner, REPO, COMMIT, new_version)
create_ref(GITHUB_TOKEN, owner, REPO, new_version, tag)
