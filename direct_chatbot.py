import os
import random
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAK0YIK3HSdhF4MyyVZoz_Qe1RcbJ_6hSc")

# Try to import Gemini API but don't fail if it's not available
try:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
    print("Gemini API imported successfully")
except Exception as e:
    print(f"Gemini API import failed: {str(e)}")
    GEMINI_AVAILABLE = False

# Pre-defined responses for common health questions
HEALTH_RESPONSES = {
    "sleep": [
        "Here are some tips to improve your sleep quality:\n\n1. **Maintain a consistent sleep schedule** - Go to bed and wake up at the same time every day\n2. **Create a relaxing bedtime routine** - Try reading, gentle stretching, or meditation\n3. **Optimize your sleep environment** - Keep your bedroom cool, dark, and quiet\n4. **Limit screen time before bed** - Avoid phones and computers at least 1 hour before sleeping\n5. **Watch your diet** - Avoid caffeine, large meals, and alcohol close to bedtime",
        
        "To improve your sleep quality:\n\n1. **Stick to a sleep schedule** of 7-9 hours, even on weekends\n2. **Exercise regularly**, but not too close to bedtime\n3. **Limit daytime naps** to 20-30 minutes\n4. **Manage stress** through meditation, deep breathing, or journaling\n5. **Create a comfortable sleep environment** with a good mattress and pillows"
    ],
    
    "heart rate": [
        "A normal resting heart rate for adults ranges from 60 to 100 beats per minute. Athletes and people who are very physically fit may have lower resting heart rates, sometimes as low as 40 BPM.\n\nFactors that can affect heart rate include:\n\n1. **Activity level** - Increases during exercise\n2. **Air temperature** - Higher temperatures can increase heart rate\n3. **Body position** - Rising from sitting to standing can increase heart rate\n4. **Emotions** - Stress and anxiety can raise heart rate\n5. **Medications** - Some drugs can increase or decrease heart rate",
        
        "Understanding your heart rate:\n\n1. **Normal resting heart rate**: 60-100 BPM for adults\n2. **Bradycardia**: Below 60 BPM (can be normal for athletes)\n3. **Tachycardia**: Above 100 BPM\n\nTo maintain a healthy heart rate:\n\n- **Regular cardiovascular exercise**\n- **Stress management techniques**\n- **Adequate sleep**\n- **Staying hydrated**\n- **Limiting caffeine and alcohol**"
    ],
    
    "stress": [
        "Here are effective strategies to reduce stress:\n\n1. **Practice mindfulness meditation** for 10-15 minutes daily\n2. **Regular physical activity** releases endorphins that improve mood\n3. **Deep breathing exercises** can quickly reduce stress hormones\n4. **Maintain social connections** with friends and family\n5. **Get enough sleep** as poor sleep increases stress\n6. **Limit caffeine and alcohol** which can worsen anxiety\n7. **Try progressive muscle relaxation** to release physical tension",
        
        "Tips for managing stress in your daily life:\n\n1. **Identify your stress triggers** and develop strategies to address them\n2. **Set realistic goals and priorities** to avoid feeling overwhelmed\n3. **Take regular breaks** throughout your day\n4. **Connect with supportive people** who lift your mood\n5. **Practice gratitude** by noting three positive things each day\n6. **Limit news and social media consumption** if it increases anxiety\n7. **Consider professional help** if stress becomes overwhelming"
    ],
    
    "steps": [
        "The commonly recommended goal is 10,000 steps per day, which is approximately 5 miles. However, any increase in steps provides health benefits.\n\nBenefits of walking more steps:\n\n1. **Improved cardiovascular health**\n2. **Better weight management**\n3. **Reduced risk of chronic diseases** like diabetes\n4. **Enhanced mood and mental wellbeing**\n5. **Stronger bones and muscles**\n\nTips to increase your daily steps:\n\n- Take the stairs instead of elevators\n- Park farther from entrances\n- Walk during phone calls\n- Set hourly reminders to move\n- Consider a walking meeting instead of sitting",
        
        "Recommendations for daily steps:\n\n- **Sedentary lifestyle**: Less than 5,000 steps/day\n- **Low active**: 5,000-7,499 steps/day\n- **Somewhat active**: 7,500-9,999 steps/day\n- **Active**: 10,000-12,499 steps/day\n- **Highly active**: 12,500+ steps/day\n\nEven increasing by just 2,000 steps daily can significantly improve health outcomes. Start where you are and gradually build up."
    ],
    
    "diet": [
        "Principles of a healthy diet:\n\n1. **Eat plenty of fruits and vegetables** - Aim for half your plate\n2. **Choose whole grains** over refined grains\n3. **Include lean protein sources** like fish, poultry, beans, and nuts\n4. **Limit added sugars, sodium, and unhealthy fats**\n5. **Stay hydrated** with water as your primary beverage\n6. **Practice portion control** even with healthy foods\n7. **Minimize ultra-processed foods** and cook at home when possible",
        
        "Balanced nutrition tips:\n\n1. **Follow the plate method**: ½ vegetables, ¼ protein, ¼ whole grains\n2. **Eat the rainbow** of colorful fruits and vegetables for diverse nutrients\n3. **Include healthy fats** from avocados, olive oil, and nuts\n4. **Choose lean proteins** including plant-based options\n5. **Limit added sugar** to less than 10% of daily calories\n6. **Read nutrition labels** to make informed choices\n7. **Plan meals ahead** to avoid unhealthy convenience options"
    ],
    
    "exercise": [
        "Exercise recommendations for adults:\n\n1. **Aerobic activity**: 150-300 minutes of moderate activity or 75-150 minutes of vigorous activity weekly\n2. **Strength training**: All major muscle groups at least twice weekly\n3. **Flexibility**: Stretching several times weekly\n4. **Balance exercises**: Especially important as you age\n\nBenefits include:\n- Reduced risk of chronic disease\n- Better weight management\n- Improved mood and mental health\n- Enhanced sleep quality\n- Increased energy levels",
        
        "Getting started with exercise:\n\n1. **Start slowly** and gradually increase intensity and duration\n2. **Find activities you enjoy** to maintain motivation\n3. **Mix up your routine** to prevent boredom and plateaus\n4. **Set SMART goals** (Specific, Measurable, Achievable, Relevant, Time-bound)\n5. **Schedule workouts** like any other important appointment\n6. **Track your progress** to stay motivated\n7. **Consider working with a professional** for proper form and personalized advice"
    ],
    
    "water": [
        "Staying properly hydrated is essential for health. The National Academies of Sciences, Engineering, and Medicine recommends:\n\n- About **15.5 cups (3.7 liters)** of fluids daily for men\n- About **11.5 cups (2.7 liters)** of fluids daily for women\n\nBenefits of proper hydration:\n1. **Regulates body temperature**\n2. **Lubricates joints**\n3. **Delivers nutrients to cells**\n4. **Keeps organs functioning properly**\n5. **Improves sleep quality, cognition, and mood**",
        
        "Tips to stay hydrated:\n\n1. **Carry a reusable water bottle** with you\n2. **Set reminders** to drink throughout the day\n3. **Eat water-rich foods** like fruits and vegetables\n4. **Flavor water naturally** with fruit or herbs if you dislike plain water\n5. **Monitor urine color** - pale yellow indicates good hydration\n6. **Increase intake during exercise** and hot weather\n7. **Start and end your day with a glass of water**"
    ],
    
    "default": [
        "Thank you for your health question. Here are some general wellness tips:\n\n1. **Stay physically active** with at least 150 minutes of moderate exercise weekly\n2. **Eat a balanced diet** rich in fruits, vegetables, and whole grains\n3. **Get 7-9 hours of quality sleep** each night\n4. **Stay hydrated** by drinking water throughout the day\n5. **Manage stress** through mindfulness, deep breathing, or other relaxation techniques\n6. **Maintain social connections** for mental and emotional wellbeing\n7. **Get regular health check-ups** for preventive care",
        
        "Here are some foundational health principles that apply to most people:\n\n1. **Regular physical activity** improves nearly every aspect of health\n2. **Nutritious eating patterns** focusing on whole foods over processed ones\n3. **Adequate sleep** is essential for physical and mental recovery\n4. **Stress management** through various techniques like meditation or exercise\n5. **Staying hydrated** with water as your primary beverage\n6. **Limiting alcohol and avoiding tobacco**\n7. **Regular health screenings** appropriate for your age and risk factors"
    ]
}

def get_direct_chatbot_response(user_question, health_data=None):
    """
    An enhanced chatbot implementation that handles a wide range of user questions.
    """
    time.sleep(0.5)
    # Compose the Gemini prompt
    prompt = (
        "You are a health assistant chatbot. Only respond to user queries that are related to health, wellness, fitness, medical advice, mental well-being, nutrition, or healthy lifestyle. "
        "If a user asks a question that is not related to health, politely respond: 'I'm here to assist you with health-related questions. Please ask me something about your health or wellness.'\n"
        f"User: {user_question}"
    )
    # Add a small delay to simulate processing
    time.sleep(0.5)
    
    # Try to use Gemini API if available
    if GEMINI_AVAILABLE:
        try:
            # Create a more conversational prompt
            current_date = time.strftime("%Y-%m-%d")
            prompt = f"""You are a helpful health assistant in the Health Tracker application. 
            Today is {current_date}. Answer the following question in a clear, helpful way. 
            Format your response with markdown using **bold** for important points and organize with numbered lists where appropriate.
            Keep your response conversational, informative, and concise.
            
            User question: {user_question}
            """
            
            # Add health data context if available
            if health_data:
                health_context = []
                if 'heart_rate' in health_data and health_data['heart_rate']:
                    health_context.append(f"Heart rate: {health_data['heart_rate']} bpm")
                if 'sleep_hours' in health_data and health_data['sleep_hours']:
                    health_context.append(f"Sleep: {health_data['sleep_hours']} hours")
                if 'steps' in health_data and health_data['steps']:
                    health_context.append(f"Steps: {health_data['steps']}")
                if 'mood' in health_data and health_data['mood']:
                    mood_value = health_data.get('mood', 0)
                    mood_text = "excellent" if mood_value >= 5 else "good" if mood_value >= 4 else "fair" if mood_value >= 3 else "poor"
                    health_context.append(f"Mood: {mood_text} ({mood_value}/5)")
                
                if health_context:
                    prompt += f"\n\nUser's health data: {', '.join(health_context)}"
                    prompt += "\n\nIncorporate this health data into your response where relevant to provide personalized advice."
            
            # Add instructions to make responses more dynamic
            prompt += """
            
            Guidelines for your response:
            1. Be conversational and engaging
            2. Provide evidence-based information
            3. Tailor advice to the user's specific question
            4. Avoid generic responses that don't directly address the question
            5. If the question is unclear, acknowledge that and provide helpful information
            6. Include specific, actionable advice where appropriate
            """
            
            # Try different models if available
            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
            except:
                try:
                    model = genai.GenerativeModel('gemini-pro')
                except:
                    model = genai.GenerativeModel('gemini-1.0-pro')
            
            # Generate response with safety settings
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
            
            try:
                response = model.generate_content(prompt, safety_settings=safety_settings)
            except:
                # Try without safety settings if they're not supported
                response = model.generate_content(prompt)
            
            if response and hasattr(response, 'text') and response.text.strip():
                return response.text
            
            # If we get here, the API didn't return a valid response
            print("API returned empty response, using fallback")
            
        except Exception as e:
            print(f"Error using Gemini API: {str(e)}")
            # Continue to fallback responses
    
    # Enhanced keyword detection for more accurate categorization
    categories = {
        "sleep": ["sleep", "insomnia", "tired", "rest", "bed", "nap", "snore", "dream", "night", "wake up", "waking up", "rem", "melatonin"],
        "heart rate": ["heart", "pulse", "bpm", "heartbeat", "cardiovascular", "cardiac", "blood pressure", "hypertension", "arrhythmia"],
        "stress": ["stress", "anxiety", "worried", "tension", "relax", "meditation", "calm", "panic", "overwhelm", "burnout", "mental health"],
        "steps": ["steps", "walking", "walk", "pedometer", "10000", "distance", "miles", "kilometers", "fitbit", "activity tracker"],
        "diet": ["diet", "nutrition", "food", "eat", "meal", "calorie", "protein", "carb", "fat", "vitamin", "mineral", "weight loss", "vegetarian", "vegan"],
        "exercise": ["exercise", "workout", "fitness", "training", "gym", "cardio", "strength", "weight lifting", "running", "jogging", "swimming"],
        "water": ["water", "hydration", "drink", "thirsty", "fluid", "dehydration", "h2o", "beverage"],
        "weight": ["weight", "bmi", "body mass", "obesity", "overweight", "underweight", "lose weight", "gain weight", "metabolism"],
        "vitamins": ["vitamin", "supplement", "mineral", "deficiency", "nutrient"],
        "mental health": ["mental health", "depression", "anxiety", "therapy", "counseling", "psychologist", "psychiatrist", "mood", "emotion"],
        "medical": ["doctor", "physician", "hospital", "clinic", "diagnosis", "treatment", "symptom", "disease", "condition", "medication", "prescription"],
        "aging": ["aging", "longevity", "lifespan", "elderly", "senior", "anti-aging"],
        "pregnancy": ["pregnancy", "pregnant", "baby", "trimester", "birth", "prenatal", "postnatal"],
        "covid": ["covid", "coronavirus", "pandemic", "virus", "vaccination", "vaccine", "booster", "mask"],
        "diabetes": ["diabetes", "blood sugar", "glucose", "insulin", "type 1", "type 2", "a1c"],
        "allergies": ["allergy", "allergic", "histamine", "pollen", "dust", "pet allergy", "food allergy"]
    }
    
    # Determine the most relevant category based on keyword matches
    category_scores = {category: 0 for category in categories}
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in user_question.lower():
                category_scores[category] += 1
    
    # Get the category with the highest score
    if max(category_scores.values()) > 0:
        response_category = max(category_scores.items(), key=lambda x: x[1])[0]
    else:
        # If no category matches, use NLP techniques to determine intent
        if any(word in user_question.lower() for word in ["how", "what", "why", "when", "where", "who", "which", "can", "should", "could", "would"]):
            # It's likely a specific question, use a more detailed default response
            response_category = "specific_question"
        else:
            response_category = "default"
    
    # Add more dynamic responses for specific questions that don't fit categories
    if response_category == "specific_question":
        # Generate a more specific response based on question type
        if "how" in user_question.lower():
            return f"That's a great question about how to approach your health. While I don't have a pre-defined answer for '{user_question}', I can suggest that you consider consulting with a healthcare professional for personalized advice. In general, making gradual changes to your lifestyle, staying consistent, and tracking your progress are key principles for most health improvements."
        
        if "what" in user_question.lower():
            return f"You've asked about '{user_question}'. This is an important topic in health and wellness. The latest research suggests that individual factors like genetics, lifestyle, and environment all play roles in this area. I recommend looking into peer-reviewed studies or speaking with a specialist who can provide guidance specific to your situation."
        
        if "why" in user_question.lower():
            return f"Understanding why certain health phenomena occur is fascinating. Regarding '{user_question}', there are often multiple factors involved including genetics, environment, lifestyle choices, and sometimes random chance. Health science is constantly evolving, so what we know today might be refined tomorrow as researchers learn more."
        
        # Default for other question types
        return f"Thank you for your question about '{user_question}'. This is an important health topic that often depends on individual circumstances. I'd recommend tracking relevant metrics in your health tracker app and consulting with a healthcare provider who can give you personalized guidance based on your specific situation."
    
    # If we have a category but it's not in our pre-defined responses, use a generic response for that category
    if response_category not in HEALTH_RESPONSES:
        return f"Thank you for your question about {response_category}. This is an important health topic that affects many aspects of wellbeing. While I don't have specific pre-defined information on this topic, I recommend consulting reliable sources like the CDC, WHO, or speaking with a healthcare professional for the most accurate and personalized guidance."
    
    # Get responses for the identified category
    responses = HEALTH_RESPONSES.get(response_category, HEALTH_RESPONSES["default"])
    
    # Select a random response from the category
    response = random.choice(responses)
    
    # Personalize the response if health data is available
    if health_data:
        personalization = "\n\nBased on your health data:\n"
        has_personalization = False
        
        if 'heart_rate' in health_data and health_data['heart_rate'] and response_category in ["heart rate", "exercise", "default"]:
            hr = health_data['heart_rate']
            if hr > 100:
                personalization += f"• Your heart rate of {hr} bpm is above the normal resting range. Consider relaxation techniques and consult a healthcare provider if this persists.\n"
                has_personalization = True
            elif hr < 60:
                personalization += f"• Your heart rate of {hr} bpm is below the typical resting range, which can be normal for athletes but worth monitoring.\n"
                has_personalization = True
            else:
                personalization += f"• Your heart rate of {hr} bpm is within the normal resting range.\n"
                has_personalization = True
                
        if 'sleep_hours' in health_data and health_data['sleep_hours'] and response_category in ["sleep", "default"]:
            sleep = health_data['sleep_hours']
            if sleep < 7:
                personalization += f"• You're getting {sleep} hours of sleep, which is below the recommended 7-9 hours for adults.\n"
                has_personalization = True
            elif sleep > 9:
                personalization += f"• You're getting {sleep} hours of sleep, which is above the typical recommendation. Excessive sleep can sometimes indicate other health issues.\n"
                has_personalization = True
            else:
                personalization += f"• Your {sleep} hours of sleep is within the recommended range for adults.\n"
                has_personalization = True
                
        if 'steps' in health_data and health_data['steps'] and response_category in ["steps", "exercise", "default"]:
            steps = health_data['steps']
            if steps < 5000:
                personalization += f"• Your step count of {steps} is considered sedentary. Try to gradually increase your daily activity.\n"
                has_personalization = True
            elif steps < 10000:
                personalization += f"• You've taken {steps} steps, which is a good start. The goal of 10,000 steps provides additional health benefits.\n"
                has_personalization = True
            else:
                personalization += f"• Great job reaching {steps} steps! You're meeting or exceeding the recommended daily activity level.\n"
                has_personalization = True
        
        # Add the personalization if we have relevant data
        if has_personalization:
            response += personalization
    
    # Add a personalized touch to make it feel more real
    current_hour = int(time.strftime("%H"))
    time_context = ""
    if 5 <= current_hour < 12:
        time_context = "Hope you're having a great morning! "
    elif 12 <= current_hour < 17:
        time_context = "Hope you're having a good afternoon! "
    elif 17 <= current_hour < 22:
        time_context = "Hope you're having a pleasant evening! "
    else:
        time_context = "Taking care of your health even at this hour shows dedication! "
    
    # Only add time context for shorter responses to avoid being too verbose
    if len(response) < 500 and random.random() < 0.3:  # Only add 30% of the time to avoid being repetitive
        response = time_context + response
    
    return response
