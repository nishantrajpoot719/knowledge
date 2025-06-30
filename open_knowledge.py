import os
import re
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

import dspy
import numpy as np
from dotenv import load_dotenv
from agno.agent import Agent, AgentKnowledge
from agno.tools import tool
from agno.models.groq import Groq as GroqModel
from agno.embedder.google import GeminiEmbedder
from pydantic import Json
from faqs_system_prompts import FAQs_system_prompt

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables with error handling
def get_env_variable(name: str, default: Optional[str] = None) -> str:
    """Get environment variable or raise an error if not found and no default provided."""
    value = os.getenv(name, default)
    if value is None:
        error_msg = f"Environment variable {name} is not set"
        logger.error(error_msg)
        raise ValueError(error_msg)
    return value

# Configure DSPy with environment variables
try:
    GROQ_API_KEY = get_env_variable("GROQ_API_KEY")
    GEMINI_API_KEY = get_env_variable("GEMINI_API_KEY")
    
    dspy.configure(
        lm=dspy.LM(
            model='openai/meta-llama/llama-4-maverick-17b-128e-instruct',
            api_key=GROQ_API_KEY,
            api_base="https://api.groq.com/openai/v1"
        )
    )
except ValueError as e:
    logger.error(f"Failed to initialize DSPy: {e}")
    raise

# @tool
# def embed_text(text: str) -> np.ndarray:
#     """Generate embeddings for the given text using Gemini API."""
#     try:
#         if not text or not isinstance(text, str):
#             raise ValueError("Text must be a non-empty string")
            
#         embedder = GeminiEmbedder(api_key=GEMINI_API_KEY)
#         return embedder.get_embedding(text)
#     except Exception as e:
#         logger.error(f"Error generating embeddings: {str(e)}")
#         raise

# def loading_knowledge() -> List[Dict[str, str]]:
#     """Load and parse the FAQ markdown file.
    
#     Returns:
#         List of dictionaries containing 'title' and 'content' for each FAQ entry.
#     """
#     try:
#         # Use pathlib for better path handling
#         faq_path = Path(__file__).parent / "faq.md"
        
#         # Check if file exists
#         if not faq_path.exists():
#             error_msg = f"FAQ file not found at {faq_path}"
#             logger.error(error_msg)
#             raise FileNotFoundError(error_msg)
            
#         # Check file size (e.g., 5MB limit)
#         if faq_path.stat().st_size > 5 * 1024 * 1024:
#             error_msg = "FAQ file is too large (max 5MB)"
#             logger.error(error_msg)
#             raise ValueError(error_msg)
            
#         with open(faq_path, "r", encoding="utf-8") as f:
#             faq_text = f.read()
            
#         if not faq_text.strip():
#             logger.warning("FAQ file is empty")
#             return []
            
#         sections = re.split(r'(?m)^##\s+', faq_text)[1:]
#         faq_entries = []
        
#         for section in sections:
#             try:
#                 if '\n' in section:
#                     title, content = section.split('\n', 1)
#                     faq_entries.append({
#                         "title": title.strip(),
#                         "content": content.strip()
#                     })
#             except Exception as e:
#                 logger.warning(f"Error parsing FAQ section: {str(e)}")
#                 continue
                
#         if not faq_entries:
#             logger.warning("No valid FAQ entries found in the file")
            
#         return faq_entries

#     except Exception as e:
#         logger.error(f"Error loading FAQs: {str(e)}")
#         raise

# def knowledge_embeddings() -> list:
#     """Generate embeddings for all FAQ entries.
    
#     Returns:
#         List of embeddings for each FAQ entry.
#     """
#     try:
#         faqs = loading_knowledge()
#         if not faqs:
#             logger.warning("No FAQs to embed")
#             return []
            
#         faq_embeddings = []
#         for entry in faqs:
#             try:
#                 text = f"{entry.get('title', '')} {entry.get('content', '')}".strip()
#                 if text:
#                     embedding = embed_text(text)
#                     faq_embeddings.append(embedding)
#             except Exception as e:
#                 logger.error(f"Failed to generate embedding for FAQ entry: {str(e)}")
#                 continue
                
#         if not faq_embeddings:
#             logger.error("No valid embeddings generated")
#             return []
            
#         return faq_embeddings

#     except Exception as e:
#         logger.error(f"Error in knowledge_embeddings: {str(e)}")
#         raise

# # Initialize knowledge base when the module is imported
# try:
#     knowledge_base = knowledge_embeddings()
# except Exception as e:
#     logger.critical(f"Failed to initialize knowledge base: {str(e)}")
#     knowledge_base = []

class KnowledgeSummarySignature(dspy.Signature):
    """You have to summarize the final answer of the tool"""
    user_query : str = dspy.InputField(desc="user's query")
    retrieved_knowledge : str = dspy.InputField(desc="retrieved relevant knowledge from the knowledge base")
    answer : str = dspy.OutputField(desc="summarized answer")

class KnowledgeSummarizer(dspy.Module):
    def __init__(self):
        self.predict = dspy.Predict(KnowledgeSummarySignature)
    
    def forward(self, user_query:str, retrieved_knowledge:str) -> str:
        try:
            result  = self.predict(user_query=user_query, retrieved_knowledge=retrieved_knowledge)
            return result.answer

        except Exception as e:
            return f"Error summarizing knowledge: {str(e)}"


class Knowledge_Agent:
    """Agent for handling knowledge-based queries using LLM and embeddings."""

    def __init__(self):
        """Initialize the Knowledge Agent with LLM and configuration."""
        try:
            # Get API key from environment
            groq_api_key = get_env_variable("GROQ_API_KEY")
            # self.knowledge_base = knowledge_base
            
            # Initialize LLM with error handling
            self.llm = GroqModel(
                api_key=groq_api_key,
                id="meta-llama/llama-4-maverick-17b-128e-instruct",
                temperature=0.7
            )

            # Initialize agent with configuration
            self.agent = Agent(
                name="Knowledge Agent",
                role=("Handles user's request in case of general enquiry about the company, "
                     "their products, or any other general FAQs related queries"),
                model=self.llm,
                # knowledge = self.knowledge_base,
                # search_knowledge = True,
                # tools = [embed_text],
                # show_tool_calls = True,
                instructions=[
                    FAQs_system_prompt,
                    "To answer any Knowledge related query refer to the instruction given in the FAQs_system_prompt. There is no need to generate a response on your own without confirming from the knowledge. If you doesn't find relevant information just humbly reply the reason, but no need to generate wrong information"
                ],
                markdown=True,
                debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true"
            )
            
            logger.info("Knowledge Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Knowledge_Agent: {str(e)}")
            raise

    def process_user_query(self, user_query: str):
        """Process user query using agent to provide the most relevant answer.
        
        Args:
            user_query: summary of the user queries, and what information user wants to know.
            
        Returns:
            The agent's response to the query in json format [{"role": "user", "content": f"{user_query}",{"role": "assistant", "content": f"{response}"}].
        """
        if not user_query or not isinstance(user_query, str):
            error_msg = "Invalid input: user_query must be a non-empty list of message dictionaries"
            logger.error(error_msg)
            return "Invalid input format. Please provide a valid query."
            
        try:
            logger.info("Processing query: ...") 
            
            response = self.agent.run(
                message=user_query,
                verbose=os.getenv("VERBOSE_LOGGING", "false").lower() == "true"
            )
            
            # Ensure the response is a string
            result = str(response.content) if hasattr(response, 'content') else str(response)
            logger.info("Query processed successfully")
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing user query: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return "I'm sorry, but I encountered an error while processing your request. Please try again later."


def main():
    agent = Knowledge_Agent()

    try:
        user_input = input()
        response = agent.process_user_query(user_input)
        print(response)

    except Exception as e:
        print(f"Error processing user query: {e}")
        return "Oops! Something went wrong on my end. Let's give it another try."

if __name__ == "__main__":
    main()
