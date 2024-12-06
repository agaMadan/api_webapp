from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import test

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Welcome"

@app.route('/run_model', methods=['POST'])
# @cross_origin()  # Enable CORS for this specific route
def run_model():
    # Extract URL from the JSON request
    data = request.get_json()
    # url = data.get('url')  
    urls = data.get('urls',[])  
    
    # print(f"URLS:{urls}")
    # print(data,urls)
    if not urls:
        return jsonify({"error": "URL is required"}), 400
    
    results = []
    for url in urls:
        print(f"Processing URL: {url}")
        try:
            prediction = test.perform_test(url)
            results.append(prediction)
        except Exception as e:
            results.append(f"Error processing {url}: {str(e)}")

    return jsonify({"results": results})

    # result = f"Model processed the URL: {url}"
    # print(result)

    # prediction = test.perform_test(url)
    # return jsonify({"message": prediction})

if __name__ == '__main__':
    app.run(debug=True)
