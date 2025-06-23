import base64

def get_trainees(gl):
    result = {}
    try:
        projects = gl.projects.list(visibility='private', owned=True, all=True)
        for project in projects:
            result[str(project.id)] = {
                "name": project.name_with_namespace,
                "project_name": project.name
            }
    except Exception as e:
        print("❌ Error fetching trainees:", str(e))
    return result


def get_branches(gl, project_id):
    try:
        project = gl.projects.get(project_id)
        branches = project.branches.list()
        return [b.name for b in branches]
    except Exception as e:
        print(f"❌ Error fetching branches for {project_id}:", e)
        return []


def get_files(gl, project_id, branch):
    allowed_extensions = ('.cls', '.trigger', '.js', '.html', '.css')
    excluded_dirs = ('.sfdx/', 'node_modules/', '__tests__/', 'test/', 'tests/', '__mockdata__/', '.github/', 'coverage/')

    try:
        project = gl.projects.get(project_id)
        files = project.repository_tree(ref=branch, recursive=True, get_all=True)
        
        filtered_files = []
        for f in files:
            path = f['path']
            if (
                f['type'] == 'blob' and
                path.endswith(allowed_extensions) and
                not path.startswith(excluded_dirs)
            ):
                filtered_files.append(path)
        
        return filtered_files

    except Exception as e:
        print(f"❌ Error fetching files from {project_id}/{branch}:", e)
        return []

def fetch_file_content(gl, project_id, branch, file_path):
    try:
        project = gl.projects.get(project_id)
        file = project.files.get(file_path=file_path, ref=branch)
        content = base64.b64decode(file.content).decode('utf-8', errors='ignore')
        return content
    except Exception as e:
        print(f"❌ Error fetching file content from {project_id}/{branch}/{file_path}:", e)
        return ""
