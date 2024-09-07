import os
from twilio.rest import Client
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from enum import Enum
from typing import Optional
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

class NotificationType(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"

class WhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.client = Client(self.account_sid, self.auth_token)
        self.from_whatsapp_number = "whatsapp:+14155238886"  # Twilio Sandbox number
        self.mongo_client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
        self.db = self.mongo_client["your_database_name"]
        self.notifications_collection = self.db["notifications"]

    async def log_notification(self, booking_id: str, customer_id: str, notification_type: NotificationType, status: str, message: str):
        notification = {
            "booking_id": booking_id,
            "customer_id": customer_id,
            "notification_type": notification_type,
            "status": status,
            "message": message,
            "date_created": datetime.utcnow()
        }
        await self.notifications_collection.insert_one(notification)

    def send_whatsapp_message(self, to: str, body: str) -> str:
        try:
            message = self.client.messages.create(
                body=body,
                from_=self.from_whatsapp_number,
                to=f"whatsapp:{to}"
            )
            return message.sid
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send WhatsApp message: {str(e)}")

    async def send_notification(self, booking_id: str, customer_id: str, to: str, body: str) -> Optional[str]:
        status = "failed"
        try:
            sid = self.send_whatsapp_message(to, body)
            status = "sent"
            await self.log_notification(booking_id, customer_id, NotificationType.WHATSAPP, status, body)
            return sid
        except Exception as e:
            await self.log_notification(booking_id, customer_id, NotificationType.WHATSAPP, status, str(e))
            raise