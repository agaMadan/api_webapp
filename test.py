import json, os, requests, sys, warnings
from dotenv import load_dotenv
from urllib.parse import urlparse
import commons, constants, feature_extractor
import numpy as np

load_dotenv()

def convert_item(item):
    if isinstance(item, (np.floating, np.integer, float, int)):
        return float(item)
    elif isinstance(item, np.ndarray):
        return [convert_item(x) for x in item]
    elif isinstance(item, list):
        return [convert_item(x) for x in item]
    return item

def send_features_to_scoring_uri(features):
    try:
        scoring_uri = os.getenv('SCORING_URI')
        
        if not scoring_uri:
            print("Error: SCORING_URI not found in environment variables")
            return None
        
        converted_features = convert_item(features)
        
        payload = {
            'data': converted_features
        }
        
        response = requests.post(
            scoring_uri, 
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print("Response Status Code:", response.status_code)
        print("Response Headers:", response.headers)
        print("Response Text:", response.text)
        # Check the response
        response.raise_for_status()
        
        return response
    
    except requests.exceptions.RequestException as e:
        print(f"Error sending features to scoring URI: {e}")
        return None

def inverse_transform(predictions):
    if isinstance(predictions, list):
        return [constants.TARGET_MAP.get(pred, f"Unknown ({pred})") for pred in predictions]
    else:
        return constants.TARGET_MAP.get(predictions, f"Unknown ({predictions})")

def perform_test(test_file_url):
    try:
        wavelength, intensity = commons.get_wavelength_intensity_test_data(test_file_url)
        processed_data = commons.get_reqd_intensity_data(wavelength, intensity)
        features = feature_extractor.write_feature_set(processed_data, constants.SUB_TASK_TEST)

        # print(f"Total features shape: {len(features)}")
        
        # Send ONLY the first row of features
        first_row_features = features[0]
        # print(f"First row features: {first_row_features}")
        # print(f"First row features length: {len(first_row_features)}")
        # print(f"Processed data: Features = {features}")
        
        response = send_features_to_scoring_uri(first_row_features)
        # print("Response:",response) # <Response [200]> is what we want
        
        if response is not None:
            try:
                # Try to parse the response
                result = response.json()
                # print("Raw Response:", result)
                result = json.loads(result)
                
                # Check if 'predictions' or 'result' key exists
                prediction = None
                if isinstance(result, dict):
                    if 'predictions' in result:
                        prediction = result['predictions'][0]  
                    elif 'result' in result:
                        prediction = result['result'][0]  
                    elif 'prediction' in result:
                        prediction = result['prediction']
                elif isinstance(result, list):
                    prediction = result[0] 
                
                if prediction is None:
                    print("Could not extract prediction from response")
                    return None
                
                # print("Extracted Prediction:", prediction)
                
                # print("Prediction:", prediction)
                prediction = inverse_transform(prediction)
                result = {
                    "status": "success",
                    "data": {
                        "prediction": prediction,
                        # "confidence": 0.95
                    }
                }

                # print(json.dumps(result))               
                # print(json.dumps(prediction))               
                return prediction
            
            except json.JSONDecodeError as e:
                print("Error decoding JSON response:", e)
                print("Response text:", response.text)
                return None
        
        return None
    
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
        return None

if __name__ == "__main__":
    # get SAS URL from the backend
    if len(sys.argv) > 1:
        sas_url = sys.argv[1] 
        parsed_url = urlparse(sas_url)
        file_name = os.path.basename(parsed_url.path)

        print("Starting test.py execution...")
        print(f"Received File: {file_name}")
        print(f"Received URL: {sas_url}")
        
        perform_test(sas_url)
    else:
        print("No SAS URL provided.")







# TODO: Uncomment and modify the loop below to send all rows
                    # predictions = []
                    # for row_features in features:
                    #     response = send_features_to_scoring_uri(row_features)
                    #     if response is not None:
                    #         try:
                    #             result = response.json()
                    #             # Extract prediction from result
                    #             if isinstance(result, dict) and 'predictions' in result:
                    #                 predictions.append(result['predictions'][0])
                    #             elif isinstance(result, list):
                    #                 predictions.append(result[0])
                    #         except Exception as e:
                    #             print(f"Error processing row: {e}")
                    #             predictions.append(None)
                    # 
                    # print("All Predictions:", predictions)