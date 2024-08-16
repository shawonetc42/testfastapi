from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# MongoDB কনফিগারেশন
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
        page = int(request.args.get('page', 1))  # পৃষ্ঠার সংখ্যা
        per_page = int(request.args.get('per_page', 10))  # প্রতি পৃষ্ঠায় কতগুলো আইটেম দেখাবে
        
        answers = []
        cursor = answers_collection.find().skip((page - 1) * per_page).limit(per_page)
        
        for answer in cursor:
            answer['_id'] = str(answer['_id'])
            answer['questionId'] = str(answer.get('questionId'))
            answers.append(answer)
        
        return jsonify(answers)
    except Exception as e:
        abort(500, description="Failed to fetch answers")

@app.route("/test", methods=["GET"])
def get_posts():
    try:
        # Get page and per_page query parameters
        page = int(request.args.get('page', 1))  # Default to page 1
        per_page = int(request.args.get('per_page', 10))  # Default to 10 items per page
        
        # Calculate the number of items to skip
        skip = (page - 1) * per_page
        
        # Use MongoDB aggregation to fetch posts with answers
        pipeline = [
            {"$skip": skip},
            {"$limit": per_page},
            {
                "$lookup": {
                    "from": "answers",
                    "localField": "_id",
                    "foreignField": "questionId",
                    "as": "answers"
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "title": 1,  # Assuming there's a 'title' field in the posts
                    "content": 1,  # Assuming there's a 'content' field in the posts
                    "user": 1,  # Assuming there's a 'created_at' field in the posts
                    "videoUrl": 1,  # Assuming there's a 'created_at' field in the posts
                    "questiontext": 1,  # Assuming there's a 'created_at' field in the posts
                    "userid": 1,  # Assuming there's a 'created_at' field in the posts
                    "username": 1,  # Assuming there's a 'created_at' field in the posts
                    "image": 1,  # Assuming there's a 'created_at' field in the posts
                    "uniqueId": 1,  # Assuming there's a 'created_at' field in the posts
                    "time": 1,  # Assuming there's a 'created_at' field in the posts
                    "answers._id": {"$toString": "$answers._id"},
                    "answers.questionId": {"$toString": "$answers.questionId"},
                    "answers.answerText": 1,
                    "answers.answeredBy": 1,
                    "answers.timestamp": 1,
                    "answers.answerUserPhoto": 1  # Include all necessary fields from answers
                }
            }
        ]
        
        posts = list(db.test.aggregate(pipeline))
        
        return jsonify(posts)
    except Exception as e:
        return jsonify({'error': 'Failed to fetch posts', 'details': str(e)}), 500


@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Hello World"})

if __name__ == "__main__":
    app.run(debug=True)
