#!/usr/bin/env python3
"""
Streamlit Application Startup Script for Personal Finance Agent

This script starts the Streamlit web application with proper configuration
and environment setup.
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment variables and configuration."""
    # Set default environment variables if not already set
    env_vars = {
        'STREAMLIT_SERVER_PORT': '8501',
        'STREAMLIT_SERVER_ADDRESS': 'localhost',
        'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
        'STREAMLIT_SERVER_HEADLESS': 'true',
        'STREAMLIT_THEME_PRIMARY_COLOR': '#1f77b4',
        'STREAMLIT_THEME_BACKGROUND_COLOR': '#ffffff',
        'STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR': '#f0f2f6',
        'STREAMLIT_THEME_TEXT_COLOR': '#262730'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            logger.info(f"Set environment variable: {key}={value}")

def check_api_server():
    """Check if the API server is running."""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ API server is running and healthy")
            return True
    except requests.exceptions.RequestException:
        pass
    
    logger.warning("⚠️ API server is not running at http://localhost:8000")
    logger.info("Please start the API server first by running: python run_api.py")
    return False

def main():
    """Main function to start the Streamlit application."""
    logger.info("🚀 Starting Personal Finance Agent Streamlit Application")
    
    # Setup environment
    setup_environment()
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "streamlit_app.py").exists():
        logger.error("❌ streamlit_app.py not found in current directory")
        logger.info("Please run this script from the personal_finance_agent directory")
        sys.exit(1)
    
    # Check API server status
    api_running = check_api_server()
    if not api_running:
        print("\n" + "="*60)
        print("🔧 SETUP INSTRUCTIONS")
        print("="*60)
        print("1. Start the API server first:")
        print("   python run_api.py")
        print("\n2. Then start the Streamlit app:")
        print("   python run_streamlit.py")
        print("="*60)
        
        # Ask if user wants to continue anyway
        try:
            choice = input("\nDo you want to start Streamlit anyway? (y/N): ").strip().lower()
            if choice not in ['y', 'yes']:
                logger.info("Exiting...")
                sys.exit(0)
        except KeyboardInterrupt:
            logger.info("\nExiting...")
            sys.exit(0)
    
    # Streamlit configuration
    streamlit_config = [
        "--server.port", os.environ.get('STREAMLIT_SERVER_PORT', '8501'),
        "--server.address", os.environ.get('STREAMLIT_SERVER_ADDRESS', 'localhost'),
        "--browser.gatherUsageStats", "false",
        "--server.headless", "true",
        "--theme.primaryColor", "#1f77b4",
        "--theme.backgroundColor", "#ffffff",
        "--theme.secondaryBackgroundColor", "#f0f2f6",
        "--theme.textColor", "#262730"
    ]
    
    # Build command
    cmd = ["streamlit", "run", "streamlit_app.py"] + streamlit_config
    
    logger.info(f"Starting Streamlit with command: {' '.join(cmd)}")
    
    # Print startup information
    print("\n" + "="*60)
    print("🌟 PERSONAL FINANCE AGENT - STREAMLIT UI")
    print("="*60)
    print(f"📱 Web Interface: http://localhost:{os.environ.get('STREAMLIT_SERVER_PORT', '8501')}")
    print(f"🔗 API Backend: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("="*60)
    print("💡 Features:")
    print("  • 🔐 User authentication and profiles")
    print("  • 💳 Transaction management with AI categorization")
    print("  • 📄 Document upload and OCR processing")
    print("  • 📊 Financial analytics and insights")
    print("  • 🎯 Goal tracking towards €100,000")
    print("  • ⚙️ Comprehensive settings and preferences")
    print("="*60)
    print("🛑 Press Ctrl+C to stop the application")
    print("="*60 + "\n")
    
    try:
        # Start Streamlit
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to start Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Streamlit application stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 