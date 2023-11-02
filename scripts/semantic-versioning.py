import json
import requests
import os
import random

REPO = os.getenv("CIRCLE_PROJECT_REPONAME")

if REPO is None:
    raise Exception("Not found CIRCLE_PROJECT_REPONAME")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if GITHUB_TOKEN is None:
    raise Exception("Not found GITHUB_TOKEN")

COMMIT = os.getenv("CIRCLE_SHA1")
if COMMIT is None:
    raise Exception("Not found CIRCLE_SHA1")


try:
    # Open the JSON file in read mode
    with open("file.json", "r") as file:
        # Load JSON content into a dictionary
        semantic_versioning = json.load(file)

    # Increment the 'version' property by 1
    semantic_versioning["version"] += 1
    semantic_versioning["release"] += random.choice([True, False])

    # Open the JSON file in write mode and save the updated data
    with open("file.json", "w") as file:
        json.dump(
            semantic_versioning, file, indent=4
        )  # indentation for better readability

    print("Version incremented successfully.")

    if semantic_versioning["release"]:
        # Create a tag on GitHub with the version number
        owner = "crcaguilerapo"
        version_number = semantic_versioning["version"]
        module_name = semantic_versioning["module"]

        # URL for the endpoint to create a tag on GitHub
        url = f"https://api.github.com/repos/{owner}/{REPO}/git/tags"

        # Create a tag object
        tag_object = {
            "tag": f"{module_name}/{version_number}",
            "message": f"Version {version_number}",
            "object": COMMIT,
            "type": "commit",
        }

        # Create the tag using the GitHub API
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        response = requests.post(url, headers=headers, json=tag_object)

        if response.status_code == 201:
            print(f"Tag created on GitHub: v{version_number}")
        else:
            print(f"Error creating tag on GitHub. Status code: {response.status_code}")

except FileNotFoundError:
    print("JSON file not found.")
