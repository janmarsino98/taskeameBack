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


@app.route("/user", methods=["POST"])

def create_user():
    new_user = request.json
    if not new_user["username"] or not new_user["name"] or not new_user["email"] or not new_user["password"] or not new_user["phone"]:
        return jsonify({"message":"User could not be created beacuse there is some missing data..."})

    if not re.search(c.USERNAME_PAT, new_user["username"]):
        return jsonify({
            "message": "The username can only contain alpahbetical characters, _ or ."
        })
    
    if len(new_user["username"]) < c.USERNAME_MIN_LEN or len(new_user["username"]) > c.USERNAME_MAX_LEN:
        return jsonify({
            "message": f"The username must be between {c.USERNAME_MIN_LEN} and {c.USERNAME_MAX_LEN} characters long."
        })
        
    if not re.search(c.NAME_PAT, new_user["name"]):
        return jsonify({
            "message": "The name can only contain alpahbetical characters, space or ."
        })
    
    if len(new_user["name"]) < c.NAME_MIN_LEN or len(new_user["name"]) > c.NAME_MAX_LEN:
        return jsonify({
            "message": f"The name must be between {c.NAME_MIN_LEN} and {c.NAME_MAX_LEN} characters long."
        })
        
    if not re.search(c.EMAIL_PAT, new_user["email"]):
        return jsonify({
            "message": "The email can only contain alpahbetical characters, space or ."
        })
    
    if len(new_user["email"]) < c.EMAIL_MIN_LEN or len(new_user["email"]) > c.EMAIL_MAX_LEN:
        return jsonify({
            "message": f"The email must be between {c.EMAIL_MIN_LEN} and {c.EMAIL_MAX_LEN} characters long."
        })
        
    if not re.search(c.PASSWORD_PAT, new_user["password"]):
        return jsonify({
            "message": "The password can only contain alpahbetical characters, space or ."
        })
    
    if len(new_user["password"]) < c.PASSWORD_MIN_LEN or len(new_user["password"]) > c.PASSWORD_MAX_LEN:
        return jsonify({
            "message": f"The password must be between {c.PASSWORD_MIN_LEN} and {c.PASSWORD_MAX_LEN} characters long."
        })
        
    users_db.insert_one({
        "username": new_user["username"],
        "name": new_user["name"],
        "email": new_user["email"],
        "password": new_user["password"],
        "created_at": datetime.utcnow()
    })
    
    
        
        

if __name__ == '__main__':
    app.run(debug=True)