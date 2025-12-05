"""
LLM service module for handling AI conversation and summarization.
Provides abstraction layer for different LLM providers (OpenAI, Anthropic, etc.)
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from enum import Enum

import openai
from anthropic import Anthropic, AsyncAnthropic

from src.config import settings


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class MessageRole(str, Enum):
    """Message roles in conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ILLMService(ABC):
    """Interface for LLM service implementations."""
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated response text
        """
        pass
    
    @abstractmethod
    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Response text chunks
        """
        pass
    
    @abstractmethod
    async def summarize_conversation(
        self,
        conversation: str,
        focus: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Summarize a conversation into structured format.
        
        Args:
            conversation: Full conversation text
            focus: Specific focus area for summarization
            **kwargs: Additional parameters
            
        Returns:
            Dict containing summary, key_points, action_items, etc.
        """
        pass
    
    @abstractmethod
    async def extract_entities(
        self,
        text: str,
        **kwargs
    ) -> List[Dict[str, str]]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to extract entities from
            **kwargs: Additional parameters
            
        Returns:
            List of entity dicts with 'type' and 'value' keys
        """
        pass
    
    @abstractmethod
    async def analyze_sentiment(
        self,
        text: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            **kwargs: Additional parameters
            
        Returns:
            Dict containing sentiment label and score
        """
        pass


class OpenAILLMService(ILLMService):
    """OpenAI implementation of LLM service."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        openai.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate response using OpenAI API."""
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **{k: v for k, v in kwargs.items() if k != "model"}
        )
        return response.choices[0].message.content
    
    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using OpenAI API."""
        stream = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **{k: v for k, v in kwargs.items() if k != "model"}
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def summarize_conversation(
        self,
        conversation: str,
        focus: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Summarize conversation using OpenAI API."""
        system_prompt = """You are an expert at summarizing conversations for journal and diary generation.
        Extract the following information in JSON format:
        - title: A concise title for the conversation
        - summary: A comprehensive summary (2-3 paragraphs)
        - key_points: List of key points discussed (3-7 items)
        - action_items: List of action items or tasks mentioned
        - topics: List of main topics/themes
        - sentiment: Overall sentiment (positive/negative/neutral/mixed)
        - entities: Named entities mentioned (people, places, organizations)
        """
        
        if focus:
            system_prompt += f"\n\nFocus specifically on: {focus}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please summarize the following conversation:\n\n{conversation}"}
        ]
        
        response = await self.generate_response(
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        import json
        return json.loads(response)
    
    async def extract_entities(
        self,
        text: str,
        **kwargs
    ) -> List[Dict[str, str]]:
        """Extract named entities using OpenAI API."""
        messages = [
            {
                "role": "system",
                "content": """Extract named entities from the text. Return as JSON array with objects containing 'type' and 'value' keys.
                Entity types: PERSON, ORGANIZATION, LOCATION, DATE, EVENT, PRODUCT, OTHER"""
            },
            {"role": "user", "content": text}
        ]
        
        response = await self.generate_response(
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response)
        return result.get("entities", [])
    
    async def analyze_sentiment(
        self,
        text: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze sentiment using OpenAI API."""
        messages = [
            {
                "role": "system",
                "content": """Analyze the sentiment of the text. Return JSON with:
                - sentiment: one of 'positive', 'negative', 'neutral', 'mixed'
                - score: confidence score 0-1
                - explanation: brief explanation"""
            },
            {"role": "user", "content": text}
        ]
        
        response = await self.generate_response(
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        import json
        return json.loads(response)


class AnthropicLLMService(ILLMService):
    """Anthropic Claude implementation of LLM service."""
    
    def __init__(self):
        """Initialize Anthropic client."""
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate response using Anthropic API."""
        # Extract system message if present
        system_message = None
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                filtered_messages.append(msg)
        
        response = await self.client.messages.create(
            model=kwargs.get("model", self.model),
            max_tokens=max_tokens or 4096,
            temperature=temperature,
            system=system_message,
            messages=filtered_messages
        )
        
        return response.content[0].text
    
    async def generate_streaming_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using Anthropic API."""
        # Extract system message if present
        system_message = None
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                filtered_messages.append(msg)
        
        async with self.client.messages.stream(
            model=kwargs.get("model", self.model),
            max_tokens=max_tokens or 4096,
            temperature=temperature,
            system=system_message,
            messages=filtered_messages
        ) as stream:
            async for text in stream.text_stream:
                yield text
    
    async def summarize_conversation(
        self,
        conversation: str,
        focus: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Summarize conversation using Anthropic API."""
        system_prompt = """You are an expert at summarizing conversations for journal and diary generation.
        Extract the following information in JSON format:
        - title: A concise title for the conversation
        - summary: A comprehensive summary (2-3 paragraphs)
        - key_points: List of key points discussed (3-7 items)
        - action_items: List of action items or tasks mentioned
        - topics: List of main topics/themes
        - sentiment: Overall sentiment (positive/negative/neutral/mixed)
        - entities: Named entities mentioned (people, places, organizations)
        """
        
        if focus:
            system_prompt += f"\n\nFocus specifically on: {focus}"
        
        messages = [
            {"role": "user", "content": f"Please summarize the following conversation:\n\n{conversation}"}
        ]
        
        response = await self.generate_response(
            messages=messages,
            temperature=0.3,
            system=system_prompt
        )
        
        import json
        # Extract JSON from response (Claude might wrap it in markdown)
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        return json.loads(response)
    
    async def extract_entities(
        self,
        text: str,
        **kwargs
    ) -> List[Dict[str, str]]:
        """Extract named entities using Anthropic API."""
        messages = [
            {
                "role": "user",
                "content": f"""Extract named entities from the following text. Return as JSON array with objects containing 'type' and 'value' keys.
                Entity types: PERSON, ORGANIZATION, LOCATION, DATE, EVENT, PRODUCT, OTHER
                
                Text: {text}"""
            }
        ]
        
        response = await self.generate_response(messages=messages, temperature=0.3)
        
        import json
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response)
        return result if isinstance(result, list) else result.get("entities", [])
    
    async def analyze_sentiment(
        self,
        text: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze sentiment using Anthropic API."""
        messages = [
            {
                "role": "user",
                "content": f"""Analyze the sentiment of the following text. Return JSON with:
                - sentiment: one of 'positive', 'negative', 'neutral', 'mixed'
                - score: confidence score 0-1
                - explanation: brief explanation
                
                Text: {text}"""
            }
        ]
        
        response = await self.generate_response(messages=messages, temperature=0.3)
        
        import json
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        return json.loads(response)


class LLMServiceFactory:
    """Factory for creating LLM service instances."""
    
    @staticmethod
    def create(provider: LLMProvider = LLMProvider.OPENAI) -> ILLMService:
        """
        Create an LLM service instance.
        
        Args:
            provider: LLM provider to use
            
        Returns:
            ILLMService implementation
        """
        if provider == LLMProvider.OPENAI:
            return OpenAILLMService()
        elif provider == LLMProvider.ANTHROPIC:
            return AnthropicLLMService()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")


# Default LLM service instance
llm_service = LLMServiceFactory.create(LLMProvider.OPENAI)
