from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from api.tasks import create_task, get_task, list_tasks, assign_task, mark_task_done, cancel_task
from api.users import getorcreateuser

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["taskdb"]

@app.route("/")
def home():
    return jsonify({"message": "Backend API is running!"})


# ✅ Create task endpoint
@app.route("/create_task", methods=["POST"])
def api_create_task():
    data = request.json
    user = getorcreateuser(None, data.get("createdby"))
    task = create_task(
        user,
        None,
        data.get("title"),
        data.get("description"),
        data.get("priority", "medium"),
        data.get("deadline", None)
    )
    return jsonify({"message": "Task created", "task": task}), 201


# ✅ List tasks
@app.route("/tasks", methods=["GET"])
def api_list_tasks():
    tasks = list_tasks()
    return jsonify(tasks), 200


# ✅ Get task by ID
@app.route("/task/<task_id>", methods=["GET"])
def api_get_task(task_id):
    task = get_task(task_id)
    if task:
        return jsonify(task)
    else:
        return jsonify({"error": "Task not found"}), 404


# ✅ Cancel task
@app.route("/cancel_task", methods=["POST"])
def api_cancel_task():
    data = request.json
    user = getorcreateuser(None, data.get("cancelledby"))
    result = cancel_task(data.get("taskid"), user)
    return jsonify({"message": "Task cancelled", "task": result}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
