import os
import json
import base64
import numpy as np
from PIL import Image
import cv2
from tensorflow.keras.models import load_model

# Global model variable to cache it across function invocations
model = None

def load_model_once():
    global model
    if model is None:
        try:
            # Try local file first (for development/testing)
            possible_paths = [
                'model.keras',
                './model.keras',
                '../model.keras',
                os.path.join(os.path.dirname(__file__), '..', 'model.keras')
            ]

            model_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    print(f"Loading model from local file: {model_path}")
                    model = load_model(model_path)
                    print("Model loaded successfully from local file")
                    return model

            # If no local file found, try loading from URL (for production)
            print("No local model found, attempting to load from cloud storage...")
            model = load_model_from_url()
            print("Model loaded successfully from cloud storage")

        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise
    return model

def load_model_from_url():
    """Load model from cloud storage URL"""
    import requests
    import io

    # Replace this URL with your actual model URL
    # You can host on: Google Drive, Dropbox, AWS S3, GitHub Releases, etc.
    model_url = os.environ.get('MODEL_URL', 'https://your-cloud-storage-url/model.keras')

    if model_url == 'https://your-cloud-storage-url/model.keras':
        raise ValueError("MODEL_URL environment variable not set. Please configure your model URL.")

    try:
        print(f"Downloading model from: {model_url}")
        response = requests.get(model_url, timeout=60)

        if response.status_code != 200:
            raise ValueError(f"Failed to download model: HTTP {response.status_code}")

        # Load model from bytes
        model_bytes = io.BytesIO(response.content)
        model = load_model(model_bytes)
        print("Model downloaded and loaded successfully")
        return model

    except Exception as e:
        print(f"Error downloading model: {str(e)}")
        raise

def getResult(image_bytes):
    """Process image bytes and return prediction"""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if image is None:
            raise ValueError("Image could not be decoded. Please ensure it's a valid image file.")

        # Process image
        image = Image.fromarray(image)
        image = image.resize((256, 256))  # Match model input shape
        image = np.array(image).astype('float32') / 255.0
        input_img = np.expand_dims(image, axis=(0, -1))  # Shape: (1, 256, 256, 1)

        # Load model and predict
        model = load_model_once()
        prediction = model.predict(input_img, verbose=0)
        pneumonia_prob = float(prediction[0][0])  # Single output neuron

        label = "Pneumonia" if pneumonia_prob > 0.95 else "Normal"
        percentage = round(pneumonia_prob * 100, 2)
        return label, percentage

    except Exception as e:
        print(f"Error in getResult: {str(e)}")
        raise

def handler(request):
    """Vercel serverless function handler"""
    try:
        print(f"Request method: {request.get('method', 'unknown')}")

        # Handle CORS preflight
        if request.get('method') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': ''
            }

        if request.get('method') != 'POST':
            return {
                'statusCode': 405,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Method not allowed. Use POST.'})
            }

        # Get the request body
        body = request.get('body', '')
        print(f"Request body length: {len(body) if body else 0}")

        if not body:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'No request body provided'})
            }

        # Parse JSON payload
        try:
            data = json.loads(body)
            image_data = data.get('image')

            if not image_data:
                return {
                    'statusCode': 400,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'No image data found in request. Expected JSON with "image" field.'})
                }

            print(f"Image data length: {len(image_data)}")

            # Decode base64 image
            try:
                if image_data.startswith('data:image'):
                    # Handle data URL format: "data:image/jpeg;base64,..."
                    header, base64_data = image_data.split(',', 1)
                    image_bytes = base64.b64decode(base64_data)
                else:
                    # Assume it's raw base64
                    image_bytes = base64.b64decode(image_data)

                print(f"Decoded image bytes: {len(image_bytes)}")

            except Exception as decode_error:
                return {
                    'statusCode': 400,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': f'Invalid base64 image data: {str(decode_error)}'})
                }

            # Get prediction
            print("Starting prediction...")
            label, percentage = getResult(image_bytes)
            print(f"Prediction result: {label}, {percentage}%")

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

        except json.JSONDecodeError as json_error:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'Invalid JSON in request body: {str(json_error)}'})
            }
        except Exception as processing_error:
            print(f"Processing error: {str(processing_error)}")
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'Error processing image: {str(processing_error)}'})
            }

    except Exception as server_error:
        print(f"Server error: {str(server_error)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Server error: {str(server_error)}'})
        }