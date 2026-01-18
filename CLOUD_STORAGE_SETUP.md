# Cloud Storage Setup for Large ML Models

## 🚨 Problem
Your `model.keras` file is 170MB, which exceeds Vercel's deployment limits (250MB total). The function crashes because the model can't be loaded.

## ✅ Solution: Cloud Storage

### Step 1: Choose Cloud Storage
**Recommended options:**

1. **Google Drive** (Free, easy)
2. **Dropbox** (Free tier available)
3. **GitHub Releases** (Free, versioned)
4. **AWS S3** (Scalable, paid)
5. **Azure Blob Storage** (Enterprise)

### Step 2: Upload Your Model

#### Option A: Google Drive
1. Upload `model.keras` to Google Drive
2. Make it publicly shareable:
   - Right-click file → "Get shareable link"
   - Change permissions to "Anyone with the link can view"
3. Copy the shareable link
4. Convert to direct download URL:
   ```
   Original: https://drive.google.com/file/d/FILE_ID/view?usp=sharing
   Direct:    https://drive.google.com/uc?export=download&id=FILE_ID
   ```

#### Option B: Dropbox
1. Upload `model.keras` to Dropbox
2. Get shareable link
3. Convert to direct download:
   ```
   Original: https://www.dropbox.com/s/.../model.keras?dl=0
   Direct:    https://www.dropbox.com/s/.../model.keras?dl=1
   ```

#### Option C: GitHub Releases
1. Create a new GitHub repository (or use existing)
2. Go to Releases → Create new release
3. Upload `model.keras` as a release asset
4. Copy the asset download URL

### Step 3: Configure Environment Variable

#### In Vercel Dashboard:
1. Go to your project dashboard
2. Navigate to Settings → Environment Variables
3. Add new variable:
   ```
   Name: MODEL_URL
   Value: YOUR_DIRECT_DOWNLOAD_URL
   Environment: Production, Preview, Development
   ```

#### Or using Vercel CLI:
```bash
vercel env add MODEL_URL
# Enter your direct download URL when prompted
```

### Step 4: Test Locally (Optional)

Before deploying, test with a small model or mock the URL loading:

```python
# In your local environment, you can still use the local file
# The cloud loading will only activate on Vercel
```

### Step 5: Deploy

```bash
vercel --prod
```

## 🔧 Troubleshooting

### "MODEL_URL environment variable not set"
- Check Vercel environment variables
- Ensure the variable is set for all environments (Production, Preview, Development)

### "Failed to download model: HTTP 403"
- Verify the URL is publicly accessible
- Check if the file permissions allow public access
- Try a different cloud storage service

### "Timeout error"
- Large files may take time to download
- Consider compressing the model or using a CDN
- Check your internet connection stability

### Slow cold starts
- Model downloads on every cold start
- Consider keeping a local cache in `/tmp` (but be aware of Vercel's limits)

## 📊 Performance Comparison

| Method | Deployment Size | Cold Start Time | Reliability |
|--------|----------------|-----------------|-------------|
| Local model | 170MB+ | Fast (< 2s) | High |
| Cloud storage | ~5MB | Medium (5-15s) | Medium |
| Model quantization | ~50MB | Fast (< 3s) | High |

## 🔄 Alternative: Model Optimization

If you prefer to keep the model local, try model quantization:

```python
import tensorflow as tf

# Load and quantize model
model = tf.keras.models.load_model('model.keras')
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save quantized model
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

Then update your code to use TensorFlow Lite instead of Keras.

## 🚀 Next Steps

1. Choose a cloud storage option
2. Upload your model and get the direct download URL
3. Set the `MODEL_URL` environment variable in Vercel
4. Deploy with `vercel --prod`
5. Test your pneumonia prediction app!

## 💡 Pro Tips

- **Monitor costs**: Cloud storage egress might have costs for large files
- **Version control**: Use different URLs for model versions
- **Caching**: Consider implementing local caching to reduce download frequency
- **CDN**: Use a CDN in front of your storage for faster downloads