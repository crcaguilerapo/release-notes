import os
import requests
import subprocess


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


print("SHELL: ", subprocess.check_output("ls -l", shell=True).decode())
print("SHELL: ", subprocess.check_output("pwd", shell=True).decode())