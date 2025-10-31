# PythonAnywhere WSGI configuration for MarkMate FastAPI backend

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/MarkMate'  # REPLACE 'yourusername' with your PythonAnywhere username
backend_path = os.path.join(project_home, 'backend')

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set working directory
os.chdir(backend_path)

# Import your FastAPI app
from main import app

# PythonAnywhere needs an 'application' callable
application = app
