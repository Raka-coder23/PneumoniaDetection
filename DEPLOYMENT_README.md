# Vercel Deployment Guide

## 🚀 Quick Deploy

1. **Install Vercel CLI** (optional, for local testing):
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel**:
   ```bash
   vercel
   ```
   Or push to GitHub and connect your repository to Vercel.

3. **Environment Variables** (if needed):
   - No environment variables required for this basic deployment
   - The model file is included in the deployment

## 🧪 Local Testing

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the test script
python test_api.py
```

## 📁 Project Structure

```
├── api/
│   ├── index.py      # Serves the main HTML page
│   └── predict.py    # Handles image prediction API
├── public/
│   └── uploads/      # Static files (sample images)
├── templates/
│   └── index.html    # Updated HTML with JavaScript API calls
├── model.keras       # Your trained TensorFlow model
├── vercel.json       # Vercel configuration
└── requirements.txt  # Python dependencies
```

## ⚠️ Important Notes

- **Model Size**: If your `model.keras` file is very large (>100MB), consider:
  - Using Git LFS for the model file
  - Storing the model on cloud storage (Google Drive, AWS S3)
  - Training a smaller model

- **Cold Starts**: Serverless functions have cold start delays. The first request after inactivity may be slower.

- **Memory Limits**: Vercel has memory limits. If you get memory errors, consider optimizing your model.

## 🔧 Troubleshooting

**FUNCTION_INVOCATION_FAILED errors:**
- Check Vercel function logs in the dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify the model file exists and is not corrupted

**Import Errors:**
- Make sure TensorFlow version is compatible with Vercel's Python runtime
- Check that all required packages are listed in requirements.txt

**Model Loading Errors:**
- Verify `model.keras` is in the project root
- Check file permissions
- Ensure the model was saved with a compatible TensorFlow version