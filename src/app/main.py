# Esse é um programa de controle financeiro chamado "Muquirano"
import sys
import os

# Calculate the project root directory and add it to sys.path
# __file__ is expected to be muquirano/src/app/main.py
# project_root will be muquirano/
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.ui import MainAppController
from src.db import database # Ensure db is initialized via its __init__ or explicit call if needed

if __name__ == "__main__":
    # Ensure database is initialized
    # database.initialize_db() # This is already called in database.py upon import and in MainAppController
    
    controller = MainAppController()
    controller.start()

