#!/usr/bin/env python3
"""
Test script for the Vercel API functions
"""
import base64
import json
import sys
import os

# Add the api directory to the path so we can import the functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

def test_predict_api():
    """Test the predict API function with a sample image"""
    try:
        # Import the predict function
        from predict import handler, load_model_once

        print("Testing model loading...")
        model = load_model_once()
        print(f"Model loaded successfully: {model}")

        # Create a mock request with a small test image
        # For a real test, you'd want to use one of the actual X-ray images
        test_image_path = "public/uploads/NORMAL2-IM-0229-0001.jpeg"

        if os.path.exists(test_image_path):
            print(f"Testing with image: {test_image_path}")

            # Read and encode image
            with open(test_image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            # Create mock request object with get method
            class MockRequest:
                def __init__(self, method, body):
                    self.method = method
                    self._body = body

                def get(self, key, default=None):
                    if key == 'body':
                        return self._body
                    elif key == 'method':
                        return self.method
                    return default

            mock_request = MockRequest('POST', json.dumps({'image': f'data:image/jpeg;base64,{image_data}'}))

            print("Testing prediction API...")
            result = handler(mock_request)

            print(f"Response status: {result.get('statusCode')}")
            if result.get('statusCode') == 200:
                response_data = json.loads(result.get('body', '{}'))
                print(f"Prediction successful: {response_data}")
            else:
                print(f"Prediction failed: {result.get('body')}")

        else:
            print(f"Test image not found: {test_image_path}")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def test_index_api():
    """Test the index API function"""
    try:
        from index import handler

        class MockRequest:
            def __init__(self, method):
                self.method = method

            def get(self, key, default=None):
                if key == 'method':
                    return self.method
                return default

        mock_request = MockRequest('GET')
        result = handler(mock_request)

        if result.get('statusCode') == 200:
            print("Index API working - returns HTML content")
        else:
            print(f"Index API failed: {result}")

    except Exception as e:
        print(f"Index API test failed: {e}")

if __name__ == "__main__":
    print("Testing Vercel API functions...\n")

    print("1. Testing index API:")
    test_index_api()

    print("\n2. Testing predict API:")
    test_predict_api()

    print("\nAll tests completed!")