import os
import json
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key specifically for OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Get Gemini API key as fallback
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_chatbot_response_gpt(user_question, health_data=None, recent_data=None):
    """
    Get a response from Google Gemini 2.5 Pro Experimental via OpenRouter API for the health chatbot feature.
    
    Args:
        user_question (str): The user's question (any topic)
        health_data (dict, optional): The user's latest health data
        recent_data (list, optional): Recent health data for context
        
    Returns:
        str: The AI-generated response to the user's question
    """
    # Print the API key (first 5 and last 5 chars) for debugging
    print(f"Using OpenRouter API Key: {OPENROUTER_API_KEY[:5]}...{OPENROUTER_API_KEY[-5:]}")
    # Check if we have a valid question
    if not user_question or not user_question.strip():
        return "Please ask a question."
    
    # Build system message with health focus
    system_message = """You are an AI health assistant in the Health Tracker application. 
    Your primary focus is on providing health-related advice, insights, and answering questions about health, 
    fitness, nutrition, and wellness. You can also answer general questions, but your expertise is in health.
    
    IMPORTANT FORMATTING INSTRUCTIONS:
    1. Format your responses as clear, numbered bullet points whenever possible
    2. Use short, concise sentences (1-2 sentences per point)
    3. Group related information under clear headings
    4. Highlight important values or metrics in bold
    5. Keep your overall response concise and easy to scan
    6. Avoid long paragraphs of text
    
    When discussing health data, be informative and supportive, providing context about what the numbers mean 
    and gentle suggestions for improvement when appropriate. Always maintain a positive, encouraging tone.
    
    The current year is 2025, and you have access to the latest health research and guidelines up to that point.
    """
    
    # Add health data if available for personalization
    if health_data:
        health_info = []
        if 'heart_rate' in health_data:
            health_info.append(f"Heart rate: {health_data['heart_rate']} bpm")
        if 'sleep_hours' in health_data:
            health_info.append(f"Sleep: {health_data['sleep_hours']} hours")
        if 'steps' in health_data:
            health_info.append(f"Steps: {health_data['steps']}")
        if 'mood' in health_data:
            mood_value = health_data['mood']
            mood_text = "excellent" if mood_value >= 5 else "good" if mood_value >= 4 else "fair" if mood_value >= 3 else "poor"
            health_info.append(f"Mood: {mood_text} ({mood_value}/5)")
        if 'stress_level' in health_data:
            stress_value = health_data['stress_level']
            stress_text = "low" if stress_value <= 2 else "moderate" if stress_value <= 3 else "high"
            health_info.append(f"Stress level: {stress_text} ({stress_value}/5)")
        
        if health_info:
            system_message += f"\n\nUser's latest health data: {', '.join(health_info)}."
    
    # Add recent trends if available
    if recent_data and len(recent_data) > 1:
        system_message += "\n\nRecent health trends:"
        
        # Calculate heart rate trend
        if all('heart_rate' in entry for entry in recent_data[-3:]):
            hr_values = [entry['heart_rate'] for entry in recent_data[-3:]]
            hr_avg = sum(hr_values) / len(hr_values)
            hr_trend = "stable" if max(hr_values) - min(hr_values) < 10 else "variable"
            system_message += f"\n- Heart rate has been {hr_trend} with an average of {hr_avg:.1f} bpm"
        
        # Calculate sleep trend
        if all('sleep_hours' in entry for entry in recent_data[-5:]):
            sleep_values = [entry['sleep_hours'] for entry in recent_data[-5:]]
            sleep_avg = sum(sleep_values) / len(sleep_values)
            system_message += f"\n- Sleep average over past 5 days: {sleep_avg:.1f} hours"
    
    # Configure OpenRouter API request with Qwen model
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Use Google Gemini 2.5 Pro Experimental via OpenRouter
    model = "google/gemini-2.5-pro-experimental"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://health-tracker-app.com"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_question}
        ],
        "max_tokens": 800,  # Increased for more detailed health responses
        "temperature": 0.5,  # More factual responses for health advice
        "top_p": 0.95,  # Focus on more likely tokens for health advice
        "route": "fallback"  # Use fallback routing for higher reliability
    }
    
    try:
        print(f"Sending request to OpenRouter API with model: {model}")
        
        # Print the full request data for debugging (excluding sensitive info)
        debug_data = data.copy()
        print(f"Request data: {debug_data}")
        
        # Make the API request with a reasonable timeout
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=30  # Longer timeout for more reliable responses
        )
        
        print(f"Response status: {response.status_code}")
        
        # Always print the response text for debugging
        print(f"Response text: {response.text[:200]}...")
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                answer = result["choices"][0]["message"]["content"]
                print(f"Successfully received response from {model}")
                return answer
            else:
                print(f"Unexpected response format: {result}")
        else:
            print(f"Error response: {response.text}")
            
            # Try fallback to another model if primary fails
            fallback_model = "anthropic/claude-3-opus:beta"
            print(f"Attempting fallback to {fallback_model}")
            
            data["model"] = fallback_model
            fallback_response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"Fallback response status: {fallback_response.status_code}")
            print(f"Fallback response text: {fallback_response.text[:200]}...")
            
            if fallback_response.status_code == 200:
                fallback_result = fallback_response.json()
                if "choices" in fallback_result and len(fallback_result["choices"]) > 0:
                    answer = fallback_result["choices"][0]["message"]["content"]
                    print(f"Successfully received response from fallback model {fallback_model}")
                    return answer
    
    except Exception as e:
        print(f"Error with OpenRouter API: {str(e)}")
    
    # Try using Gemini API as a final fallback
    try:
        import google.generativeai as genai
        
        # Configure Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create a more conversational prompt for Gemini
        gemini_prompt = f"""You are a helpful health assistant. Please answer the following question about health, fitness, or wellness:

{user_question}

"""
        
        # Add health context if available
        if health_data:
            health_context = []
            if 'heart_rate' in health_data:
                health_context.append(f"Heart rate: {health_data['heart_rate']} bpm")
            if 'sleep_hours' in health_data:
                health_context.append(f"Sleep: {health_data['sleep_hours']} hours")
            if 'steps' in health_data:
                health_context.append(f"Steps: {health_data['steps']}")
            if 'mood' in health_data:
                health_context.append(f"Mood: {health_data['mood']}/5")
            
            if health_context:
                gemini_prompt += f"\n\nUser's health data: {', '.join(health_context)}"
        
        # Get response from Gemini
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(gemini_prompt)
        
        if response and hasattr(response, 'text'):
            print("Successfully received response from Gemini API fallback")
            return response.text
    
    except Exception as e:
        print(f"Error with Gemini API fallback: {str(e)}")
    
    # If all API calls fail, return an error message
    return "I'm having trouble connecting to my AI services right now. Please try again in a moment."
