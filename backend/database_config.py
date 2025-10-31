"""
Database configuration for PythonAnywhere deployment
"""
import os

# For PythonAnywhere, use this format:
# MySQL: mysql+pymysql://username:password@username.mysql.pythonanywhere-services.com/username$dbname
# SQLite (local): sqlite:///./instance/markmate.db

def get_database_url():
    """
    Get database URL based on environment
    """
    # Check if we're on PythonAnywhere or have MySQL credentials
    pa_user = os.environ.get('PYTHONANYWHERE_USER')
    db_password = os.environ.get('DB_PASSWORD')
    
    if pa_user and db_password:
        # PythonAnywhere MySQL
        db_host = f"{pa_user}.mysql.pythonanywhere-services.com"
        db_name = f"{pa_user}$markmate"
        return f"mysql+pymysql://{pa_user}:{db_password}@{db_host}/{db_name}"
    
    # Check for explicit DATABASE_URL environment variable
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return database_url
    
    # Default to SQLite for local development
    return "sqlite:///./instance/markmate.db"


# Example usage in models.py:
# from database_config import get_database_url
# SQLALCHEMY_DATABASE_URL = get_database_url()
