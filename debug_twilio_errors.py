
import asyncio
import os
from twilio.rest import Client
from src.config import settings

async def check_twilio_errors():
    print("Fetching recent Twilio errors...")
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    
    # Fetch last 5 calls
    calls = client.calls.list(limit=5)
    
    for call in calls:
        print(f"\nCall SID: {call.sid}")
        print(f"Status: {call.status}")
        print(f"To: {call.to}")
        print(f"Date: {call.date_created}")
        
        # Check for notifications (errors)
        notifications = client.calls(call.sid).notifications.list()
        if notifications:
            print("Errors found:")
            for n in notifications:
                print(f"  - Error {n.error_code}: {n.message_text}")
                print(f"    More info: {n.more_info}")
        else:
            print("No errors reported for this call.")

if __name__ == "__main__":
    asyncio.run(check_twilio_errors())
