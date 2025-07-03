import sys

def check_import(module_name):
    try:
        __import__(module_name)
        print(f"✓ {module_name} is installed")
        return True
    except ImportError:
        print(f"✗ {module_name} is NOT installed")
        return False

# Check all required packages
all_good = True
all_good &= check_import('flask')
all_good &= check_import('flask_sqlalchemy')
all_good &= check_import('flask_login')
all_good &= check_import('werkzeug')
all_good &= check_import('PIL')
all_good &= check_import('requests')

if all_good:
    print("\nAll required packages are installed!")
else:
    print("\nSome packages are missing. Please install them using:")
    print("pip install flask flask-sqlalchemy flask-login werkzeug pillow requests")

# Print Python path
print("\nPython path:")
for path in sys.path:
    print(path)
