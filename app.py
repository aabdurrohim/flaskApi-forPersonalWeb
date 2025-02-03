from flask import Flask, jsonify, request
from flask_cors import CORS
from db import dbProject  # Assuming this is where your project data is
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # More robust CORS

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
    project = next((item for item in dbProject if item["id"] == project_id), None)
    if project:
        return jsonify(project)
    return jsonify({"error": "Project not found"}), 404

@app.route('/project', methods=['GET'])
def get_projects():
    auth = verify_api_key()
    if auth:
        return auth

    category = request.args.get('category')

    if category:
        filtered_projects = [project for project in dbProject if project.get("categories") == category]
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

if __name__ == '__main__':
    app.run()
