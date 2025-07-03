# 🚀 Complete Azure Deployment Guide

## 📋 Overview
This guide provides complete instructions for deploying the Daily Water Intake app to Azure App Service using GitHub Actions.

## 🔧 Prerequisites
- GitHub repository with the code
- Azure App Service created (`Dailywaterintake`)
- Azure service principal configured with GitHub secrets

## 📦 Deployment Process

### 1. Automatic Deployment
- **Trigger**: Push to `main` branch
- **Process**: Build → Test → Deploy
- **Duration**: ~5-10 minutes

### 2. Manual Deployment
- Go to GitHub Actions tab
- Select "Deploy to Azure Web App - Dailywaterintake"
- Click "Run workflow"

## 🏗️ Build Process

### Dependencies Used
```
Flask==3.1.0           # Web framework
Flask-SQLAlchemy==3.1.1 # Database ORM
Flask-Login==0.6.3     # User authentication
gunicorn==22.0.0       # Production server
requests==2.32.3       # HTTP requests
```

### Files Deployed
- `water_tracker/` - Main application code
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version (3.11.9)
- `startup.sh` - Azure startup script
- `web.config` - Azure configuration

## ⚙️ Azure Configuration

### Environment Variables to Set
After deployment, configure these in Azure Portal:

```bash
# Google Fit API
GOOGLE_FIT_CLIENT_ID=your_google_client_id
GOOGLE_FIT_CLIENT_SECRET=your_google_client_secret
GOOGLE_FIT_REDIRECT_URI=https://dailywaterintake.azurewebsites.net/wearable/oauth/google_fit/callback

# Flask Configuration
FLASK_SECRET_KEY=your_production_secret_key
FLASK_ENV=production

# Database (if using external DB)
DATABASE_URL=your_database_connection_string
```

### How to Set Environment Variables
1. Go to Azure Portal
2. Navigate to your App Service (`Dailywaterintake`)
3. Go to **Configuration** → **Application settings**
4. Click **+ New application setting**
5. Add each variable above

## 🔍 Troubleshooting

### Common Issues

#### 1. Deployment Fails
- Check GitHub Actions logs
- Verify Azure secrets are configured
- Ensure all required files exist

#### 2. App Won't Start
- Check Azure App Service logs
- Verify `startup.sh` permissions
- Check Python version compatibility

#### 3. Google Fit API Not Working
- Verify environment variables are set
- Check redirect URI matches exactly
- Ensure Google Cloud Console is configured

### Viewing Logs
1. Azure Portal → App Service → **Log stream**
2. Or use Azure CLI: `az webapp log tail --name Dailywaterintake --resource-group <your-rg>`

## 🎯 Post-Deployment Steps

### 1. Verify Deployment
- Visit: https://dailywaterintake.azurewebsites.net
- Check basic functionality

### 2. Configure Google Fit API
- Update redirect URIs in Google Cloud Console
- Test OAuth flow

### 3. Test Features
- User registration/login
- Water intake tracking
- Google Fit integration
- Data visualization

## 📈 Scaling for Multiple Users

### Performance Optimization
- Enable Application Insights
- Configure auto-scaling rules
- Set up CDN for static files
- Optimize database queries

### Monitoring
- Set up alerts for errors
- Monitor response times
- Track user metrics

## 🔄 Continuous Deployment

### Workflow Triggers
- **Push to main**: Automatic deployment
- **Manual trigger**: On-demand deployment
- **Pull request**: Build and test only

### Branch Strategy
- `main` - Production deployments
- `develop` - Development/staging
- Feature branches - Development work

## 📞 Support

### If Deployment Fails
1. Check GitHub Actions tab for error details
2. Review Azure App Service logs
3. Verify all configuration files
4. Test locally first

### Resources
- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)

---

## 🎉 Success Indicators

✅ GitHub Actions workflow completes successfully  
✅ App loads at https://dailywaterintake.azurewebsites.net  
✅ User can register and login  
✅ Google Fit integration works  
✅ Data persists correctly  

**Your app is now ready for production use!** 🚀
