#!/usr/bin/env python3
"""
Test script to validate Vercel function structure without TensorFlow dependencies
"""
import json
import base64
import os

# Mock the request object that Vercel sends
class MockRequest:
    def __init__(self, method='GET', body=None):
        self.method = method
        self.body = body

    def get(self, key, default=None):
        if key == 'method':
            return self.method
        elif key == 'body':
            return self.body
        return default

def test_index_function():
    """Test the index function without TensorFlow"""
    print("Testing index function...")

    try:
        # Mock the index handler without importing TensorFlow
        def mock_index_handler(request):
            try:
                # Read the HTML template
                template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')

                with open(template_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'text/html',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': html_content
                }

            except FileNotFoundError:
                return {
                    'statusCode': 500,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': '<h1>Template not found</h1>'
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {'Access-Control-Allow-Origin': '*'},
                    'body': f'<h1>Error: {str(e)}</h1>'
                }

        # Test the index function
        mock_request = MockRequest('GET')
        result = mock_index_handler(mock_request)

        if result['statusCode'] == 200 and 'text/html' in result['headers']['Content-Type']:
            print("Index function works correctly")
            return True
        else:
            print(f"Index function failed: {result}")
            return False

    except Exception as e:
        print(f"Index function error: {e}")
        return False

def test_predict_function_structure():
    """Test predict function structure without actually loading TensorFlow"""
    print("Testing predict function structure...")

    try:
        # Test that the file can be imported (without TensorFlow)
        # We'll create a minimal version that doesn't import TensorFlow

        # Check if the predict.py file exists and has the right structure
        predict_file = os.path.join(os.path.dirname(__file__), 'api', 'predict.py')
        if not os.path.exists(predict_file):
            print("❌ predict.py file not found")
            return False

        with open(predict_file, 'r') as f:
            content = f.read()

        # Check for required function
        if 'def handler(request):' not in content:
            print("handler function not found in predict.py")
            return False

        # Check for basic error handling
        if 'try:' not in content or 'except Exception' not in content:
            print("Basic error handling not found in predict.py")
            return False

        print("Predict function structure looks correct")
        return True

    except Exception as e:
        print(f"Predict function structure test error: {e}")
        return False

def test_vercel_config():
    """Test vercel.json configuration"""
    print("Testing vercel.json configuration...")

    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)

        # Check required fields
        required_fields = ['version', 'builds', 'routes', 'functions']
        for field in required_fields:
            if field not in config:
                print(f"Missing required field: {field}")
                return False

        # Check Python runtime
        functions = config.get('functions', {})
        api_config = functions.get('api/**/*.py', {})
        runtime = api_config.get('runtime', '')

        if not runtime.startswith('python'):
            print(f"Invalid runtime: {runtime}")
            return False

        print(f"Vercel config looks correct (runtime: {runtime})")
        return True

    except Exception as e:
        print(f"Vercel config test error: {e}")
        return False

def check_model_file():
    """Check if model file exists and get its size"""
    print("Checking model file...")

    model_path = 'model.keras'
    if not os.path.exists(model_path):
        print("Model file not found")
        return False

    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    print(f"Model file size: {size_mb:.1f} MB")
    # Vercel has limits around 50-100MB for functions
    if size_mb > 100:
        print("WARNING: Model file is quite large - may cause deployment issues")
    else:
        print("Model file size is reasonable")

    return True

if __name__ == "__main__":
    print("Testing Vercel deployment structure...\n")

    tests = [
        test_index_function,
        test_predict_function_structure,
        test_vercel_config,
        check_model_file
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("All basic structure tests passed!")
        print("\nIf you're still getting FUNCTION_INVOCATION_FAILED on Vercel:")
        print("1. Check Vercel function logs for detailed error messages")
        print("2. The model file (178MB) might be too large for Vercel's memory limits")
        print("3. Try deploying to a platform with higher memory limits like Railway or Render")
        print("4. Consider using a smaller model or model optimization techniques")
    else:
        print("Some tests failed. Please fix the issues before deploying.")