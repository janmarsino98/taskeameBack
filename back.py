from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, ObjectId
from dotenv import load_dotenv
import os
from flask_cors import CORS
from flask_session import Session
from datetime import datetime
from flask_bcrypt import Bcrypt
import random
import re
import constants as c

load_dotenv()

app = Flask(__name__)

CORS(app)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
BACK_ADDRESS = os.getenv('BACK_ADDRESS')

mongo = PyMongo(app)

users_db = mongo.db.users
tasks_db = mongo.db.tasks
reviews_db = mongo.db.reviews


@app.route("/user", methods=["POST"])

def create_user():
    new_user = request.json
    required_fields = ["username", "name", "email", "password", "phone"]
    for field in required_fields:
        if field not in new_user:
            return jsonify({"message":"User could not be created beacuse there is some missing data..."}), 400

    if not re.search(c.USERNAME_PAT, new_user["username"]):
            return jsonify({"message": "The username can only contain alphabetical characters, _ or ."}), 400

    if len(new_user["username"]) < c.USERNAME_MIN_LEN or len(new_user["username"]) > c.USERNAME_MAX_LEN:
        return jsonify({"message": f"The username must be between {c.USERNAME_MIN_LEN} and {c.USERNAME_MAX_LEN} characters long."}), 400
    
    if not re.search(c.NAME_PAT, new_user["name"]):
        return jsonify({"message": "The name can only contain alphabetical characters, space or ."}), 400
    
    if len(new_user["name"]) < c.NAME_MIN_LEN or len(new_user["name"]) > c.NAME_MAX_LEN:
        return jsonify({"message": f"The name must be between {c.NAME_MIN_LEN} and {c.NAME_MAX_LEN} characters long."}), 400
    
    if not re.search(c.EMAIL_PAT, new_user["email"]):
        return jsonify({"message": "The email is not valid."}), 400
    
    if len(new_user["email"]) < c.EMAIL_MIN_LEN or len(new_user["email"]) > c.EMAIL_MAX_LEN:
        return jsonify({"message": f"The email must be between {c.EMAIL_MIN_LEN} and {c.EMAIL_MAX_LEN} characters long."}), 400
    
    if not re.search(c.PASSWORD_PAT, new_user["password"]):
        return jsonify({"message": "The password is not valid."}), 400
    
    if len(new_user["password"]) < c.PASSWORD_MIN_LEN or len(new_user["password"]) > c.PASSWORD_MAX_LEN:
        return jsonify({"message": f"The password must be between {c.PASSWORD_MIN_LEN} and {c.PASSWORD_MAX_LEN} characters long."}), 400
    
    if users_db.find_one({
        "username": new_user["username"]
    }) or users_db.find_one({
        "email": new_user["email"]
    }) or users_db.find_one({
        "phone": new_user["phone"]
    }):
        return jsonify({"message": "A user with the same username, email or phone already exists"}), 201

        
    users_db.insert_one({
        "username": new_user["username"],
        "name": new_user["name"],
        "email": new_user["email"],
        "password": new_user["password"],
        "phone": new_user["phone"],
        "created_at": datetime.utcnow(),
        "verified": False,
        "avg_review_score": None,
    })
    
    return jsonify(new_user), 200
    

@app.route("/user/<username>", methods=["GET"]) 
def get_user(username):
    user = users_db.find_one({"username": username})
    if not user:
        return jsonify({"message": "No user found with the specified username"}), 404
    else:
        user["_id"] = str(user["_id"])  
        return jsonify(user), 200


@app.route("/user/<username>", methods=["DELETE"])   
def delete_user(username):
    result = users_db.delete_one({"username": username})
    if result.deleted_count == 1:
        return '', 204
    else:
        return jsonify({"message": "No user found with the specified username"}), 404


@app.route("/verify_user/<username>", methods=["PUT"])
def verify_user(username):
    result = users_db.update_one({"username":username},{"$set": {"verified": True}})
    if result.matched_count == 1:
        return '', 201
    
    else:
        return jsonify({"message": "There is no user with the specified username"}), 404

@app.route("/review_user", methods=["POST"])
def review_user():
    mandatory_field = ["reviewer_username", "reviewed_username", "task_id", "rating","comment"]
    data = request.json
    for field in mandatory_field:
        if field not in data:
            return jsonify({"message":f"You must specify {field}"})
        
    if not (0<=data["rating"]<=5):
        return jsonify({"message": "Your rating must be a number between 0 and 5"})
    
    if not re.search(c.COMMENT_PAT, data["comment"]):
        return jsonify({"message": "The comment can only contain alpha characters."})
    
    if c.COMMENT_MIN_LEN > len(data["comment"]) or c.COMMENT_MAX_LEN < len(data["comment"]):
        return jsonify({"message": f"The comment must have at least {c.COMMENT_MIN_LEN} and at most {c.COMMENT_MAX_LEN} characters."})
        
    if not reviews_db.find_one({
        "task_id": data["task_id"], 
        "reviewer_username": data["reviewer_username"],
        "reviewed_username": data["reviewed_username"] 
        }):
        reviews_db.insert_one(
            {
                "reviewer_username": data["reviewer_username"],
                "reviewed_username": data["reviewed_username"],
                "task_id": data["task_id"],
                "rating": data["rating"],
                "comment": data["comment"],
            }
        )

        return jsonify(""), 200
    
    return jsonify({"message": "Tasker already rated by this user for this task"}), 400

@app.route("/task", methods=["POST"])
def create_task():
    mandatory_fields = ["title", "description", "compensation", "requester_username"]
    data = request.json
    for field in mandatory_fields:
        if field not in data:
            return jsonify({"message": f"You must specify {field} to create a task."})

    if not re.search(c.TITLE_PAT, data["title"]):
        return jsonify({"message": "The title contains forbidden characters."})
    
    if c.TITLE_MIN_LEN > len(data["title"]) or c.TITLE_MAX_LEN < len(data["title"]):
        return jsonify({"message": f"The title must have at least {c.TITLE_MIN_LEN} and at most {c.TITLE_MAX_LEN} characters."})
        
    if not re.search(c.DESCRIPTION_PAT, data["title"]):
        return jsonify({"message": "The description contains forbidden characters."})
    
    if c.DESCRIPTION_MIN_LEN > len(data["description"]) or c.DESCRIPTION_MAX_LEN < len(data["description"]):
        return jsonify({"message": f"The description must have at least {c.DESCRIPTION_MIN_LEN} and at most {c.DESCRIPTION_MAX_LEN} characters."})
        
    try:
        compensation = float(data["compensation"])
        if compensation <= 0:
            return jsonify({"message": "The compensation must be a positive number"}), 409
        
    except:
        return jsonify({"message": "The compensation must be a decimal number"})
    
    if not users_db.find_one({"username": data["requester_username"]}):
        return jsonify({"message": "The requester was not find in the users DB."})
    
    data["state"] = "pending"
    data["limit_day"] = None
    data["tasker_username"] = None
    data["location"] = None
    
    tasks_db.insert_one(
        data
        )
    
    return jsonify(""), 200
        
@app.route("/task/<task_id>", methods=["GET"])
def get_task(task_id):
    task = tasks_db.find_one({"_id": ObjectId(task_id)})
    if not task:
        return jsonify({"message": "Task not found"}), 404
    else:
        task["_id"] = str(task["_id"])
        return jsonify(task), 200
        
if __name__ == '__main__':
    app.run(debug=True)