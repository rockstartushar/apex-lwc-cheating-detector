import gitlab
import base64
gl = None  # Global GitLab object, initialized after login

def init_gitlab_connection(url, token):
    global gl
    try:
        print(f"🔌 Connecting to GitLab at {url}...")
        gl = gitlab.Gitlab(url, private_token=token)
        gl.auth()  # Raises error if auth fails
        user = gl.user
        print(f"✅ Connected as {user.name} ({user.username})")
        return True, f"Connected as {user.name} ({user.username})"
    except Exception as e:
        print("❌ Connection failed:", str(e))
        gl = None
        return False, str(e)

def is_connected():
    return gl is not None

def get_trainees():
    """Fetches all private projects owned by the current user."""
    result = {}
    if not gl:
        print("❌ GitLab not initialized.")
        return result
    try:
        projects = gl.projects.list(visibility='private', owned=True, all=True)
        for project in projects:
            result[str(project.id)] = {
                "name": project.name,
                "project_name": project.name_with_namespace
            }
    except Exception as e:
        print("❌ Error fetching trainees:", str(e))
    return result

def get_branches(project_id):
    if not gl:
        print("❌ GitLab not initialized.")
        return []
    try:
        project = gl.projects.get(project_id)
        branches = project.branches.list()
        return [b.name for b in branches]
    except Exception as e:
        print(f"❌ Error fetching branches for {project_id}:", e)
        return []

def get_files(project_id, branch):
    allowed_extensions = ('.cls', '.trigger', '.js', '.html', '.css')
    if not gl:
        print("❌ GitLab not initialized.")
        return []
    try:
        project = gl.projects.get(project_id)
        files = project.repository_tree(ref=branch, recursive=True, get_all=True)
        return [
            f['path'] for f in files
            if f['type'] == 'blob' and f['path'].endswith(allowed_extensions)
        ]
    except Exception as e:
        print(f"❌ Error fetching files from {project_id}/{branch}:", e)
        return []

def fetch_file_content(project_id, branch, file_path):
    if not gl:
        print("❌ GitLab not initialized.")
        return ""
    try:
        project = gl.projects.get(project_id)
        file = project.files.get(file_path=file_path, ref=branch)
        content = base64.b64decode(file.content).decode('utf-8', errors='ignore')
        return content
    except Exception as e:
        print(f"❌ Error fetching file content from {project_id}/{branch}/{file_path}:", e)
        return ""
