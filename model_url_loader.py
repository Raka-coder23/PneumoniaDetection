
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
