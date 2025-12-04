# services/llm_service.py
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config.settings import get_settings


class LLMService:
    """Service for interacting with LLM (GPT-4o) via LangChain."""

    SYSTEM_PROMPT = """You are a compassionate AI companion for a mental wellness diary application. 
                    Your role is to:
                    1. Guide users through reflective conversations about their day
                    2. Ask thoughtful follow-up questions to help them process their feelings
                    3. Be empathetic, supportive, and non-judgmental
                    4. Help users identify patterns in their emotions and thoughts
                    5. Encourage self-reflection without being pushy
                    
                    Keep your responses conversational and warm. Avoid being overly clinical or formal.
                    If the user shares something concerning about their mental health, gently acknowledge it 
                    and remind them that professional support is available if needed.
                    
                    Previous context from past journals (if available):
                    {rag_context}
                    """

    def __init__(self):
        self.settings = get_settings()
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            api_key=self.settings.openai_api_key,
            temperature=0.7,
            streaming=True
        )
        self.conversation_history: list = []
        self.rag_context: str = ""

    def set_rag_context(self, context: str):
        """Set RAG context from past journals."""
        self.rag_context = context

    def clear_history(self):
        """Clear conversation history for new session."""
        self.conversation_history = []
        self.rag_context = ""

    def get_system_message(self) -> SystemMessage:
        """Get system message with RAG context."""
        context = self.rag_context if self.rag_context else "No previous context available."
        return SystemMessage(content=self.SYSTEM_PROMPT.format(rag_context=context))

    def chat(self, user_message: str) -> str:
        """Send a message and get a response."""
        # Add user message to history
        self.conversation_history.append(HumanMessage(content=user_message))

        # Build messages list
        messages = [self.get_system_message()] + self.conversation_history

        # Get response
        response = self.llm.invoke(messages)

        # Add assistant response to history
        self.conversation_history.append(AIMessage(content=response.content))

        return response.content

    def chat_stream(self, user_message: str):
        """Send a message and stream the response."""
        # Add user message to history
        self.conversation_history.append(HumanMessage(content=user_message))

        # Build messages list
        messages = [self.get_system_message()] + self.conversation_history

        # Stream response
        full_response = ""
        for chunk in self.llm.stream(messages):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content

        # Add complete response to history
        self.conversation_history.append(AIMessage(content=full_response))

    def generate_journal_summary(self, conversation_transcript: list[dict]) -> str:
        """Generate a journal summary from conversation transcript."""
        transcript_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_transcript
        ])

        summary_prompt = f"""Based on the following conversation, create a reflective journal entry summary.

        Include:
        1. Main topics discussed
        2. Key emotions expressed
        3. Any insights or realizations the user had
        4. Progress notes if applicable

        Conversation:
        {transcript_text}

        IMPORTANT FORMATTING RULES:
        - Write the summary in first person as if the user wrote it
        - Keep it personal and reflective
        - Use plain text paragraphs only (NO markdown, NO headers, NO bullet points, NO code blocks)
        - Write naturally flowing prose, 2-4 paragraphs
        - Do NOT include any formatting symbols like #, *, -, or ```
        """

        messages = [
            SystemMessage(content="You are a helpful assistant that creates journal summaries."),
            HumanMessage(content=summary_prompt)
        ]

        response = self.llm.invoke(messages)
        return response.content

    def extract_topics(self, text: str) -> list[str]:
        """Extract topics from text using LLM."""
        prompt = f"""Extract the main topics from this text. Return only a JSON array of topic strings.
Topics should be single words or short phrases like: "work", "stress", "relationships", "sleep", "exercise", etc.

Text: {text}

Return ONLY a JSON array, nothing else. Example: ["work", "stress", "sleep"]"""

        messages = [
            SystemMessage(content="You extract topics from text and return them as a JSON array."),
            HumanMessage(content=prompt)
        ]

        response = self.llm.invoke(messages)

        # Parse response - basic parsing
        import json
        try:
            topics = json.loads(response.content.strip())
            return topics if isinstance(topics, list) else []
        except json.JSONDecodeError:
            return []

    def analyze_emotions(self, text: str) -> dict:
        """Analyze emotions in text using LLM."""
        prompt = f"""You are an emotion analysis expert. Carefully read the following journal text and analyze the emotional content.

        For each emotion, assign a score from 0.0 to 1.0 based on how strongly that emotion is expressed or implied in the text:
        - 0.0 = emotion not present at all
        - 0.3 = slightly present / mild
        - 0.5 = moderately present
        - 0.7 = strongly present
        - 1.0 = dominant / overwhelming

        Text to analyze:
        \"\"\"
        {text}
        \"\"\"

        Analyze the text above and provide scores for these 8 emotions:
        1. anxiety - worry, nervousness, unease about future
        2. depression - deep sadness, hopelessness, low mood
        3. stress - feeling overwhelmed, pressure, tension
        4. sadness - grief, sorrow, disappointment
        5. happiness - joy, pleasure, positive feelings
        6. relief - feeling of reassurance after worry
        7. anger - frustration, irritation, annoyance
        8. contentment - peaceful satisfaction, calm acceptance

        IMPORTANT: Actually analyze the text content. Do NOT return all zeros. Most journal entries contain some emotional content.

        Return ONLY a valid JSON object with all 8 emotions. Example format:
        {{"anxiety": 0.4, "depression": 0.1, "stress": 0.6, "sadness": 0.2, "happiness": 0.3, "relief": 0.5, "anger": 0.0, "contentment": 0.4}}"""

        messages = [
            SystemMessage(content="You are an expert emotion analyst. You carefully read text and accurately identify "
                                  "emotional content, returning precise scores as JSON. "
                                  "You never return all zeros unless the text is completely emotionless."),
            HumanMessage(content=prompt)
        ]

        response = self.llm.invoke(messages)

        import json
        import re
        try:
            response_text = response.content.strip()

            # Remove markdown code blocks (handles ```json\n...\n``` format)
            # Pattern matches ```json or ``` at start, and ``` at end
            response_text = re.sub(r'^```(?:json)?\s*\n?', '', response_text)
            response_text = re.sub(r'\n?```\s*$', '', response_text)
            response_text = response_text.strip()

            emotions = json.loads(response_text)
            return emotions if isinstance(emotions, dict) else {}
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response was: {response.content}")
            return {}

    def get_opening_message(self, user_name: str = "there", previous_context: Optional[str] = None) -> str:
        """Generate an opening message for a new conversation."""
        if previous_context:
            prompt = f"""Generate a warm, personalized opening message for a mental wellness check-in.
                    The user's name is {user_name}.
                    Here's some context from their previous journal: {previous_context}
                    
                    Reference something specific from their past entry to show continuity.
                    Keep it brief and conversational (1-2 sentences + a question).
            """
        else:
            prompt = f"""Generate a warm opening message for a mental wellness check-in.
                        The user's name is {user_name}.
                        This is their first conversation, so keep it simple and welcoming.
                        Keep it brief and conversational (1-2 sentences + a question).
                    """

        messages = [
            SystemMessage(content="You are a compassionate AI wellness companion."),
            HumanMessage(content=prompt)
        ]

        response = self.llm.invoke(messages)
        return response.content
