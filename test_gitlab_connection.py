import os
from dotenv import load_dotenv
import gitlab

# Load environment
load_dotenv()

GITLAB_URL = os.getenv("GITLAB_URL")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")

try:
    print(f"🔌 Connecting to GitLab at {GITLAB_URL}...")
    gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)

    # 🔐 Explicitly authenticate
    gl.auth()  # Raises an exception if token is invalid

    user = gl.user  # Should now work after auth()

    print(f"✅ Connected as {user.name} ({user.username})")

    print("\n📁 Your Private Projects:")
    projects = gl.projects.list(visibility='private', owned=True, all=True)
    for i, p in enumerate(projects, 1):
        print(f"{i}. {p.name_with_namespace} (ID: {p.id})")

except Exception as e:
    print("❌ Connection failed:", str(e))
