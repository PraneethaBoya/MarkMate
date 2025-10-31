# MarkMate - Quick Start Guide

## 🚀 Your App is LIVE!

- **Frontend**: https://praneethaboya.github.io/MarkMate/login.html
- **Backend API**: https://markmate-api-vbm1.onrender.com/api
- **API Docs**: https://markmate-api-vbm1.onrender.com/docs

---

## 👥 Login Credentials

### Administrator:
- **Username**: `K.Nagaraju`
- **Password**: `IIITDMK`

### Students (20 users):
| Username | Password |
|----------|----------|
| Praneetha | 123CS0053 |
| Manasa | 123CS0021 |
| Sujith | 123CS0025 |
| Aarav Das | 123CS0001 |
| Aarav Gupta | 123CS0002 |
| Aarav Reddy | 123CS0003 |
| Aarav Saxena | 123CS0004 |
| Aditi Menon | 123CS0005 |
| Aditya Jain | 123CS0006 |
| Aditya Kulkarni | 123CS0007 |
| Aditya Shetty | 123CS0008 |
| Advait Bose | 123CS0009 |
| Advait Prasad | 123CS0010 |
| Akash Kulkarni | 123CS0011 |
| Akash Pathak | 123CS0012 |
| Aman Pillai | 123CS0013 |
| Aman Reddy | 123CS0014 |
| Amrita Bose | 123CS0015 |
| Amrita Mahajan | 123CS0016 |
| Anika Das | 123CS0017 |

---

## 🔧 If Login Fails (Database was reset)

### ✅ ONE-CLICK FIX:

1. Go to: `C:\Users\boyas\OneDrive\Desktop\ML project\scripts`
2. **Double-click** `quick_setup.bat`
3. Wait **30 seconds**
4. Done! ✅

### OR Run Manually:
```bash
cd "c:\Users\boyas\OneDrive\Desktop\ML project\scripts"
python register_remote_users.py
python train_via_api.py
```

---

## 📱 Features

### Student Dashboard:
- ✅ View pass probability
- ✅ See predicted marks
- ✅ Plan study hours (interactive slider)
- ✅ View attendance and test scores
- ✅ Get personalized suggestions

### Admin Dashboard:
- ✅ View all students
- ✅ Upload CSV metrics
- ✅ See student analytics
- ✅ Set pass rules (35% of highest or 50% of average)
- ✅ Provide individual suggestions
- ✅ Track attendance threshold (75%)

---

## 🛠️ Technologies Used

- **Backend**: Python, FastAPI, SQLAlchemy, Scikit-learn
- **Frontend**: HTML, JavaScript, Tailwind CSS, Chart.js
- **Database**: SQLite (on Render)
- **ML**: Logistic Regression, Decision Trees, Random Forest
- **Deployment**: Render (Backend), GitHub Pages (Frontend)

---

## ⚠️ Known Limitations (Render Free Tier)

- **Database resets** after periods of inactivity
- **Backend sleeps** after 15 minutes of inactivity (wakes up on first request)
- **Just use the one-click fix** when login fails - takes 30 seconds!

---

## 📞 Support

If you encounter any issues:
1. Try the **one-click setup** first (`quick_setup.bat`)
2. Check if backend is running: https://markmate-api-vbm1.onrender.com/api
3. Clear browser cache and try again

---

## 🎓 Pass Requirements

Students must meet these criteria to pass:
- ✅ Minimum **75% Attendance**
- ✅ Minimum **50% Marks** (or as per pass rule selected)
- ✅ Complete **All Assignments**

---

**Enjoy using MarkMate! 🎉**
