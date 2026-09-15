import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# את יכולה לשנות את הטוקן הזה לאיזו מחרוזת שבא לך. נצטרך אותו בהמשך במטא.
VERIFY_TOKEN = "my_custom_verify_token_123"

# פונקציה 1: מטא בודקת שהשרת שלנו באמת קיים (GET)
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403
    return "Bot is running!", 200

# פונקציה 2: מטא שולחת לנו את ההודעות שהמשתמש שלח (POST)
@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.get_json()
    print("Received data:", data) # כרגע רק נדפיס את זה ללוגים בענן כדי לראות שזה עובד
    
    # חובה להחזיר 200 OK למטא כדי שידעו שקיבלנו את ההודעה
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # Render מספקת את הפורט באופן דינמי
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
