from enum import Enum
from dataclasses import dataclass

class TransactionType(Enum):
    INCOME = "receita"
    EXPENSE = "despesa"

@dataclass
class User:
    id: int
    name: str
    password: str

@dataclass
class Transaction:
    id: int
    user_id: int
    type: TransactionType
    amount: float
    date: str
    description: str
    installment_group_id: str | None = None
    installment_number: int | None = None
    total_installments: int | None = None

    # Fields for recurring transactions
    is_recurring: bool = False
    recurring_group_id: str | None = None      # To group all occurrences of a recurring transaction
    recurrence_frequency: str | None = None    # e.g., "monthly", "weekly", "yearly"
    occurrence_number: int | None = None       # e.g., 1st, 2nd, ... occurrence in the series
    total_occurrences_in_group: int | None = None # Total occurrences planned/generated for this group

Users = list[User]
Transactions = list[Transaction] 