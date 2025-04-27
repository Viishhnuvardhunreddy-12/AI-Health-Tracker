from app import create_app

# Create the Flask application instance
app = create_app()
app.app_context().push()  # Push an application context

if __name__ == "__main__":
    # Run the app with explicit settings to avoid lazy loading
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=True, load_dotenv=False)