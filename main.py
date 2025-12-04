#!/usr/bin/env python3
# main.py
"""
Console-based demo for AI-Powered Conversational Diary.

This demo simulates the conversation flow through text input/output.
Type your messages and press Enter. Type 'end' to finish the conversation.
"""

import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from config.settings import get_settings
from models.entities import User, EmotionScore
from db.connection import get_db_connection
from dao.user_dao import UserDAO
from dao.conversation_dao import ConversationDAO
from dao.journal_dao import JournalDAO
from services.llm_service import LLMService
from services.embedding_service import EmbeddingService
from services.journal_service import JournalService
from services.conversation_service import ConversationService
from utils.mock_data import MockDataGenerator, MockUserDAO, MockConversationDAO, MockJournalDAO


def print_header():
    """Print application header."""
    print("\n" + "=" * 60)
    print("🌙 AI-Powered Conversational Diary")
    print("   Mental Wellness Check-in Demo")
    print("=" * 60)
    print("\nType your messages and press Enter.")
    print("Type 'end' to finish the conversation and generate journal.")
    print("Type 'quit' to exit without saving.")
    print("Type 'history' to see conversation history.")
    print("-" * 60 + "\n")


def print_assistant_message(message: str):
    """Print assistant message with formatting."""
    print(f"\n🤖 Assistant: {message}\n")


def print_user_prompt():
    """Print user input prompt."""
    print("👤 You: ", end="")


def print_journal_summary(result: dict):
    """Print journal generation summary."""
    print("\n" + "=" * 60)
    print("📔 Conversation Summary")
    print("=" * 60)
    print(f"  Conversation ID: {result.get('conversation_id')}")
    print(f"  Duration: {result.get('duration_seconds', 0) // 60} minutes {result.get('duration_seconds', 0) % 60} seconds")
    if result.get('journal_id'):
        print(f"  Journal ID: {result.get('journal_id')}")
        print(f"  Journal Path: {result.get('journal_path')}")
        if result.get('topics'):
            print(f"  Topics: {', '.join(result.get('topics', []))}")
        if result.get('emotions'):
            emotions = result.get('emotions', {})
            top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"  Top Emotions: {', '.join([f'{e[0]}: {e[1]:.0%}' for e in top_emotions if e[1] > 0])}")
    print("=" * 60 + "\n")


def print_journal_content(journal_path: str):
    """Print the generated journal markdown content."""
    if os.path.exists(journal_path):
        print("\n" + "=" * 60)
        print("📝 Generated Journal Entry")
        print("=" * 60)
        with open(journal_path, "r", encoding="utf-8") as f:
            print(f.read())
        print("=" * 60 + "\n")


def run_demo_with_mock_llm():
    """Run demo with mock LLM responses (no API key needed)."""
    print("\n⚠️  Running in MOCK MODE (no OpenAI API key detected)")
    print("   Using pre-defined responses for demonstration.\n")
    
    mock_responses = [
        "Hi there! How was your day today? I'd love to hear what's been on your mind.",
        "I hear you. Work presentations can definitely bring up a lot of anxiety. How did it go in the end?",
        "It sounds like the anticipation was worse than the actual event - that's often the case! How are you feeling now that it's over?",
        "That's completely understandable. Sleep and anxiety often go hand in hand. Have you tried any relaxation techniques before bed?",
        "Those are great ideas! Even small changes to your evening routine can make a big difference. Is there anything else you'd like to talk about tonight?",
        "Thank you for sharing with me today. Remember, it's okay to feel stressed sometimes - what matters is how we take care of ourselves. Take care, and I'll check in with you again soon! 💙"
    ]
    
    print_header()
    
    response_index = 0
    conversation_messages = []
    
    # Opening message
    opening = mock_responses[response_index]
    print_assistant_message(opening)
    conversation_messages.append({"role": "assistant", "content": opening})
    response_index += 1
    
    while True:
        print_user_prompt()
        user_input = input().strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("\n👋 Goodbye! Session ended without saving.\n")
            break
        
        if user_input.lower() == 'end':
            # Final response
            if response_index < len(mock_responses):
                final_response = mock_responses[-1]
                print_assistant_message(final_response)
            
            print_journal_summary({
                "conversation_id": 1,
                "duration_seconds": 300,
                "journal_id": 1,
                "journal_path": f"./journals/{datetime.now().strftime('%Y-%m-%d')}/journal_mock.md"
            })
            break
        
        conversation_messages.append({"role": "user", "content": user_input})
        
        # Get mock response
        if response_index < len(mock_responses) - 1:
            response = mock_responses[response_index]
            response_index += 1
        else:
            response = "Thank you for sharing that. Is there anything else you'd like to discuss?"
        
        print_assistant_message(response)
        conversation_messages.append({"role": "assistant", "content": response})


def run_demo_with_real_llm(use_database: bool = True):
    """
    Run demo with real LLM and full service integration.
    
    Args:
        use_database: If True, use real PostgreSQL. If False, use mock DAOs.
    """
    print("\n✅ OpenAI API key detected. Running with real LLM.")
    
    # Initialize services
    llm_service = LLMService()
    embedding_service = EmbeddingService()
    
    if use_database:
        print("📦 Connecting to PostgreSQL database...")
        try:
            # Test database connection
            db = get_db_connection()
            db.connect()
            print("✅ Database connected successfully!\n")
            
            # Initialize real DAOs
            user_dao = UserDAO(db)
            conversation_dao = ConversationDAO(db)
            journal_dao = JournalDAO(db)
            
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            print("   Falling back to mock DAOs...\n")
            use_database = False
    
    if not use_database:
        print("📦 Using mock DAOs (no database)...\n")
        user_dao = MockUserDAO()
        conversation_dao = MockConversationDAO()
        journal_dao = MockJournalDAO()
    
    # Initialize services with DAOs
    journal_service = JournalService(
        journal_dao=journal_dao,
        llm_service=llm_service,
        embedding_service=embedding_service
    )
    
    conversation_service = ConversationService(
        user_dao=user_dao,
        conversation_dao=conversation_dao,
        llm_service=llm_service,
        embedding_service=embedding_service,
        journal_service=journal_service
    )
    
    # Get or create user
    print("👤 Setting up user...")
    user = user_dao.get_by_id(1)
    if not user:
        print("   Creating new user...")
        user = User(
            phone_number="+12345678888",
            timezone="America/New_York"
        )
        user = user_dao.create(user)
        print(f"   Created user with ID: {user.id}")
    else:
        print(f"   Found existing user with ID: {user.id}")
    
    print_header()
    
    # Start conversation using ConversationService
    try:
        print("⏳ Starting conversation...\n")
        opening_message = conversation_service.start_conversation(
            user_id=user.id,
            # twilio_call_sid=f"DEMO_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        print_assistant_message(opening_message)
        
    except Exception as e:
        print(f"\n❌ Error starting conversation: {e}")
        print("   Please check your OpenAI API key.\n")
        return
    
    # Main conversation loop
    while True:
        print_user_prompt()
        try:
            user_input = input().strip()
        except EOFError:
            break
        
        if not user_input:
            continue
        
        # Handle special commands
        if user_input.lower() == 'quit':
            print("\n👋 Goodbye! Session ended without saving.\n")
            break
        
        if user_input.lower() == 'history':
            history = conversation_service.get_conversation_history()
            print("\n📜 Conversation History:")
            print("-" * 40)
            for msg in history:
                role = "🤖" if msg["role"] == "assistant" else "👤"
                print(f"{role} {msg['role'].upper()}: {msg['content'][:100]}...")
            print("-" * 40 + "\n")
            continue
        
        if user_input.lower() == 'end':
            print("\n⏳ Ending conversation and generating journal...\n")
            
            try:
                # End conversation - this triggers journal generation
                result = conversation_service.end_conversation()
                
                if result:
                    # Enhance result with journal details if available
                    if result.get('journal_id') and hasattr(journal_dao, 'get_by_id'):
                        journal = journal_dao.get_by_id(result['journal_id'])
                        if journal:
                            result['topics'] = journal.topics
                            result['emotions'] = journal.detected_emotions.to_dict()
                    
                    print_journal_summary(result)
                    
                    # Print the actual journal content
                    if result.get('journal_path'):
                        print_journal_content(result['journal_path'])
                else:
                    print("⚠️  No journal generated (conversation too short).\n")
                    
            except Exception as e:
                print(f"\n❌ Error ending conversation: {e}")
                import traceback
                traceback.print_exc()
            
            break
        
        # Process user message through ConversationService
        try:
            print("\n🤖 Assistant: ", end="", flush=True)
            
            # Use streaming response
            for chunk in conversation_service.process_user_message_stream(user_input):
                print(chunk, end="", flush=True)
            print("\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("   Please try again.\n")


def run_demo_with_mock_dao():
    """Run demo with real LLM but mock DAOs (no database needed)."""
    run_demo_with_real_llm(use_database=False)


def show_menu():
    """Show main menu and get user choice."""
    settings = get_settings()
    has_api_key = bool(settings.openai_api_key)
    
    print("\n" + "=" * 60)
    print("🌙 AI-Powered Conversational Diary")
    print("=" * 60)
    print("\nSelect mode:\n")
    
    if has_api_key:
        print("  1. Full Demo (Real LLM + Database)")
        print("  2. LLM Demo (Real LLM + Mock Database)")
        print("  3. Mock Demo (No API needed)")
    else:
        print("  1. Mock Demo (No API key detected)")
        print("\n  ⚠️  Set OPENAI_API_KEY in .env for full features")
    
    print("\n  q. Quit")
    print("-" * 60)
    
    choice = input("\nEnter choice: ").strip().lower()
    return choice, has_api_key


def main():
    """Main entry point."""
    choice, has_api_key = show_menu()
    
    if choice == 'q':
        print("\n👋 Goodbye!\n")
        return
    
    if has_api_key:
        if choice == '1':
            run_demo_with_real_llm(use_database=True)
        elif choice == '2':
            run_demo_with_real_llm(use_database=False)
        elif choice == '3':
            run_demo_with_mock_llm()
        else:
            print("Invalid choice. Running default demo...")
            run_demo_with_real_llm(use_database=False)
    else:
        run_demo_with_mock_llm()


if __name__ == "__main__":
    main()