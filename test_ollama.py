"""
Simple script to test Ollama connection
"""

import requests
import time
import json

print("Testing connection to Ollama service...")

# Test 1: Check if Ollama API is accessible
try:
    print("\nTest 1: Checking API accessibility...")
    start_time = time.time()
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    elapsed_time = time.time() - start_time
    
    print(f"API response time: {elapsed_time:.2f} seconds")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("Success! Ollama API is accessible.")
        models = response.json().get('models', [])
        print(f"Available models: {[model.get('name') for model in models]}")
    else:
        print(f"Error: Failed to connect to Ollama API. Status: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error connecting to Ollama API: {type(e).__name__}: {str(e)}")

# Test 2: Try sending a simple prompt
try:
    print("\nTest 2: Sending a simple prompt...")
    prompt = "Say hello in one word."
    model = "deepseek-r1:1.5b"
    
    print(f"Sending prompt to model {model}: '{prompt}'")
    start_time = time.time()
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        },
        timeout=30
    )
    
    elapsed_time = time.time() - start_time
    print(f"Response time: {elapsed_time:.2f} seconds")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Response: {result.get('response')}")
    else:
        print(f"Error from Ollama API: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error sending prompt to Ollama: {type(e).__name__}: {str(e)}")

print("\nTest complete.")
