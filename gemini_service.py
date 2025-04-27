import os
import google.generativeai as genai
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime, timedelta
import json

# Load environment variables
load_dotenv()

# Configure the Gemini API - Only read the API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables.")

# Configure the Gemini API with explicit error handling
try:
    genai.configure(api_key=api_key)
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini API: {str(e)}")

def analyze_trends(recent_vitals):
    """Analyze trends in vital data to provide statistical insights"""
    if not recent_vitals or len(recent_vitals) < 3:
        return {}
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(recent_vitals)
    
    # Calculate trends
    trends = {}
    for metric in ['heart_rate', 'sleep_hours', 'steps', 'mood']:
        if metric in df.columns:
            values = df[metric].astype(float).values
            
            # Calculate trend direction using linear regression
            x = np.arange(len(values))
            slope, _, r_value, p_value, _ = stats.linregress(x, values)
            
            # Determine trend direction and strength
            if p_value < 0.05:  # Statistically significant
                if slope > 0:
                    direction = "increasing"
                else:
                    direction = "decreasing"
                
                # Determine strength based on r-squared value
                r_squared = r_value ** 2
                if r_squared > 0.7:
                    strength = "strong"
                elif r_squared > 0.3:
                    strength = "moderate"
                else:
                    strength = "slight"
            else:
                direction = "stable"
                strength = "consistent"
            
            # Calculate variability (coefficient of variation)
            mean = np.mean(values)
            std = np.std(values)
            if mean > 0:
                cv = (std / mean) * 100
                if cv > 25:
                    variability = "highly variable"
                elif cv > 10:
                    variability = "somewhat variable"
                else:
                    variability = "consistent"
            else:
                variability = "unknown"
            
            # Calculate recent change (last 3 entries)
            if len(values) >= 3:
                recent_change = values[-1] - np.mean(values[-4:-1])
                recent_pct_change = (recent_change / np.mean(values[-4:-1])) * 100 if np.mean(values[-4:-1]) > 0 else 0
            else:
                recent_change = 0
                recent_pct_change = 0
            
            # Store results
            trends[metric] = {
                "direction": direction,
                "strength": strength,
                "variability": variability,
                "recent_change": recent_change,
                "recent_pct_change": recent_pct_change,
                "mean": float(mean),
                "std": float(std),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "latest": float(values[-1])
            }
    
    return trends

def identify_correlations(recent_vitals):
    """Identify correlations between different health metrics"""
    if not recent_vitals or len(recent_vitals) < 5:  # Need at least 5 data points for meaningful correlation
        return []
    
    # Convert to DataFrame
    df = pd.DataFrame(recent_vitals)
    
    # Calculate correlation matrix
    metrics = ['heart_rate', 'sleep_hours', 'steps', 'mood']
    available_metrics = [m for m in metrics if m in df.columns]
    
    if len(available_metrics) < 2:
        return []
    
    corr_matrix = df[available_metrics].corr()
    
    # Extract significant correlations
    correlations = []
    for i in range(len(available_metrics)):
        for j in range(i+1, len(available_metrics)):
            metric1 = available_metrics[i]
            metric2 = available_metrics[j]
            corr_value = corr_matrix.loc[metric1, metric2]
            
            # Only include strong correlations
            if abs(corr_value) > 0.5:
                direction = "positive" if corr_value > 0 else "negative"
                strength = "strong" if abs(corr_value) > 0.7 else "moderate"
                
                correlations.append({
                    "metric1": metric1,
                    "metric2": metric2,
                    "correlation": float(corr_value),
                    "direction": direction,
                    "strength": strength
                })
    
    return correlations

def get_health_insights(latest_vitals, recent_vitals):
    try:
        # If no data is provided, return a default message
        if not latest_vitals or not recent_vitals:
            return "<p>Not enough data to generate insights. Please continue recording your vitals.</p>"
        
        # Try to use Gemini API if available
        try:
            # List available models to find one that works
            available_models = [m.name for m in genai.list_models()]
            print(f"Available Gemini models: {available_models}")
            
            # Try to find a suitable model
            model_name = None
            for model_option in ["gemini-pro", "gemini-1.0-pro", "gemini-1.5-pro"]:
                if model_option in str(available_models):
                    model_name = model_option
                    break
                    
            # If no specific model found, use the first text model available
            if not model_name:
                for model in genai.list_models():
                    if "generateContent" in model.supported_generation_methods:
                        model_name = model.name
                        break
                        
            print(f"Selected Gemini model: {model_name}")
            
            # If still no model found, use the fallback analysis
            if not model_name:
                print("No suitable Gemini model found. Using fallback analysis.")
                return generate_fallback_insights(latest_vitals, recent_vitals)
            
            # Analyze trends and correlations
            trends = analyze_trends(recent_vitals)
            correlations = identify_correlations(recent_vitals)
            
            # Calculate health score based on latest vitals
            health_score = calculate_health_score(latest_vitals)
            
            # Initialize the model
            model = genai.GenerativeModel(model_name)
            
            # Create the prompt with enhanced data
            prompt = f"""
            Analyze the following health data and provide detailed, personalized insights:
            
            Latest vitals: {json.dumps(latest_vitals, indent=2)}
            
            Health score: {health_score}/100
            
            Trend analysis: {json.dumps(trends, indent=2)}
            
            Correlations found: {json.dumps(correlations, indent=2)}
            
            Recent data history: {json.dumps(recent_vitals[-5:], indent=2)}
            
            IMPORTANT: Format your response as a clear, concise, numbered list of points. Do NOT use paragraphs or long text blocks.
            
            Please provide the following sections, each with numbered bullet points:
            
            1. CURRENT STATUS: 3-4 bullet points about current health status
            2. KEY PATTERNS: 2-3 bullet points about patterns in the data
            3. POTENTIAL RISKS: 2-3 bullet points about health risks
            4. ACTION STEPS: 3-4 bullet points with specific recommendations
            
            Format your response using HTML with proper section headings (<h4>) and numbered lists (<ol> and <li>).
            Keep each bullet point concise (1-2 sentences maximum).
            Use <strong> tags to highlight important metrics or values.
            
            Example format:
            <h4>CURRENT STATUS:</h4>
            <ol>
              <li>Point 1 about current status with <strong>key metric</strong>.</li>
              <li>Point 2 about current status.</li>
            </ol>
            
            <h4>KEY PATTERNS:</h4>
            <ol>
              <li>Pattern 1 with specific data.</li>
              <li>Pattern 2 with specific data.</li>
            </ol>
            """
            
            # Generate content with safety measures
            try:
                response = model.generate_content(prompt)
                if response and hasattr(response, 'text') and response.text.strip():
                    return response.text
                else:
                    print("Empty response from Gemini API. Using fallback analysis.")
                    return generate_fallback_insights(latest_vitals, recent_vitals)
            except Exception as api_error:
                print(f"Error in Gemini API response: {str(api_error)}")
                return generate_fallback_insights(latest_vitals, recent_vitals)
                
        except Exception as gemini_error:
            print(f"Error with Gemini service: {str(gemini_error)}")
            return generate_fallback_insights(latest_vitals, recent_vitals)
            
    except Exception as e:
        print(f"Error generating health insights: {str(e)}")
        return generate_fallback_insights(latest_vitals, recent_vitals)


def generate_fallback_insights(latest_vitals, recent_vitals):
    """Generate fallback health insights when Gemini API is unavailable"""
    try:
        # Extract the latest values
        heart_rate = latest_vitals.get('heart_rate', 0)
        sleep_hours = latest_vitals.get('sleep_hours', 0)
        steps = latest_vitals.get('steps', 0)
        mood = latest_vitals.get('mood', 0)
        
        # Calculate health score
        health_score = calculate_health_score(latest_vitals)
        
        # Generate basic insights based on the data
        insights = []
        insights.append(f"<p>Your current health score is <strong>{health_score}/100</strong>.</p>")
        
        # Heart rate insights
        if heart_rate > 100:
            insights.append("<p>Your <strong>heart rate is elevated</strong>. This could be due to recent physical activity, stress, or caffeine intake. If consistently high, consider consulting a healthcare professional.</p>")
        elif heart_rate < 60:
            insights.append("<p>Your <strong>heart rate is lower than average</strong>. This could be a sign of good cardiovascular fitness if you're an athlete, but if accompanied by symptoms like dizziness, consult a healthcare professional.</p>")
        else:
            insights.append("<p>Your <strong>heart rate is within normal range</strong>, indicating good cardiovascular health.</p>")
        
        # Sleep insights
        if sleep_hours < 6:
            insights.append("<p>You're <strong>not getting enough sleep</strong>. Chronic sleep deprivation can impact cognitive function, mood, and overall health. Aim for 7-9 hours of quality sleep.</p>")
        elif sleep_hours > 9:
            insights.append("<p>You're getting <strong>more sleep than average</strong>. While extra rest can be beneficial, consistently sleeping more than 9 hours might be worth discussing with a healthcare provider.</p>")
        else:
            insights.append("<p>Your <strong>sleep duration is optimal</strong>, which supports cognitive function, emotional well-being, and physical recovery.</p>")
        
        # Steps insights
        if steps < 5000:
            insights.append("<p>Your <strong>daily step count is below recommended levels</strong>. Try to increase physical activity gradually to improve cardiovascular health and energy levels.</p>")
        elif steps > 10000:
            insights.append("<p>You're <strong>exceeding the recommended daily step count</strong>, which is excellent for cardiovascular health, weight management, and overall well-being.</p>")
        else:
            insights.append("<p>Your <strong>step count is good</strong>, but increasing to 10,000 steps daily could provide additional health benefits.</p>")
        
        # Mood insights
        mood_descriptions = {1: "very poor", 2: "poor", 3: "neutral", 4: "good", 5: "excellent"}
        mood_desc = mood_descriptions.get(mood, "variable")
        
        if mood <= 2:
            insights.append(f"<p>Your mood is reported as <strong>{mood_desc}</strong>. Consider activities that boost mental well-being, such as exercise, social connection, or mindfulness practices.</p>")
        elif mood >= 4:
            insights.append(f"<p>Your mood is <strong>{mood_desc}</strong>, which is beneficial for overall health and productivity.</p>")
        else:
            insights.append(f"<p>Your mood is <strong>{mood_desc}</strong>. Regular exercise, adequate sleep, and stress management can help improve emotional well-being.</p>")
        
        # Analyze trends if we have enough data
        if len(recent_vitals) >= 3:
            # Get the last 3 entries to check recent trends
            recent_three = recent_vitals[-3:]
            
            # Check heart rate trend
            hr_values = [entry.get('heart_rate', 0) for entry in recent_three if 'heart_rate' in entry]
            if len(hr_values) >= 3 and all(hr_values):
                if hr_values[0] < hr_values[1] < hr_values[2]:
                    insights.append("<p><strong>Trend alert:</strong> Your heart rate has been steadily increasing. Monitor this trend and consider factors like stress or activity levels.</p>")
                elif hr_values[0] > hr_values[1] > hr_values[2]:
                    insights.append("<p><strong>Positive trend:</strong> Your heart rate has been steadily decreasing, which could indicate improving cardiovascular health or reduced stress.</p>")
            
            # Check sleep trend
            sleep_values = [entry.get('sleep_hours', 0) for entry in recent_three if 'sleep_hours' in entry]
            if len(sleep_values) >= 3 and all(sleep_values):
                if sleep_values[0] > sleep_values[1] > sleep_values[2]:
                    insights.append("<p><strong>Trend alert:</strong> Your sleep duration has been decreasing. Prioritize sleep hygiene to ensure adequate rest.</p>")
                elif sleep_values[0] < sleep_values[1] < sleep_values[2]:
                    insights.append("<p><strong>Positive trend:</strong> Your sleep duration has been increasing, which supports better overall health.</p>")
        
        # Add recommendations section
        insights.append("<h5 class='mt-3'>Recommendations:</h5>")
        insights.append("<ul>")
        
        if heart_rate > 90:
            insights.append("<li>Consider stress-reduction techniques like deep breathing or meditation.</li>")
        
        if sleep_hours < 7:
            insights.append("<li>Improve sleep hygiene by maintaining a consistent sleep schedule and limiting screen time before bed.</li>")
        
        if steps < 7500:
            insights.append("<li>Gradually increase daily physical activity by taking short walks throughout the day.</li>")
        
        if mood <= 3:
            insights.append("<li>Engage in activities you enjoy and consider mindfulness practices to improve mood.</li>")
        
        # General recommendations
        insights.append("<li>Stay hydrated by drinking at least 8 glasses of water daily.</li>")
        insights.append("<li>Maintain a balanced diet rich in fruits, vegetables, and whole grains.</li>")
        insights.append("<li>Schedule regular health check-ups with your healthcare provider.</li>")
        insights.append("</ul>")
        
        return "\n".join(insights)
        
    except Exception as e:
        print(f"Error generating fallback insights: {str(e)}")
        return "<p>Unable to generate health insights at this time. Please try again later.</p>"

def calculate_health_score(vitals):
    """Calculate an overall health score based on vitals data"""
    if not vitals:
        return 50  # Default neutral score
    
    score = 50  # Start with neutral score
    
    # Heart rate scoring (normal range: 60-100 bpm)
    if 'heart_rate' in vitals:
        hr = vitals['heart_rate']
        if 60 <= hr <= 100:
            score += 10  # Normal range
        elif 50 <= hr < 60 or 100 < hr <= 110:
            score += 5   # Slightly outside normal range
        elif hr < 50 or hr > 110:
            score -= 5   # Significantly outside normal range
    
    # Sleep hours scoring (ideal: 7-9 hours)
    if 'sleep_hours' in vitals:
        sleep = vitals['sleep_hours']
        if 7 <= sleep <= 9:
            score += 15  # Ideal sleep range
        elif 6 <= sleep < 7 or 9 < sleep <= 10:
            score += 7   # Acceptable sleep range
        elif sleep < 6:
            score -= 10  # Too little sleep
        elif sleep > 10:
            score -= 5   # Too much sleep may indicate issues
    
    # Steps scoring (target: 10,000 steps)
    if 'steps' in vitals:
        steps = vitals['steps']
        if steps >= 10000:
            score += 15  # Met or exceeded target
        elif 7000 <= steps < 10000:
            score += 10  # Good progress
        elif 5000 <= steps < 7000:
            score += 5   # Moderate activity
        elif steps < 5000:
            score += 0   # Low activity
    
    # Mood scoring (scale 1-5)
    if 'mood' in vitals:
        mood = vitals['mood']
        if mood == 5:
            score += 10  # Excellent mood
        elif mood == 4:
            score += 7   # Good mood
        elif mood == 3:
            score += 3   # Neutral mood
        elif mood <= 2:
            score -= 5   # Poor mood
    
    # Ensure score stays within 0-100 range
    return max(0, min(100, score))

# Renamed from get_recommendations to get_personalized_recommendations to match import in routes.py
def get_personalized_recommendations(vitals_data):
    try:
        # Ensure we have valid vitals data
        if not vitals_data or not isinstance(vitals_data, dict):
            raise ValueError("Invalid vitals data provided")
            
        # Print vitals data for debugging
        print(f"Generating recommendations for vitals: {json.dumps(vitals_data)}")
        
        # Force use of Gemini API by ensuring we have a model
        available_models = [m.name for m in genai.list_models()]
        print(f"Available models: {available_models}")
        
        # Try to find a suitable model
        model_name = None
        for model_option in ["gemini-pro", "gemini-1.0-pro", "gemini-1.5-pro"]:
            if model_option in str(available_models):
                model_name = model_option
                break
        
        # If no specific model found, use the first text model available
        if not model_name:
            for model in genai.list_models():
                if "generateContent" in model.supported_generation_methods:
                    model_name = model.name
                    break
        
        # If still no model found, use a default model name
        if not model_name:
            model_name = "gemini-pro"  # Use a default model name
            print("Warning: No model found, using default model name")
        
        print(f"Using model: {model_name}")
        
        # Initialize the model
        model = genai.GenerativeModel(model_name)
        
        # Calculate health score
        health_score = calculate_health_score(vitals_data)
        
        # Determine areas needing improvement
        areas_to_improve = []
        if 'heart_rate' in vitals_data:
            hr = vitals_data['heart_rate']
            if hr < 60 or hr > 100:
                areas_to_improve.append("heart_rate")
        
        if 'sleep_hours' in vitals_data:
            sleep = vitals_data['sleep_hours']
            if sleep < 7 or sleep > 9:
                areas_to_improve.append("sleep_hours")
        
        if 'steps' in vitals_data:
            steps = vitals_data['steps']
            if steps < 10000:
                areas_to_improve.append("steps")
        
        if 'mood' in vitals_data:
            mood = vitals_data['mood']
            if mood < 4:
                areas_to_improve.append("mood")
        
        # Add timestamp to ensure uniqueness in each request
        current_time = datetime.now().isoformat()
        
        # Create a more detailed prompt with specific instructions
        prompt = f"""
        Based on the following health data, provide specific, personalized recommendations:
        
        Health data: {json.dumps(vitals_data, indent=2)}
        Health score: {health_score}/100
        Areas needing improvement: {areas_to_improve}
        Current time: {current_time}
        
        IMPORTANT: Format your response as a NUMBERED LIST of 3-5 specific, actionable recommendations.
        
        Each recommendation MUST:
        1. Be clear, concise, and easy to read (maximum 1-2 sentences)
        2. Include specific metrics or timeframes (e.g., "Walk 2,000 more steps" not just "Walk more")
        3. Be immediately actionable today
        4. Address one of the areas needing improvement
        5. Include a clear, measurable goal
        
        Format your response as an HTML ordered list (<ol> with <li> items).
        Start with a brief heading: "<h4>YOUR ACTION PLAN:</h4>"
        
        Example format:
        <h4>YOUR ACTION PLAN:</h4>
        <ol>
          <li>Take a 15-minute walk at lunchtime to add <strong>2,000 steps</strong> to your daily count.</li>
          <li>Set a bedtime alarm for <strong>10:30 PM</strong> to ensure you get at least 7 hours of sleep.</li>
          <li>Practice deep breathing for <strong>5 minutes</strong> to lower your heart rate by 5-10 bpm.</li>
        </ol>
        
        IMPORTANT: Do not include generic recommendations. Each recommendation must include specific metrics, 
        times, or actions tailored to this individual's exact data.
        """
        
        # Generate content with safety settings to ensure we get a response
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        print("Sending request to Gemini API...")
        response = model.generate_content(prompt, safety_settings=safety_settings)
        
        # Ensure we have a valid response
        if response and hasattr(response, 'text') and response.text:
            print("Received valid response from Gemini API")
            return response.text
        else:
            print("Empty response from Gemini API")
            raise Exception("Empty response from Gemini API")
            
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        # Generate dynamic fallback recommendations instead of static ones
        fallback_recommendations = [
            f"Consider aiming for {vitals_data.get('steps', 7000) + 1000} steps tomorrow to improve your activity level",
            f"Try sleeping {8 if vitals_data.get('sleep_hours', 7) < 7 else 7} hours tonight for better recovery",
            f"Monitor your heart rate and aim to keep it between {max(60, vitals_data.get('heart_rate', 70) - 5)} and {min(100, vitals_data.get('heart_rate', 70) + 5)} bpm",
            f"Schedule a 15-minute relaxation break at {datetime.now().hour + 1}:00 to improve your mood",
            f"Try a new physical activity that you enjoy to increase your daily movement",
            f"Set a reminder to drink water every {max(1, vitals_data.get('heart_rate', 70) // 20)} hours to stay hydrated",
            f"Consider a {10 if vitals_data.get('mood', 3) < 3 else 5}-minute meditation session to improve focus"
        ]
        
        # Select 3 random recommendations to ensure variety
        import random
        selected_recommendations = random.sample(fallback_recommendations, min(3, len(fallback_recommendations)))
        
        return "<ul>" + "".join([f"<li>{rec}</li>" for rec in selected_recommendations]) + "</ul>"

def get_chatbot_response(user_question, health_data=None, recent_data=None):
    """
    Get a response from the Gemini API for the health chatbot feature.
    
    Args:
        user_question (str): The user's health-related question
        health_data (dict, optional): The user's latest health data
        recent_data (list, optional): Recent health data for context
        
    Returns:
        str: The AI-generated response to the user's question
    """
    if not user_question:
        return "Please ask a health-related question."
    
    try:
        # Ensure API key is configured
        if not api_key:
            return "API key not configured. Please check your environment variables."
        
        # Create a simple prompt for better reliability
        prompt = f"""
        You are a helpful health assistant. Answer the following health-related question:
        
        {user_question}
        """
        
        # Add minimal health data context if available
        if health_data:
            health_summary = ""
            if 'heart_rate' in health_data:
                health_summary += f"Heart rate: {health_data['heart_rate']} bpm. "
            if 'sleep_hours' in health_data:
                health_summary += f"Sleep: {health_data['sleep_hours']} hours. "
            if 'steps' in health_data:
                health_summary += f"Steps: {health_data['steps']}. "
            if 'mood' in health_data:
                mood_level = health_data['mood']
                mood_desc = "excellent" if mood_level >= 5 else "good" if mood_level >= 4 else "fair" if mood_level >= 3 else "poor"
                health_summary += f"Mood: {mood_desc}. "
                
            if health_summary:
                prompt += f"\n\nRecent health metrics: {health_summary}"
        
        # Initialize the model with minimal settings
        model = genai.GenerativeModel("gemini-pro")
        
        # Generate content with minimal parameters for reliability
        response = model.generate_content(prompt)
        
        # Return the response text
        if response and hasattr(response, 'text') and response.text:
            return response.text
        else:
            return "I'm sorry, I couldn't generate a response. Please try asking a different question."
            
    except Exception as e:
        print(f"Detailed error in chatbot response generation: {type(e).__name__}: {str(e)}")
        
        # Try a simpler approach as fallback
        try:
            model = genai.GenerativeModel("gemini-pro")
            simple_prompt = f"Answer this health question briefly: {user_question}"
            response = model.generate_content(simple_prompt)
            if response and hasattr(response, 'text') and response.text:
                return response.text
        except Exception as fallback_error:
            print(f"Fallback also failed: {str(fallback_error)}")
        
        return "I'm currently experiencing technical difficulties. Please try a simple health question or try again later."