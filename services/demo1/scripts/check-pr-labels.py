import os
import subprocess

# Obtener la URL y el número del Pull Request
pr_list_output = subprocess.check_output(["gh", "pr", "list", "--state", "merged", "--search", "af1dcb84c0c0ea637550a27b9f77c5e8e309b485", "--json", "url,number", "--jq", ".[].url, .[].number"]).decode("utf-8").strip().splitlines()
PR_URL, PR_NUMBER = pr_list_output[0], pr_list_output[1]

print(f"Pull Request Url: {PR_URL}")

# Obtener las etiquetas del Pull Request
pr_view_output = subprocess.check_output(["gh", "pr", "view", PR_URL, "--json", "labels", "--jq", ".labels[] | select((.name == \"breaking change\") or (.name == \"feature\") or (.name == \"fix\")) | .name"]).decode("utf-8").strip().splitlines()
LABELS = pr_view_output
NUMBER_OF_LABELS = len(LABELS)

if NUMBER_OF_LABELS == 1:
    print(f"Found: {LABELS[0]}")
    RELEASE_TYPE = LABELS[0]
    os.environ["RELEASE_TYPE"] = RELEASE_TYPE
elif NUMBER_OF_LABELS > 1:
    if "breaking change" in LABELS:
        print("Found: breaking change")
        RELEASE_TYPE = "breaking change"
        os.environ["RELEASE_TYPE"] = RELEASE_TYPE
    else:
        print(f"::error ::Too many release type labels: {' '.join(LABELS)}")
        exit(1)
else:
    RELEASE_TYPE = "no release"
    os.environ["RELEASE_TYPE"] = RELEASE_TYPE
    print("🚫 No release type labels found (breaking change/feature/fix)")

OUTPUT_FILES = "outputFiles"
os.makedirs(OUTPUT_FILES, exist_ok=True)
os.environ["OUTPUT_FILES"] = OUTPUT_FILES
os.environ["PR_NUMBER"] = PR_NUMBER