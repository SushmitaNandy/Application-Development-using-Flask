import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SCERECT_KEY') or  'my website is highly secrured'
    #SESSION_KEYS = {"_user_id","_remember","_remember_seconds","_id","_fresh","next",}
    JWT_SECRET_KEY = "please-remember-that-my-website-is-highly-secured"
    
    

class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "blogdb.sqlite3")
    DEBUG = True
    
