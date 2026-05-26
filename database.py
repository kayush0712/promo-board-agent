# backend/database.py

import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


MONGO_URL    = os.environ.get("MONGO_URL")
MONGO_DB     = os.environ.get("MONGO_DB_NAME", "promotion_review")

client = AsyncIOMotorClient(MONGO_URL)
db     = client[MONGO_DB]
reviews_collection = db["reviews"]


async def save_review_start(employee_id: str, employee_name: str):
    doc = {
        "_id":            employee_id,   # use employee_id as the unique key
        "employee_id":    employee_id,
        "employee_name":  employee_name,
        "status":         "in_progress",
        "started_at":     datetime.utcnow(),
        "completed_at":   None,
        "agent_outputs": {
            "harvester":   None,
            "advocate":    None,
            "evaluator":   None,
            "sentinel":    None,
            "orchestrator":None
        },
        "final_packet":   None,
        "human_decision": "pending",
        "human_comment":  "",
        "token_usage":    None
    }


    await reviews_collection.replace_one(
        {"_id": employee_id},
        doc,
        upsert=True
    )


async def save_agent_output(employee_id: str, agent_name: str, output: dict):

    await reviews_collection.update_one(
        {"_id": employee_id},
        {"$set": {
            f"agent_outputs.{agent_name}": output,
            "updated_at": datetime.utcnow()
        }}
    )


async def save_final_packet(employee_id: str, final_packet: dict, token_usage: dict):
    
    #Saves the AI's final recommendation Called after orchestrator completes.
    
    await reviews_collection.update_one(
        {"_id": employee_id},
        {"$set": {
            "final_packet": final_packet,
            "token_usage":  token_usage,
            "status":       "awaiting_decision",
            "updated_at":   datetime.utcnow()
        }}
    )



async def save_human_decision(employee_id: str, decision: str, comment: str):
   
    await reviews_collection.update_one(
        {"_id": employee_id},
        {"$set": {
            "human_decision": decision,
            "human_comment":  comment,
            "status":         "complete",
            "completed_at":   datetime.utcnow(),
            "updated_at":     datetime.utcnow()
        }}
    )




async def load_review(employee_id: str) -> dict | None:
    
    return await reviews_collection.find_one({"_id": employee_id})


async def load_all_active_reviews() -> list:
  
    cursor = reviews_collection.find({
        "status": {"$in": ["in_progress", "awaiting_decision"]}
    })
    return await cursor.to_list(length=100)




async def get_all_reviews(limit: int = 50) -> list:

    cursor = reviews_collection.find(
        {},
        {"employee_id": 1, "employee_name": 1, "status": 1,
         "human_decision": 1, "started_at": 1, "completed_at": 1,
         "final_packet.decision": 1, "final_packet.confidence": 1}
    ).sort("started_at", -1).limit(limit)

    return await cursor.to_list(length=limit)