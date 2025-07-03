# 🔧 Google Fit Integration Troubleshooting Guide

## 🚨 Common Issues & Solutions

### **Issue 1: "Failed to connect to API" (401 Unauthorized)**

**Symptoms:**
- Sync button shows "google_fit: Failed to connect to API"
- Error message: "Request had invalid authentication credentials"
- Token expired message in logs

**Solution:**
1. **Use the Reconnect Button** (Easiest):
   - Go to `/wearable/` page
   - Click the **"Reconnect"** button next to Google Fit
   - Complete the Google authentication flow
   - Try syncing again

2. **Manual Reconnection**:
   - Click "Disconnect" on Google Fit connection
   - Click "Connect Device" → "Google Fit"
   - Complete OAuth flow
   - Try syncing

---

### **Issue 2: Connection Timeout**

**Symptoms:**
- "Read timed out" errors
- SSL handshake timeout
- Network connection issues

**Solution:**
1. **Check Internet Connection**
2. **Try Again Later** - Google APIs may be temporarily unavailable
3. **Use Mock Data** - The mock connection still works for testing

---

### **Issue 3: OAuth Configuration Missing**

**Symptoms:**
- "OAuth not configured" error
- Missing client credentials

**Solution:**
1. **Set Environment Variables**:
   ```bash
   set GOOGLE_FIT_CLIENT_ID=your_client_id
   set GOOGLE_FIT_CLIENT_SECRET=your_client_secret
   ```

2. **Follow Setup Guide**:
   - See `GOOGLE_FIT_SETUP_INSTRUCTIONS.md`
   - Create Google Cloud project
   - Enable Fitness API
   - Create OAuth credentials

---

## 🔄 Quick Fix Steps

### **For Expired Tokens (Most Common)**

1. **Go to Wearable Page**: http://localhost:5201/wearable/
2. **Click "Reconnect"** next to Google Fit
3. **Complete Google Login** when redirected
4. **Try Sync Again**

### **If Reconnect Doesn't Work**

1. **Disconnect Google Fit**:
   - Click "Disconnect" button
   - Confirm disconnection

2. **Connect Fresh**:
   - Click "Connect Device"
   - Select "Google Fit"
   - Complete OAuth flow

3. **Test Sync**:
   - Click "Sync" button
   - Check for success message

---

## 📊 Current Status Check

### **Working Features** ✅
- **Mock Integration**: Always works for testing
- **Database Storage**: Activity data is saved
- **Charts & Analytics**: Display properly
- **Hydration Recommendations**: Based on activity

### **Google Fit Status** ⚠️
- **Authentication**: Requires fresh token
- **API Access**: Depends on valid credentials
- **Data Sync**: Works after reconnection

---

## 🛠️ Debug Information

### **Check Connection Status**
```python
# Run this to see connection details
python view_wearable_data.py
```

### **Check Token Expiration**
- Look for `token_expires_at` in database
- Compare with current date/time
- Expired tokens need refresh

### **Test API Manually**
```bash
# Test Google Fit API directly
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://www.googleapis.com/fitness/v1/users/me/dataSources
```

---

## 🎯 Recommended Workflow

### **For Development/Testing**
1. **Use Mock Data** - Always reliable
2. **Test Features** - Charts, recommendations, etc.
3. **Connect Google Fit** - When needed for real data

### **For Production Use**
1. **Set Up OAuth Properly** - Follow setup guide
2. **Monitor Token Expiration** - Refresh as needed
3. **Handle Errors Gracefully** - Fallback to mock data

---

## 📞 Support

### **If Issues Persist**
1. **Check Logs** - Look for detailed error messages
2. **Verify Setup** - Follow `GOOGLE_FIT_SETUP_INSTRUCTIONS.md`
3. **Use Mock Data** - For continued functionality
4. **Report Issues** - With specific error messages

### **Working Alternatives**
- **Mock Integration**: Provides realistic test data
- **Manual Logging**: Direct water intake tracking
- **Charts & Analytics**: Work with any data source

---

## ✅ Success Indicators

### **Google Fit Working**
- ✅ Sync button shows "Success"
- ✅ Activity data appears in charts
- ✅ Hydration recommendations update
- ✅ No error messages in logs

### **Fallback Working**
- ✅ Mock data syncs successfully
- ✅ Charts display activity data
- ✅ Recommendations are generated
- ✅ Water tracking continues normally

---

## 🚀 Next Steps

1. **Try the Reconnect Button** - Should fix most issues
2. **Check the Setup Guide** - For proper OAuth configuration
3. **Use Mock Data** - For continued development
4. **Monitor Logs** - For debugging information

Your Water Intake Tracker will continue working with mock data even if Google Fit has issues! 🚰💧
