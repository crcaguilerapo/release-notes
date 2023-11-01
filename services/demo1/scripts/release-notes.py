import os
import requests

REPO = os.getenv("CIRCLE_PROJECT_REPONAME")

if REPO is None:
    raise Exception("Not found CIRCLE_PROJECT_REPONAME")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if GITHUB_TOKEN is None:
    raise Exception("Not found GITHUB_TOKEN")

owner = "crcaguilerapo"
branch = "main"

url = f"https://api.github.com/repos/{owner}/{REPO}/releases"

datos = {
  "owner": owner,
  "repo": REPO,
  "tag_name": 'demo1 v1.0.0',
  "target_commitish": branch,
  "name": 'v1.0.0',
  "generate_release_notes": True,
}

respuesta = requests.post(url, json=datos, headers={"Authorization": f"token {GITHUB_TOKEN}"})

# Verificar el código de estado de la respuesta
if respuesta.status_code == 201:
    print(f"Tag creado correctamente en el repositorio '{REPO}'.")
else:
    print(f"Error al crear el tag. Código de estado: {respuesta.status_code}")
    print(respuesta.text)