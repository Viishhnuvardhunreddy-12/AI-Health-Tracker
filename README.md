# Health Tracker: Personalized Health Monitoring App

## Overview

Health Tracker is a Flask-based web application designed to help users monitor and improve their health by tracking daily vitals and receiving personalized insights. Leveraging the Google Gemini API for AI-driven recommendations and Chart.js for visualizations, the app empowers users with actionable health advice. It also includes SMS notification capabilities for real-time health tips.

---

## Features
- **Track Vitals:** Record heart rate, sleep hours, steps, mood, and stress levels.
- **Personalized Insights:** Get AI-generated health advice using Google Gemini API.
- **Data Visualization:** View trends and patterns with interactive charts (Chart.js).
- **User Identification:** Store name and phone number with each entry.
- **SMS Notifications:** Receive health insights via SMS (currently logs messages; can be connected to Twilio).
- **Machine Learning Analysis:** Basic ML analytics using scikit-learn.
- **Secure Data:** All data stored locally with SQLite.

---

## Technology Stack
- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Database:** SQLite
- **AI Integration:** Google Gemini API
- **ML:** scikit-learn
- **SMS Service:** Placeholder (can integrate with Twilio)

---

## Project Structure
```
health tracker/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   ├── forms.py
│   ├── chatbot.py (Gemini API integration)
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   └── templates/
│       ├── base.html
│       └── ...
├── requirements.txt
├── run.py
├── .env
└── README.md
```

---

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repo_url>
   cd "health tracker"
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Create a `.env` file in the project root with your Google Gemini API key:
     ```env
     GEMINI_API_KEY=AIzaSyAK0YIK3HSdhF4MyyVZoz_Qe1RcbJ_6hSc
     # Add other secrets as needed
     ```

5. **Run the application:**
   ```bash
   python run.py
   ```
   The app will be available at `http://127.0.0.1:5000/`.

---

## Usage Guide
1. **Open the app in your browser.**
2. **Enter your name, phone number, and daily vitals.**
3. **Submit the form to save your data.**
4. **View personalized insights and charts.**
5. **(Optional) Receive insights via SMS (currently logs to console).**

---

## Google Gemini API Integration
- The app uses Gemini API to analyze user data and provide health tips.
- API key is read from the `.env` file.
- For more information, see [Google Gemini documentation](https://ai.google.dev/).

---

## SMS Notification (Placeholder)
- SMS functionality is implemented as a placeholder that logs messages to the console.
- To enable real SMS notifications, integrate with a service like [Twilio](https://www.twilio.com/):
  1. Sign up for Twilio and get API credentials.
  2. Replace the placeholder code in the SMS sending function with Twilio's API calls.

---

## Customization & Extensions
- **Integrate more vitals:** Add new fields in `forms.py`, update `models.py`, and adjust templates.
- **Enhance ML analysis:** Expand ML models in the backend for advanced insights.
- **UI Improvements:** Customize styles in `app/static/css/style.css` and templates.
- **Production Deployment:** Use a production server (e.g., Gunicorn) and configure environment variables securely.

---

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## License
[MIT](LICENSE)

---

## Contact
- **Author:** [Your Name]
- **Project Maintainer:** [Your Contact Info]

For questions or support, please open an issue or contact the maintainer.

---

*Last updated: April 27, 2025*