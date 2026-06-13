from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all

# pyrefly: ignore [missing-import]
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

import traceback
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def run_pipeline(source: str, language: str = "english") -> dict:
    """Run the complete video analysis pipeline."""
    try:
        print("\n" + "=" * 60)
        print("🎬 Starting AI Video Assistant")
        print("=" * 60)
        
        print("\n📍 Stage 1: Audio Processing...")
        chunks = process_input(source)

        print("\n📍 Stage 2: Transcription...")
        transcript = transcribe_all(chunks, language)
        
        if not transcript or len(transcript.strip()) < 10:
            raise ValueError("Transcription failed - result is empty")
        
        print(f"✓ Transcribed {len(transcript)} characters")
        print(f"  Preview: {transcript[:100]}...")

        print("\n📍 Stage 3: Title Generation...")
        title = generate_title(transcript)
        print(f"✓ Title: {title}")

        print("\n📍 Stage 4: Summarization...")
        summary = summarize(transcript)
        print(f"✓ Summary length: {len(summary)} characters")

        print("\n📍 Stage 5: Extraction (Parallel)...")
        action_item = extract_action_items(transcript)
        print(f"  ✓ Action items extracted")
        
        decisions = extract_key_decisions(transcript)
        print(f"  ✓ Decisions extracted")
        
        questions = extract_questions(transcript)
        print(f"  ✓ Questions extracted")

        print("\n📍 Stage 6: RAG Engine Setup...")
        rag_chain = build_rag_chain(transcript)
        print(f"✓ RAG chain ready for questions")

        print("\n✅ Pipeline complete!\n")

        return {
            "title": title,
            "transcript": transcript,
            "summary": summary,
            "action_items": action_item,
            "key_decisions": decisions,
            "open_questions": questions,
            "rag_chain": rag_chain,
        }
    
    except Exception as e:
        print(f"\n❌ Pipeline failed at a stage")
        print(f"Error: {str(e)}\n")
        logger.error(f"Pipeline error: {e}")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # CLI entry point
    try:
        print("\n🎬 AI Video Assistant (CLI Mode)\n")
        
        source = input("Enter YouTube URL or local file path: ").strip()
        if not source:
            print("❌ Please provide a valid URL or file path")
            exit(1)
        
        language = input("Language (english/hinglish) [default: english]: ").strip() or "english"
        
        # Run pipeline
        result = run_pipeline(source, language)

        # Display results
        print("\n" + "=" * 60)
        print("📊 RESULTS")
        print("=" * 60)
        print(f"\n📌 Title:\n{result['title']}")
        print(f"\n📋 Summary:\n{result['summary']}")
        print(f"\n✅ Action Items:\n{result['action_items']}")
        print(f"\n🔑 Key Decisions:\n{result['key_decisions']}")
        print(f"\n❓ Open Questions:\n{result['open_questions']}")
        print("\n" + "=" * 60)

        # Phase 2 — Chat with your meeting via RAG
        print("\n💬 Chat with your meeting (type 'exit' to quit)\n")
        rag_chain = result["rag_chain"]
        while True:
            question = input("You: ").strip()
            if question.lower() in ["exit", "quit", "q"]:
                print("👋 Goodbye!")
                break
            if not question:
                continue
            
            try:
                answer = ask_question(rag_chain, question)
                print(f"\n🤖 Assistant: {answer}\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")
                logger.error(f"Q&A error: {e}")

    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        exit(1)