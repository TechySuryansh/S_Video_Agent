from core import vector_store
import os
import logging

# pyrefly: ignore [missing-import]
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from core.vector_store import build_vector_store, load_vector_store, get_retriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.3,
        max_tokens=500,  # Limit output
    )


def format_docs(docs):
    """Format retrieved documents for context."""
    if not docs:
        return "[No relevant context found]"
    return "\n\n".join([doc.page_content for doc in docs])


def build_rag_chain(transcript: str):
    """Build a RAG chain from transcript."""
    try:
        if not transcript or len(transcript.strip()) < 20:
            raise ValueError("Transcript is too short to build RAG chain")
        
        logger.info("Building vector store...")
        vector_store_obj = build_vector_store(transcript)
        
        logger.info("Building retriever...")
        retriever = get_retriever(vector_store_obj, k=4)
        
        llm = get_llm()

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
            ),
            ("human", "{question}"),
        ])

        # Full LCEL RAG pipeline
        rag_chain = (
            {
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        logger.info("RAG chain built successfully")
        return rag_chain
    
    except Exception as e:
        logger.error(f"Failed to build RAG chain: {e}")
        raise


def load_rag_chain():
    """Load a previously persisted RAG chain."""
    try:
        logger.info("Loading persisted vector store...")
        vector_store_obj = load_vector_store()
        
        retriever = get_retriever(vector_store_obj)
        llm = get_llm()
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
            ),
            ("human", "{question}"),
        ])

        rag_chain = (
            {
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        logger.info("RAG chain loaded successfully")
        return rag_chain
    
    except Exception as e:
        logger.error(f"Failed to load RAG chain: {e}")
        raise


def ask_question(rag_chain, question: str) -> str:
    """Ask a question using the RAG chain."""
    try:
        if not question or len(question.strip()) < 2:
            return "Please enter a valid question."
        
        logger.info(f"Answering question: {question[:50]}...")
        answer = rag_chain.invoke(question)
        
        if not answer or len(answer.strip()) == 0:
            return "Unable to generate an answer at this time."
        
        return answer
    
    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        return f"Error processing question: {str(e)}"