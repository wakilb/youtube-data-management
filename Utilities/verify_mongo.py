from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["youtube_comments"]
    collections = db.list_collection_names()
    print("MongoDB connection successful! Collections:", collections)

except Exception as e:
    print("MongoDB connection failed:", e)
