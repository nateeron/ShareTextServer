"""
Configuration module for Collaborative Text Editor
================================================

This module manages all configuration settings for the application,
including server ports, hosts, and other settings.
"""

import os
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, continue without it
    pass

class Config:
    """Configuration class for the collaborative text editor"""
    
    # Server Configuration
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "1133"))
    
    # Client Configuration
    CLIENT_HOST: str = os.getenv("CLIENT_HOST", "localhost")
    CLIENT_PORT: int = int(os.getenv("CLIENT_PORT", "1133"))
    
    # WebSocket Configuration
    WS_HOST: str = os.getenv("WS_HOST", "localhost")
    WS_PORT: int = int(os.getenv("WS_PORT", "1133"))
    
    # File Configuration
    TEXT_FILE: str = os.getenv("TEXT_FILE", "shared_text.txt")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    
    @classmethod
    def get_server_url(cls) -> str:
        """Get the server URL for REST API calls"""
        return f"http://{cls.CLIENT_HOST}:{cls.CLIENT_PORT}"
    
    @classmethod
    def get_websocket_url(cls) -> str:
        """Get the WebSocket URL for real-time connections"""
        return f"ws://{cls.WS_HOST}:{cls.WS_PORT}/ws"
    
    @classmethod
    def get_api_docs_url(cls) -> str:
        """Get the API documentation URL"""
        return f"http://{cls.CLIENT_HOST}:{cls.CLIENT_PORT}/docs"
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("🔧 Current Configuration:")
        print(f"   Server Host: {cls.SERVER_HOST}")
        print(f"   Server Port: {cls.SERVER_PORT}")
        print(f"   Client Host: {cls.CLIENT_HOST}")
        print(f"   Client Port: {cls.CLIENT_PORT}")
        print(f"   WebSocket Host: {cls.WS_HOST}")
        print(f"   WebSocket Port: {cls.WS_PORT}")
        print(f"   Text File: {cls.TEXT_FILE}")
        print(f"   Log Level: {cls.LOG_LEVEL}")
        print(f"   Server URL: {cls.get_server_url()}")
        print(f"   WebSocket URL: {cls.get_websocket_url()}")
        print(f"   API Docs URL: {cls.get_api_docs_url()}")

# Create a .env template file
def create_env_template():
    """Create a .env template file"""
    template = """# Collaborative Text Editor Configuration
# =====================================

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=1133

# Client Configuration
CLIENT_HOST=localhost
CLIENT_PORT=1133

# WebSocket Configuration
WS_HOST=localhost
WS_PORT=1133

# File Configuration
TEXT_FILE=shared_text.txt

# Logging Configuration
LOG_LEVEL=info
"""
    
    try:
        with open(".env.template", "w") as f:
            f.write(template)
        print("✅ Created .env.template file")
        print("📝 Copy .env.template to .env and modify as needed")
    except Exception as e:
        print(f"❌ Failed to create .env.template: {e}")

if __name__ == "__main__":
    # Print current configuration
    Config.print_config()
    
    # Create .env template
    create_env_template()
