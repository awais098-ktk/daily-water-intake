# 🔵 Google Fit OAuth Setup Instructions

## ✅ **Your Credentials Are Integrated!**

Your Google Fit OAuth credentials have been successfully integrated into the Water Intake Tracker app:

- **Client ID**: `YOUR_GOOGLE_CLIENT_ID_HERE`
- **Client Secret**: `YOUR_GOOGLE_CLIENT_SECRET_HERE`

---

## 🔧 **IMPORTANT: Update Redirect URI**

Your current redirect URI in Google Cloud Console is:
```
http://127.0.0.1:8080
```

But it needs to be:
```
http://127.0.0.1:5001/wearable/oauth/google_fit/callback
```

### **Steps to Update:**

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Select your project: `cedar-gift-460910-b4`

2. **Navigate to Credentials**
   - Go to: **APIs & Services** → **Credentials**
   - Find your OAuth 2.0 Client ID: `YOUR_GOOGLE_CLIENT_ID_HERE`
   - Click on it to edit

3. **Update Authorized Redirect URIs**
   - In the **Authorized redirect URIs** section
   - Add this new URI: `http://127.0.0.1:5001/wearable/oauth/google_fit/callback`
   - You can keep the old one too: `http://127.0.0.1:8080`
   - Click **Save**

---

## 🚀 **Testing the OAuth Flow**

Once you've updated the redirect URI:

### **Step 1: Start the App**
```bash
python run.py
```

### **Step 2: Go to Connect Page**
- Open: http://127.0.0.1:8080/wearable/connect
- You should see Google Fit shows **"Available"** (green badge)

### **Step 3: Connect Google Fit**
1. Click **"Connect Google Fit"** button
2. You'll be redirected to Google's authorization page
3. Sign in with your Google account
4. Grant permissions for:
   - Read your fitness activity data
   - Read your body measurements
   - Read your location data
5. You'll be redirected back to the app
6. You should see a success message

### **Step 4: View Connected Device**
- Go to: http://127.0.0.1:5001/wearable/
- You should see your Google Fit connection
- Try syncing data to get your real activity information

---

## 🔍 **Troubleshooting**

### **If you get "redirect_uri_mismatch" error:**
- Double-check the redirect URI in Google Cloud Console
- Make sure it's exactly: `http://127.0.0.1:5001/wearable/oauth/google_fit/callback`
- No trailing slashes, exact case

### **If you get "invalid_client" error:**
- Verify the Client ID and Secret are correct
- Check that the Fitness API is enabled in your project

### **If you get "access_denied" error:**
- This means you denied permission during OAuth
- Try the flow again and grant all requested permissions

---

## 📊 **What Happens After Connection**

Once connected, the app will:

1. **Sync Your Activity Data**
   - Steps, distance, calories burned
   - Heart rate data (if available)
   - Exercise sessions

2. **Calculate Personalized Hydration**
   - Base recommendation based on your profile
   - Activity bonus based on your actual exercise
   - Smart recommendations for different activity levels

3. **Provide Real-Time Insights**
   - Daily activity summaries
   - Hydration recommendations
   - Progress tracking

---

## 🎯 **Current Status**

✅ **Google Fit credentials integrated**  
✅ **OAuth flow implemented**  
✅ **App ready for testing**  
⚠️  **Redirect URI needs update** (one-time setup)  
🚀 **Ready to connect real Google Fit data!**

---

## 📱 **Next Steps**

1. **Update redirect URI** in Google Cloud Console
2. **Test OAuth flow** with your Google account
3. **Sync real activity data** from Google Fit
4. **Get personalized hydration recommendations**
5. **Enjoy smart hydration tracking!**

Your Google Fit integration is now ready! 🎉
