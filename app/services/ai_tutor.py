import requests
import os

def get_ai_explanation(query, grade_level=4):
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    # Use the exact name from your 'ollama list'
    model = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')

    payload = {
        "model": model,
        "prompt": f"Explain this to a Grade {grade_level} student: {query}",
        "stream": False
    }

    try:
        # Increase timeout to 120 seconds (2 minutes)
        response = requests.post(f"{base_url}/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get('response')
    
    except requests.exceptions.Timeout:
        return "The teacher is thinking deeply! (Model loading took too long). Please refresh and try one more time."
    except Exception as e:
        print(f"AI Service Error: {str(e)}")
        return "The AI tutor is resting. Check if Ollama is running!"