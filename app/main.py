import os
from typing import Optional
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from notification_service import NotificationService, NotificationType

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Suav Beauty Technologies Inc. API for Web Application",
    description="The following documentation describes the API endpoints for the Suav Beauty Technologies Inc. These can be used by the frontend developers to build the web application with the required data.",
    version="1.0.0",
    openapi_url="/openapi.json",
)

notification_service = NotificationService()

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
            return {"sid": sid, "message": "Notification sent successfully."}
        else:
            return {"message": f"{request.notification_type} notifications are not implemented yet."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-booking-reminder", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def send_booking_reminder(request: MessageRequest):
    sid = await notification_service.booking_reminder(request.booking_id, request.customer_id, request.to)
    return {"sid": sid, "message": "Booking reminder sent successfully."}

@app.post("/send-booking-rejected", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def send_booking_rejected(request: MessageRequest):
    sid = await notification_service.booking_rejected(request.booking_id, request.customer_id, request.to)
    return {"sid": sid, "message": "Booking rejection sent successfully."}

@app.post("/send-booking-rescheduled", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def send_booking_rescheduled(request: MessageRequest):
    sid = await notification_service.booking_rescheduling(request.booking_id, request.customer_id, request.to)
    return {"sid": sid, "message": "Booking rescheduling sent successfully."}

@app.post("/send-booking-canceled", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def send_booking_canceled(request: MessageRequest):
    sid = await notification_service.booking_canceled(request.booking_id, request.customer_id, request.to)
    return {"sid": sid, "message": "Booking cancellation sent successfully."}