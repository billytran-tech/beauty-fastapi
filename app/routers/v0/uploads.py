from datetime import datetime, timedelta
from random import randbytes
import hashlib
from typing import Annotated, List
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from fastapi import APIRouter, Request, Response, Security, status, Depends, HTTPException, UploadFile, File
from fastapi.encoders import jsonable_encoder

# from app.auth import oauth2, utils
from app.config.config import settings

# from app.models import user_auth, merchant_models
from app.config.database.database import get_db

# from app.email.helpers.email import send_mail
from app.auth.auth import Auth0, Auth0User
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient

auth0_domain = settings.AUTH0_DOMAIN
auth0_api_audience = settings.AUTH0_API_AUDIENCE
auth = Auth0(domain=auth0_domain, api_audience=auth0_api_audience, scopes={})

router = APIRouter(
    prefix='/api/uploads',
    tags=['Image Uploads']
)


def get_blob_service_client():
    try:
        connect_str = settings.AZURE_STORAGE_CONNECTION_STRING
        return BlobServiceClient.from_connection_string(connect_str)
    except AzureError as azure_error:
        # Handle Azure-specific exceptions here
        print(f"An Azure error occurred: {azure_error}")
        # You can choose to log the error, raise a custom exception, or take other actions as needed
        return None  # Return None or raise a custom exception depending on your requirements


container_name = settings.IMAGE_CONTAINER_NAME


async def get_merchant_id(user_id: str, db: AsyncIOMotorDatabase):
    user = await db['merchants'].find_one({'user_id': user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = jsonable_encoder(user)
    return user['_id']


@router.post('/merchant/profile_image/', status_code=status.HTTP_200_OK)
async def upload_profile_image(user_profile: Auth0User = Security(auth.get_user), image: UploadFile = File(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        blob_service_client = get_blob_service_client()
        user_id = await get_merchant_id(user_profile.id, db)
        renamed_file = f"SB{datetime.now().strftime('%Y%m%d%H%M%S')}{randbytes(4).hex()}{image.filename.strip().replace(' ', '_')}"
        file_name = f"{user_id}/profile/{renamed_file}"
        with blob_service_client.get_blob_client(container=container_name, blob=file_name) as blob_client:
            blob_client.upload_blob(image.file, overwrite=True)

        image_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{file_name}"
        # print(image_url)
        updated_account = await db['merchants'].update_one({'user_id': user_profile.id}, {'$set': {'profile_image_url': image_url}})

        if updated_account.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED, detail="Profile image not updated")
        if updated_account.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        return {
            "message": "Profile Image Updated Successfully!",
            "URL": image_url
        }
    except AzureError as azure_error:
        # Handle Azure-specific exceptions here
        print(f"An Azure error occurred: {azure_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{azure_error}")
    except Exception as e:
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")
        raise e


@router.post("/upload/service/")
async def upload_service_images(user_profile: Auth0User = Security(auth.get_user), images: List[UploadFile] = File(...), db: AsyncIOMotorDatabase = Depends(get_db)):

    try:
        blob_service_client = get_blob_service_client()
        directory_name = "services"  # Specify the name of the directory
        user_id = await get_merchant_id(user_profile.id, db)
        image_urls = []
        directory_name = f"{user_id}/services"
        for image in images:
            # renamed_file = image.filename.strip().replace(" ", "_")
            renamed_file = f"SB{datetime.now().strftime('%Y%m%d%H%M%S')}{randbytes(4).hex()}{image.filename.strip().replace(' ', '_')}"
            blob_name = f"{directory_name}/{renamed_file}"
            with blob_service_client.get_blob_client(container=container_name, blob=blob_name) as blob_client:
                blob_client.upload_blob(image.file, overwrite=True)
            image_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"
            image_urls.append(image_url)

        return {"image_urls": image_urls}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")


# @router.post("/upload/intro-video/")
# async def upload_intro_video(authProfile: Auth0User = Security(auth.get_user), video: UploadFile = File(...)):

#     try:
#         blob_video_client = get_blob_service_client()
#         directory_name = "intro-videos"  # Specify the name of the directory
#         user_id = 'tshiamo_test'
#         video_url = None
#         directory_name = f"{user_id}/intro-videos"

#         renamed_file = f"SB{datetime.now().strftime('%Y%m%d%H%M%S')}{randbytes(4).hex()}{video.filename.strip().replace(' ', '_')}"
#         blob_name = f"{directory_name}/{renamed_file}"

#         with blob_video_client.get_blob_client(container=container_name, blob=blob_name) as blob_client:
#             blob_client.upload_blob(video.file, overwrite=True)

#         video_url = f"https://{blob_video_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"

#         updated_account = await collections['merchants'].update_one({'auth0id': authProfile.id}, {'$set': {'intro_video_url': video_url}})

#         if updated_account.modified_count == 0:
#             raise HTTPException(
#                 status_code=status.HTTP_304_NOT_MODIFIED, detail="Profile image not updated")
#         if updated_account.matched_count == 0:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

#         return {
#             "message": "Profile Video Updated Successfully!",
#             "URL": video_url
#         }

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")
