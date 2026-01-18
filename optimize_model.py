#!/usr/bin/env python3
"""
Model optimization script for Vercel deployment
Reduces model size and improves loading performance
"""
import os
import tensorflow as tf
from tensorflow.keras.models import load_model, save_model
import numpy as np
import tempfile

def optimize_model_for_vercel():
    """Optimize the model for serverless deployment"""
    print("Loading original model...")
    model_path = 'model.keras'

    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        return False

    # Load the model
    model = load_model(model_path)
    print(f"Original model size: {os.path.getsize(model_path) / (1024*1024):.1f} MB")

    # Create a temporary optimized version
    with tempfile.NamedTemporaryFile(suffix='.keras', delete=False) as tmp_file:
        optimized_path = tmp_file.name

    try:
        # Save with optimization options
        print("Optimizing model...")
        save_model(model, optimized_path,
                  include_optimizer=False,  # Remove optimizer state
                  save_format='keras_v3')

        optimized_size = os.path.getsize(optimized_path) / (1024*1024)
        original_size = os.path.getsize(model_path) / (1024*1024)

        print(f"Optimized model size: {optimized_size:.1f} MB")
        print(f"Size reduction: {((original_size - optimized_size) / original_size * 100):.1f}%")

        if optimized_size < 50:  # If under 50MB, use optimized version
            print("Using optimized model...")
            os.replace(optimized_path, 'model_optimized.keras')
            print("Saved as: model_optimized.keras")
            print("Update your API code to use 'model_optimized.keras'")
        else:
            print("Model still too large. Consider:")
            print("1. Using model quantization")
            print("2. Storing model on cloud storage (S3, Google Drive)")
            print("3. Using a smaller model architecture")
            os.unlink(optimized_path)

        return True

    except Exception as e:
        print(f"Optimization failed: {e}")
        if os.path.exists(optimized_path):
            os.unlink(optimized_path)
        return False

def create_model_url_loader():
    """Create a version that loads model from URL"""
    print("\nAlternative: Model URL Loading")
    print("For large models, consider hosting on cloud storage:")
    print("1. Upload model.keras to Google Drive, Dropbox, or AWS S3")
    print("2. Make it publicly accessible")
    print("3. Update the load_model_once() function to download from URL")

    url_loader_code = '''
def load_model_from_url():
    import requests
    import io

    model_url = "YOUR_MODEL_URL_HERE"  # Replace with actual URL

    if not os.path.exists('model.keras'):
        print("Downloading model from cloud storage...")
        response = requests.get(model_url)
        with open('model.keras', 'wb') as f:
            f.write(response.content)
        print("Model downloaded successfully")

    return load_model('model.keras')
'''

    with open('model_url_loader.py', 'w') as f:
        f.write(url_loader_code)

    print("Created model_url_loader.py template")
    print("Edit it with your model URL and integrate into your API")

if __name__ == "__main__":
    print("Model Optimization for Vercel Deployment")
    print("=" * 50)

    success = optimize_model_for_vercel()

    if not success:
        print("\nOptimization failed. Trying alternative approaches...")

    create_model_url_loader()

    print("\nNext steps:")
    print("1. If optimized model < 50MB: use model_optimized.keras")
    print("2. If still too large: use cloud storage approach")
    print("3. Test deployment with: vercel --prod")
    print("4. Monitor function logs in Vercel dashboard")