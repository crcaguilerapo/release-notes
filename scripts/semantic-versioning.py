import json
import requests
import os

REPO = os.getenv("CIRCLE_PROJECT_REPONAME")

if REPO is None:
    raise Exception("Not found CIRCLE_PROJECT_REPONAME")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if GITHUB_TOKEN is None:
    raise Exception("Not found GITHUB_TOKEN")

COMMIT = os.getenv("CIRCLE_SHA1")
if COMMIT is None:
    raise Exception("Not found CIRCLE_SHA1")

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
    ref_data = {
        "ref": f"refs/tags/{tag_name}",
        "sha": tag_sha
    }

    response = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=ref_data
    )

    if response.status_code == 201:
        print(f"Tag {tag_name} y su referencia fueron creados exitosamente.")
    else:
        print(f"Error al crear el tag y su referencia. Código de estado: {response.status_code}")
        print(response.text)




owner = "crcaguilerapo"
version = get_version(GITHUB_TOKEN, owner, REPO)
tag = create_tag(GITHUB_TOKEN, owner, REPO, COMMIT, str (int (version) + 1))
create_ref(GITHUB_TOKEN, owner, REPO, str (int (version) + 1), tag)


    
