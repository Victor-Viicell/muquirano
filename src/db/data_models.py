"""
Sistema Muquirano - Modelos de Dados

Este módulo define as estruturas de dados (dataclasses e enums) utilizadas
em todo o sistema Muquirano para representar usuários e transações financeiras.

Classes principais:
- TransactionType: Enum para tipos de transação (receita/despesa)
- User: Dataclass representando um usuário do sistema
- Transaction: Dataclass representando uma transação financeira

Os modelos suportam funcionalidades avançadas como:
- Transações parceladas com agrupamento
- Transações recorrentes com frequência definida
- Rastreamento de posição em grupos (parcela X de Y)

Autor: Sistema Muquirano
Data: 2024
"""

from enum import Enum
from dataclasses import dataclass

class TransactionType(Enum):
    """
    Enumeração para tipos de transação financeira
    
    Valores:
        INCOME: Representa receitas/entradas de dinheiro
        EXPENSE: Representa despesas/saídas de dinheiro
    """
    INCOME = "receita"
    EXPENSE = "despesa"

@dataclass
class User:
    """
    Representa um usuário do sistema Muquirano
    
    Attributes:
        id (int): Identificador único do usuário
        name (str): Nome do usuário (deve ser único no sistema)
        password (str): Senha do usuário (hashada quando armazenada)
    """
    id: int
    name: str
    password: str

@dataclass
class Transaction:
    """
    Representa uma transação financeira no sistema
    
    Esta classe suporta tanto transações simples quanto agrupadas
    (parceladas ou recorrentes), com campos específicos para rastreamento
    de grupos e posicionamento dentro dos mesmos.
    
    Attributes:
        id (int): Identificador único da transação
        user_id (int): ID do usuário proprietário
        type (TransactionType): Tipo da transação (receita ou despesa)
        amount (float): Valor da transação
        date (str): Data da transação no formato YYYY-MM-DD
        description (str): Descrição/título da transação
        
        # Campos para transações parceladas
        installment_group_id (str | None): ID do grupo de parcelamento
        installment_number (int | None): Número da parcela atual (ex: 2)
        total_installments (int | None): Total de parcelas (ex: 12)
        
        # Campos para transações recorrentes
        is_recurring (bool): Indica se é transação recorrente
        recurring_group_id (str | None): ID do grupo de recorrência
        recurrence_frequency (str | None): Frequência (ex: "monthly", "weekly")
        occurrence_number (int | None): Número da ocorrência atual
        total_occurrences_in_group (int | None): Total de ocorrências no grupo
    """
    id: int
    user_id: int
    type: TransactionType
    amount: float
    date: str
    description: str
    installment_group_id: str | None = None
    installment_number: int | None = None
    total_installments: int | None = None

    # Campos para transações recorrentes
    is_recurring: bool = False
    recurring_group_id: str | None = None      # Para agrupar todas as ocorrências de uma transação recorrente
    recurrence_frequency: str | None = None    # ex: "monthly", "weekly", "yearly"
    occurrence_number: int | None = None       # ex: 1ª, 2ª, ... ocorrência na série
    total_occurrences_in_group: int | None = None # Total de ocorrências planejadas/geradas para este grupo

# Aliases de tipo para listas
Users = list[User]
Transactions = list[Transaction] 