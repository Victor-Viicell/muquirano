"""
Sistema Muquirano - Arquivo Principal de Execução

Este é o ponto de entrada principal do sistema de controle financeiro Muquirano.
Configura o ambiente Python, inicializa o banco de dados e inicia a aplicação.

Funcionalidades:
- Configuração do PATH do projeto para imports
- Inicialização do banco de dados SQLite
- Lançamento da interface gráfica principal

Uso:
    python src/app/main.py

Requisitos:
    - PySide6 para interface gráfica
    - SQLite para banco de dados
    - Pandas e Matplotlib para análises
    - bcrypt para segurança de senhas

Autor: Viicell
Data: 2025
"""

# Esse é um programa de controle financeiro chamado "Muquirano"
import sys
import os

# Calcula o diretório raiz do projeto e adiciona ao sys.path
# __file__ deve ser muquirano/src/app/main.py
# project_root será muquirano/
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.ui import MainAppController
from src.db import database # Garante que o banco seja inicializado via __init__ ou chamada explícita se necessário

if __name__ == "__main__":
    # Garante que o banco de dados seja inicializado
    # database.initialize_db() # Isso já é chamado em database.py na importação e em MainAppController
    
    controller = MainAppController()
    controller.start()

