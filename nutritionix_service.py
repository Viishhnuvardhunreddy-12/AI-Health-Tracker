import os
import requests

NUTRITIONIX_APP_ID = os.environ.get('NUTRITIONIX_APP_ID')
NUTRITIONIX_API_KEY = os.environ.get('NUTRITIONIX_API_KEY')


def get_nutritionix_data(food_name):
    """
    Query Nutritionix API for nutrition data for a given food name.
    Returns a dict with nutrition info or None if failed.
    """
    url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
    headers = {
        'x-app-id': NUTRITIONIX_APP_ID,
        'x-app-key': NUTRITIONIX_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'query': food_name
    }
    try:
        print(f"[Nutritionix] Sending request for: {food_name}")
        print(f"[Nutritionix] Using App ID: {NUTRITIONIX_APP_ID}, API Key present: {bool(NUTRITIONIX_API_KEY)}")
        response = requests.post(url, headers=headers, json=data)
        print(f"[Nutritionix] Response status: {response.status_code}")
        print(f"[Nutritionix] Response body: {response.text}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[Nutritionix] API error: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"[Nutritionix] Exception: {e}")
        return None
