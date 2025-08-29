# run.py - Simple startup script for Inventory Management System

import os
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['flask', 'werkzeug', 'reportlab']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(packages):
    """Install missing packages"""
    print("Installing required packages...")
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("All dependencies installed successfully!")

def main():
    print("=" * 50)
    print("    INVENTORY MANAGEMENT SYSTEM")
    print("=" * 50)
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        response = input("Would you like to install them automatically? (y/n): ")
        if response.lower() == 'y':
            try:
                install_dependencies(missing)
            except Exception as e:
                print(f"Error installing packages: {e}")
                print("Please install manually using: pip install flask werkzeug reportlab")
                return
        else:
            print("Please install the required packages manually:")
            print("pip install flask werkzeug reportlab")
            return
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("Error: app.py not found in current directory!")
        print("Please make sure the main application file is named 'app.py'")
        return
    
    print("\nStarting Inventory Management System...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Import and run the app
    try:
        from app import app, init_db
        init_db()  # Initialize database
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"Error importing app: {e}")
        print("Make sure app.py contains the Flask application")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == '__main__':
    main()