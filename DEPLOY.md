# 🚀 Deploy MarkMate to GitHub Pages

## Quick Setup (5 minutes)

### 1. Create GitHub Repository
```bash
# Initialize git (if not already done)
cd "c:\Users\boyas\OneDrive\Desktop\ML project"
git init
git add .
git commit -m "Initial commit: MarkMate student performance platform"
```

### 2. Push to GitHub
```bash
# Create a new repo on github.com (e.g., markmate)
# Then run:
git remote add origin https://github.com/YOUR_USERNAME/markmate.git
git branch -M main
git push -u origin main
```

### 3. Enable GitHub Pages
1. Go to your repo on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select:
   - **Source**: GitHub Actions
4. The workflow will auto-deploy on every push to `main`

### 4. Access Your Site
After ~2 minutes, your site will be live at:
```
https://YOUR_USERNAME.github.io/markmate/
```

## 📁 What Gets Deployed
- Only the `frontend/` folder is deployed (static HTML/CSS/JS)
- Backend API is NOT included (GitHub Pages only hosts static sites)

## 🔧 For Full-Stack Deployment
If you need the backend API working:
1. **Frontend**: GitHub Pages (free)
2. **Backend**: Deploy to Railway/Render (free tier)
3. Update `frontend/index.html` API base to point to your backend URL

Example:
```javascript
const API = "https://markmate-api.railway.app/api";
```

## 🎯 Custom Domain (Optional)
1. Buy a domain (e.g., markmate.com)
2. Add CNAME record pointing to `YOUR_USERNAME.github.io`
3. In GitHub repo settings, add custom domain

## 📝 Notes
- The `.github/workflows/deploy.yml` file handles automatic deployment
- Every push to `main` triggers a new deployment
- Build time: ~1-2 minutes

## 🆘 Troubleshooting
- **404 Error**: Check that Pages source is set to "GitHub Actions"
- **Workflow Failed**: Check Actions tab for error logs
- **CSS Not Loading**: Ensure all paths in HTML are relative (no leading `/`)

---

**Live Demo**: https://YOUR_USERNAME.github.io/markmate/
**Repository**: https://github.com/YOUR_USERNAME/markmate
