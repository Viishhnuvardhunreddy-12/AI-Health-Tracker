import os
import json
from app.gemini_service import genai
from PIL import Image
import io
import base64
import joblib
import requests
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- ML Model Loading ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'calorie_predictor.pkl')
calorie_model = None
if os.path.exists(MODEL_PATH):
    calorie_model = joblib.load(MODEL_PATH)

def recognize_food_from_image(image_data):
    """
    Recognize food items from an image using Google's Gemini Vision API
    Args:
        image_data: file path to the image
    Returns:
        List of recognized food items
    """
    try:
        from app.gemini_service import genai
        # Debug log
        print(f"[DEBUG] Recognizing food from image: {image_data}")
        # Open image as bytes
        with open(image_data, 'rb') as img_file:
            image_bytes = img_file.read()
        prompt = """
        Analyze this food image and identify all food items present. Return ONLY a JSON array of food item names, nothing else. Example: [\"apple\", \"banana\", \"chicken sandwich\"] Be specific but concise with food names.
        """
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])
        text_response = response.text.strip()
        print(f"[DEBUG] Gemini API raw response: {text_response}")
        # Clean up Gemini output
        if text_response.startswith('```json'):
            text_response = text_response[7:]
        if text_response.endswith('```'):
            text_response = text_response[:-3]
        text_response = text_response.strip()
        # Try to parse JSON
        try:
            food_items = json.loads(text_response)
            if isinstance(food_items, list) and all(isinstance(f, str) for f in food_items):
                print(f"[DEBUG] Recognized food items: {food_items}")
                return food_items
            else:
                print(f"[ERROR] Gemini did not return a valid list: {food_items}")
                return ["Unable to recognize food items"]
        except Exception as parse_err:
            print(f"[ERROR] Failed to parse Gemini response: {parse_err}")
            return ["Unable to recognize food items"]
    except Exception as e:
        print(f"[ERROR] Exception during food recognition: {str(e)}")
        import traceback
        traceback.print_exc()
        return ["Unable to recognize food items"]

def get_food_insights(food_items):
    """
    Get health insights about the food items using OpenRouter API (GPT-3.5 Turbo model)
    Args:
        food_items: List of food items
    Returns:
        String with health insights
    """
    try:
        if not OPENROUTER_API_KEY:
            print("[OpenRouter] API key not found in environment variables.")
            return "Unable to generate health insights: API key missing."

        prompt = f"""
        Analyze the following food items from a health perspective: {', '.join(food_items)}\n\nProvide a brief health assessment covering:\n1. Overall nutritional value\n2. Potential health benefits\n3. Any concerns or recommendations\n4. Suggestions for healthier alternatives if needed\n\nKeep your response concise but informative, around 150-200 words.\n"""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-3.5-turbo",  # Switched to a free/available model
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 512,
            "temperature": 0.7
        }
        print(f"[OpenRouter] Sending prompt to model: {data['model']}")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            result = response.json()
            print(f"[OpenRouter] Raw response: {result}")
            return result['choices'][0]['message']['content']
        else:
            print(f"[OpenRouter] API error: {response.status_code} {response.text}")
            return "Unable to generate health insights for these food items."
    except Exception as e:
        print(f"[OpenRouter] Error getting food insights: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Unable to generate health insights for these food items."

def get_nutrition_data(food_item):
    """
    Get nutrition data for a food item from the CSV database or ML model
    """
    try:
        import pandas as pd
        import os
        # Path to the CSV file
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               'static', 'data', 'food_nutrition.csv')
        if not os.path.exists(csv_path):
            print(f"CSV file not found at: {csv_path}")
            return default_nutrition_values(food_item)
        df = pd.read_csv(csv_path)
        food_item_lower = food_item.lower()
        matches = df[df['Description'].str.lower().str.contains(food_item_lower, na=False)]
        if len(matches) == 0:
            matches = df[df['Category'].str.lower().str.contains(food_item_lower, na=False)]
        if len(matches) == 0 and ' ' in food_item_lower:
            words = food_item_lower.split()
            for word in words:
                if len(word) > 3:
                    word_matches = df[df['Description'].str.lower().str.contains(word, na=False)]
                    if len(word_matches) > 0:
                        matches = word_matches
                        break
        if len(matches) == 0:
            # Try ML model prediction if available
            if calorie_model is not None:
                # For demo, use average macros for unknown food (could be improved by user input)
                # In a real app, ask user for macros or estimate from context
                avg_protein = df['Data.Protein'].mean()
                avg_fat = df['Data.Fat.Total Lipid'].mean()
                avg_carbs = df['Data.Carbohydrate'].mean()
                avg_fiber = df['Data.Fiber'].mean()
                avg_sugar = df['Data.Sugar Total'].mean()
                features = [[avg_protein, avg_fat, avg_carbs, avg_fiber, avg_sugar]]
                calories_pred = float(calorie_model.predict(features)[0])
                return {
                    'food_item': food_item,
                    'calories': calories_pred,
                    'protein': avg_protein,
                    'fat': avg_fat,
                    'carbohydrates': avg_carbs,
                    'fiber': avg_fiber,
                    'sugar': avg_sugar
                }
            else:
                print(f"No nutrition data found for: {food_item}")
                return default_nutrition_values(food_item)
        food_data = matches.iloc[0]
        nutrition_data = {
            'food_item': food_item,
            'calories': float(food_data.get('Data.Kilocalories', 0)),
            'protein': float(food_data.get('Data.Protein', 0)),
            'fat': float(food_data.get('Data.Fat.Total Lipid', 0)),
            'carbohydrates': float(food_data.get('Data.Carbohydrate', 0)),
            'fiber': float(food_data.get('Data.Fiber', 0)),
            'sugar': float(food_data.get('Data.Sugar Total', 0))
        }
        return nutrition_data
    except Exception as e:
        print(f"Error getting nutrition data: {str(e)}")
        import traceback
        traceback.print_exc()
        return default_nutrition_values(food_item)

def default_nutrition_values(food_item):
    """Return default nutrition values for a food item"""
    return {
        'food_item': food_item,
        'calories': 100,
        'protein': 2,
        'fat': 2,
        'carbohydrates': 15,
        'fiber': 1,
        'sugar': 5
    }