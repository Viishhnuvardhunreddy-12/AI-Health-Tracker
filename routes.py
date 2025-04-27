from flask import render_template, request, redirect, url_for, flash, session
from flask import Blueprint
from app.forms import VitalsForm
from app.gemini_service import get_health_insights, get_personalized_recommendations, genai, get_chatbot_response
from app.models import save_vitals, get_recent_vitals, analyze_vitals
from app.openai_service import get_chatbot_response_gpt
from app.email_service import send_health_notification
import secrets  # Added for secret key generation
import json  # Added for json.dumps
import requests  # For API requests
import datetime
import re  # For regex
from dotenv import load_dotenv  # Added for loading environment variables
from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField
from app.nutritionix_service import get_nutritionix_data

# Generate a secure secret key (64-character hex string)
print("Generated secret key:", secrets.token_hex(32))

# Load environment variables
load_dotenv(override=True)

main = Blueprint('main', __name__)

@main.route('/chatbot')
def chatbot_page():
    """Render the standalone chatbot page"""
    return render_template('chatbot.html')

# Function to send SMS
def send_sms_notification(phone_number, message):
    """
    Send SMS notification using Twilio service or mock service
    
    This function uses Twilio to send SMS notifications to users
    with their health insights and recommendations.
    If Twilio verification fails, it falls back to a mock service.
    """
    # Import Twilio client and os for environment variables
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    import os
    import datetime
    
    # Format the phone number to E.164 format if needed
    if phone_number and not phone_number.startswith('+'):
        # Assuming Indian number if no country code
        phone_number = '+91' + phone_number.lstrip('0')
        print(f"Formatted phone number to: {phone_number}")
    
    # Log the SMS that would be sent (for debugging)
    print(f"\n==== SMS MESSAGE ====")
    print(f"TO: {phone_number}")
    print(f"TIME: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"CONTENT:\n{message}")
    print(f"==== END MESSAGE ====\n")
    
    # Set this to True to use mock SMS service instead of Twilio
    USE_MOCK_SMS = True
    
    if USE_MOCK_SMS:
        # Use mock SMS service (just logs the message)
        print("Using MOCK SMS service - message logged but not actually sent")
        flash("SMS notification simulated successfully! Check console for the message content.", "success")
        return True
    
    # Otherwise, use real Twilio service
    try:
        # Get Twilio credentials from environment variables
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')
        
        # Debug output to verify credentials are loaded
        print(f"TWILIO_ACCOUNT_SID: {'Found' if account_sid else 'Not found'}")
        print(f"TWILIO_AUTH_TOKEN: {'Found' if auth_token else 'Not found'}")
        print(f"TWILIO_PHONE_NUMBER: {twilio_number if twilio_number else 'Not found'}")
        
        # Check if credentials are available
        if not all([account_sid, auth_token, twilio_number]):
            print("ERROR: Twilio credentials not found in environment variables. SMS not sent.")
            flash("SMS notification could not be sent: Missing Twilio credentials", "warning")
            return False
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send the message
        sms = client.messages.create(
            body=message,
            from_=twilio_number,
            to=phone_number
        )
        
        print(f"SMS sent successfully! SID: {sms.sid}")
        flash("SMS notification sent successfully!", "success")
        return True
    except TwilioRestException as e:
        error_message = f"Twilio Error: {str(e)}"
        print(error_message)
        
        # Provide more specific error messages based on error code
        if hasattr(e, 'code') and e.code == 21608:  # Unverified number in trial account
            flash("SMS not sent via Twilio: Your phone number is not verified. Using mock SMS service instead.", "warning")
            # Fall back to mock SMS service
            return True
        elif hasattr(e, 'code') and e.code == 21211:  # Invalid phone number
            flash("SMS not sent: The phone number you provided is invalid. Please enter a valid phone number with country code.", "danger")
        else:
            flash(f"SMS notification failed: {str(e)}", "danger")
        return False
    except Exception as e:
        print(f"Unexpected error sending SMS: {str(e)}")
        flash(f"SMS notification failed: {str(e)}", "danger")
        return False

@main.route('/')
@main.route('/index')  # Add this route
def index():
    return render_template('index.html')

@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form = VitalsForm()
    
    # Get recent vitals data for charts
    recent_data = get_recent_vitals(days=30)
    
    # Prepare data for charts
    dates = [entry.get('date', '') for entry in recent_data]
    heart_rates = [entry.get('heart_rate', 0) for entry in recent_data]
    sleep_hours = [entry.get('sleep_hours', 0) for entry in recent_data]
    steps = [entry.get('steps', 0) for entry in recent_data]
    # Normalize moods to string labels for frontend chart
    mood_map = {5: 'excellent', 4: 'great', 3: 'good', 2: 'okay', 1: 'poor', 0: 'unknown'}
    moods = [(mood_map[entry.get('mood', 0)] if isinstance(entry.get('mood', 0), int) else entry.get('mood', 'unknown')).lower() for entry in recent_data]
    
    # Get anomalies
    analysis_result = analyze_vitals(recent_data)
    anomalies = analysis_result.get('anomalies', [])
    
    # Initialize variables
    health_insights = None
    recommendations = None
    user_name = None
    
    if form.validate_on_submit():
        # Process form data and save to storage
        latest_vitals = {
            'name': form.name.data,
            'email': form.email.data,
            'heart_rate': form.heart_rate.data,
            'sleep_hours': form.sleep_hours.data,
            'steps': form.steps.data,
            'mood': int(form.mood.data) if isinstance(form.mood.data, str) else form.mood.data
        }
        
        # Save the data
        saved_vitals = save_vitals(latest_vitals)
        
        # Get insights based on all data
        health_insights = get_health_insights(saved_vitals, recent_data)
        recommendations = get_personalized_recommendations(saved_vitals)
        
        # Store user name for personalized greeting
        user_name = saved_vitals.get('name')
        
        # Send email notification if email is provided
        if saved_vitals.get('email'):
            try:
                # Create HTML email content with vitals summary and insights
                email_subject = f"Health Tracker: Your Health Update - {datetime.datetime.now().strftime('%b %d, %Y')}"
                
                # Start building HTML email content
                email_html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                        .header {{ background-color: #4a6fdc; color: white; padding: 20px; text-align: center; }}
                        .content {{ padding: 20px; }}
                        .vitals {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                        .insights {{ margin-bottom: 20px; }}
                        .recommendations {{ background-color: #e6f7ff; padding: 15px; border-radius: 5px; }}
                        h2 {{ color: #4a6fdc; }}
                        .footer {{ font-size: 12px; text-align: center; margin-top: 30px; color: #777; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Your Health Update</h1>
                    </div>
                    <div class="content">
                        <p>Hello {user_name},</p>
                        
                        <p>Thank you for recording your health data. Here's your personalized health update:</p>
                        
                        <div class="vitals">
                            <h2>Your Vitals</h2>
                            <p><strong>Heart Rate:</strong> {saved_vitals.get('heart_rate')} bpm</p>
                            <p><strong>Sleep:</strong> {saved_vitals.get('sleep_hours')} hours</p>
                            <p><strong>Steps:</strong> {saved_vitals.get('steps')}</p>
                            <p><strong>Mood:</strong> {saved_vitals.get('mood')}/10</p>
                        </div>
                """
                
                # Add basic analysis
                email_html += "<div class=\"insights\">\n<h2>Quick Analysis</h2>\n<ul>"
                
                if saved_vitals.get('heart_rate') > 100:
                    email_html += "<li>Your heart rate is elevated. Consider relaxation techniques.</li>"
                elif saved_vitals.get('heart_rate') < 60:
                    email_html += "<li>Your heart rate is lower than normal. Monitor for symptoms.</li>"
                else:
                    email_html += "<li>Your heart rate is within normal range.</li>"
                    
                if saved_vitals.get('sleep_hours') < 6:
                    email_html += "<li>You need more sleep for optimal health.</li>"
                elif saved_vitals.get('sleep_hours') > 9:
                    email_html += "<li>You're getting excellent sleep duration.</li>"
                else:
                    email_html += "<li>Your sleep duration is good.</li>"
                    
                if saved_vitals.get('steps') < 5000:
                    email_html += "<li>Try to increase your daily steps for better health.</li>"
                elif saved_vitals.get('steps') > 10000:
                    email_html += "<li>Great job on your step count!</li>"
                else:
                    email_html += "<li>Your step count is good, but aim for 10,000 steps daily.</li>"
                
                email_html += "</ul>\n</div>"
                
                # Add AI-generated health insights if available
                if health_insights:
                    email_html += f"""
                    <div class="insights">
                        <h2>AI Health Insights</h2>
                        {health_insights}
                    </div>
                    """
                
                # Add AI-generated recommendations if available
                if recommendations:
                    email_html += f"""
                    <div class="recommendations">
                        <h2>Personalized Recommendations</h2>
                        {recommendations}
                    </div>
                    """
                
                # Close the HTML email
                email_html += f"""
                        <div class="footer">
                            <p>This email was sent from the Health Tracker application. Your health data is kept private and secure.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # Send the email notification
                email_sent = send_health_notification(
                    to_email=saved_vitals.get('email'),
                    subject=email_subject,
                    html_content=email_html
                )
                
                if email_sent:
                    flash("Health insights sent to your email successfully!", "success")
                else:
                    flash("Could not send email. Please check the console for error details.", "warning")
                    
            except Exception as e:
                print(f"Error sending email notification: {str(e)}")
                flash(f"Error sending email: {str(e)}", "danger")
        
        # Flash success message and redirect to refresh the page with new data
        flash('Health data recorded successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    # For GET requests
    # If we have recent data, get insights for the latest entry
    if recent_data:
        latest = recent_data[-1]
        health_insights = get_health_insights(latest, recent_data)
        recommendations = get_personalized_recommendations(latest)
        user_name = latest.get('name')
    
    # Remove the today's date for the dashboard header
    # today = datetime.datetime.now()  # Remove this line
    
    # Add latest_vitals for the stats cards
    latest_vitals = {}
    if recent_data and len(recent_data) > 0:
        latest_vitals = recent_data[-1]
    
    # Remove the current datetime
    # now = datetime.now()  # Remove this line
    
    # Define any missing variables
    latest_heart_rate = latest_vitals.get('heart_rate', 0)
    latest_sleep = latest_vitals.get('sleep_hours', 0)
    latest_steps = latest_vitals.get('steps', 0)
    latest_mood = latest_vitals.get('mood', 0)
    
    # Prepare chart data as JSON
    chart_data = {
        'dates': dates,
        'heart_rates': heart_rates,
        'sleep_hours': sleep_hours,
        'steps': steps,
        'moods': moods
    }
    chart_data_json = json.dumps(chart_data)
    
    # Single return statement with all variables - remove 'now' and 'today'
    return render_template('dashboard.html',
                          form=form,
                          user_name=user_name,
                          latest_heart_rate=latest_heart_rate,
                          latest_sleep=latest_sleep,
                          latest_steps=latest_steps,
                          latest_mood=latest_mood,
                          health_insights=health_insights,
                          recommendations=recommendations,
                          chart_data=chart_data_json,
                          dates=dates,
                          heart_rates=heart_rates,
                          sleep_hours=sleep_hours,
                          steps=steps,
                          moods=moods,
                          anomalies=anomalies,
                          latest_vitals=latest_vitals)

@main.route('/api/alerts', methods=['GET'])
def get_real_time_alerts():
    """
    API endpoint to fetch real-time health alerts
    Returns alerts based on recent health data
    """
    try:
        # Get recent vitals data
        recent_data = get_recent_vitals(days=7)
        
        # If no data is available, return empty alerts
        if not recent_data:
            return {"alerts": []}
        
        # Create simple alerts based on the most recent data
        alerts = []
        
        # Get the most recent entry
        latest = recent_data[-1] if recent_data else {}
        
        # Check for heart rate issues
        if latest.get('heart_rate', 0) > 100:
            alerts.append({
                'date': latest.get('date', ''),
                'type': 'heart_rate',
                'message': f"Elevated heart rate detected: {latest.get('heart_rate')} bpm",
                'data': {'heart_rate': latest.get('heart_rate')}
            })
        elif latest.get('heart_rate', 0) < 60 and latest.get('heart_rate', 0) > 0:
            alerts.append({
                'date': latest.get('date', ''),
                'type': 'heart_rate',
                'message': f"Low heart rate detected: {latest.get('heart_rate')} bpm",
                'data': {'heart_rate': latest.get('heart_rate')}
            })
        
        # Check for sleep issues
        if latest.get('sleep_hours', 0) < 6 and latest.get('sleep_hours', 0) > 0:
            alerts.append({
                'date': latest.get('date', ''),
                'type': 'sleep_hours',
                'message': f"Sleep duration below recommended levels: {latest.get('sleep_hours')} hours",
                'data': {'sleep_hours': latest.get('sleep_hours')}
            })
        
        # Check for mood issues
        if latest.get('mood', 5) <= 2:
            alerts.append({
                'date': latest.get('date', ''),
                'type': 'mood',
                'message': f"Mood score indicates potential concern: {latest.get('mood')}/5",
                'data': {'mood': latest.get('mood')}
            })
        
        # Check for low steps
        if latest.get('steps', 0) < 5000 and latest.get('steps', 0) > 0:
            alerts.append({
                'date': latest.get('date', ''),
                'type': 'steps',
                'message': f"Step count below daily target: {latest.get('steps')} steps",
                'data': {'steps': latest.get('steps')}
            })
        
        print(f"Returning {len(alerts)} health alerts")
        return {"alerts": alerts}
    
    except Exception as e:
        print(f"Error generating alerts: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"alerts": [], "error": str(e)}

@main.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    # Placeholder: Simulate a leaderboard based on steps
    from app.models import get_recent_vitals
    recent_data = get_recent_vitals(days=30)
    # Simulate users (in real app, use user accounts)
    leaderboard = []
    for entry in recent_data:
        leaderboard.append({
            "date": entry.get("date", ""),
            "steps": entry.get("steps", 0)
        })
    leaderboard = sorted(leaderboard, key=lambda x: x["steps"], reverse=True)[:10]
    return {"leaderboard": leaderboard}

@main.route('/api/ai-goal', methods=['POST'])
def ai_goal_setting():
    # AI-powered goal suggestion based on recent data
    from app.models import get_recent_vitals
    from app.gemini_service import get_health_insights
    recent_data = get_recent_vitals(days=14)
    if not recent_data:
        return {"goal": "Record more data to get personalized goals."}
    latest = recent_data[-1]
    insights = get_health_insights(latest, recent_data)
    # Simulate extracting a goal from insights
    goal = "Increase your daily steps by 10% for the next week!"
    return {"goal": goal, "insights": insights}

@main.route('/api/chatbot', methods=['POST'])
def health_chatbot():
    """
    Simplified chatbot endpoint that directly uses the Google Gemini API
    """
    from app.direct_chatbot import get_direct_chatbot_response
    from app.models import get_recent_vitals
    import traceback
    import time
    
    start_time = time.time()
    
    try:
        # Get user question
        user_question = request.json.get("question", "")
        if not user_question:
            return {"answer": "Please ask a question."}
        
        # Log the question for debugging
        print(f"Received chatbot question: {user_question}")
        
        # Get context with latest vitals
        recent_data = get_recent_vitals(days=14)
        latest = recent_data[-1] if recent_data else {}
        
        # Get response directly from Gemini API
        answer = get_direct_chatbot_response(user_question, health_data=latest)
        
        # Log the response time and preview
        elapsed_time = time.time() - start_time
        print(f"Generated chatbot response in {elapsed_time:.2f}s: {answer[:50]}...")
        
        return {"answer": answer}
    
    except Exception as e:
        # Log the full error with traceback
        error_msg = f"Error in chatbot: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        
        # Return a user-friendly error message
        return {
            "answer": "I'm having trouble processing your request right now. Please try again later."
        }, 500  # Return 500 status code to indicate server error

@main.route('/activity-log')
def activity_log():
    # In a real application, you would fetch activity data from the database
    # For now, we'll just render the template
    return render_template('activity_log.html')

class SettingsForm(FlaskForm):
    daily_reminder = BooleanField('Daily Reminders')
    goal_achievement = BooleanField('Goal Achievements')
    health_insights = BooleanField('Health Insights')
    weekly_reports = BooleanField('Weekly Reports')
    submit = SubmitField('Save Settings')

@main.route('/settings', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()
    
    if form.validate_on_submit():
        # Save settings to session for now (since we don't have a database model yet)
        session['settings'] = {
            'daily_reminder': form.daily_reminder.data,
            'goal_achievement': form.goal_achievement.data,
            'health_insights': form.health_insights.data,
            'weekly_reports': form.weekly_reports.data
        }
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('main.settings'))
    
    # Load current settings from session
    if 'settings' in session:
        form.daily_reminder.data = session['settings'].get('daily_reminder', True)
        form.goal_achievement.data = session['settings'].get('goal_achievement', True)
        form.health_insights.data = session['settings'].get('health_insights', True)
        form.weekly_reports.data = session['settings'].get('weekly_reports', True)
    
    return render_template('settings.html', form=form)

from werkzeug.utils import secure_filename
import os
from app.food_recognition import recognize_food_from_image, get_nutrition_data, get_food_insights

@main.route('/calorie_check', methods=['GET', 'POST'])
def calorie_check():
    from flask import session
    # On POST, process and redirect (PRG pattern)
    if request.method == 'POST':
        food_items = []
        nutrition_data = []
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbohydrates': 0,
            'fiber': 0,
            'sugar': 0
        }
        food_insights = ""
        image_path = None
        raw_api_output = None
        # ... (existing POST logic for analyzing food and populating above variables)
        # Process form submission
        food_items = []  # Always reset to avoid carryover between form types
        nutrition_data = []
        image_path = None
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbohydrates': 0,
            'fiber': 0,
            'sugar': 0
        }
        food_insights = ""
        manual_food = request.form.get('manual_food', '').strip()
        if 'food_image' in request.files and request.files['food_image'].filename:
            # Handle image upload
            file = request.files['food_image']
            filename = secure_filename(file.filename)
            upload_folder = os.path.join('app', 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join('static', 'uploads', filename)
            file_path = os.path.join('app', image_path)
            file.save(file_path)
            # Call recognition and capture raw output
            from app.food_recognition import recognize_food_from_image
            try:
                food_items = recognize_food_from_image(file_path)
                if hasattr(recognize_food_from_image, 'last_raw_output'):
                    raw_api_output = recognize_food_from_image.last_raw_output
            except Exception as e:
                raw_api_output = str(e)
            print(f"Recognized food items: {food_items}")
        elif manual_food:
            # Only process manual food if no image uploaded
            food_items = [item.strip() for item in manual_food.split(',') if item.strip()]
        food_items = [item for item in food_items if item and "Unable to recognize" not in item]
        nutrition_data = []
        for item in food_items:
            # Try Nutritionix API first
            nutritionix_response = get_nutritionix_data(item)
            if nutritionix_response and 'foods' in nutritionix_response:
                for food in nutritionix_response['foods']:
                    data = {
                        'food_item': food.get('food_name', item),
                        'calories': food.get('nf_calories', 0),
                        'protein': food.get('nf_protein', 0),
                        'fat': food.get('nf_total_fat', 0),
                        'carbohydrates': food.get('nf_total_carbohydrate', 0),
                        'fiber': food.get('nf_dietary_fiber', 0),
                        'sugar': food.get('nf_sugars', 0)
                    }
                    nutrition_data.append(data)
                    try:
                        total_nutrition['calories'] += float(data.get('calories', 0))
                        total_nutrition['protein'] += float(data.get('protein', 0))
                        total_nutrition['fat'] += float(data.get('fat', 0))
                        total_nutrition['carbohydrates'] += float(data.get('carbohydrates', 0))
                        total_nutrition['fiber'] += float(data.get('fiber', 0))
                        total_nutrition['sugar'] += float(data.get('sugar', 0))
                    except Exception as agg_err:
                        print(f"[ERROR] Aggregating nutrition for {item}: {agg_err}")
            else:
                # Fallback to old method if Nutritionix fails
                data = get_nutrition_data(item)
                if data:
                    nutrition_data.append(data)
                    try:
                        total_nutrition['calories'] += float(data.get('calories', 0))
                        total_nutrition['protein'] += float(data.get('protein', 0))
                        total_nutrition['fat'] += float(data.get('fat', 0))
                        total_nutrition['carbohydrates'] += float(data.get('carbohydrates', 0))
                        total_nutrition['fiber'] += float(data.get('fiber', 0))
                        total_nutrition['sugar'] += float(data.get('sugar', 0))
                    except Exception as agg_err:
                        print(f"[ERROR] Aggregating nutrition for {item}: {agg_err}")
                else:
                    print(f"[WARN] No nutrition data for: {item}")
        food_insights = get_food_insights([d['food_item'] for d in nutrition_data]) if nutrition_data else ""
        # Pass raw_api_output to template for debugging
        # Store results in session
        session['food_items'] = food_items
        session['nutrition_data'] = nutrition_data
        session['total_nutrition'] = total_nutrition
        session['food_insights'] = food_insights
        session['image_path'] = image_path
        session['raw_api_output'] = raw_api_output
        return redirect(url_for('main.calorie_check'))

    # On GET, show results if in session, else show defaults
    food_items = session.pop('food_items', [])
    nutrition_data = session.pop('nutrition_data', [])
    total_nutrition = session.pop('total_nutrition', {
        'calories': 0,
        'protein': 0,
        'fat': 0,
        'carbohydrates': 0,
        'fiber': 0,
        'sugar': 0
    })
    food_insights = session.pop('food_insights', "")
    image_path = session.pop('image_path', None)
    raw_api_output = session.pop('raw_api_output', None)
    return render_template('calorie_check.html', 
                          food_items=food_items,
                          nutrition_data=nutrition_data,
                          total_nutrition=total_nutrition,
                          food_insights=food_insights,
                          image_path=image_path,
                          raw_api_output=raw_api_output)
