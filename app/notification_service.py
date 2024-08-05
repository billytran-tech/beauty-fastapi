import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from twilio.rest import Client
from enum import Enum
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class NotificationType(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"

class NotificationService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.client = Client(self.account_sid, self.auth_token)
        self.from_number = "+12086685034"  # Replace with your Twilio number
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
        # await self.notifications_collection.insert_one(notification)

    def send_sms(self, to: str, body: str) -> str:
        message = self.client.messages.create(
            body=body,
            from_=self.from_number,
            to=to
        )
        return message.sid

    async def send_notification(self, booking_id: str, customer_id: str, to: str, body: str, notification_type: NotificationType) -> Optional[str]:
        status = "failed"
        try:
            if notification_type == NotificationType.SMS:
                sid = self.send_sms(to, body)
                status = "sent"
            else:
                sid = None
            await self.log_notification(booking_id, customer_id, notification_type, status, body)
            return sid
        except Exception as e:
            await self.log_notification(booking_id, customer_id, notification_type, status, str(e))
            raise

    async def booking_reminder(self, booking_id: str, customer_id: str, to: str) -> str:
        body = "This is a reminder for your upcoming booking."
        return await self.send_notification(booking_id, customer_id, to, body, NotificationType.SMS)

    async def payment_update(self, booking_id: str, customer_id: str, to: str, update_text: str) -> str:
        body = f"Payment update: {update_text}"
        return await self.send_notification(booking_id, customer_id, to, body, NotificationType.SMS)

    async def booking_rejected(self, booking_id: str, customer_id: str, to: str) -> str:
        body = "Your booking has been rejected."
        return await self.send_notification(booking_id, customer_id, to, body, NotificationType.SMS)

    async def new_booking(self, booking_id: str, customer_id: str, to: str) -> str:
        body = "You have a new booking."
        return await self.send_notification(booking_id, customer_id, to, body, NotificationType.SMS)

    async def booking_rescheduling(self, booking_id: str, customer_id: str, to: str) -> str:
        body = "Your booking has been rescheduled."
        return await self.send_notification(booking_id, customer_id, to, body, NotificationType.SMS)

    async def booking_canceled(self, booking_id: str, customer_id: str, to: str) -> str:
        body = "Your booking has been canceled."
        return await self.send_notification(booking_id, customer_id, to, body, NotificationType.SMS)