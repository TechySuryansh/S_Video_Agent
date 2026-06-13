# pyrefly: ignore [missing-import]
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.3,
        max_tokens=500,  # Limit tokens to prevent cost overruns
    )


def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200
    )
    return splitter.split_text(transcript)


def summarize(transcript: str) -> str:
    """Generate a map-reduce summary of the transcript."""
    try:
        if not transcript or len(transcript.strip()) < 20:
            return "No sufficient content to summarize."
        
        llm = get_llm()
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", "Summarize this portion of a meeting transcript concisely in 2-3 sentences."),
            ("human", "{text}"),
        ])
        map_chain = map_prompt | llm | StrOutputParser()
        chunks = split_transcript(transcript)

        logger.info(f"Summarizing {len(chunks)} chunks...")
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            try:
                summary = map_chain.invoke({"text": chunk})
                chunk_summaries.append(summary)
            except Exception as e:
                logger.warning(f"Failed to summarize chunk {i}: {e}")
                chunk_summaries.append("[Summarization failed for this section]")

        combined = "\n\n".join(chunk_summaries)

        combined_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert meeting summarizer. Combine these partial summaries "
                "into one final professional meeting summary in 5-7 bullet points. Be concise.",
            ),
            ("human", "{text}"),
        ])

        combined_chain = (
            RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) | combined_prompt | llm | StrOutputParser()
        )

        return combined_chain.invoke(combined)
    
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise


def generate_title(transcript: str) -> str:
    """Generate a concise title from the transcript."""
    try:
        if not transcript or len(transcript.strip()) < 10:
            return "Untitled Meeting"
        
        llm = get_llm()

        title_chain = (
            RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) |
            ChatPromptTemplate.from_messages([
                (
                    "system",
                    "Based on the meeting transcript, generate a short professional meeting title "
                    "(max 8 words). Return ONLY the title, nothing else.",
                ),
                ("human", "{text}"),
            ])
            | llm
            | StrOutputParser()
        )

        title = title_chain.invoke(transcript[:2000])
        return title.strip() if title else "Untitled Meeting"
    
    except Exception as e:
        logger.error(f"Title generation failed: {e}")
        raise
    
