import requests

def get_version(token, owner, repo):
    headers = {"Authorization": f"token {token}"}

    url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/tags"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        tags = response.json()
        last_tag = tags[-1]["ref"].split("/")[-1]
        return last_tag
    elif response.status_code == 404:
        return "0.0.0"
    else:
        print(f"Error getting tags: {response.status_code}")

def get_pull_request(token, owner, repo, commit):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit}/pulls"

    response = requests.get(url, headers={"Authorization": f"token {token}"})

    if response.status_code == 200:
        pull_requests = response.json()
        if len(pull_requests) > 0:
            return pull_requests[0]["number"]
        else:
            raise Exception("PR on commit not found")
    else:
        print(f"Error getting PR number: {response.status_code} - {response.text}")