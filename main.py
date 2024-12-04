from flask import Flask, jsonify, request
from flask_cors import CORS
import test 

app = Flask(__name__)
CORS(app)

# Home route
@app.route('/')
def home():
    return "Welcome to the Flask API!"

# Endpoint to add a new business
@app.route('/run_model', methods=['POST'])
def run_model():
    # Extract URL from the JSON request
    data = request.get_json()
    url = data.get('url')  # Expecting {"url": "some_url_here"}
    
    print(url)
    print(data,url)
    if not url:
        return jsonify({"error": "URL is required"}), 400

    result = f"Model processed the URL: {url}"
    print(result)

    prediction = test.perform_test(url)
    return jsonify({"message": prediction})

# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True)
