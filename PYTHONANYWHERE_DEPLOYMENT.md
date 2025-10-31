# Deploy MarkMate to PythonAnywhere

## Step 1: Create PythonAnywhere Account

1. Go to https://www.pythonanywhere.com/
2. Click "Start running Python online in less than a minute!"
3. Sign up for a **FREE Beginner account**
4. Verify your email

## Step 2: Upload Your Code

### Option A: Using Git (Recommended)
1. Open a **Bash console** in PythonAnywhere (from Dashboard)
2. Run these commands:
```bash
git clone https://github.com/PraneethaBoya/MarkMate.git
cd MarkMate
```

### Option B: Manual Upload
1. Go to **Files** tab
2. Upload your `backend` folder
3. Upload `requirements.txt`

## Step 3: Set Up Virtual Environment

In the Bash console, run:
```bash
cd MarkMate
mkvirtualenv --python=/usr/bin/python3.10 markmate-env
pip install -r requirements.txt
```

## Step 4: Set Up Database

1. Go to **Databases** tab in PythonAnywhere
2. Initialize a **MySQL database** (or PostgreSQL if available)
3. Note your database details:
   - Host: `yourusername.mysql.pythonanywhere-services.com`
   - Database name: `yourusername$markmate`
   - Username: `yourusername`
   - Password: (you'll set this)

## Step 5: Configure Web App

1. Go to **Web** tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select **Python 3.10**
5. Click through the wizard

## Step 6: Configure WSGI File

1. In the **Web** tab, click on the **WSGI configuration file** link
2. Replace the entire contents with the code from `pythonanywhere_wsgi.py` (I'll create this)

## Step 7: Set Working Directory and Virtual Environment

1. In the **Web** tab, set:
   - **Source code**: `/home/yourusername/MarkMate/backend`
   - **Working directory**: `/home/yourusername/MarkMate/backend`
   - **Virtualenv**: `/home/yourusername/.virtualenvs/markmate-env`

## Step 8: Reload Web App

1. Click the **Reload** button (green button at the top)
2. Your app will be live at: `https://yourusername.pythonanywhere.com`

## Step 9: Initialize Database & Register Users

In a Bash console:
```bash
cd MarkMate/scripts
python register_remote_users.py  # (you'll need to update the API URL in this script first)
python train_via_api.py
```

## Step 10: Update Frontend

Update all frontend files to use your new PythonAnywhere URL:
```javascript
const API = "https://yourusername.pythonanywhere.com/api";
```

---

## Troubleshooting

### Error Logs
- Go to **Web** tab → **Error log** link
- Check for any Python errors

### Common Issues
1. **Import errors**: Make sure all requirements are installed in virtualenv
2. **Database connection errors**: Double-check database credentials
3. **CORS errors**: Ensure CORS middleware is properly configured

---

## Your URLs After Deployment

- **Backend API**: `https://yourusername.pythonanywhere.com/api`
- **API Docs**: `https://yourusername.pythonanywhere.com/docs`
- **Frontend**: `https://praneethaboya.github.io/MarkMate/` (update to use new backend URL)

---

## Notes

- Free tier has **100 seconds CPU time per day** - should be enough for light usage
- Database is **persistent** - won't be cleared like Render
- App is **always running** - no cold starts
- You can upgrade to paid tier ($5/month) for more CPU time and features
