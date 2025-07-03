# 🚰 Water Intake Tracker - Quick Reference Guide

## 🎯 Most Important Files

### **🏠 Main Application**
- **`water_tracker/app.py`** - Main Flask application (START HERE)
- **`water_tracker/templates/dashboard.html`** - Main user interface
- **`instance/water_tracker.db`** - Your database file

### **🔧 Core Functionality**
- **`water_tracker/chart.py`** - Analytics and charts
- **`water_tracker/image_processing.py`** - Container recognition
- **`water_tracker/ocr.py`** - Label scanning
- **`water_tracker/voice_recognition.py`** - Voice commands

### **🔗 Google Fit Integration**
- **`water_tracker/wearable_integration/routes.py`** - Main wearable routes
- **`water_tracker/wearable_integration/fitness_apis.py`** - Google Fit API
- **`water_tracker/wearable_integration/oauth_manager.py`** - Authentication

### **🤖 AI Features**
- **`water_tracker/sarcastic_chatbot/chatbot.py`** - AI assistant
- **`water_tracker/smart_hydration/hydration_calculator.py`** - Smart recommendations

---

## 🚀 How to Run

### **Start the Application**
```bash
# Method 1: Direct
python water_tracker/app.py

# Method 2: Using runner
python run_app.py

# Method 3: Batch file (Windows)
start_app.bat
```

### **Access the Application**
- **URL:** http://localhost:5201
- **Login:** Use existing account or register new one

---

## 🗄️ Database Access

### **View Database in Browser**
```bash
# Export for SQLite browser
python export_database.py

# View in terminal
python view_db_data.py
python view_wearable_data.py
```

### **Database Location**
- **Main DB:** `instance/water_tracker.db`
- **Exported:** `database_export/water_tracker_db_*.db`

---

## 🔧 Configuration

### **Environment Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### **Google Fit Setup**
1. Follow `GOOGLE_FIT_SETUP_INSTRUCTIONS.md`
2. Configure OAuth credentials
3. Test connection in `/wearable/` page

---

## 📊 Key Features

### **Water Logging Methods**
1. **Manual Entry** - Type amount directly
2. **Container Selection** - Choose pre-defined container
3. **OCR Scanning** - Photo of drink label
4. **Voice Input** - "I drank 500ml of water"
5. **Image Recognition** - Photo of container

### **Analytics**
- Daily/weekly/monthly charts
- Goal tracking and progress
- Hydration patterns analysis
- Google Fit activity correlation

### **Smart Features**
- Weather-based recommendations
- Activity-based hydration goals
- AI chatbot motivation
- Automated reminders

---

## 🐛 Troubleshooting

### **Common Issues**
1. **Database errors** - Check `instance/water_tracker.db` exists
2. **Google Fit sync fails** - Verify OAuth setup
3. **OCR not working** - Check image quality
4. **Voice recognition issues** - Check microphone permissions

### **Debug Tools**
```bash
# Check database
python check_db.py

# Test Google Fit
python test_google_fit_oauth.py

# View logs
# Check console output when running app
```

---

## 📁 File Organization

### **Templates (UI)**
```
water_tracker/templates/
├── dashboard.html          # Main dashboard
├── containers.html         # Container management
├── wearable/              # Google Fit pages
├── chatbot/               # AI assistant
└── base.html              # Common layout
```

### **Static Assets**
```
water_tracker/static/
├── css/                   # Stylesheets
├── js/                    # JavaScript
├── images/                # UI images
└── uploads/               # User uploads
```

### **User Data**
```
├── instance/              # Database files
├── images/                # User uploaded images
└── static/uploads/        # Container images
```

---

## 🔑 Important URLs

### **Main Pages**
- `/` - Dashboard
- `/containers` - Manage containers
- `/wearable/` - Google Fit integration
- `/chatbot/` - AI assistant
- `/export` - Data export

### **API Endpoints**
- `/log_water` - Log water intake
- `/wearable/sync` - Sync Google Fit
- `/chatbot/chat` - Chat with AI
- `/recognize_container` - Image recognition

---

## 📈 Current Status

### **Working Features** ✅
- User authentication and profiles
- Multiple water logging methods
- Google Fit integration and sync
- Container management with images
- OCR label scanning
- Voice recognition
- AI chatbot assistant
- Data export (CSV/Excel)
- Analytics and charts
- Weather-based recommendations

### **Database Stats**
- **6 users** registered
- **186 water logs** recorded
- **6 Google Fit connections**
- **19 activity data records**
- **11 custom containers**

---

## 🎯 Quick Start Checklist

1. ✅ **Install dependencies:** `pip install -r requirements.txt`
2. ✅ **Run application:** `python water_tracker/app.py`
3. ✅ **Open browser:** http://localhost:5201
4. ✅ **Register/Login:** Create account or use existing
5. ✅ **Connect Google Fit:** Go to `/wearable/` page
6. ✅ **Log water:** Try different input methods
7. ✅ **View analytics:** Check dashboard charts
8. ✅ **Export data:** Use `/export` page

Your Water Intake Tracker is ready to use! 🚰💧
