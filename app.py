from flask import Flask, request, jsonify
from twilio.rest import Client
import os
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Twilio Configuration - Will use environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_SID', 'AC_your_sid_here')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_TOKEN', 'your_auth_token_here')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE', '+1234567890')

# Your phone number - PUT YOUR REAL PHONE HERE
FARMER_PHONE_NUMBER = os.getenv('FARMER_PHONE', '+21612345678')  # CHANGE THIS!

def send_sms_alert(alert_data):
    """Send SMS using Twilio"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message_body = f"🚨 RPW ALERT! {alert_data['message']} at {alert_data['location']}. Detection count: {alert_data['count']}. Time: {datetime.now().strftime('%H:%M')}"
        
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=FARMER_PHONE_NUMBER
        )
        
        return {'success': True, 'message_sid': message.sid}
        
    except Exception as e:
        # Fallback: log the SMS that would be sent
        print(f"💬 SMS WOULD BE SENT: {message_body}")
        return {'success': False, 'error': str(e), 'simulated': True}

@app.route('/send_alert', methods=['POST'])
def send_alert():
    """Receive alerts and send SMS"""
    try:
        data = request.get_json()
        print(f"📨 Received alert: {data}")
        
        # Send SMS
        sms_result = send_sms_alert(data)
        
        response = {
            'status': 'success' if sms_result['success'] else 'error',
            'sms_sent': sms_result['success'],
            'message': 'Alert processed',
            'timestamp': datetime.now().isoformat()
        }
        
        if sms_result.get('simulated'):
            response['note'] = 'SMS simulation mode - no actual SMS sent'
        
        print(f"📱 SMS Result: {response}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Alert error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'SMS Alert Server Running', 'mode': 'simulation'})

@app.route('/test_sms', methods=['GET'])
def test_sms():
    """Test SMS functionality"""
    test_data = {
        'message': 'TEST ALERT - RPW Detection System',
        'location': 'Test Field',
        'count': 3
    }
    result = send_sms_alert(test_data)
    return jsonify({'test_result': result})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print("🚀 SMS Alert Server Starting...")
    print(f"📱 Target phone: {FARMER_PHONE_NUMBER}")
    app.run(host='0.0.0.0', port=port, debug=False)
