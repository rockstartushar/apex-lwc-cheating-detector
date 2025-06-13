from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
import os
import gitlab
from backend.gitlab_utils import (
    get_trainees,
    get_branches,
    get_files
)
from backend.similarity_checker import compare_similarity

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def get_gitlab_instance():
    url = session.get("gitlab_url")
    token = session.get("gitlab_token")

    if not url or not token:
        return None

    try:
        gl = gitlab.Gitlab(url, private_token=token)
        gl.auth()
        return gl
    except Exception as e:
        print("❌ Error initializing GitLab session:", e)
        return None


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    url = data.get("url")
    token = data.get("token")

    try:
        gl = gitlab.Gitlab(url, private_token=token)
        gl.auth()
        session['gitlab_url'] = url
        session['gitlab_token'] = token
        return jsonify({"success": True, "message": "Login successful"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/trainees", methods=["POST"])
def trainees():
    gl = get_gitlab_instance()
    if not gl:
        return jsonify({"error": "GitLab not initialized"}), 400

    return jsonify(get_trainees(gl))


@app.route("/api/branches/<int:project_id>", methods=["GET"])
def branches(project_id):
    gl = get_gitlab_instance()
    if not gl:
        return jsonify({"error": "GitLab not initialized"}), 400

    return jsonify(get_branches(gl, project_id))


@app.route("/api/files/<int:project_id>/<path:branch>", methods=["GET"])
def files(project_id, branch):
    gl = get_gitlab_instance()
    if not gl:
        return jsonify({"error": "GitLab not initialized"}), 400

    return jsonify(get_files(gl, project_id, branch))

@app.route("/api/save-config", methods=["POST"])
def similarity():
    gl = get_gitlab_instance()
    if not gl:
        return jsonify({"error": "GitLab not initialized"}), 400

    config = request.get_json()
    return jsonify(compare_similarity(gl, config))


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
