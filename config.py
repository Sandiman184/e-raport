import os

class Config:
    # Static Secret Key is CRITICAL for session persistence
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci-rahasia-albarokah-2024-fix-session'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session & Cookie Security
    # False forces it to work on HTTP (Localhost)
    SESSION_COOKIE_SECURE = False 
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = SECRET_KEY 
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'storage')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.getcwd(), 'storage', 'data-dev.sqlite')

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.getcwd(), 'storage', 'data.sqlite')
    
    # Production Security Settings for HTTPS
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PREFERRED_URL_SCHEME = 'https'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
