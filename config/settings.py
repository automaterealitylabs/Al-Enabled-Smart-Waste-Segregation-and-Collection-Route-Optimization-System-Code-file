import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

class Config:
    IS_PRODUCTION = os.getenv('RENDER') == 'true' or os.getenv('FLASK_ENV') == 'production'

    # Secret key for session signing
    SECRET_KEY = os.getenv('SECRET_KEY')
    if IS_PRODUCTION and not SECRET_KEY:
        raise ValueError(
            "CRITICAL CONFIGURATION ERROR: SECRET_KEY environment variable is not set. "
            "In production on Render, SECRET_KEY must be configured in the Render Dashboard "
            "under Environment Variables to ensure secure session signing."
        )
    elif not SECRET_KEY:
        # Fixed development secret key (do not generate random secret per restart)
        SECRET_KEY = 'smartwaste-dev-secret-key-not-for-production'

    # Ensure debug mode is strictly disabled in production
    DEBUG = False if IS_PRODUCTION else os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']

    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

    # Default Municipal Depot Coordinates (Pune Central Depot)
    DEFAULT_DEPOT_LAT = 18.5204
    DEFAULT_DEPOT_LNG = 73.8567
