# Import library
from flask import Flask  # API servers frameworks
from waitress import serve  # Serve API servers frameworks
from routes import setup_routes  # Import routes

# Membuat objek Flask
app = Flask(__name__)

# Membuat Limit 50mb upload file
app.config['MAX_CONTENT_LENGTH'] = 50 * 1000 * 1000

# Setup routes endpoint dari Flask
setup_routes(app)

# Start server
if __name__ == "__main__":
    print("Server: http://0.0.0.0:8080")
    serve(app, host="0.0.0.0", port=8080)

