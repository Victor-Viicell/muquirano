# Esse é um programa de controle financeiro chamado "Muquirano"
import sys
from src.app.ui import MainAppController
from src.db import database # Ensure db is initialized via its __init__ or explicit call if needed

if __name__ == "__main__":
    # Ensure database is initialized
    # database.initialize_db() # This is already called in database.py upon import and in MainAppController
    
    controller = MainAppController()
    controller.start()

