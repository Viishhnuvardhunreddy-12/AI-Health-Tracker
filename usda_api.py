import os
import requests

USDA_API_KEY = os.getenv("USDA_API_KEY")

def get_usda_nutrition(food_name):
    """Query USDA FoodData Central for nutrition info by food name."""
    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "api_key": USDA_API_KEY,
        "query": food_name,
        "pageSize": 1
    }
    try:
        resp = requests.get(search_url, params=params)
        resp.raise_for_status()
        results = resp.json()
        if results.get("foods"):
            food = results["foods"][0]
            # Extract common nutrients
            nutrients = {n["nutrientName"]: n["value"] for n in food.get("foodNutrients", [])}
            return {
                "food_item": food.get("description", food_name),
                "calories": nutrients.get("Energy", 0),
                "protein": nutrients.get("Protein", 0),
                "fat": nutrients.get("Total lipid (fat)", 0),
                "carbohydrates": nutrients.get("Carbohydrate, by difference", 0),
                "fiber": nutrients.get("Fiber, total dietary", 0),
                "sugar": nutrients.get("Sugars, total including NLEA", 0)
            }
        else:
            print(f"[USDA] No foods found for: {food_name}")
            return None
    except Exception as e:
        print(f"[USDA] Error fetching data for {food_name}: {e}")
        return None
