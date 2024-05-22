from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from config import config

client = MongoClient(config.MONGO_DB_URL, server_api=ServerApi("1"))

try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.recommend
user_item = db["user_item"]
post_categories = db["post_categories"]