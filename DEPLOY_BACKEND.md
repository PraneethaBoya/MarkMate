# 🚀 Deploy MarkMate Backend to Railway

## Quick Setup (10 minutes)

### Prerequisites
- GitHub account
- Railway account (sign up at railway.app with GitHub)

---

## Option 1: Railway (Recommended - Free $5/month credit)

### 1. Push to GitHub First
```powershell
cd "c:\Users\boyas\OneDrive\Desktop\ML project"
git init
git add .
git commit -m "Initial commit: MarkMate backend"
git remote add origin https://github.com/YOUR_USERNAME/markmate.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `markmate` repository
5. Railway will auto-detect Python and deploy

### 3. Add Database (Optional but recommended)
1. In your Railway project, click **"+ New"**
2. Select **"Database" → "PostgreSQL"**
3. Railway will auto-create and link it

### 4. Configure Environment Variables
In Railway dashboard → Variables tab, add:
```
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-filled if you added Postgres
PORT=${{PORT}}  # Auto-filled by Railway
```

### 5. Get Your Backend URL
After deployment (~2-3 minutes):
```
https://markmate-production.up.railway.app
```

---

## Option 2: Render (Alternative - Free tier)

### 1. Push to GitHub (same as above)

### 2. Deploy to Render
1. Go to [render.com](https://render.com)
2. Click **"New +" → "Web Service"**
3. Connect your GitHub repo
4. Configure:
   - **Name**: markmate-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### 3. Add Database
1. Create new **PostgreSQL** database
2. Copy connection string
3. Add as environment variable `DATABASE_URL`

### 4. Environment Variables
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=<from-render-postgres>
```

---

## 📡 Update Frontend to Use Deployed Backend

After backend is live, update your frontend API base:

### For GitHub Pages deployment:
Edit `frontend/index.html`, `frontend/login.html`, `frontend/student.html`, `frontend/admin.html`:

```javascript
// Change this line:
const API = "/api";

// To your Railway/Render URL:
const API = "https://markmate-production.up.railway.app/api";
```

### Quick script to update all files:
```powershell
# Update API base in all frontend files
$backendUrl = "https://markmate-production.up.railway.app"
$files = @(
    "frontend/index.html",
    "frontend/login.html", 
    "frontend/student.html",
    "frontend/admin.html",
    "frontend/predict.html",
    "frontend/charts.html"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        (Get-Content $file) -replace 'const API = "/api";', "const API = `"$backendUrl/api`";" | Set-Content $file
    }
}

Write-Host "✅ Updated API base in all frontend files"
```

---

## 🔒 Security Checklist

Before going live:
- [ ] Change `SECRET_KEY` in environment variables
- [ ] Enable HTTPS (auto-enabled on Railway/Render)
- [ ] Set proper CORS origins in `backend/main.py`:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://YOUR_USERNAME.github.io"],  # Your GitHub Pages URL
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- [ ] Use PostgreSQL instead of SQLite for production

---

## 🧪 Test Your Deployment

### 1. Test Backend API
```bash
curl https://markmate-production.up.railway.app/api/
```

Expected response:
```json
{
  "message": "Student Performance Prediction API",
  "endpoints": [...]
}
```

### 2. Test Frontend
Visit: `https://YOUR_USERNAME.github.io/markmate/`
- Click Login
- Register a test user
- Try predictions

---

## 📊 Monitor Your App

### Railway Dashboard
- View logs in real-time
- Monitor CPU/Memory usage
- Check deployment history

### Render Dashboard
- View logs
- Check metrics
- Manage environment variables

---

## 💰 Cost Breakdown

### Railway (Recommended)
- **Free**: $5/month credit (enough for small projects)
- **Hobby**: $5/month after credit expires
- Includes: 512MB RAM, shared CPU, 1GB storage

### Render
- **Free**: 750 hours/month
- Spins down after 15 min inactivity
- Includes: 512MB RAM, shared CPU

---

## 🆘 Troubleshooting

### "Module not found" error
- Check `requirements.txt` includes all dependencies
- Redeploy after updating requirements

### Database connection error
- Verify `DATABASE_URL` environment variable
- Check database is running

### CORS error in browser
- Update `allow_origins` in `backend/main.py`
- Redeploy backend

### 502 Bad Gateway
- Check logs for Python errors
- Verify start command is correct
- Ensure port binding uses `$PORT` variable

---

## 🎯 Final Architecture

```
┌─────────────────────────────────────┐
│  GitHub Pages (Frontend)            │
│  https://username.github.io/markmate│
└──────────────┬──────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────┐
│  Railway/Render (Backend API)       │
│  https://markmate.up.railway.app    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  PostgreSQL Database                │
│  (Managed by Railway/Render)        │
└─────────────────────────────────────┘
```

---

## ✅ Deployment Checklist

- [ ] Backend deployed to Railway/Render
- [ ] Database created and connected
- [ ] Environment variables configured
- [ ] Frontend updated with backend URL
- [ ] Frontend deployed to GitHub Pages
- [ ] CORS configured correctly
- [ ] Test login/register works
- [ ] Test predictions work
- [ ] Monitor logs for errors

---

**Backend URL**: https://markmate-production.up.railway.app
**Frontend URL**: https://YOUR_USERNAME.github.io/markmate/
**API Docs**: https://markmate-production.up.railway.app/docs
