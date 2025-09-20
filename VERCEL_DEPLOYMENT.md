# 🚀 Vercel Deployment Guide

This guide explains how to deploy the Salaaz CSV Converter Streamlit app to Vercel.

## 📋 Prerequisites

- GitHub account
- Vercel account (free tier available)
- Git repository with your project

## 🔧 Deployment Files Created

The following files have been configured for Vercel deployment:

### 1. `vercel.json`
Main Vercel configuration file that:
- Specifies Python 3.9 runtime
- Sets up Streamlit-specific environment variables
- Configures routing to `streamlit_app.py`
- Sets function timeout to 30 seconds

### 2. `streamlit_app.py` 
Vercel entry point that imports and runs the main [`app.py`](app.py) application.

### 3. `.vercelignore`
Excludes unnecessary files from deployment to optimize build size and speed.

### 4. `requirements.txt`
Already exists - contains all Python dependencies needed for the app.

## 🚀 Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Vercel deployment configuration"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Sign in with your GitHub account
   - Click "New Project"
   - Import your GitHub repository

3. **Configure Project**
   - Framework Preset: **Other**
   - Root Directory: **/**
   - Build Command: **(leave empty)**
   - Output Directory: **(leave empty)**
   - Install Command: `pip install -r requirements.txt`

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your app will be available at `https://your-project-name.vercel.app`

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

## 🔍 Verification

After deployment, verify your app works by:

1. **Accessing the URL** - Visit your deployed app URL
2. **Testing File Upload** - Try uploading a sample CSV/Excel file
3. **Column Mapping** - Verify the mapping interface works
4. **Data Download** - Test CSV and Excel download functionality

## 📁 File Structure

```
streamlit_converter/
├── vercel.json              # Vercel configuration
├── streamlit_app.py         # Vercel entry point
├── app.py                   # Main Streamlit application
├── requirements.txt         # Python dependencies
├── .vercelignore           # Files to exclude from deployment
├── categories.csv          # Category mapping data
├── sub_categories.csv      # Sub-category mapping data
├── sub_sub_categories.csv  # Sub-sub-category mapping data
└── VERCEL_DEPLOYMENT.md    # This deployment guide
```

## ⚙️ Environment Variables

The app is configured with these Streamlit environment variables in `vercel.json`:

- `STREAMLIT_SERVER_PORT=8501`
- `STREAMLIT_SERVER_ADDRESS=0.0.0.0`
- `STREAMLIT_SERVER_HEADLESS=true`
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`
- `STREAMLIT_SERVER_ENABLE_CORS=false`
- `STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false`

## 🔧 Troubleshooting

### Common Issues:

1. **Build Timeout**
   - Vercel functions have a 30-second timeout limit
   - Large file processing may need optimization

2. **Memory Limits**
   - Vercel has memory constraints for the free tier
   - Consider file size limitations

3. **File Uploads**
   - Vercel serverless functions handle file uploads differently
   - The current implementation should work with typical CSV/Excel files

### Solutions:

- Monitor deployment logs in Vercel dashboard
- Check function execution times
- Optimize large file processing if needed

## 📞 Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)

---

**Ready to deploy!** 🚀 Your Salaaz CSV Converter is now configured for Vercel deployment.