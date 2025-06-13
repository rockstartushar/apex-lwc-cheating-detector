from flask import Flask, request, jsonify, render_template
from backend.gitlab_utils import (
    init_gitlab_connection,
    get_trainees,
    get_branches,
    get_files
)
from backend.similarity_checker import compare_similarity

app = Flask(__name__)
gl = None  # Store the GitLab instance globally

@app.route("/")
def home():
    return render_template('index.html')


@app.route("/api/login", methods=["POST"])
def login():
    global gl
    data = request.get_json()
    url = data.get("url")
    token = data.get("token")

    success, message, connection = init_gitlab_connection(url, token)
    if success:
        gl = connection

    return jsonify({"success": success, "message": message})


@app.route("/api/trainees", methods=["POST"])
def trainees():
    global gl
    if not gl:
        return jsonify({"error": "GitLab not initialized"}), 400

    return jsonify(get_trainees(gl))


@app.route("/api/branches/<int:project_id>", methods=["GET"])
def branches(project_id):
    global gl
    if not gl:
        return jsonify({"error": "GitLab not initialized"}), 400

    return jsonify(get_branches(gl, project_id))


@app.route("/api/files/<int:project_id>/<branch>", methods=["GET"])
def files(project_id, branch):
    global gl
    if not gl:
        return jsonify({"error": "GitLab not initialized"}), 400

    return jsonify(get_files(gl, project_id, branch))


@app.route("/api/save-config", methods=["POST"])
def similarity():
    config = request.get_json()
    return jsonify(compare_similarity(config))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
