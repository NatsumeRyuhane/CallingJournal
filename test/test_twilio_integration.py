
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from src.services.phone_service import phone_service

client = TestClient(app)

def test_twilio_voice_webhook_returns_stream():
    """
    Verify that the Twilio voice webhook returns TwiML with <Stream>.
    """
    # Mock the phone service to just return the TwiML string as it would normally
    # But we are testing the webhook endpoint logic which calls phone_service.generate_twiml_response
    
    # We don't need to mock generate_twiml_response if we want to test the actual integration
    # unless we want to avoid side effects. generate_twiml_response is pure logic mostly.
    
    response = client.post(
        "/webhooks/twilio/voice",
        data={
            "CallSid": "CA12345",
            "CallStatus": "ringing",
            "From": "+15551234567",
            "To": "+15557654321"
        },
        headers={"host": "testserver"}
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    content = response.text
    
    # Check for <Stream> verb
    assert "<Stream" in content
    # TestClient uses http by default, so we expect ws
    assert 'url="ws://testserver/streams/twilio"' in content
    assert "<Connect>" in content

def test_websocket_stream_connection():
    """
    Verify that the WebSocket endpoint accepts connections and handles messages.
    """
    with client.websocket_connect("/streams/twilio") as websocket:
        # Simulate Twilio 'connected' event
        websocket.send_json({
            "event": "connected",
            "protocol": "Call",
            "version": "1.0.0"
        })
        
        # Simulate 'start' event
        websocket.send_json({
            "event": "start",
            "sequenceNumber": "1",
            "start": {
                "streamSid": "MZ12345",
                "accountSid": "AC12345",
                "callSid": "CA12345",
                "tracks": ["inbound"],
                "mediaFormat": {
                    "encoding": "audio/x-mulaw",
                    "sampleRate": 8000,
                    "channels": 1
                }
            },
            "streamSid": "MZ12345"
        })
        
        # Simulate 'media' event
        websocket.send_json({
            "event": "media",
            "sequenceNumber": "2",
            "media": {
                "track": "inbound",
                "chunk": "1",
                "timestamp": "5",
                "payload": "no-op"
            },
            "streamSid": "MZ12345"
        })
        
        # Simulate 'stop' event
        websocket.send_json({
            "event": "stop",
            "sequenceNumber": "3",
            "stop": {
                "accountSid": "AC12345",
                "callSid": "CA12345"
            },
            "streamSid": "MZ12345"
        })
        
        # If no exception, test passes
        assert True
