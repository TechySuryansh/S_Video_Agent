import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from utils.audio_processor import process_input
from core.gemini_service import analyze_audio, ask_question_about_transcript

def run_pipeline(source: str) -> dict:
    print("🎬 Starting AI Video Assistant (Cloud Gemini Edition)...")
    chunks = process_input(source)
    result = analyze_audio(chunks[0])
    return result

if __name__ == "__main__":
    # CLI entry point
    source = input("Enter YouTube URL or local file path: ").strip()
    if not source:
        print("❌ Error: Please enter a valid URL or file path.")
        exit(1)
        
    result = run_pipeline(source)

    print("\n" + "=" * 60)
    print(f"📌 Title: {result['title']}")
    print(f"\n📋 Summary:\n{result['summary']}")
    print(f"\n✅ Action Items:\n{result['action_items']}")
    print(f"\n🔑 Key Decisions:\n{result['key_decisions']}")
    print(f"\n❓ Open Questions:\n{result['open_questions']}")
    print("=" * 60)

    # Chat loop
    print("\n💬 Chat with your meeting (type 'exit' to quit)\n")
    chat_history = []
    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break
        if not question:
            continue
        
        print("Thinking...")
        answer = ask_question_about_transcript(result["transcript"], chat_history, question)
        print(f"\n🤖 Assistant: {answer}\n")
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "model", "content": answer})