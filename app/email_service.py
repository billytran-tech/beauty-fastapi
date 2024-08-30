import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from enum import Enum
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException


class NotificationType(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = os.getenv("SMTP_PORT")
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD_FASTAPI")
        self.from_email = os.getenv("FROM_EMAIL")
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

    def send_email(self, to: str, subject: str, body: str):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    async def send_notification(self, booking_id: str, customer_id: str, to: str, subject: str, body: str, notification_type: NotificationType) -> Optional[str]:
        status = "failed"
        try:
            if notification_type == NotificationType.EMAIL:
                self.send_email(to, subject, body)
                status = "sent"
            else:
                raise ValueError("Unsupported notification type")

            await self.log_notification(booking_id, customer_id, notification_type, status, body)
            return "Email sent successfully"
        except Exception as e:
            await self.log_notification(booking_id, customer_id, notification_type, status, str(e))
            raise

    async def booking_reminder(self, booking_id: str, customer_id: str, to: str) -> str:
        subject = "Booking Reminder"
        body = "This is a reminder for your upcoming booking."
        return await self.send_notification(booking_id, customer_id, to, subject, body, NotificationType.EMAIL)

    async def payment_update(self, booking_id: str, customer_id: str, to: str, update_text: str) -> str:
        subject = "Payment Update"
        body = f"Payment update: {update_text}"
        return await self.send_notification(booking_id, customer_id, to, subject, body, NotificationType.EMAIL)

    async def booking_rejected(self, booking_id: str, customer_id: str, to: str) -> str:
        subject = "Booking Rejected"
        body = "Your booking has been rejected."
        return await self.send_notification(booking_id, customer_id, to, subject, body, NotificationType.EMAIL)

    async def new_booking(self, booking_id: str, customer_id: str, to: str) -> str:
        subject = "New Booking"
        body = "You have a new booking."
        return await self.send_notification(booking_id, customer_id, to, subject, body, NotificationType.EMAIL)

    async def booking_rescheduling(self, booking_id: str, customer_id: str, to: str) -> str:
        subject = "Booking Rescheduled"
        body = "Your booking has been rescheduled."
        return await self.send_notification(booking_id, customer_id, to, subject, body, NotificationType.EMAIL)

    async def booking_canceled(self, booking_id: str, customer_id: str, to: str) -> str:
        subject = "Booking Canceled"
        body = "Your booking has been canceled."
        return await self.send_notification(booking_id, customer_id, to, subject, body, NotificationType.EMAIL)

