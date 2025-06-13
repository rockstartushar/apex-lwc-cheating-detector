from flask import Flask, request, jsonify, render_template
from backend.gitlab_utils import (
    get_trainees,
    get_branches,
    get_files
)
from backend.similarity_checker import compare_similarity
import gitlab

app = Flask(__name__)
gl_instance = None  # Global GitLab object


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/api/login", methods=["POST"])
def login():
    global gl_instance
    data = request.get_json()
    url = data.get("url")
    token = data.get("token")

    try:
        gl = gitlab.Gitlab(url, private_token=token)
        gl.auth()
        gl_instance = gl
        return jsonify({"success": True, "message": "Login successful"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/trainees", methods=["GET"])
def trainees():
    global gl_instance
    if not gl_instance:
        return jsonify({"error": "GitLab not initialized"}), 400

    return jsonify(get_trainees(gl_instance))


@app.route("/api/branches/<int:project_id>", methods=["GET"])
def branches(project_id):
    global gl_instance
    if not gl_instance:
        return jsonify({"error": "GitLab not initialized"}), 400

    return jsonify(get_branches(gl_instance, project_id))


@app.route("/api/files/<int:project_id>/<branch>", methods=["GET"])
def files(project_id, branch):
    global gl_instance
    if not gl_instance:
        return jsonify({"error": "GitLab not initialized"}), 400

    return jsonify(get_files(gl_instance, project_id, branch))


@app.route("/api/save-config", methods=["POST"])
def similarity():
    config = request.get_json()
    return jsonify(compare_similarity(config))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
