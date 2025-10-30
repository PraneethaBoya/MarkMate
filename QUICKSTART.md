# ⚡ MarkMate Deployment Quickstart

## 🎯 Goal
Deploy MarkMate with:
- **Frontend** on GitHub Pages (free, static hosting)
- **Backend** on Railway (free $5/month credit)

---

## 🚀 One-Command Deployment

```powershell
cd "c:\Users\boyas\OneDrive\Desktop\ML project"
.\deploy-full.ps1
```

This script will:
1. ✅ Initialize Git
2. ✅ Push to GitHub
3. ✅ Guide you through Railway setup
4. ✅ Update frontend API URLs
5. ✅ Enable GitHub Pages

**Time**: ~10 minutes

---

## 📋 Manual Deployment (Step-by-Step)

### Part 1: Deploy Backend (5 min)

1. **Push to GitHub**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/markmate.git
   git push -u origin main
   ```

2. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub"
   - Select your `markmate` repo
   - Wait 2-3 minutes
   - Copy your URL: `https://markmate-production.up.railway.app`

3. **Update Frontend**
   ```powershell
   .\update-api-url.ps1
   # Enter your Railway URL when prompted
   ```

### Part 2: Deploy Frontend (2 min)

1. **Enable GitHub Pages**
   - Go to `https://github.com/YOUR_USERNAME/markmate/settings/pages`
   - Source: **GitHub Actions**
   - Wait 2 minutes

2. **Visit Your Site**
   ```
   https://YOUR_USERNAME.github.io/markmate/
   ```

---

## 🔗 Your Live URLs

After deployment:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | `https://YOUR_USERNAME.github.io/markmate/` | Main website |
| **Backend API** | `https://markmate-production.up.railway.app/api` | REST API |
| **API Docs** | `https://markmate-production.up.railway.app/docs` | Interactive API docs |

---

## ✅ Test Your Deployment

1. **Visit frontend**: `https://YOUR_USERNAME.github.io/markmate/`
2. **Click "Login"**
3. **Register a test user**
4. **Try making a prediction**

If everything works → 🎉 **Success!**

---

## 🆘 Common Issues

### Frontend loads but login fails
- Check browser console for CORS errors
- Verify API URL is correct in frontend files
- Check Railway logs for backend errors

### Backend deployment failed
- Check Railway logs
- Verify `requirements.txt` is complete
- Ensure Python version is compatible

### GitHub Pages shows 404
- Wait 2-3 minutes after enabling Pages
- Check Actions tab for deployment status
- Verify workflow file exists: `.github/workflows/deploy.yml`

---

## 📚 Full Documentation

- **DEPLOY.md** - Frontend deployment details
- **DEPLOY_BACKEND.md** - Backend deployment details
- **README.md** - Project overview

---

## 💡 Pro Tips

1. **Monitor Railway logs** to debug backend issues
2. **Use Railway's free $5/month credit** wisely (enough for small projects)
3. **Add PostgreSQL database** in Railway for production (optional)
4. **Set up custom domain** in GitHub Pages settings (optional)
5. **Enable Railway metrics** to track API usage

---

## 🎓 What You've Built

```
┌─────────────────────────────────────┐
│  GitHub Pages                       │
│  ├─ Home (index.html)              │
│  ├─ About (about.html)             │
│  ├─ Login (login.html)             │
│  ├─ Student Dashboard              │
│  └─ Admin Dashboard                │
└──────────────┬──────────────────────┘
               │ HTTPS API Calls
               ▼
┌─────────────────────────────────────┐
│  Railway (FastAPI Backend)          │
│  ├─ Authentication (JWT)           │
│  ├─ ML Predictions                 │
│  ├─ Student Metrics                │
│  └─ Admin Analytics                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  SQLite/PostgreSQL Database         │
│  ├─ Users                          │
│  ├─ Predictions                    │
│  ├─ Student Metrics                │
│  └─ Messages                       │
└─────────────────────────────────────┘
```

---

**Ready to deploy?** Run `.\deploy-full.ps1` and follow the prompts!
