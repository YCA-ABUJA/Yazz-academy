import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SERVER_NAME = os.environ.get('SERVER_NAME')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:"
        f"{os.environ.get('DB_PASSWORD', '')}@"
        f"{os.environ.get('DB_HOST', 'localhost')}:"
        f"{os.environ.get('DB_PORT', '3306')}/"
        f"{os.environ.get('DB_NAME', 'yazz_academy')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS_IMAGES = set(os.environ.get('ALLOWED_EXTENSIONS_IMAGES', 'pdf,png,jpg,jpeg,gif').split(','))
    ALLOWED_EXTENSIONS_DOCS = set(os.environ.get('ALLOWED_EXTENSIONS_DOCS', 'pdf,doc,docx').split(','))
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@yca-abuja.com')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 86400))
    
    # Security
    SESSION_COOKIE_SECURE = os.environ.get('ENFORCE_SSL', 'false').lower() == 'true'
    REMEMBER_COOKIE_SECURE = os.environ.get('ENFORCE_SSL', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Rate Limiting - FIXED: Use string format
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('RATE_LIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"  # FIX: Changed from tuple to string
    
    # Application URLs
    APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')
    API_URL = os.environ.get('API_URL', 'http://localhost:5000/api/v1')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    # Use more permissive limits in development
    RATELIMIT_DEFAULT = "500 per day, 100 per hour"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False  # Disable rate limiting for tests


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}