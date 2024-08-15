from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

app = FastAPI()

# MongoDB এর সাথে সংযোগ স্থাপন
client = AsyncIOMotorClient("mongodb+srv://shawondata:shawondata@cluster0.sigdzxx.mongodb.net/shawon?retryWrites=true&w=majority")
db = client.shawon
answers_collection = db.answers

@app.get("/answers/{id}")
async def get_answer(id: str):
    try:
        # _id কে ObjectId তে রূপান্তর করা
        object_id = ObjectId(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # MongoDB থেকে নির্দিষ্ট _id ব্যবহার করে ডেটা রিড করা
    answer = await answers_collection.find_one({"_id": object_id})
    
    if answer:
        # ObjectId কে স্ট্রিং এ রূপান্তর করা
        answer["_id"] = str(answer["_id"])
        answer["questionId"] = str(answer.get("questionId"))
        return answer
    else:
        # যদি ডেটা না পাওয়া যায়
        raise HTTPException(status_code=404, detail="Answer not found!")

@app.post("/answers")
async def create_answer(answer: dict):
    try:
        # MongoDB answers এ নতুন ডকুমেন্ট সংরক্ষণ করা
        answer["questionId"] = ObjectId(answer["questionId"])
        answer["timestamp"] = datetime.utcnow()
        result = await answers_collection.insert_one(answer)
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error inserting data")

@app.get('/answers')
async def get_answers():
    try:
        answers = []
        async for answer in answers_collection.find():
            answer['_id'] = str(answer['_id'])  # Convert ObjectId to string for JSON serialization
            answer['questionId'] = str(answer.get('questionId'))
            answers.append(answer)
        return answers
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch answers")

@app.get("/")
async def root():
    return {"message": "Hello World"}
