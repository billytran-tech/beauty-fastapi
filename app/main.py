import os
from typing import Optional
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from app.notification_service import NotificationService, NotificationType
from app.email_service import EmailService  # Import the EmailService
from app.whatsapp_service import WhatsAppService  # Import the WhatsAppService


# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Suav Beauty Technologies Inc. API for Web Application",
    description="The following documentation describes the API endpoints for the Suav Beauty Technologies Inc. These can be used by the frontend developers to build the web application with the required data.",
    version="1.0.0",
    openapi_url="/openapi.json",
)

notification_service = NotificationService()
whatsapp_service = WhatsAppService()
email_service = EmailService()

class MessageRequest(BaseModel):
    booking_id: str
    customer_id: str
    to: str
    update_text: Optional[str] = Field(None, description="Text for payment update")
    notification_type: NotificationType

class MessageResponse(BaseModel):
    sid: Optional[str] = None
    message: str

@app.get("/", status_code=status.HTTP_200_OK, response_model=MessageResponse)
def read_root():
    return {"message": "Welcome to Suav Beauty"}

@app.post("/send-notification", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def send_notification(request: MessageRequest):
    try:
        if request.notification_type == NotificationType.SMS:
            if request.update_text:
                sid = await notification_service.payment_update(request.booking_id, request.customer_id, request.to, request.update_text)
            else:
                sid = await notification_service.new_booking(request.booking_id, request.customer_id, request.to)
            return {"sid": sid, "message": "SMS notification sent successfully."}
        
        elif request.notification_type == NotificationType.EMAIL:
            if request.update_text:
                sid = await email_service.payment_update(request.booking_id, request.customer_id, request.to, request.update_text)
            else:
                sid = await email_service.new_booking(request.booking_id, request.customer_id, request.to)
            return {"sid": sid, "message": "Email notification sent successfully."}

        else:
            return {"message": f"{request.notification_type} notifications are not implemented yet."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-booking-reminder", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def send_booking_reminder(request: MessageRequest):
    try:
        if request.notification_type == NotificationType.SMS:
            sid = await notification_service.booking_reminder(request.booking_id, request.customer_id, request.to)
            return {"sid": sid, "message": "SMS booking reminder sent successfully."}
        elif request.notification_type == NotificationType.EMAIL:
            sid = await email_service.booking_reminder(request.booking_id, request.customer_id, request.to)
            return {"sid": sid, "message": "Email booking reminder sent successfully."}
        else:
            return {"message": f"{request.notification_type} notifications are not implemented yet."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-booking-rejected", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def send_booking_rejected(request: MessageRequest):
    try:
        if request.notification_type == NotificationType.SMS:
            sid = await notification_service.booking_rejected(request.booking_id, request.customer_id, request.to)
            return {"sid": sid, "message": "SMS booking rejection sent successfully."}
        elif request.notification_type == NotificationType.EMAIL:
            sid = await email_service.booking_rejected(request.booking_id, request.customer_id, request.to)
            return {"sid": sid, "message": "Email booking rejection sent successfully."}
        else:
            return {"message": f"{request.notification_type} notifications are not implemented yet."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-booking-rescheduled", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def send_booking_rescheduled(request: MessageRequest):
    try:
        if request.notification_type == NotificationType.SMS:
            sid = await notification_service.booking_rescheduling(request.booking_id, request.customer_id, request.to)
            return {"sid": sid, "message": "SMS booking rescheduling sent successfully."}
        elif request.notification_type == NotificationType.EMAIL:
            sid = await email_service.booking_rescheduling(request.booking_id, request.customer_id, request.to)
            return {"sid": sid, "message": "Email booking rescheduling sent successfully."}
        else:
            return {"message": f"{request.notification_type} notifications are not implemented yet."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-booking-canceled", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def send_booking_canceled(request: MessageRequest):
    try:
        if request.notification_type == NotificationType.SMS:
            sid = await notification_service.booking_canceled(request.booking_id, request.customer_id, request.to)
            return {"sid": sid, "message": "SMS booking cancellation sent successfully."}
        elif request.notification_type == NotificationType.EMAIL:
            sid = await email_service.booking_canceled(request.booking_id, request.customer_id, request.to)
            return {"sid": sid, "message": "Email booking cancellation sent successfully."}
        else:
            return {"message": f"{request.notification_type} notifications are not implemented yet."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-whatsapp-notification", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def send_whatsapp_notification(request: MessageRequest):
    try:
        sid = await whatsapp_service.send_notification(request.booking_id, request.customer_id, request.to, request.update_text or "New WhatsApp message.")
        return {"sid": sid, "message": "WhatsApp notification sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-whatsapp-reminder", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def send_whatsapp_reminder(request: MessageRequest):
    try:
        sid = await whatsapp_service.send_notification(request.booking_id, request.customer_id, request.to, "This is a reminder for your booking.")
        return {"sid": sid, "message": "WhatsApp booking reminder sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
