"""
Sistema Muquirano - Módulo de Utilitários

Este módulo contém funções auxiliares utilizadas em diversas partes do sistema
Muquirano para formatação de dados, conversões e operações comuns.

Principais funcionalidades:
- Formatação de datas para exibição
- Conversões entre formatos de data
- Funções auxiliares para interface gráfica

Autor: Viicell
Data: 2025
"""

from PySide6.QtCore import QDate

# Helper to convert YYYY-MM-DD to dd/MM/yyyy for display
def format_date_for_display(date_str_db):
    """
    Converte data do formato banco de dados (YYYY-MM-DD) para formato de exibição (dd/MM/yyyy)
    
    Args:
        date_str_db (str): Data no formato YYYY-MM-DD do banco de dados
    
    Returns:
        str: Data formatada para exibição (dd/MM/yyyy) ou string original em caso de erro
    
    Examples:
        >>> format_date_for_display("2024-03-15")
        "15/03/2024"
        
        >>> format_date_for_display("")
        ""
        
        >>> format_date_for_display("invalid-date")
        "invalid-date"
    """
    if not date_str_db:
        return ""
    try:
        date_obj = QDate.fromString(date_str_db, "yyyy-MM-dd")
        return date_obj.toString("dd/MM/yyyy")
    except Exception:
        return date_str_db # Fallback para original se análise falhar 