from flask import Flask, jsonify, request, render_template
from gitlab_utils import get_trainees, get_branches, get_files
from similarity_checker import compare_similarity
import os
from gitlab_utils import init_gitlab_connection

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATES_DIR)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/trainees', methods=['GET'])
def api_get_trainees():
    return jsonify(get_trainees())

@app.route('/api/branches/<int:project_id>', methods=['GET'])
def api_get_branches(project_id):
    return jsonify(get_branches(project_id))



@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    url = data.get("url")
    token = data.get("token")

    success, msg = init_gitlab_connection(url, token)
    return jsonify({"status": "success", "message": msg}) if success else jsonify({"status": "error", "message": msg})


# ✅ Use <path:branch_name> so feature/xyz works
@app.route('/api/files/<int:project_id>/<path:branch_name>', methods=['GET'])
def api_get_files(project_id, branch_name):
    return jsonify(get_files(project_id, branch_name))

@app.route('/api/save-config', methods=['POST'])
def api_save_config():
    data = request.get_json()
    result = compare_similarity(data)
    print("🔍 Similarity comparison results:", result )
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
