#!/usr/bin/env python3
"""
Launch script for the Salaaz CSV Converter Streamlit app.
This script is completely separate from the Django application.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages if they're not already installed."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if requirements_file.exists():
        print("Installing required packages...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ])
            print("✅ Requirements installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False
    return True

def launch_app():
    """Launch the Streamlit application."""
    app_file = Path(__file__).parent / "app.py"
    
    if not app_file.exists():
        print(f"❌ App file not found: {app_file}")
        return False
    
    print("🚀 Launching Salaaz CSV Converter...")
    print("📱 The app will open in your default web browser")
    print("🛑 Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Change to the app directory
        os.chdir(Path(__file__).parent)
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--theme.base", "light",
            "--theme.primaryColor", "#ff6b6b",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f2f6"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        return False
    
    return True

def main():
    """Main function to set up and launch the app."""
    print("🔄 Salaaz CSV Converter - Launch Script")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Launch the app
    return launch_app()

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)