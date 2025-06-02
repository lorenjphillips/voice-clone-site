# 🚀 Voice Clone Site - Deployment Guide

## ✅ Pre-Deployment Checklist

Your voice cloning site is ready to deploy! Here's what you have:

- ✅ **FastAPI Backend** (`api_server.py`) - Handles TTS generation
- ✅ **Modern Frontend** (`index.html`) - Beautiful web interface
- ✅ **Production Config** (`render.yaml`, `Procfile`) - Ready for deployment
- ✅ **API Testing** (`test_api.py`) - Verify everything works

## 🖥️ Local Development

```bash
# Start the API backend
python api_server.py

# Open the frontend (in another terminal)
open index.html

# Test the API
python test_api.py
```

Your site will be available at:
- **API**: http://localhost:8000
- **Frontend**: Opens in browser automatically
- **API Docs**: http://localhost:8000/docs

## 🌐 Production Deployment

### Step 1: Deploy Backend to Render

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Create Render Web Service**:
   - Go to [render.com](https://render.com/dashboard)
   - Click "New" → "Web Service"
   - Connect your GitHub repo
   - Use these settings:
     ```
     Name: voice-clone-api
     Build Command: pip install -r requirements.txt
     Start Command: python api_server.py
     Plan: Starter ($7/month)
     ```

3. **Add Environment Variables**:
   ```
   PYTORCH_ENABLE_MPS_FALLBACK = 1
   ```

4. **Deploy**: Click "Create Web Service"

Your API will be available at: `https://voice-clone-api.onrender.com`

### Step 2: Deploy Frontend to Vercel

1. **Update API URL in `index.html`**:
   ```javascript
   // Change this line (around line 133):
   const API_BASE_URL = 'https://voice-clone-api.onrender.com';
   ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repo
   - Vercel auto-detects it's a static site
   - Click "Deploy"

Your site will be available at: `https://your-project.vercel.app`

### Step 3: Update CORS (Backend)

Update `api_server.py` with your frontend URL:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-project.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy the backend after this change.

## 🔧 Production Configuration

### Backend (Render)
- **Plan**: Start with Starter ($7/month)
- **Auto-scaling**: Enabled by default
- **Health checks**: Built-in monitoring
- **Logs**: Available in Render dashboard

### Frontend (Vercel)
- **Plan**: Hobby (Free) for personal projects
- **CDN**: Global edge network included
- **HTTPS**: Automatic SSL certificates
- **Custom Domain**: Add your own domain (optional)

## 📊 Monitoring & Testing

### Health Checks
```bash
# Test your deployed API
curl https://voice-clone-api.onrender.com/health

# Test TTS generation
curl -X POST "https://voice-clone-api.onrender.com/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from production!"}'
```

### Performance Monitoring
- **Render**: Built-in metrics and logs
- **Vercel**: Analytics dashboard
- **Uptime**: Both services have 99.9% uptime SLA

## 🐛 Common Issues & Solutions

### 1. Backend Deploy Fails
```bash
# Check logs in Render dashboard
# Common issue: Missing dependencies

# Fix: Update requirements.txt
pip freeze > requirements.txt
```

### 2. Frontend Can't Connect to API
```bash
# Check CORS settings in api_server.py
# Ensure API URL is correct in index.html
# Verify API is running: curl https://your-api.onrender.com/health
```

### 3. Slow TTS Generation
```bash
# Upgrade Render plan:
# Starter: ~20 seconds
# Standard: ~15 seconds  
# Pro: ~10 seconds (GPU)
```

### 4. API Timeout Errors
```bash
# Increase timeout in frontend (index.html)
# Add loading indicators
# Consider async processing for long texts
```

## 💰 Cost Breakdown

### Monthly Costs:
- **Render Starter**: $7/month (API backend)
- **Vercel Hobby**: $0/month (Frontend)
- **Total**: $7/month

### Scaling Costs:
- **Render Standard**: $25/month (faster generation)
- **Render Pro**: $85/month (GPU acceleration)
- **Vercel Pro**: $20/month (production features)

## 🚀 Going Live Checklist

- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel  
- [ ] API URL updated in frontend
- [ ] CORS configured correctly
- [ ] Health checks passing
- [ ] Test TTS generation works
- [ ] Custom domain added (optional)
- [ ] Analytics setup (optional)

## 🎉 You're Live!

Your voice cloning site is now available worldwide:

- **Frontend**: `https://your-project.vercel.app`
- **API**: `https://voice-clone-api.onrender.com`
- **API Docs**: `https://voice-clone-api.onrender.com/docs`

Share your site and start generating amazing voices! 🎙️

## 📞 Support

- **Render Issues**: Check Render docs or support
- **Vercel Issues**: Check Vercel docs or support  
- **Code Issues**: Review logs and test locally first

---

*Deployment typically takes 5-10 minutes total. Your voice cloning site will be ready for users immediately after deployment!* 