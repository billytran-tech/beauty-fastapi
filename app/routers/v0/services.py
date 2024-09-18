import random
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Depends
from fastapi.encoders import jsonable_encoder
from app.config.config import settings
from app.schema.object_models.v0 import service_model
from app.auth.auth import Auth0, Auth0User
from app.config.database.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(
    prefix='/api/services',
    tags=['Products/Services']
)
auth = Auth0(domain=settings.AUTH0_DOMAIN,
             api_audience=settings.AUTH0_API_AUDIENCE, scopes={})


async def get_owner_details(owner_id: str, db: AsyncIOMotorDatabase):
    owner_details = await db['merchants'].find_one({"user_id": owner_id})
    owner_details = jsonable_encoder(owner_details)

    username = await db['usernames'].find_one({'user_id': owner_id})
    username = jsonable_encoder(username).get('username')

    return service_model.ServiceOwner(username=username, **owner_details)


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=service_model.ProfileServiceResponse, dependencies=[Depends(auth.implicit_scheme)])
async def create_service(payload: service_model.CreateService, user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):

    merchant = await db['merchants'].find_one({"user_id": user_profile.id})
    if not merchant:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have a business profile activated yet. You cannot add a service.")

    payload = jsonable_encoder(payload)
    payload["owner_id"] = user_profile.id

    new_service = await db['services'].insert_one(payload)
    created_service = await db['services'].find_one({"_id": new_service.inserted_id})
    return jsonable_encoder(created_service)


@router.get('/', response_model=List[service_model.ServiceResponse])
async def get_all_services(db: AsyncIOMotorDatabase = Depends(get_db)):
    services = await db['services'].find().to_list(length=None)
    for service in services:
        service['owner'] = await get_owner_details(service.get('owner_id'), db)

    return services


@router.get("/get_my_services", status_code=status.HTTP_200_OK, response_model=List[service_model.ProfileServiceResponse])
async def get_my_services(user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    services = await db['services'].find({"owner_id": user_profile.id}).to_list(length=None)
    return jsonable_encoder(services)


def build_service_query(service_name, min_price, max_price):
    query = {}
    if service_name:
        query["description"] = {"$regex": service_name, "$options": "i"}
    if min_price is not None:
        query["price.amount"] = {"$gte": min_price}
    if max_price is not None:
        query["price.amount"] = {"$lte": max_price}
    return query


def build_location_query(country, city):
    query = {}
    if country:
        query["owner.location.country"] = country.capitalize()
    if city:
        query["owner.location.city"] = city.capitalize()
    return query


def build_aggregation_pipeline(service_query, user_location_query, page, per_page):
    return [
        {
            "$lookup": {
                "from": "merchants",
                "localField": "owner_id",
                "foreignField": "user_id",  # Use "_id" to match the users collection
                "as": "owner"
            }
        },
        {
            "$lookup": {
                "from": "usernames",
                "localField": "owner_id",
                "foreignField": "user_id",
                "as": "username"
            }
        },
        {
            "$unwind": "$username"
        },
        {
            "$unwind": "$owner"
        },
        {
            "$match": user_location_query  # Filter based on user location
        },
        {
            "$match": service_query  # Filter based on service criteria
        },
        {
            "$skip": (page - 1) * per_page
        },
        {
            "$limit": per_page
        }
    ]


def format_service_results(results):
    formatted_results = []
    for item in results:
        owner_info = None  # Initialize owner_info to None

        if "owner" in item:
            if not item.get('owner').get('public'):
                continue

            owner_info = {
                "username": item["username"]["username"],
                "name": item.get('owner').get("name"),
                "profile_image_url": item.get('owner').get("profile_image_url"),
                "profession": item.get('owner').get("profession"),
                "location": item.get('owner').get("location")
            }

        transformed_item = {
            "_id": item.get("_id", ""),
            "service_name": item.get("service_name", ""),
            "duration": item.get("duration", ""),
            "out_call": item.get("out_call", ""),
            "description": item.get("description", ""),
            "customisation": item.get("customisation", ""),
            "owner": owner_info,  # Use the owner_info obtained above
            "images": item.get("images", []),
            "price": item.get("price", "")
        }

        formatted_results.append(transformed_item)
        random.shuffle(formatted_results)
    return formatted_results


@router.get("/search-services", response_model=List[service_model.ServiceResponse])
async def filter_services(service_name: str = None, min_price: float = None, max_price: float = None,
                          country: str = None, city: str = None, page: int = 1, per_page: int = 10, db: AsyncIOMotorDatabase = Depends(get_db)):
    service_query = build_service_query(service_name, min_price, max_price)
    user_location_query = build_location_query(country, city)
    pipeline = build_aggregation_pipeline(
        service_query, user_location_query, page, per_page)

    results = await db['services'].aggregate(pipeline).to_list(length=None)
    return format_service_results(results)


@router.get("/get/{service_id}", status_code=status.HTTP_200_OK, response_model=service_model.ServiceResponse)
async def get_service(service_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    service = await db['services'].find_one({"_id": service_id})
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

    owner = await get_owner_details(service["owner_id"], db)
    service = jsonable_encoder(service)
    service["owner"] = owner
    return service


@router.put("/update/{service_id}", status_code=status.HTTP_200_OK, response_model=service_model.ProfileServiceResponse, dependencies=[Depends(auth.implicit_scheme)])
async def update_service(service_id: str, payload: service_model.UpdateService, user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    service = await db['services'].find_one({"_id": service_id})
    if not service or service["owner_id"] != user_profile.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized or service not found")

    updated_service = await db['services'].update_one({"_id": service_id}, {"$set": jsonable_encoder(payload)})
    if updated_service.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

    updated_service = await db['services'].find_one({"_id": service_id})
    updated_service = jsonable_encoder(updated_service)
    owner = await get_owner_details(updated_service["owner_id"], db)
    updated_service["owner"] = owner
    return updated_service


@router.delete("/delete/{service_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(auth.implicit_scheme)])
async def delete_service(service_id: str, user_profile: Auth0User = Depends(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    service = await db['services'].find_one({"_id": service_id})
    if not service or service["owner_id"] != user_profile.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized or service not found")

    await db['services'].delete_one({"_id": service_id})
    return {"message": "Service deleted successfully."}
