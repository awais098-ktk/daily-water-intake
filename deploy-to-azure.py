#!/usr/bin/env python3
"""
Direct Azure deployment script - bypasses GitHub Actions
Run this locally to deploy your app directly to Azure
"""

import os
import zipfile
import subprocess
import sys

def create_minimal_requirements():
    """Create a minimal requirements.txt for deployment"""
    print("📦 Creating minimal requirements.txt...")
    
    minimal_reqs = """Flask==3.1.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
gunicorn==22.0.0
requests==2.32.3
"""
    
    with open('requirements-deploy.txt', 'w') as f:
        f.write(minimal_reqs)
    
    print("✅ Created requirements-deploy.txt")

def create_deployment_package():
    """Create a ZIP package for Azure deployment"""
    print("📁 Creating deployment package...")
    
    # Files to include in deployment
    files_to_include = [
        'water_tracker/',
        'requirements-deploy.txt',
        'runtime.txt',
        'startup.sh',
        'web.config'
    ]
    
    with zipfile.ZipFile('azure-deploy.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in files_to_include:
            if os.path.exists(item):
                if os.path.isdir(item):
                    # Add directory recursively
                    for root, dirs, files in os.walk(item):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path)
                else:
                    # Add single file
                    zipf.write(item)
                print(f"✅ Added {item}")
            else:
                print(f"⚠️  {item} not found, skipping")
    
    print("✅ Created azure-deploy.zip")

def show_manual_deployment_instructions():
    """Show instructions for manual Azure deployment"""
    print("\n" + "="*60)
    print("🚀 MANUAL AZURE DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    
    print("""
Since GitHub Actions isn't working, here are 3 ways to deploy:

📋 OPTION 1: Azure Portal Upload
1. Go to https://portal.azure.com
2. Find your 'Dailywaterintake' App Service
3. Go to 'Deployment Center' → 'Manual Deployment (Push/Sync)'
4. Upload the 'azure-deploy.zip' file created above
5. Click 'Deploy'

📋 OPTION 2: Azure CLI (if you have it installed)
Run these commands:
   az login
   az webapp deployment source config-zip --resource-group <your-resource-group> --name Dailywaterintake --src azure-deploy.zip

📋 OPTION 3: FTP Upload
1. In Azure Portal, go to your App Service
2. Go to 'Deployment Center' → 'FTP/Credentials'
3. Get FTP credentials
4. Upload files via FTP client

📋 OPTION 4: Try GitHub Actions One More Time
1. Go to: https://github.com/awais098-ktk/daily-water-intake/actions
2. Look for "🚀 CLICK HERE TO DEPLOY TO AZURE"
3. Click "Run workflow" → "Run workflow"
""")

def check_files():
    """Check if required files exist"""
    print("🔍 Checking required files...")
    
    required_files = {
        'water_tracker/app.py': 'Main Flask application',
        'runtime.txt': 'Python version specification',
        'startup.sh': 'Azure startup script',
        'web.config': 'Azure configuration'
    }
    
    all_good = True
    for file, description in required_files.items():
        if os.path.exists(file):
            print(f"✅ {file} - {description}")
        else:
            print(f"❌ {file} - {description} (MISSING)")
            all_good = False
    
    return all_good

def main():
    print("🚀 Azure Deployment Helper")
    print("="*40)
    
    # Check if we're in the right directory
    if not os.path.exists('water_tracker'):
        print("❌ Error: water_tracker directory not found!")
        print("Please run this script from your project root directory.")
        return 1
    
    # Check required files
    if not check_files():
        print("\n⚠️  Some required files are missing!")
        print("The deployment might not work properly.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return 1
    
    # Create minimal requirements
    create_minimal_requirements()
    
    # Create deployment package
    create_deployment_package()
    
    # Show instructions
    show_manual_deployment_instructions()
    
    print("\n🎉 Deployment package ready!")
    print("📦 File created: azure-deploy.zip")
    print("📋 Follow the instructions above to deploy manually.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
