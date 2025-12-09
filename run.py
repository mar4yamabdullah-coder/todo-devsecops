from app.create_app import create_app

# Create the Flask application using the factory pattern
app = create_app()


if __name__ == "__main__":
    # Secure version of the application (debug should be False in production,
    # but kept True here for demo and local testing).
    app.run(host="0.0.0.0", port=5000, debug=True)
