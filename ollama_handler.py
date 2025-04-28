"""
Ollama API Handler for DeepSeek Chat

This module provides functions for interacting with the Ollama API,
sending prompts and processing responses.
"""

import requests
import re
import logging
import subprocess
import json
from typing import Dict, Any, Optional, List

# Try to import the RAG handler
try:
    from rag_handler import RAGHandler
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("RAG functionality not available. To enable, install required packages.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global RAG handler instance
rag_handler = None

def initialize_rag(model_name="deepseek-r1:1.5b"):
    """
    Initialize the RAG system if available.
    
    Args:
        model_name: The model to use for the RAG system
        
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    global rag_handler
    
    if not RAG_AVAILABLE:
        logger.warning("RAG functionality not available. Missing rag_handler module.")
        return False
    
    try:
        rag_handler = RAGHandler(model_name=model_name)
        return rag_handler.is_enabled()
    except Exception as e:
        logger.error(f"Error initializing RAG system: {str(e)}")
        return False

def load_rag_documents(documents: List[Dict[str, str]]) -> bool:
    """
    Load documents into the RAG system.
    
    Args:
        documents: List of document dictionaries with 'content' and 'metadata'
        
    Returns:
        bool: True if successful, False otherwise
    """
    global rag_handler
    
    if not rag_handler:
        success = initialize_rag()
        if not success:
            return False
    
    return rag_handler.load_documents(documents)

def load_rag_from_urls(urls: List[str]) -> bool:
    """
    Load documents from URLs into the RAG system.
    
    Args:
        urls: List of URLs to load
        
    Returns:
        bool: True if successful, False otherwise
    """
    global rag_handler
    
    if not rag_handler:
        success = initialize_rag()
        if not success:
            return False
    
    return rag_handler.load_from_urls(urls)

def send_prompt_to_ollama(prompt, model="deepseek-r1:1.5b", timeout=300, temperature=0.7, use_rag=False):
    """
    Send a prompt to the Ollama API and return the response with thinking sections removed.
    
    Args:
        prompt (str): The prompt to send to Ollama
        model (str): The model to use, defaults to "deepseek-r1:1.5b"
        timeout (int): Request timeout in seconds (5 minutes by default)
        temperature (float): Sampling temperature (higher = more creative, lower = more deterministic)
        use_rag (bool): Whether to use RAG if available
        
    Returns:
        tuple: The processed response from Ollama and a boolean indicating whether RAG was used
        
    Raises:
        Exception: If there's an error connecting to Ollama or processing the response
    """
    try:
        # If RAG is enabled and available, use it
        rag_used = False
        if use_rag and rag_handler is not None and rag_handler.is_enabled():
            logger.info(f"Using RAG for prompt: {prompt[:50]}...")
            response, context = rag_handler.query(prompt)
            rag_used = True
            
            if response:
                logger.info(f"Got RAG response: {response[:50]}...")
                # Return a tuple with the response and whether RAG was used
                return response, rag_used
        
        # If RAG is not available or failed, use standard Ollama API call
        logger.info(f"Using standard Ollama API call for prompt: {prompt[:50]}...")
        try:
            logger.info(f"Sending request to Ollama API at http://localhost:11434/api/generate with model {model}")
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": temperature
                },
                timeout=timeout
            )
            
            logger.info(f"Received response from Ollama API with status code: {response.status_code}")
            
            if response.status_code == 200:
                bot_response = response.json().get('response', '')
                
                # Remove content between <think> and </think> tags
                clean_response = re.sub(r'<think>.*?</think>', '', bot_response, flags=re.DOTALL)
                
                # Clean up any extra whitespace
                clean_response = clean_response.strip()
                
                logger.info(f"Successfully received response from Ollama (length: {len(clean_response)} chars)")
                return clean_response, rag_used
            else:
                error_msg = f"Error from Ollama API: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return f"I apologize, but I encountered an error. (Status: {response.status_code})", rag_used
        except Exception as e:
            logger.error(f"Exception during Ollama API call: {type(e).__name__}: {str(e)}")
            raise
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout connecting to Ollama API after {timeout} seconds")
        return "I apologize for the delay. The service is taking longer than expected to respond.", False
        
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to Ollama API. Is Ollama running?")
        logger.info("Trying to use Ollama CLI as fallback...")
        
        # Try using the Ollama CLI as a fallback method
        try:
            cli_response = run_ollama_cli(prompt, model)
            if cli_response:
                logger.info(f"Successfully received response from Ollama CLI (length: {len(cli_response)} chars)")
                # Remove content between <think> and </think> tags
                clean_response = re.sub(r'<think>.*?</think>', '', cli_response, flags=re.DOTALL)
                clean_response = clean_response.strip()
                return clean_response, False
        except Exception as cli_err:
            logger.error(f"CLI fallback also failed: {str(cli_err)}")
            
        return "I apologize, but I'm having trouble connecting to my knowledge base. Is the Ollama server running?", False
        
    except Exception as e:
        logger.error(f"Unexpected error communicating with Ollama: {str(e)}")
        return f"I apologize, but I encountered an unexpected error. Please try again.", False

def create_mental_health_prompt(user_message, system_prompt=None):
    """
    Create a complete prompt for mental health support
    
    Args:
        user_message (str): The user's message
        system_prompt (str): Optional custom system prompt
        
    Returns:
        str: The complete prompt for the model
    """
    if not system_prompt:
        system_prompt = """You are a supportive mental health chatbot designed to provide empathetic responses.
Remember these guidelines:
- Prioritize empathy and emotional support in your responses
- Validate the user's feelings and experiences
- Avoid diagnostic language or making promises about outcomes
- Suggest helpful coping strategies when appropriate
- Be mindful of serious concerns that might require professional help
- Ensure users feel heard and respected, reinforcing autonomy in their healing journey

Your responses should be warm, evidence-based, and adaptable to different emotional states.
Always validate the user's feelings and guide them toward self-reflection and professional resources where necessary.
"""

    return f"{system_prompt}\n\nRespond with empathy and understanding to the following message: {user_message}"

# Example usage
if __name__ == "__main__":
    # Test the function
    test_prompt = create_mental_health_prompt("I've been feeling really anxious lately.")
    response, rag_used = send_prompt_to_ollama(test_prompt)
    print(f"Response: {response}")
    print(f"RAG used: {rag_used}")
