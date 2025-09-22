from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage
import os
from datetime import datetime
from dotenv import load_dotenv
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import webbrowser

# Load environment variables from .env
load_dotenv()

EMAIL_ADDRESS = ""
EMAIL_PASSWORD = ""

# --- Google Calendar API Configuration ---
SCOPES = ["https://www.googleapis.com/auth/calendar"]

app = Flask(__name__)

# ---------- EMAIL SENDING ----------
@app.route("/send-email", methods=["POST"])
def send_email():
    """
    Send a plain email.
    """
    data = request.get_json()
    to_email = data.get("to")
    subject = data.get("subject")
    body = data.get("body")

    if not (to_email and subject and body):
        return jsonify({"error": "Missing required fields"}), 400

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    return jsonify({"status": "success", "message": "Email sent"}), 200


# ---------- CALENDAR INVITE (Google Calendar) ----------
@app.route("/create-calendar-event", methods=["POST"])
def create_calendar_event():
    """
    Creates a calendar event in Google Calendar.
    
    JSON Payload Example:
    {
        "summary": "Procurement Meeting",
        "description": "Discuss procurement requirements",
        "start": "2025-09-21T10:00:00",
        "end": "2025-09-21T11:00:00",
        "attendees": ["someone@example.com", "other@example.com"],
        "timezone": "America/Los_Angeles",
        "body": "Long description of meeting generate by LLM"
    }
    """ 
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                return jsonify({"error": "credentials.json not found. Please follow the setup instructions."}), 500
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            try:
                creds = flow.run_local_server(port=0)
            except webbrowser.Error as e:
                return jsonify({
                    "error": "Could not open a web browser for authentication.",
                    "message": "This application needs to open a browser for you to authenticate with Google. This is not possible in the current environment (e.g., inside a Docker container without a graphical interface).",
                    "instructions": "To fix this, please run the application once in your local environment (not in Docker) to generate a 'token.json' file. Then, mount this file into the Docker container. See the README for more details.",
                    "details": str(e)
                }), 500
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        data = request.get_json()

        required_fields = ["summary", "description", "start", "end", "attendees"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        timezone = data.get("timezone", "Asia/Bangkok")

        attendees_list = [{'email': email} for email in data["attendees"]]

        start_dt = datetime.strptime(data["start"], "%Y%m%dT%H%M%S").isoformat()
        end_dt = datetime.strptime(data["end"], "%Y%m%dT%H%M%S").isoformat()

        event = {
            'summary': data["summary"],
            'description': data["description"],
            'start': {
                'dateTime': start_dt,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_dt,
                'timeZone': timezone,
            },
            'attendees': attendees_list,
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        return jsonify({"status": "success", "message": f"Event created: {event.get('htmlLink')}"}), 201

    except HttpError as error:
        return jsonify({"error": f"An error occurred: {error}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- SEND EMAIL AND CALENDAR INVITE ----------
@app.route("/send-email-and-calendar-event", methods=["POST"])
def send_email_and_calendar_event():
    """
    Sends an email and creates a calendar event in Google Calendar.
    """
    data = request.get_json()

    # --- Send Email ---
    to_email = ", ".join(data.get("email_attendees", []))
    subject = data.get("summary")
    body = data.get("description")

    if not (to_email and subject and body):
        return jsonify({"error": "Missing required fields for email (attendees, summary, description)"}), 400

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    # --- Create Calendar Event ---
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                return jsonify({"error": "credentials.json not found. Please follow the setup instructions."}), 500
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            try:
                creds = flow.run_local_server(port=0)
            except webbrowser.Error as e:
                return jsonify({
                    "error": "Could not open a web browser for authentication.",
                    "message": "This application needs to open a browser for you to authenticate with Google. This is not possible in the current environment (e.g., inside a Docker container without a graphical interface).",
                    "instructions": "To fix this, please run the application once in your local environment (not in Docker) to generate a 'token.json' file. Then, mount this file into the Docker container. See the README for more details.",
                    "details": str(e)
                }), 500
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        required_fields = ["summary", "description", "start", "end", "email_attendees"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        timezone = data.get("timezone", "Asia/Bangkok")

        attendees_list = [{'email': email} for email in data["email_attendees"]]

        start_dt = datetime.strptime(data["start"], "%Y%m%dT%H%M%S").isoformat()
        end_dt = datetime.strptime(data["end"], "%Y%m%dT%H%M%S").isoformat()

        event = {
            'summary': data["summary"],
            'description': data["description"],
            'start': {
                'dateTime': start_dt,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_dt,
                'timeZone': timezone,
            },
            'attendees': attendees_list,
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        return jsonify({"status": "success", "message": f"Email sent and event created: {event.get('htmlLink')}"}), 201

    except HttpError as error:
        return jsonify({"error": f"An error occurred: {error}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
