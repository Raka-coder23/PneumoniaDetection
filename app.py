import os
import numpy as np
from PIL import Image
import cv2
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model

# ✅ Load full model (architecture + weights)
model_path = 'model.keras'
if not os.path.exists(model_path):
    print("❌ Model file not found! Please ensure model.keras is in the project root.")
    print("For deployment, you may need to:")
    print("1. Upload model.keras to a cloud storage (Google Drive, Dropbox, etc.)")
    print("2. Or use Git LFS for large files")
    print("3. Or train a smaller model")
    exit(1)

model_03 = load_model(model_path)

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print('✅ Model loaded. Visit http://127.0.0.1:5000/')

# 🧪 Prediction logic using sigmoid output
def getResult(img_path):
    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image not found or unreadable.")

    image = Image.fromarray(image)
    image = image.resize((256, 256))  # Match model input shape
    image = np.array(image).astype('float32') / 255.0
    input_img = np.expand_dims(image, axis=(0, -1))  # Shape: (1, 256, 256, 1)

    prediction = model_03.predict(input_img)
    pneumonia_prob = prediction[0][0]  # Single output neuron

    label = "Pneumonia" if pneumonia_prob > 0.95 else "Normal"
    percentage = round(pneumonia_prob * 100, 2)
    return label, percentage

# 🌐 Routes
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return render_template('index.html', prediction_text="⚠️ No file uploaded.")

    f = request.files['image']
    if f.filename == '':
        return render_template('index.html', prediction_text="⚠️ No file selected.")

    filename = secure_filename(f.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    f.save(file_path)

    try:
        label, percentage = getResult(file_path)
        result_text = f"{label} ({percentage}%)"
        return render_template('index.html', prediction_text=result_text, image_name=filename, percentage=percentage)
    except Exception as e:
        return render_template('index.html', prediction_text=f"❌ Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))