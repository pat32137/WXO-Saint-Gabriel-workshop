from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from fastapi.responses import JSONResponse
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from email.message import EmailMessage  # For creating email messages
import smtplib          # For SMTP email sending
from datetime import datetime  # For timestamp


env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="Classroom Behavior Monitoring API",
    description="Classroom behavior monitoring API for recording and viewing student behavior observations, tracking behavior patterns, and managing class notes. Compatible with Watsonx Orchestrate and Swagger UI.",
    version="1.0.0",
    openapi_version="3.0.0"
)

# Add servers section to OpenAPI spec
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {
            "url": "https://be-class-behavior-ggs.20lxtlu1ylfn.us-south.codeengine.appdomain.cloud",
            "description": "Production server"
        }
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Google Sheets setup
SHEET_ID = "1kH5pafULRdw1rZ2YaRhNLkxZizVrxQDcWa3uIyL9ADw"  # Replace with your actual spreadsheet ID

# Email configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def get_gsheet(sheet_name: str):
    try:
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path or not os.path.exists(creds_path):
            raise FileNotFoundError(f"Service account credentials file not found at {creds_path}")
        creds = Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SHEET_ID)
        worksheet = spreadsheet.worksheet(sheet_name)
        return worksheet
    except Exception as e:
        print(f"[ERROR] Google Sheets access failed: {e}")
        raise

class BehaviorRequest(BaseModel):
    date: str = Field(..., description="Date of observation (DD-MM-YYYY format, e.g., 22-09-2025)")
    student: str = Field(..., description="Student name with title (e.g., ด.ญ. กานดา พิพัฒน์, ด.ช. ณัฐพล ศรีวงศ์)")
    behavior: str = Field(..., description="Behavior category: 'เชิงบวก' (positive), 'ควรปรับปรุง' (needs improvement)")
    notes: Optional[str] = Field("", description="Detailed notes about the behavior observation (optional)")

class BehaviorResponse(BaseModel):
    message: str = Field(..., description="Status message for the behavior record")
    date: str = Field(..., description="Date of observation (DD-MM-YYYY)")
    student: str = Field(..., description="Student name with title")
    behavior: str = Field(..., description="Behavior category")
    notes: Optional[str] = Field("", description="Detailed notes about the behavior")
    
class BehaviorHistoryItem(BaseModel):
    date: str
    student: str
    behavior: str
    notes: Optional[str] = ""
    
class BehaviorHistoryResponse(BaseModel):
    behaviors: List[BehaviorHistoryItem]

class GmailRequest(BaseModel):
    to_email: str = Field(..., description="Recipient email address")
    cc_email: Optional[str] = Field(None, description="CC email address (optional)")
    subject: str = Field(..., description="Email subject/topic")
    content: str = Field(..., description="Email content/body")

class GmailResponse(BaseModel):
    message: str = Field(..., description="Status message for the email")
    to_email: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    sent_at: str = Field(..., description="Timestamp when email was sent")

class ErrorResponse(BaseModel):
    detail: str

@app.post(
    "/behaviors",
    response_model=BehaviorResponse,
    summary="Record student behavior observation",
    description="""Record a new student behavior observation with date, student name, behavior category, and detailed notes.
        All fields except notes are required. Notes can be provided or left empty. The behavior category must be one of: 'เชิงบวก' (positive), 'ควรปรับปรุง' (needs improvement).
        """,
    response_description="Returns the recorded behavior observation with a status message.\nFields returned:\n- message: Status message\n- date: Date of observation (DD-MM-YYYY)\n- student: Student name with title\n- behavior: Behavior category\n- notes: Detailed notes about the behavior",
    operation_id="addBehavior"
)
def add_behavior(behavior: BehaviorRequest):
    """
    Record a new student behavior observation.
    User needs to provide date (DD-MM-YYYY), student name, and behavior category. Notes are optional.
    """
    try:
        sheet = get_gsheet('Sheet1')
        # Append new behavior record
        sheet.append_row([
            behavior.date,
            behavior.student,
            behavior.behavior,
            behavior.notes or "",
        ])
    except Exception as e:
        print(f"[ERROR] Failed to add behavior record: {e}")
        return JSONResponse(status_code=500, content={"detail": f"Error accessing Google Sheet: {str(e)}"})
    
    return BehaviorResponse(
        message="Behavior observation recorded successfully",
        date=behavior.date,
        student=behavior.student,
        behavior=behavior.behavior,
        notes=behavior.notes
    )

@app.get(
    "/behaviors",
    response_model=BehaviorHistoryResponse,
    summary="View student behavior history",
    description="Retrieve the complete history of student behavior observations, including date, student, behavior category,and notes.",
    response_description="Returns a list of behavior observations. Each record includes:\n- date: Date of observation (DD-MM-YYYY)\n- student: Student name with title\n- behavior: Behavior category\n- notes: Detailed notes about the behavior",
    operation_id="getBehaviorHistory"
)
def get_behavior_history():
    """
    Retrieve the full behavior observation history.
    Returns all recorded student behavior observations.
    """
    behaviors = []
    try:
        sheet = get_gsheet('Sheet1')
        records = sheet.get_all_records()
        for row in records:
            try:
                behaviors.append(BehaviorHistoryItem(
                    date=row.get("Date", ""),
                    student=row.get("Student", ""),
                    behavior=row.get("Behavior", ""),
                    notes=row.get("Notes", ""),
                ))
            except Exception as item_error:
                print(f"[ERROR] Failed to parse row: {row}, error: {item_error}")
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch behavior history: {e}")
        return JSONResponse(status_code=500, content={"detail": f"Error accessing Google Sheet: {str(e)}"})
    
    return BehaviorHistoryResponse(behaviors=behaviors)

@app.get("/health", summary="Health check")
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "Classroom Behavior Monitoring API"}

@app.post(
    "/send-email",
    response_model=GmailResponse,
    summary="Send email notification",
    description="""Send an email notification using Gmail SMTP. 
        Requires to_email, subject, and content. CC is optional.
        """,
    response_description="Returns the email sending status with details.",
    operation_id="sendEmail"
)
def send_email(email_request: GmailRequest):
    """
    Send a plain email using Gmail SMTP.
    User needs to provide to_email, subject, and content. CC is optional.
    """
    try:
        # Validate email credentials
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            return JSONResponse(
                status_code=500, 
                content={"detail": "Email credentials not configured. Please set EMAIL_ADDRESS and EMAIL_PASSWORD environment variables."}
            )
        
        # Create email message
        msg = EmailMessage()
        msg["Subject"] = email_request.subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email_request.to_email
        
        # Add CC if provided
        if email_request.cc_email:
            msg["Cc"] = email_request.cc_email
        
        msg.set_content(email_request.content)

        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        # Return success response
        return GmailResponse(
            message="Email sent successfully",
            to_email=email_request.to_email,
            subject=email_request.subject,
            sent_at=datetime.now().isoformat()
        )

    except smtplib.SMTPAuthenticationError:
        return JSONResponse(
            status_code=401,
            content={"detail": "Email authentication failed. Please check EMAIL_ADDRESS and EMAIL_PASSWORD."}
        )
    except smtplib.SMTPException as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"SMTP error occurred: {str(e)}"}
        )
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        return JSONResponse(
            status_code=500, 
            content={"detail": f"Error sending email: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
