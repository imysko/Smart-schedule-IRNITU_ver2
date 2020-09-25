from pymongo import MongoClient


client = MongoClient(
    host="localshost",
    port=27017,
    serverSelectionTimeMS=1000
)
client.server_info()

