from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)

# Initialize CORS
CORS(app)

# MongoDB configuration
client = MongoClient("mongodb+srv://shawondata:shawondata@cluster0.sigdzxx.mongodb.net/shawon?retryWrites=true&w=majority")
db = client.shawon
answers_collection = db.answers

@app.route("/answers/<id>", methods=["GET"])
def get_answer(id):
    try:
        object_id = ObjectId(id)
    except Exception:
        abort(400, description="Invalid ID format")
    
    answer = answers_collection.find_one({"_id": object_id})
    
    if answer:
        answer["_id"] = str(answer["_id"])
        answer["questionId"] = str(answer.get("questionId"))
        return jsonify(answer)
    else:
        abort(404, description="Answer not found!")

@app.route("/answers", methods=["POST"])
def create_answer():
    try:
        answer = request.json
        answer["questionId"] = ObjectId(answer["questionId"])
        answer["timestamp"] = datetime.utcnow()
        result = answers_collection.insert_one(answer)
        return jsonify({"inserted_id": str(result.inserted_id)})
    except Exception:
        abort(400, description="Error inserting data")

@app.route('/answers', methods=["GET"])
def get_answers():
    try:
        page = int(request.args.get('page', 1))  # Page number
        per_page = int(request.args.get('per_page', 10))  # Items per page
        
        answers = []
        cursor = answers_collection.find().skip((page - 1) * per_page).limit(per_page)
        
        for answer in cursor:
            answer['_id'] = str(answer['_id'])
            answer['questionId'] = str(answer.get('questionId'))
            answers.append(answer)
        
        return jsonify(answers)
    except Exception as e:
        abort(500, description="Failed to fetch answers")

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Hello World"})

if __name__ == "__main__":
    app.run(debug=True)
