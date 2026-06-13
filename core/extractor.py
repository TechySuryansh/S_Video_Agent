# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
        max_tokens=500,  # Limit tokens to prevent cost overruns
    )


def build_chain(system_prompt: str):
    llm = get_llm()
    return (
        RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) | ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{text}"),
        ]) | llm | StrOutputParser()
    )


def extract_action_items(transcript: str) -> str:
    """Extract action items from transcript."""
    try:
        if not transcript or len(transcript.strip()) < 20:
            return "No sufficient content to extract action items."
        
        chain = build_chain(
            "You are an expert meeting analyst. From the meeting transcript, "
            "extract all action items (5 max). For each provide:\n"
            "- Task description\n"
            "- Owner (who is responsible)\n"
            "- Deadline (if mentioned, else write 'Not specified')\n\n"
            "Format as a numbered list. If none found say 'No action items found.'"
        )
        result = chain.invoke(transcript)
        return result if result else "No action items found."
    
    except Exception as e:
        logger.error(f"Action item extraction failed: {e}")
        raise


def extract_key_decisions(transcript: str) -> str:
    """Extract key decisions from transcript."""
    try:
        if not transcript or len(transcript.strip()) < 20:
            return "No sufficient content to extract decisions."
        
        chain = build_chain(
            "You are an expert meeting analyst. From the meeting transcript, "
            "extract all key decisions made (5 max). Format as a numbered list. "
            "If none found say 'No key decisions found.'"
        )
        result = chain.invoke(transcript)
        return result if result else "No key decisions found."
    
    except Exception as e:
        logger.error(f"Key decision extraction failed: {e}")
        raise


def extract_questions(transcript: str) -> str:
    """Extract unresolved questions from transcript."""
    try:
        if not transcript or len(transcript.strip()) < 20:
            return "No sufficient content to extract questions."
        
        chain = build_chain(
            "From the meeting transcript, extract all unresolved questions "
            "or topics needing follow-up (5 max). Format as a numbered list. "
            "If none found say 'No open questions found.'"
        )
        result = chain.invoke(transcript)
        return result if result else "No open questions found."
    
    except Exception as e:
        logger.error(f"Question extraction failed: {e}")
        raise