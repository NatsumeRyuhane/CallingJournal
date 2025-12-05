"""
Transcription service for converting audio to text.
Supports multiple transcription backends: Whisper (OpenAI), SpeechRecognition.
"""
import os
import tempfile
from typing import Optional, Dict, Any
from enum import Enum
import logging

import speech_recognition as sr
import whisper
import httpx
from pydub import AudioSegment

from src.config import settings

logger = logging.getLogger(__name__)


class TranscriptionProvider(str, Enum):
    """Supported transcription providers."""
    WHISPER = "whisper"
    SPEECH_RECOGNITION = "speech_recognition"
    GOOGLE = "google"  # Via SpeechRecognition


class TranscriptionService:
    """Service for transcribing audio files to text."""
    
    def __init__(
        self,
        provider: TranscriptionProvider = TranscriptionProvider.WHISPER,
        whisper_model: str = "base"
    ):
        """
        Initialize transcription service.
        
        Args:
            provider: Transcription provider to use
            whisper_model: Whisper model size (tiny, base, small, medium, large)
        """
        self.provider = provider
        self.whisper_model_name = whisper_model
        self._whisper_model = None
        self._recognizer = None
        
    def _get_whisper_model(self):
        """Lazy load Whisper model."""
        if self._whisper_model is None:
            logger.info(f"Loading Whisper model: {self.whisper_model_name}")
            self._whisper_model = whisper.load_model(self.whisper_model_name)
        return self._whisper_model
    
    def _get_recognizer(self):
        """Lazy load SpeechRecognition recognizer."""
        if self._recognizer is None:
            self._recognizer = sr.Recognizer()
        return self._recognizer
    
    async def download_audio(self, audio_url: str, output_path: str) -> str:
        """
        Download audio file from URL.
        
        Args:
            audio_url: URL of the audio file
            output_path: Path to save the downloaded file
            
        Returns:
            Path to downloaded file
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(audio_url)
            response.raise_for_status()
            
            with open(output_path, "wb") as f:
                f.write(response.content)
                
        return output_path
    
    def convert_to_wav(self, audio_path: str) -> str:
        """
        Convert audio file to WAV format (required for SpeechRecognition).
        
        Args:
            audio_path: Path to input audio file
            
        Returns:
            Path to converted WAV file
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            
            # Convert to mono and set sample rate
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(16000)
            
            # Create temporary WAV file
            wav_path = audio_path.rsplit(".", 1)[0] + ".wav"
            audio.export(wav_path, format="wav")
            
            return wav_path
        except Exception as e:
            logger.error(f"Error converting audio to WAV: {e}")
            raise
    
    async def transcribe_with_whisper(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio using Whisper.
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'es')
            
        Returns:
            Dict with transcription text and metadata
        """
        try:
            model = self._get_whisper_model()
            
            # Transcribe
            result = model.transcribe(
                audio_path,
                language=language,
                fp16=False  # Use FP32 for better compatibility
            )
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language"),
                "segments": result.get("segments", []),
                "provider": "whisper"
            }
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            raise
    
    async def transcribe_with_speech_recognition(
        self,
        audio_path: str,
        use_google: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe audio using SpeechRecognition library.
        
        Args:
            audio_path: Path to audio file
            use_google: Whether to use Google Speech Recognition (requires internet)
            
        Returns:
            Dict with transcription text and metadata
        """
        try:
            recognizer = self._get_recognizer()
            
            # Convert to WAV if needed
            if not audio_path.endswith(".wav"):
                audio_path = self.convert_to_wav(audio_path)
            
            # Load audio file
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
            
            # Transcribe
            if use_google:
                text = recognizer.recognize_google(audio_data)
            else:
                # Use Sphinx (offline, less accurate)
                text = recognizer.recognize_sphinx(audio_data)
            
            return {
                "text": text.strip(),
                "provider": "google" if use_google else "sphinx"
            }
        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio")
            return {
                "text": "",
                "error": "Could not understand audio",
                "provider": "speech_recognition"
            }
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            raise
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            raise
    
    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using configured provider.
        
        Args:
            audio_path: Path to audio file
            language: Language code (optional)
            
        Returns:
            Dict with transcription text and metadata
        """
        if self.provider == TranscriptionProvider.WHISPER:
            return await self.transcribe_with_whisper(audio_path, language)
        elif self.provider == TranscriptionProvider.SPEECH_RECOGNITION:
            return await self.transcribe_with_speech_recognition(audio_path, use_google=False)
        elif self.provider == TranscriptionProvider.GOOGLE:
            return await self.transcribe_with_speech_recognition(audio_path, use_google=True)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    async def transcribe_from_url(
        self,
        audio_url: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download and transcribe audio from URL.
        
        Args:
            audio_url: URL of audio file
            language: Language code (optional)
            
        Returns:
            Dict with transcription text and metadata
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_path = temp_file.name
        
        try:
            # Download audio
            await self.download_audio(audio_url, temp_path)
            
            # Transcribe
            result = await self.transcribe(temp_path, language)
            
            return result
        finally:
            # Clean up temporary files
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Clean up WAV file if created
            wav_path = temp_path.rsplit(".", 1)[0] + ".wav"
            if os.path.exists(wav_path):
                os.remove(wav_path)


# Global transcription service instance
transcription_service = TranscriptionService(
    provider=TranscriptionProvider.WHISPER,
    whisper_model="base"  # Options: tiny, base, small, medium, large
)
