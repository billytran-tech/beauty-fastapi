import motor.motor_asyncio
import certifi
from pymongo.server_api import ServerApi
from app.config.config import settings

# Global variables for MongoDB client and collections
client = None
database = None
collections = {}


def create_index(collection, field, unique=False, sparse=False):
    """
    Create an index for a MongoDB collection.

    Args:
        collection (Collection): The MongoDB collection.
        field (str or list): The field or fields to index.
        unique (bool, optional): If set to True, creates a unique index. Defaults to False.
        sparse (bool, optional): If set to True, creates a sparse index. Defaults to False.
    """
    collection.create_index(field, unique=unique, sparse=sparse)


def connect_to_database():
    global client, database, collections

    ca = certifi.where()
    db_url = settings.DB_URL
    db_name = settings.DB_NAME

    client = motor.motor_asyncio.AsyncIOMotorClient(
        db_url, tlsCAFile=ca, server_api=ServerApi('1'))
    database = client[db_name]

    # Initialize collections
    collections = {
        "usernames": database["usernames"],
        "merchants": database["merchants"],
        "customers": database["customers"],
        "services": database["services"],
        "bookings": database["bookings"],
        "transactions": database["transactions"],
    }

    # Create indexes
    create_index(collections["usernames"], "username", unique=True)
    create_index(collections["merchants"], [
                 ("username_id", 1)], unique=True, sparse=True)
    create_index(collections["merchants"], [("auth0id", 1)], unique=True)
    create_index(collections["merchants"],
                 "profiles.username", unique=True, sparse=True)
    create_index(collections["customers"], [("auth0id", 1)], unique=True)
    create_index(collections["bookings"], "merchant_id")
    create_index(collections["bookings"], "customer_id")
    create_index(collections["transactions"], "booking_id")


def close_database_connection():
    client.close()
