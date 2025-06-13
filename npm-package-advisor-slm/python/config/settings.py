import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    # Groq AI Configuration
    AI_API_BASE_URL = os.getenv('AI_API_BASE_URL', 'https://api.groq.com/openai/v1')
    AI_API_KEY = os.getenv('AI_API_KEY')  # Required (no default)
    AI_MODEL = os.getenv('AI_MODEL', 'llama3-70b-8192')  # Groq's fastest model
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', 2000))
    
    # Email Configuration
    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
    EMAIL_RECIPIENTS = os.getenv('EMAIL_RECIPIENTS', '').split(',')
    
    # Project Settings
    SCAN_PROJECT_PATH = os.path.normpath(os.getenv('SCAN_PROJECT_PATH', os.getcwd()))
    REPORT_OUTPUT_DIR = os.getenv('REPORT_OUTPUT_DIR', 'reports')
    
    @classmethod
    def validate(cls):
        """Validate required settings for Groq"""
        required = [
            'AI_API_KEY',  # Changed from OPENAI_API_KEY
            'SMTP_SERVER',
            'SMTP_USER',
            'SMTP_PASSWORD',
            'EMAIL_FROM'
        ]
        
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Validate settings on import
Settings.validate()