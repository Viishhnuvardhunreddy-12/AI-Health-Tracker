import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAK0YIK3HSdhF4MyyVZoz_Qe1RcbJ_6hSc")

def get_simple_chatbot_response(user_question, health_data=None):
    """
    A simplified, reliable chatbot implementation using Google's Gemini API.
    
    Args:
        user_question (str): The user's question
        health_data (dict, optional): The user's latest health data
        
    Returns:
        str: The AI-generated response
    """
    if not user_question or not user_question.strip():
        return "Please ask a question."
    # Compose the Gemini prompt
    prompt = (
        "You are a health assistant chatbot. Only respond to user queries that are related to health, wellness, fitness, medical advice, mental well-being, nutrition, or healthy lifestyle. "
        "If a user asks a question that is not related to health, politely respond: 'I'm here to assist you with health-related questions. Please ask me something about your health or wellness.'\n"
        f"User: {user_question}"
    )
    # Add health data context if available
    if health_data:
        health_context = []
        if 'heart_rate' in health_data:
            health_context.append(f"Heart rate: {health_data['heart_rate']} bpm")
        if 'sleep_hours' in health_data:
            health_context.append(f"Sleep: {health_data['sleep_hours']} hours")
        if 'steps' in health_data:
            health_context.append(f"Steps: {health_data['steps']}")
        if 'mood' in health_data:
            mood_value = health_data.get('mood', 0)
            mood_text = "excellent" if mood_value >= 5 else "good" if mood_value >= 4 else "fair" if mood_value >= 3 else "poor"
            health_context.append(f"Mood: {mood_text} ({mood_value}/5)")
        
        if health_context:
            prompt += f"\n\nUser's health data: {', '.join(health_context)}"
    
    try:
        # Configure the API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Generate response with safety settings
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        if response and hasattr(response, 'text'):
            return response.text
        else:
            return "I couldn't generate a response. Please try again."
            
    except Exception as e:
        print(f"Error in simple chatbot: {str(e)}")
        
        # Provide a fallback response
        return f"I'm currently experiencing technical difficulties. Please try a simple health question or try again later."
