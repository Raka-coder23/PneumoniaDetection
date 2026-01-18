# Model Size Optimization for Vercel Deployment

## 🚨 The Problem
Your `model.keras` file is **170MB**, which exceeds Vercel's typical memory limits for serverless functions. This is causing the `FUNCTION_INVOCATION_FAILED` error.

## 🔧 Immediate Solutions

### Option 1: Use Railway or Render (Recommended)
These platforms offer more generous memory limits:

#### Railway Deployment:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway deploy
```

#### Render Deployment:
1. Connect your GitHub repo to Render
2. Choose "Web Service" with Python
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`

### Option 2: Model Optimization (Advanced)
Reduce model size while maintaining accuracy:

#### 1. Model Quantization
```python
import tensorflow as tf

# Load your model
model = tf.keras.models.load_model('model.keras')

# Convert to TFLite with quantization
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]  # or tf.int8

tflite_model = converter.convert()

# Save quantized model
with open('model_quantized.tflite', 'wb') as f:
    f.write(tflite_model)
```

#### 2. Use TFLite Model Instead
Update your `predict.py` to use TFLite:

```python
import tensorflow as tf

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path="model_quantized.tflite")
interpreter.allocate_tensors()

# Get input/output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def predict_tflite(image):
    interpreter.set_tensor(input_details[0]['index'], image)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])
    return output
```

### Option 3: Model Pruning (Advanced)
Remove unnecessary weights:

```python
import tensorflow_model_optimization as tfmot

# Apply pruning
pruning_schedule = tfmot.sparsity.keras.PolynomialDecay(
    initial_sparsity=0.0,
    final_sparsity=0.5,
    begin_step=0,
    end_step=1000
)

model_for_pruning = tfmot.sparsity.keras.prune_low_magnitude(model, pruning_schedule)
```

### Option 4: Cloud Storage Model Loading
Store model on cloud storage and load on-demand:

```python
import requests

def load_model_from_cloud():
    if not os.path.exists('model.keras'):
        print("Downloading model from cloud...")
        # Download from Google Drive, S3, etc.
        response = requests.get('YOUR_MODEL_URL')
        with open('model.keras', 'wb') as f:
            f.write(response.content)
    return tf.keras.models.load_model('model.keras')
```

## 📊 Expected Results

| Method | Model Size | Memory Usage | Accuracy Impact |
|--------|------------|--------------|-----------------|
| Original | 170MB | High | None |
| TFLite (float16) | ~40MB | Medium | Minimal (~1-2%) |
| TFLite (int8) | ~20MB | Low | Moderate (2-5%) |
| Pruning + TFLite | ~15MB | Low | Moderate (3-8%) |

## 🚀 Quick Vercel Fix (Temporary)

If you must use Vercel, try this minimal version:

1. **Create a lighter model** by reducing layers/neurons
2. **Use model quantization** to reduce size by 50-70%
3. **Implement lazy loading** from cloud storage

## 🔍 Debugging Steps

1. **Check Vercel Logs**: Go to your deployment → Functions → View Logs
2. **Test Locally**: Run `python test_api.py` to isolate issues
3. **Monitor Memory**: Add memory logging to your functions

## 📈 Performance Comparison

| Platform | Memory Limit | Cold Start | Cost | Best For |
|----------|--------------|------------|------|----------|
| Vercel | ~100MB | 1-5s | Free tier | Prototypes |
| Railway | 512MB-8GB | 2-10s | $5/month | Small apps |
| Render | 512MB-4GB | 1-8s | $7/month | Full-stack |
| AWS Lambda | 128MB-10GB | 1-30s | Pay-per-use | Production |

**Recommendation**: Start with Railway for your ML app - it offers better ML support and more memory.