import motor.motor_asyncio
import certifi
from pymongo.server_api import ServerApi
from app.config.config import settings


def create_collection_index(collection, field, unique=False, sparse=False):
    """
    Create an index for a MongoDB collection.

    Args:
        collection (Collection): The MongoDB collection.
        field (str or list): The field or fields to index.
        unique (bool, optional): If set to True, creates a unique index. Defaults to False.
        sparse (bool, optional): If set to True, creates a sparse index. Defaults to False.
    """
    collection.create_index(field, unique=unique, sparse=sparse)


def initiate_collections(db):
    collections = {
        "users": db["users"],
        "usernames": db["usernames"],
        "merchants": db["merchants"],
        "customers": db["customers"],
        "services": db["services"],
        "bookings": db["bookings"],
        "transactions": db["transactions"],
    }
    create_collection_index(collections["usernames"], "username", unique=True)
    create_collection_index(collections["merchants"], [
        ("username_id", 1)], unique=True, sparse=True)
    create_collection_index(collections["merchants"], [
                            ("user_id", 1)], unique=True)
    create_collection_index(collections["merchants"],
                            "profiles.username", unique=True, sparse=True)
    create_collection_index(collections["customers"], [
                            ("user_id", 1)], unique=True)
    create_collection_index(collections["bookings"], "merchant_id")
    create_collection_index(collections["bookings"], "customer_id")
    create_collection_index(collections["transactions"], "booking_id")

    create_collection_index(collections["users"], [(
        "contact_info.phone_number.dialing_code", 1), ("contact_info.phone_number.phone_number", 1)], unique=True)

    create_collection_index(collections["users"], [
                            ("user_id", 1)], unique=True)


def connect_db_client(db_url: str = settings.DB_URL):
    ca = certifi.where()
    client = motor.motor_asyncio.AsyncIOMotorClient(
        db_url, tlsCAFile=ca, server_api=ServerApi('1'))
    return client


def connect_to_database(db_name: str = settings.DB_NAME):
    client = connect_db_client()
    database = client[db_name]
    initiate_collections(database)
    return database


client = connect_db_client()
db = connect_to_database()


def get_db():
    return db


def get_db_client():
    return client


def get_db_name():
    return settings.DB_NAME
