# test_conversation_api.py
"""
==============================================================================
TEST CONSOLE FOR CONVERSATION API
==============================================================================

This script tests the 3 main functions from conversation_api.py
using console input to simulate a phone call.

Run: python test_conversation_api.py

==============================================================================
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

load_dotenv()


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def print_section(text: str):
    """Print a section divider."""
    print("\n" + "-" * 40)
    print(f" {text}")
    print("-" * 40)


def main():
    print_header("🧪 CONVERSATION API TEST CONSOLE")
    print("""
This tests the 3 main functions:
  1. start_conversation(phone_number)
  2. process_message(text)
  3. end_conversation()

Simulates a phone call using console input.
    """)

    # Import the API functions
    print("Loading conversation API...")
    try:
        from utils.conversation_api import (
            start_conversation,
            process_message,
            end_conversation,
            get_user_by_phone
        )
        print("✅ API loaded successfully!\n")
    except Exception as e:
        print(f"❌ Failed to load API: {e}")
        print("\nMake sure your .env file has:")
        print("  - OPENAI_API_KEY")
        print("  - Database credentials (DB_HOST, DB_USER, etc.)")
        print("  - PINECONE_API_KEY (optional)")
        return

    # Get phone number or user ID
    print_section("Step 0: Identify User")
    print("Enter phone number (or press Enter to use user_id=1):")
    phone_input = input("> ").strip()

    user_id = None
    phone_number = None

    if phone_input:
        phone_number = phone_input
        user = get_user_by_phone(phone_number)
        if user:
            print(f"✅ Found user: ID={user.id}, Phone={user.phone_number}")
        else:
            print(f"❌ User not found with phone: {phone_number}")
            print("Using user_id=1 instead...")
            user_id = 1
    else:
        user_id = 1
        print(f"Using user_id={user_id}")

    # ==============================================================================
    # TEST 1: start_conversation()
    # ==============================================================================
    print_section("Step 1: start_conversation()")
    print("Simulating: User answers the phone...\n")

    try:
        if phone_number:
            opening_message = start_conversation(phone_number=phone_number)
        else:
            opening_message = start_conversation(user_id=user_id)

        print("🤖 AI (Opening Message):")
        print(f"   \"{opening_message}\"")
        print("\n   [This would be sent to TTS → played to user]")
        print("\n✅ start_conversation() successful!")
    except Exception as e:
        print(f"❌ start_conversation() failed: {e}")
        return

    # ==============================================================================
    # TEST 2: process_message() - Multiple rounds
    # ==============================================================================
    print_section("Step 2: process_message()")
    print("""
Now simulate the conversation.
Type what the user "says" (as if from Speech-to-Text).

Commands:
  - Type a message to chat
  - Type 'stream' to test streaming mode
  - Type 'end' to end the conversation
  - Type 'quit' to exit without saving
    """)

    message_count = 0

    while True:
        print("\n🎤 User (from STT):", end=" ")
        user_input = input().strip()

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            print("\n👋 Exiting without saving...")
            return

        if user_input.lower() == 'end':
            break

        if user_input.lower() == 'stream':
            # Test streaming mode
            print("\n📝 Testing streaming mode...")
            print("🎤 Enter message for streaming test:", end=" ")
            stream_input = input().strip()

            if stream_input:
                print("\n🤖 AI (Streaming):")
                print("   \"", end="", flush=True)
                try:
                    for chunk in process_message(stream_input, stream=True):
                        print(chunk, end="", flush=True)
                    print("\"")
                    print("\n✅ Streaming test successful!")
                    message_count += 1
                except Exception as e:
                    print(f"\n❌ Streaming failed: {e}")
            continue

        # Normal message processing
        try:
            response = process_message(user_input)
            message_count += 1

            print("\n🤖 AI Response:")
            print(f"   \"{response}\"")
            print("\n   [This would be sent to TTS → played to user]")
        except Exception as e:
            print(f"❌ process_message() failed: {e}")

    # ==============================================================================
    # TEST 3: end_conversation()
    # ==============================================================================
    print_section("Step 3: end_conversation()")
    print("Simulating: User hangs up...\n")
    print("Generating journal (this may take a moment)...\n")

    try:
        result = end_conversation()

        print("✅ end_conversation() successful!\n")
        print("📊 Results:")
        print(f"   Conversation ID: {result.get('conversation_id')}")
        print(f"   Duration: {result.get('duration_seconds', 0)} seconds")
        print(f"   Journal ID: {result.get('journal_id')}")
        print(f"   Journal Path: {result.get('journal_path')}")

        topics = result.get('topics', [])
        if topics:
            print(f"\n   📌 Topics: {', '.join(topics)}")

        emotions = result.get('emotions', {})
        if emotions:
            print("\n   😊 Emotions Detected:")
            sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
            for emotion, score in sorted_emotions:
                if score > 0:
                    bar = "█" * int(score * 10)
                    print(f"      {emotion:12}: {bar} {score:.0%}")

        # Show journal content if available
        journal_path = result.get('journal_path')
        if journal_path and os.path.exists(journal_path):
            print_section("📔 Generated Journal")
            with open(journal_path, 'r', encoding='utf-8') as f:
                print(f.read())

    except Exception as e:
        print(f"❌ end_conversation() failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # ==============================================================================
    # Summary
    # ==============================================================================
    print_header("✅ TEST COMPLETE")
    print(f"""
Summary:
  - Messages exchanged: {message_count}
  - Journal generated: {'Yes' if result.get('journal_id') else 'No'}
  - Topics extracted: {len(topics)}
  - Emotions analyzed: {len([e for e, s in emotions.items() if s > 0])}

All 3 API functions working correctly!
    """)


if __name__ == "__main__":
    main()