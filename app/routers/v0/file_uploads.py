from datetime import datetime
from random import randbytes
import boto3
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.encoders import jsonable_encoder
from app.auth.auth import Auth0, Auth0User
from app.config.config import settings
from botocore.exceptions import ClientError
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database.database import get_db


auth0_domain = settings.AUTH0_DOMAIN
auth0_api_audience = settings.AUTH0_API_AUDIENCE
auth = Auth0(domain=auth0_domain, api_audience=auth0_api_audience, scopes={})

router = APIRouter(
    prefix='/api/file-uploads',
    tags=['File Uploads']
)

aws_access_key = settings.AWS_ACCESS_KEY
aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
aws_bucket_region = settings.AWS_BUCKET_REGION
aws_bucket_name = settings.AWS_BUCKET_NAME


def get_signed_url(object_name: str):
    """
    Generate a presigned URL to upload a file to S3.

    :param bucket_name: string
    :param object_name: string
    :param region_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :param aws_access_key_id: string (optional)
    :param aws_secret_access_key: string (optional)
    :return: Presigned URL as string. If error, returns None.
    """
    # Create a boto3 client
    if aws_access_key and aws_secret_access_key:
        s3_client = boto3.client('s3',
                                 region_name=aws_bucket_region,
                                 aws_access_key_id=aws_access_key,
                                 aws_secret_access_key=aws_secret_access_key)
    else:
        s3_client = boto3.client('s3', region_name=aws_bucket_region)

    try:
        # Generate the presigned URL for put_object operation
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': aws_bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=60)
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None

    # Return the presigned URL
    return response


async def get_merchant_id(user_id: str, db: AsyncIOMotorDatabase):
    user = await db['merchants'].find_one({'user_id': user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = jsonable_encoder(user)
    return user['_id']


@router.get("/signed-url/service/")
async def get_service_image_signed_url(user_profile: Auth0User = Security(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    file_name = f"SB{datetime.now().strftime('%Y%m%d%H%M%S')}{randbytes(4).hex()}"
    user_id = await get_merchant_id(user_profile.id, db)
    directory_name = f"{user_id}/services"
    object_name = f"{directory_name}/{file_name}"

    signed_url = get_signed_url(object_name)
    return {
        "url": signed_url
    }


@router.get("/signed-url/intro-video/")
async def get_intro_video_signed_url(user_profile: Auth0User = Security(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    file_name = f"SB{datetime.now().strftime('%Y%m%d%H%M%S')}{randbytes(4).hex()}"
    user_id = await get_merchant_id(user_profile.id, db)
    directory_name = f"{user_id}/videos"
    object_name = f"{directory_name}/{file_name}"

    signed_url = get_signed_url(object_name)
    return {
        "url": signed_url
    }


@router.get("/signed-url/profile-image")
async def get_profile_image_signed_url(user_profile: Auth0User = Security(auth.get_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    file_name = f"SB{datetime.now().strftime('%Y%m%d%H%M%S')}{randbytes(4).hex()}"
    user_id = await get_merchant_id(user_profile.id, db)
    directory_name = f"{user_id}/images"
    object_name = f"{directory_name}/{file_name}"

    signed_url = get_signed_url(object_name)
    return {
        "url": signed_url
    }
