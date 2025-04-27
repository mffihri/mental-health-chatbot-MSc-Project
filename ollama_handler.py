"""
Ollama API Handler for DeepSeek Chat

This module provides functions for interacting with the Ollama API,
sending prompts and processing responses.
"""

import requests
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_prompt_to_ollama(prompt, model="deepseek-r1:1.5b", timeout=30, temperature=0.7):
    """
    Send a prompt to the Ollama API and return the response with thinking sections removed.
    
    Args:
        prompt (str): The prompt to send to Ollama
        model (str): The model to use, defaults to "deepseek-r1:1.5b"
        timeout (int): Request timeout in seconds
        temperature (float): Sampling temperature (higher = more creative, lower = more deterministic)
        
    Returns:
        str: The processed response from Ollama
        
    Raises:
        Exception: If there's an error connecting to Ollama or processing the response
    """
    try:
        logger.info(f"Sending prompt to Ollama using model {model}")
        
        # Make the API request to Ollama
        response = requests.post('http://localhost:11434/api/generate',
                              json={
                                  "model": model,
                                  "prompt": prompt,
                                  "stream": False,
                                  "temperature": temperature
                              },
                              timeout=timeout)
        
        # Check if the request was successful
        if response.status_code == 200:
            bot_response = response.json().get('response', '')
            
            # Remove content between <think> and </think> tags
            clean_response = re.sub(r'<think>.*?</think>', '', bot_response, flags=re.DOTALL)
            
            # Clean up any extra whitespace
            clean_response = clean_response.strip()
            
            logger.info(f"Successfully received response from Ollama (length: {len(clean_response)} chars)")
            return clean_response
        else:
            error_msg = f"Error from Ollama API: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return f"I apologize, but I encountered an error. (Status: {response.status_code})"
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout connecting to Ollama API after {timeout} seconds")
        return "I apologize for the delay. The service is taking longer than expected to respond."
        
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to Ollama API. Is Ollama running?")
        return "I apologize, but I'm having trouble connecting to my knowledge base. Is the Ollama server running?"
        
    except Exception as e:
        logger.error(f"Unexpected error communicating with Ollama: {str(e)}")
        return f"I apologize, but I encountered an unexpected error. Please try again."

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
    response = send_prompt_to_ollama(test_prompt)
    print(f"Response: {response}")
