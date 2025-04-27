import pandas as pd
import os
import csv
import difflib
from app.usda_api import get_usda_nutrition

# Path to the CSV file
CSV_PATH = os.path.join(os.path.dirname(__file__), 'static', 'data', 'food_nutrition.csv')

def ensure_nutrition_data_exists():
    """Ensure the nutrition data CSV exists, create with sample data if not"""
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    
    if not os.path.exists(CSV_PATH):
        # Create a sample nutrition database if it doesn't exist
        with open(CSV_PATH, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['food_item', 'calories', 'protein', 'fat', 'carbohydrates', 'fiber', 'sugar'])
            
            # Add some common food items with their nutritional values (per 100g)
            sample_data = [
                ['apple', 52, 0.3, 0.2, 14, 2.4, 10.3],
                ['banana', 89, 1.1, 0.3, 22.8, 2.6, 12.2],
                ['rice', 130, 2.7, 0.3, 28.2, 0.4, 0.1],
                ['chicken breast', 165, 31, 3.6, 0, 0, 0],
                ['egg', 155, 12.6, 10.6, 1.1, 0, 1.1],
                ['bread', 265, 9, 3.2, 49, 2.7, 5],
                ['potato', 77, 2, 0.1, 17, 2.2, 0.8],
                ['tomato', 18, 0.9, 0.2, 3.9, 1.2, 2.6],
                ['carrot', 41, 0.9, 0.2, 9.6, 2.8, 4.7],
                ['broccoli', 34, 2.8, 0.4, 6.6, 2.6, 1.7],
                ['salmon', 206, 22, 13, 0, 0, 0],
                ['milk', 42, 3.4, 1, 5, 0, 5],
                ['cheese', 402, 25, 33, 1.3, 0, 0.1],
                ['yogurt', 59, 3.5, 3.3, 4.7, 0, 4.7],
                ['orange', 43, 0.9, 0.1, 8.3, 2.4, 8.2],
                ['pasta', 131, 5, 1.1, 25, 1.2, 0.9],
                ['beef', 250, 26, 17, 0, 0, 0],
                ['spinach', 23, 2.9, 0.4, 3.6, 2.2, 0.4],
                ['avocado', 160, 2, 14.7, 8.5, 6.7, 0.7],
                ['chocolate', 546, 4.9, 31, 61, 7, 48]
            ]
            
            for item in sample_data:
                writer.writerow(item)
        
        print(f"Created sample nutrition database at {CSV_PATH}")

def get_nutrition_data(food_item):
    """
    Retrieve nutrition data for a food item from the CSV file.
    Uses exact and fuzzy matching for best results.
    If not found locally, queries the USDA API.
    Returns a dict with nutrition info or None if not found.
    """
    try:
        df = pd.read_csv(CSV_PATH)
        food_item_clean = food_item.lower().strip()
        # Exact match (case-insensitive)
        matches = df[df['food_item'].str.lower().str.strip() == food_item_clean]
        if not matches.empty:
            return matches.iloc[0].to_dict()
        # Fuzzy match if exact fails
        close_matches = difflib.get_close_matches(food_item_clean, df['food_item'].str.lower().tolist(), n=1, cutoff=0.8)
        if close_matches:
            match = df[df['food_item'].str.lower() == close_matches[0]]
            if not match.empty:
                return match.iloc[0].to_dict()
        # Not found locally, try USDA API
        usda_data = get_usda_nutrition(food_item)
        if usda_data:
            return usda_data
        print(f"[WARN] Nutrition data not found for: {food_item}")
        return None
    except Exception as e:
        print(f"Error getting nutrition data for {food_item}: {str(e)}")
        return None

def get_all_food_items():
    """Get a list of all food items in the database"""
    ensure_nutrition_data_exists()
    
    try:
        df = pd.read_csv(CSV_PATH)
        return df['food_item'].tolist()
    except Exception as e:
        print(f"Error getting food items: {str(e)}")
        return []