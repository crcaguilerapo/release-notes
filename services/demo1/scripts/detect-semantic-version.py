import os
import argparse
import requests

def detect_previous_version():
    print(os.environ['PACKAGE_NAME_MODULE'])
    query = '''
    query($owner: String!, $repo: String!, $refPrefix: String!) {
        repository(owner: $owner, name: $repo) {
            refs(refPrefix: $refPrefix, first: 1, orderBy: {field: TAG_COMMIT_DATE, direction: DESC}) {
                edges { node { name } }
            }
        }
    }
    '''

    variables = {
        'owner': os.environ['CIRCLE_PROJECT_USERNAME'],
        'repo': os.environ['CIRCLE_PROJECT_REPONAME'],
        'refPrefix': 'refs/tags/rel/' + os.environ['PACKAGE_NAME_MODULE']+'/'
    }
    headers = {
        'authorization': 'token ' + os.environ['GITHUB_TOKEN']
    }
    response = requests.post('https://api.github.com/graphql', 
                             json={'query': query, 'variables': variables}, 
                             headers=headers)
    result = response.json()
    prevNode = result['data']['repository']['refs']['edges'][0]
    prevVer = prevNode['node']['name'] if prevNode else '0.0.0'
    print('Found previous version', prevVer)
    with open(os.path.join(os.environ['OUTPUT_FILES'], 'previous-version.txt'), 'w', encoding='utf-8') as file:
        file.write(prevVer)

def detect_new_version():
    PREV_VERSION = os.environ['PREV_VERSION']
    RELEASE_TYPE = os.environ['RELEASE_TYPE']
    resultReleaseType = ""

    if RELEASE_TYPE == "breaking change":
        resultReleaseType = "major"
    elif RELEASE_TYPE == "feature":
        resultReleaseType = "minor"
    elif RELEASE_TYPE == "fix":
        resultReleaseType = "patch"
    else:
        resultReleaseType = "no release"
    
    numbers = PREV_VERSION.split('.')
    numberIdx = ['major', 'minor', 'patch'].index(resultReleaseType)
    numbers[numberIdx] = str(int(numbers[numberIdx]) + 1)
    for i in range(numberIdx + 1, len(numbers)):
        numbers[i] = '0'
    
    print('New version is', '.'.join(numbers))
    with open(os.path.join(os.environ['OUTPUT_FILES'], 'new-version.txt'), 'w', encoding='utf-8') as file:
        file.write('.'.join(numbers))

def extract_changelog_entry():
    headers = {
        'authorization': 'token ' + os.environ['GITHUB_TOKEN']
    }
    prInfo = requests.get("https://api.github.com/repos/" + 
                          os.environ['CIRCLE_PROJECT_USERNAME'] + "/" 
                          + os.environ['CIRCLE_PROJECT_REPONAME'] + "/pulls/" 
                          + os.environ['PR_NUMBER'], headers=headers).json()
    print(prInfo)
    print('PR body is:')
    print(prInfo['body'])

if __name__ == "_main_":
    parser = argparse.ArgumentParser()
    parser.add_argument("-function", type=str)
    args = parser.parse_args()
    if args.function == "detect_previous_version":
        detect_previous_version()
    elif args.function == "detect_new_version":
        detect_new_version()
    elif args.function == "extract_changelog_entry":
        extract_changelog_entry()