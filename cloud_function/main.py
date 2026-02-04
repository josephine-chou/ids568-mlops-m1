import functions_framework
import joblib
import numpy as np
from flask import jsonify
import os

# Global variable for model caching
model = None

def load_model():
    """Load model once and cache in global variable"""
    global model
    if model is None:
        # Model file should be in the same directory
        model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
        model = joblib.load(model_path)
    return model

@functions_framework.http
def predict(request):
    """HTTP Cloud Function for iris prediction
    Args:
        request (flask.Request): The request object.
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
    """
    # Set CORS headers for preflight requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    try:
        # Get request JSON
        request_json = request.get_json(silent=True)
        
        if not request_json or 'features' not in request_json:
            return (jsonify({
                'error': 'Missing features in request body',
                'expected_format': {'features': [5.1, 3.5, 1.4, 0.2]}
            }), 400, headers)
        
        features = request_json['features']
        
        # Validate features length
        if len(features) != 4:
            return (jsonify({
                'error': 'Features must contain exactly 4 values',
                'received': len(features)
            }), 400, headers)
        
        # Load model (cached after first call)
        clf = load_model()
        
        # Convert to numpy array and predict
        features_array = np.array([features])
        prediction = int(clf.predict(features_array)[0])
        probabilities = clf.predict_proba(features_array)[0].tolist()
        
        # Map to class names
        class_names = ["setosa", "versicolor", "virginica"]
        class_name = class_names[prediction]
        
        response = {
            'prediction': prediction,
            'class_name': class_name,
            'probabilities': probabilities
        }
        
        return (jsonify(response), 200, headers)
        
    except Exception as e:
        return (jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500, headers)