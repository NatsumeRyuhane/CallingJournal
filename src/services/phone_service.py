"""
Phone service module for handling phone calls.
Provides abstraction layer for different phone service providers (Twilio, Vonage, etc.)
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import VoiceResponse

from src.config import settings


class PhoneProvider(str, Enum):
    """Supported phone service providers."""
    TWILIO = "twilio"
    VONAGE = "vonage"


class CallDirection(str, Enum):
    """Call direction."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class IPhoneService(ABC):
    """Interface for phone service implementations."""
    
    @abstractmethod
    async def initiate_call(
        self,
        to_number: str,
        from_number: Optional[str] = None,
        callback_url: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Initiate an outbound call.
        
        Args:
            to_number: Phone number to call
            from_number: Phone number to call from (uses default if not provided)
            callback_url: URL for call status callbacks
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict containing call_id and other metadata
        """
        pass
    
    @abstractmethod
    async def end_call(self, call_id: str) -> bool:
        """
        End an active call.
        
        Args:
            call_id: Unique identifier for the call
            
        Returns:
            True if call was ended successfully
        """
        pass
    
    @abstractmethod
    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """
        Get the status of a call.
        
        Args:
            call_id: Unique identifier for the call
            
        Returns:
            Dict containing call status and metadata
        """
        pass
    
    @abstractmethod
    async def get_call_recording(self, call_id: str) -> Optional[str]:
        """
        Get recording URL for a call.
        
        Args:
            call_id: Unique identifier for the call
            
        Returns:
            Recording URL or None if not available
        """
        pass
    
    @abstractmethod
    def generate_twiml_response(
        self,
        message: Optional[str] = None,
        gather_input: bool = False,
        **kwargs
    ) -> str:
        """
        Generate TwiML/equivalent response for call control.
        
        Args:
            message: Text to speak to the caller
            gather_input: Whether to gather user input
            **kwargs: Additional parameters for the response
            
        Returns:
            TwiML or equivalent XML/JSON response
        """
        pass


class TwilioPhoneService(IPhoneService):
    """Twilio implementation of phone service."""
    
    def __init__(self):
        """Initialize Twilio client."""
        self.client = TwilioClient(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.default_phone_number = settings.twilio_phone_number
    
    async def initiate_call(
        self,
        to_number: str,
        from_number: Optional[str] = None,
        callback_url: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Initiate outbound call via Twilio."""
        call = self.client.calls.create(
            to=to_number,
            from_=from_number or self.default_phone_number,
            url=callback_url or kwargs.get("url"),
            status_callback=kwargs.get("status_callback"),
            record=kwargs.get("record", True),
            **{k: v for k, v in kwargs.items() if k not in ["url", "status_callback", "record"]}
        )
        
        return {
            "call_id": call.sid,
            "status": call.status,
            "direction": call.direction,
            "to": call.to,
            "from": call.from_,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def end_call(self, call_id: str) -> bool:
        """End active Twilio call."""
        try:
            call = self.client.calls(call_id).update(status="completed")
            return call.status == "completed"
        except Exception as e:
            print(f"Error ending call: {e}")
            return False
    
    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """Get Twilio call status."""
        call = self.client.calls(call_id).fetch()
        return {
            "call_id": call.sid,
            "status": call.status,
            "direction": call.direction,
            "duration": call.duration,
            "start_time": call.start_time.isoformat() if call.start_time else None,
            "end_time": call.end_time.isoformat() if call.end_time else None,
            "price": call.price,
            "price_unit": call.price_unit
        }
    
    async def get_call_recording(self, call_id: str) -> Optional[str]:
        """Get Twilio call recording URL."""
        recordings = self.client.recordings.list(call_sid=call_id, limit=1)
        if recordings:
            recording = recordings[0]
            return f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
        return None
    
    def generate_twiml_response(
        self,
        message: Optional[str] = None,
        gather_input: bool = False,
        **kwargs
    ) -> str:
        """Generate TwiML response."""
        response = VoiceResponse()
        
        if gather_input:
            gather = response.gather(
                input=kwargs.get("input", "speech"),
                action=kwargs.get("action"),
                timeout=kwargs.get("timeout", 5),
                speech_timeout=kwargs.get("speech_timeout", "auto"),
                language=kwargs.get("language", "en-US")
            )
            if message:
                gather.say(message, voice=kwargs.get("voice", "Polly.Joanna"))
        elif message:
            response.say(message, voice=kwargs.get("voice", "Polly.Joanna"))
        
        if kwargs.get("record"):
            response.record(
                max_length=kwargs.get("max_length", 3600),
                transcribe=kwargs.get("transcribe", True),
                transcribe_callback=kwargs.get("transcribe_callback")
            )
        
        return str(response)


class PhoneServiceFactory:
    """Factory for creating phone service instances."""
    
    @staticmethod
    def create(provider: PhoneProvider = PhoneProvider.TWILIO) -> IPhoneService:
        """
        Create a phone service instance.
        
        Args:
            provider: Phone service provider to use
            
        Returns:
            IPhoneService implementation
        """
        if provider == PhoneProvider.TWILIO:
            return TwilioPhoneService()
        else:
            raise ValueError(f"Unsupported phone provider: {provider}")


# Default phone service instance
phone_service = PhoneServiceFactory.create(PhoneProvider.TWILIO)
