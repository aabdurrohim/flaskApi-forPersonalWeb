from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from db import dbProject  # Assuming this is where your project data is
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # More robust CORS

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
    return jsonify({
        "message": "Hello ab, welcome back!",
    })

@app.route('/project', methods=['POST'])
def add_project():
    auth = verify_api_key()
    if auth:
        return auth

    image = request.files.get('image')
    image_name = None

    if image and image.filename:
        image_name = image.filename
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
        try:
            image.save(image_path)
        except Exception as e:
            return jsonify({"error": "Image upload failed", "message": str(e)}), 500

    new_id = dbProject[-1]["id"] + 1 if dbProject else 1
    new_project = {
        "id": new_id,
        "title": request.form.get("title"),
        "image": f"/static/images/{image_name}" if image_name else None,
        "categories": request.form.get("categories"),
        "description": request.form.get("description")
    }
    dbProject.append(new_project)

    return jsonify({"message": "Project successfully added.", "project": new_project}), 201

@app.route('/project/<int:project_id>', methods=['GET'])
def get_project_byId(project_id):
    project = next((item for item in dbProject if item["id"] == project_id), None)
    if project:
        return jsonify(project)
    return jsonify({"error": "Project not found"}), 404

@app.route('/static/images/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    print(f"Server is running on port: {port}")
    app.run(debug=debug, port=port)