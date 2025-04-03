from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from db import dbProject  # Asumsikan ini adalah data proyek
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Konfigurasi CORS lebih fleksibel

load_dotenv()
API_KEY = os.getenv("API_KEY")

def verify_api_key():
    key = request.headers.get("X-API-KEY")
    if not key or key != API_KEY:
        return jsonify({"error": "Unauthorized", "message": "Invalid or missing API Key"}), 401
    return None

@app.route('/')
def index():
    auth = verify_api_key()
    if auth:
        return auth
    return jsonify({"message": "Hello ab, welcome back!"})

@app.route('/project/<int:project_id>', methods=['GET'])
def get_project_by_id(project_id):
    """
    Get a project by ID
    ---
    parameters:
      - name: project_id
        in: path
        type: integer
        required: true
        description: The ID of the project
    responses:
      200:
        description: A project object
      404:
        description: Project not found
    """
    project = next((item for item in dbProject if item["id"] == project_id), None)
    if project:
        return jsonify(project)
    return jsonify({"error": "Project not found"}), 404

@app.route('/project', methods=['GET'])
def get_projects():
    """
    Get all projects or filter by category
    ---
    parameters:
      - name: category
        in: query
        type: string
        required: false
        description: Filter projects by category
    responses:
      200:
        description: A list of projects
    """
    auth = verify_api_key()
    if auth:
        return auth

    category = request.args.get('category')

    if category:
        filtered_projects = [project for project in dbProject if category.lower() in project.get("categories", "").lower()]
        return jsonify({
            "message": f"Projects in category '{category}'.",
            "projects": filtered_projects
        }), 200

    return jsonify({
        "message": "All projects.",
        "projects": dbProject
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "message": "The requested resource could not be found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500

# **Swagger Configuration**
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={"app_name": "Personal Web API"})
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(debug=True)
