import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# הגדרת הרשאות גוגל יומן
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """יוצר חיבור מורשה ל-Google Calendar מתוך משתנה הסביבה ב-Render"""
    creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if creds_json:
        creds_info = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    else:
        # גיבוי מקומי אם הקובץ נמצא בתיקייה
        creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    
    service = build('calendar', 'v3', credentials=creds)
    return service

def create_google_event(summary, start_time_str, end_time_str):
    """מוסיף אירוע חדש ליומן הראשי"""
    try:
        service = get_calendar_service()
        
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time_str,  # פורמט: '2026-09-20T10:00:00+03:00'
                'timeZone': 'Asia/Jerusalem',
            },
            'end': {
                'dateTime': end_time_str,    # פורמט: '2026-09-20T11:00:00+03:00'
                'timeZone': 'Asia/Jerusalem',
            },
        }
        
        calendar_id = 'primary'
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        return created_event.get('htmlLink')
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return None

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """אימות ה-Webhook מול מטא"""
    verify_token = "YOUR_VERIFY_TOKEN" # שימי לב להחליף או לוודא שזה תואם למה שהגדרת במטא
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == verify_token:
            return challenge, 200
        else:
            return "Verification failed", 403
    return "Hello world", 200

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """קליטת הודעות נכנסות ויצירת פגישה ביומן לצרכי בדיקה"""
    data = request.json
    print("Received WhatsApp Data:", json.dumps(data, indent=2))
    
    try:
        sender_phone = "Test User"
        # מנסים לחלץ את מספר הטלפון אם יש הודעה אמיתית
        if (data.get("entry") and 
            data["entry"][0].get("changes") and 
            data["entry"][0]["changes"][0].get("value").get("messages")):
            
            message_data = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender_phone = message_data.get("from", "Unknown")
        
        # יוצרים פגישה בכל מקרה כדי לבדוק את החיבור לגוגל!
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=0, second=0).isoformat() + "+03:00"
        end_time = tomorrow.replace(hour=11, minute=0, second=0).isoformat() + "+03:00"
        
        event_title = f"פגישה מתואמת מוואטסאפ ({sender_phone})"
        event_link = create_google_event(event_title, start_time, end_time)
        
        if event_link:
            print(f"Event created successfully: {event_link}")
        else:
            print("Failed to create event. Check Google Credentials.")
                    
    except Exception as e:
        print(f"CRITICAL Error processing webhook: {e}")

    return jsonify({"status": "success"}), 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
