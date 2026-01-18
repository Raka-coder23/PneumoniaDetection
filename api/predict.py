import os
import json
import base64
import numpy as np
from PIL import Image
import cv2
import io
from tensorflow.keras.models import load_model

# Global model variable to cache it across function invocations
model = None

def load_model_once():
    global model
    if model is None:
        model_path = 'model.keras'
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file {model_path} not found")
        model = load_model(model_path)
    return model

def getResult(image_bytes):
    """Process image bytes and return prediction"""
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise ValueError("Image not found or unreadable.")

    # Process image
    image = Image.fromarray(image)
    image = image.resize((256, 256))  # Match model input shape
    image = np.array(image).astype('float32') / 255.0
    input_img = np.expand_dims(image, axis=(0, -1))  # Shape: (1, 256, 256, 1)

    # Load model and predict
    model = load_model_once()
    prediction = model.predict(input_img)
    pneumonia_prob = prediction[0][0]  # Single output neuron

    label = "Pneumonia" if float(pneumonia_prob) > 0.95 else "Normal"
    percentage = round(float(pneumonia_prob) * 100, 2)
    return label, percentage

def handler(request):
    """Vercel serverless function handler"""
    try:
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': ''
            }

        if request.method != 'POST':
            return {
                'statusCode': 405,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Method not allowed'})
            }

        # Get the request body
        body = request.get('body', '')
        if not body:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'No image data provided'})
            }

        # Parse the multipart form data (simplified approach)
        # For production, consider using a proper multipart parser
        try:
            # Assuming the image is sent as base64 in JSON payload
            data = json.loads(body)
            image_data = data.get('image')

            if not image_data:
                return {
                    'statusCode': 400,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'No image data in request'})
                }

            # Decode base64 image
            if image_data.startswith('data:image'):
                # Handle data URL format: "data:image/jpeg;base64,..."
                header, base64_data = image_data.split(',', 1)
                image_bytes = base64.b64decode(base64_data)
            else:
                # Assume it's raw base64
                image_bytes = base64.b64decode(image_data)

            # Get prediction
            label, percentage = getResult(image_bytes)

            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'prediction': label,
                    'percentage': percentage,
                    'confidence': percentage
                })
            }

        except Exception as e:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'Invalid image data: {str(e)}'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Server error: {str(e)}'})
        }