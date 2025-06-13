from flask import Flask, request, jsonify
from backend.gitlab_utils import (
    init_gitlab_connection,
    get_trainees,
    get_branches,
    get_files
)
from backend.similarity_checker import compare_similarity

app = Flask(__name__)

@app.route("/")
def home():
    return "🔍 Apex Code Similarity Checker is running!", 200


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    url = data.get("url")
    token = data.get("token")

    success, message = init_gitlab_connection(url, token)
    return jsonify({"success": success, "message": message})


@app.route("/api/trainees", methods=["POST"])
def trainees():
    data = request.get_json()
    token = data.get("token")
    gl = ''
    if not gl:
        return jsonify({"error": "GitLab not initialized"}), 400

    return jsonify(get_trainees(token))


@app.route("/api/branches", methods=["POST"])
def branches():
    data = request.get_json()
    token = data.get("token")
    project_id = data.get("project_id")

    return jsonify(get_branches(token, project_id))


@app.route("/api/files", methods=["POST"])
def files():
    data = request.get_json()
    token = data.get("token")
    project_id = data.get("project_id")
    branch = data.get("branch")

    return jsonify(get_files(token, project_id, branch))


@app.route("/api/similarity", methods=["POST"])
def similarity():
    config = request.get_json()
    return jsonify(compare_similarity(config))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
