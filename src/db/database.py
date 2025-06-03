"""
Sistema Muquirano - Módulo de Banco de Dados

Este módulo gerencia todas as operações de banco de dados do sistema Muquirano,
incluindo criação, leitura, atualização e exclusão de usuários e transações.
Utiliza SQLite como banco de dados e bcrypt para hash de senhas.

Principais funcionalidades:
- Gerenciamento de usuários com autenticação segura
- CRUD completo para transações financeiras
- Suporte a transações parceladas e recorrentes
- Validação e busca avançada de transações
- Operações em lote para grupos de transações

Tabelas do banco:
- users: Informações de usuários e senhas hashadas
- transactions: Transações financeiras com suporte a agrupamento

Autor: Viicell
Data: 2025
"""

import sqlite3
from typing import Optional, List
import bcrypt # Para hash de senhas
import uuid # Para gerar IDs únicos de grupos de parcelas
from datetime import datetime, date # Para manipulação de datas
from dateutil.relativedelta import relativedelta # Para cálculos de data
from .data_models import User, Transaction, TransactionType

DB_NAME = "muquirano.db"

def initialize_db():
    """
    Inicializa o banco de dados criando as tabelas necessárias
    
    Cria as tabelas 'users' e 'transactions' se elas não existirem.
    Esta função é chamada automaticamente na inicialização da aplicação.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Cria tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    # Cria tabela de transações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            installment_group_id TEXT,
            installment_number INTEGER,
            total_installments INTEGER,
            is_recurring INTEGER DEFAULT 0,      -- SQLite usa INTEGER para BOOLEAN (0 ou 1)
            recurring_group_id TEXT,
            recurrence_frequency TEXT,         -- ex: 'monthly', 'weekly', 'yearly'
            occurrence_number INTEGER,         -- ex: 1, 2, 3 para a ocorrência atual no grupo
            total_occurrences_in_group INTEGER,-- Número total de ocorrências planejadas para este grupo na criação
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

def add_user(name: str, password: str) -> Optional[User]:
    """
    Adiciona um novo usuário ao banco de dados
    
    Args:
        name (str): Nome do usuário (deve ser único)
        password (str): Senha em texto plano (será hashada)
    
    Returns:
        Optional[User]: Objeto User se criado com sucesso, None caso contrário
        
    Note:
        A senha é automaticamente hashada usando bcrypt antes do armazenamento.
        Retorna None se o nome de usuário já existir.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # Faz hash da senha
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, hashed_password))
        conn.commit()
        user_id = cursor.lastrowid
        if user_id is not None:
            # Retorna usuário com senha em texto plano para uso imediato se necessário
            # Para esta estrutura de aplicação, retornar a senha hashada não é útil para o objeto User
            return User(id=user_id, name=name, password=password) # Ou considere não retornar senha alguma
        return None
    except sqlite3.IntegrityError: # Nome de usuário já existe
        return None
    finally:
        conn.close()

def get_user(name: str) -> Optional[User]:
    """
    Busca um usuário pelo nome
    
    Args:
        name (str): Nome do usuário a ser buscado
    
    Returns:
        Optional[User]: Objeto User se encontrado, None caso contrário
        
    Note:
        O campo password do objeto User retornado contém o hash da senha.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, password FROM users WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        user_id, user_name, stored_hashed_password_bytes = row
        # O objeto User retornado aqui não precisa que a senha seja em texto plano
        # A verificação acontece aqui. Se bem-sucedida, a UI sabe.
        # Estamos retornando um objeto User que ainda tem um campo password,
        # mas para um usuário logado, seu valor não é usado diretamente para re-autenticação tipicamente.
        # Por ora, vamos manter simples e não armazenar a senha em texto plano no objeto User após login.
        # Precisaremos ajustar handle_login em ui.py porque ele compara user.password == password
        return User(id=user_id, name=user_name, password=stored_hashed_password_bytes.decode('utf-8', errors='ignore')) # Armazena hash como string
    return None

def check_user_password(username: str, password_to_check: str) -> Optional[User]:
    """
    Verifica as credenciais do usuário e retorna o objeto User se válidas
    
    Args:
        username (str): Nome do usuário
        password_to_check (str): Senha em texto plano para verificação
    
    Returns:
        Optional[User]: Objeto User se credenciais válidas, None caso contrário
    
    Note:
        Esta função substitui a verificação de senha em LoginWindow.handle_login.
        Usa bcrypt para comparação segura de senhas.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, password FROM users WHERE name = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        user_id, user_name, stored_hashed_password_bytes = row
        if bcrypt.checkpw(password_to_check.encode('utf-8'), stored_hashed_password_bytes):
            return User(id=user_id, name=user_name, password='') # Não retorna hash ou senha em texto plano
        else:
            return None # Senha incorreta
    return None # Usuário não encontrado

def get_all_usernames() -> List[str]:
    """
    Busca todos os nomes de usuário do banco de dados
    
    Returns:
        List[str]: Lista de nomes de usuário ordenada alfabeticamente
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def add_transaction(
    user_id: int,
    type: TransactionType,
    total_amount: float, 
    date_str: str, 
    description: str,
    num_installments: int = 1,
    is_recurring_input: bool = False, # Novo: se esta transação é parte de uma série recorrente
    recurrence_frequency_input: Optional[str] = None, # Novo: ex: 'monthly', 'weekly'
    num_occurrences_to_generate_input: int = 0 # Novo: Quantas ocorrências futuras gerar automaticamente
) -> List[Transaction]:
    """
    Adiciona uma ou múltiplas transações ao banco de dados
    
    Esta função suporta três tipos de transação:
    1. Simples: Uma única transação
    2. Parcelada: Múltiplas parcelas com datas consecutivas mensais
    3. Recorrente: Múltiplas ocorrências com frequência definida
    
    Args:
        user_id (int): ID do usuário proprietário
        type (TransactionType): Tipo da transação (INCOME ou EXPENSE)
        total_amount (float): Valor total (para parcelas) ou valor por ocorrência (para recorrentes)
        date_str (str): Data inicial no formato YYYY-MM-DD
        description (str): Descrição base da transação
        num_installments (int, optional): Número de parcelas. Defaults to 1.
        is_recurring_input (bool, optional): Se é transação recorrente. Defaults to False.
        recurrence_frequency_input (Optional[str], optional): Frequência da recorrência. Defaults to None.
        num_occurrences_to_generate_input (int, optional): Número de ocorrências a gerar. Defaults to 0.
    
    Returns:
        List[Transaction]: Lista de transações criadas
    
    Note:
        Para transações parceladas, o valor é dividido igualmente entre as parcelas.
        Para transações recorrentes, cada ocorrência tem o valor total especificado.
        As datas são calculadas automaticamente baseadas na frequência escolhida.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    created_transactions: List[Transaction] = []
    
    base_start_date = datetime.strptime(date_str, "%Y-%m-%d").date() # Usa .date() para objetos date

    # Determina iterações do loop: 1 para simples, N para parcelas, M para lote recorrente
    # Se é recorrente, num_installments é implicitamente 1 para cada ocorrência gerada.
    # Se é parcela, is_recurring_input deve ser False para a chamada inicial da UI para esse grupo.

    # Para transações recorrentes, geramos um lote baseado em num_occurrences_to_generate_input
    if is_recurring_input and num_occurrences_to_generate_input > 0:
        current_recurring_group_id = str(uuid.uuid4())
        amount_per_occurrence = total_amount # Para recorrentes, total_amount é o valor para CADA ocorrência
        
        for occurrence_idx in range(num_occurrences_to_generate_input):
            occurrence_num = occurrence_idx + 1
            occurrence_date = base_start_date
            if recurrence_frequency_input == 'monthly':
                occurrence_date = base_start_date + relativedelta(months=occurrence_idx)
            elif recurrence_frequency_input == 'weekly':
                occurrence_date = base_start_date + relativedelta(weeks=occurrence_idx)
            elif recurrence_frequency_input == 'yearly':
                occurrence_date = base_start_date + relativedelta(years=occurrence_idx)
            else: # Padrão para base_start_date se frequência for desconhecida ou não aplicável para geração em lote
                if occurrence_idx > 0: # apenas avança se não for a primeira e frequência for estranha
                    # Potencialmente registra um aviso ou trata este caso como erro
                    print(f"Aviso: Frequência de recorrência desconhecida '{recurrence_frequency_input}' para geração em lote de {description}")
                    occurrence_date = base_start_date + relativedelta(months=occurrence_idx) # fallback para mensal por segurança
            
            occurrence_date_str = occurrence_date.strftime("%Y-%m-%d")
            occurrence_description = f"{description} (Recorrente {occurrence_num}/{num_occurrences_to_generate_input})"

            try:
                cursor.execute(
                    "INSERT INTO transactions (user_id, type, amount, date, description, "
                    "is_recurring, recurring_group_id, recurrence_frequency, occurrence_number, total_occurrences_in_group) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id, type.value, amount_per_occurrence, occurrence_date_str, occurrence_description,
                     1, current_recurring_group_id, recurrence_frequency_input, occurrence_num, num_occurrences_to_generate_input)
                )
                transaction_id = cursor.lastrowid
                if transaction_id is not None:
                    created_transactions.append(Transaction(
                        id=transaction_id, user_id=user_id, type=type, amount=amount_per_occurrence, date=occurrence_date_str,
                        description=occurrence_description, is_recurring=True, recurring_group_id=current_recurring_group_id,
                        recurrence_frequency=recurrence_frequency_input, occurrence_number=occurrence_num, total_occurrences_in_group=num_occurrences_to_generate_input
                    ))
                else: print(f"Erro: Falha ao obter lastrowid para transação recorrente: {occurrence_description}")
            except Exception as e:
                print(f"Erro adicionando transação recorrente: {occurrence_description}: {e}")
                conn.close(); return []
    
    # Para transações parceladas (não podem ser simultaneamente lote-recorrentes de uma chamada UI como esta)
    elif num_installments > 1 and not is_recurring_input:
        current_installment_group_id = str(uuid.uuid4())
        amount_per_installment = round(total_amount / num_installments, 2)
        
        for installment_idx in range(num_installments):
            installment_num = installment_idx + 1
            installment_date = base_start_date + relativedelta(months=installment_idx)
            installment_date_str = installment_date.strftime("%Y-%m-%d")
            installment_description = f"{description} ({installment_num}/{num_installments})"

            try:
                cursor.execute(
                    "INSERT INTO transactions (user_id, type, amount, date, description, "
                    "installment_group_id, installment_number, total_installments) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id, type.value, amount_per_installment, installment_date_str, installment_description,
                     current_installment_group_id, installment_num, num_installments)
                )
                transaction_id = cursor.lastrowid
                if transaction_id is not None:
                    created_transactions.append(Transaction(
                        id=transaction_id, user_id=user_id, type=type, amount=amount_per_installment, date=installment_date_str,
                        description=installment_description, installment_group_id=current_installment_group_id,
                        installment_number=installment_num, total_installments=num_installments
                    ))
                else: print(f"Erro: Falha ao obter lastrowid para parcela: {installment_description}")
            except Exception as e:
                print(f"Erro adicionando transação parcelada: {installment_description}: {e}")
                conn.close(); return []

    # Para transações simples, sem parcela, sem lote-recorrente
    else:
        try:
            cursor.execute(
                "INSERT INTO transactions (user_id, type, amount, date, description) VALUES (?, ?, ?, ?, ?)",
                (user_id, type.value, total_amount, date_str, description)
            )
            transaction_id = cursor.lastrowid
            if transaction_id is not None:
                created_transactions.append(Transaction(
                    id=transaction_id, user_id=user_id, type=type, amount=total_amount, date=date_str,
                    description=description
                ))
            else: print(f"Erro: Falha ao obter lastrowid para transação simples: {description}")
        except Exception as e:
            print(f"Erro adicionando transação simples: {description}: {e}")
            conn.close(); return []

    conn.commit()
    conn.close()
    return created_transactions

def get_transactions_by_user(user_id: int, 
                             search_term: Optional[str] = None, 
                             filter_type: Optional[TransactionType] = None,
                             sort_by: str = "date", 
                             sort_order: str = "DESC") -> List[Transaction]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = ("SELECT id, user_id, type, amount, date, description, "
             "installment_group_id, installment_number, total_installments, "
             "is_recurring, recurring_group_id, recurrence_frequency, occurrence_number, total_occurrences_in_group "
             "FROM transactions WHERE user_id = ?")
    params: list[any] = [user_id]

    if search_term:
        query += " AND description LIKE ?"
        params.append(f"%{search_term}%")
    
    if filter_type:
        query += " AND type = ?"
        params.append(filter_type.value)

    allowed_sort_columns = {"date", "description", "amount"} # Add more if needed for new fields
    if sort_by not in allowed_sort_columns:
        sort_by = "date" 
    
    allowed_sort_orders = {"ASC", "DESC"}
    if sort_order.upper() not in allowed_sort_orders:
        sort_order = "DESC"

    query += f" ORDER BY {sort_by} {sort_order.upper()}, id {sort_order.upper()}" 

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    transactions = []
    for row in rows:
        transactions.append(
            Transaction(
                id=row[0],
                user_id=row[1],
                type=TransactionType(row[2]),
                amount=row[3],
                date=row[4],
                description=row[5],
                installment_group_id=row[6],
                installment_number=row[7],
                total_installments=row[8],
                is_recurring=bool(row[9] if row[9] is not None else 0),
                recurring_group_id=row[10],
                recurrence_frequency=row[11],
                occurrence_number=row[12],
                total_occurrences_in_group=row[13]
            )
        )
    return transactions

def get_transaction_by_id(transaction_id: int) -> Optional[Transaction]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = ("SELECT id, user_id, type, amount, date, description, "
             "installment_group_id, installment_number, total_installments, "
             "is_recurring, recurring_group_id, recurrence_frequency, occurrence_number, total_occurrences_in_group "
             "FROM transactions WHERE id = ?")
    cursor.execute(query, (transaction_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Transaction(
            id=row[0],
            user_id=row[1],
            type=TransactionType(row[2]),
            amount=row[3],
            date=row[4],
            description=row[5],
            installment_group_id=row[6],
            installment_number=row[7],
            total_installments=row[8],
            is_recurring=bool(row[9] if row[9] is not None else 0),
            recurring_group_id=row[10],
            recurrence_frequency=row[11],
            occurrence_number=row[12],
            total_occurrences_in_group=row[13]
        )
    return None

def update_transaction(
    transaction_id: int, 
    type_val: TransactionType, 
    amount_val: float, 
    date_val: str, 
    description_val: str
) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE transactions 
            SET type = ?, amount = ?, date = ?, description = ?
            WHERE id = ?
        """, (type_val.value, amount_val, date_val, description_val, transaction_id))
        conn.commit()
        return cursor.rowcount > 0 # True if a row was updated
    except Exception as e:
        print(f"Error updating transaction ID {transaction_id}: {e}")
        return False
    finally:
        conn.close()

def delete_transaction(transaction_id: int) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting transaction: {e}")
        return False
    finally:
        conn.close()

def delete_transaction_group(group_id: str, group_field_name: str) -> tuple[bool, int]:
    """Deletes all transactions belonging to a specific group.

    Args:
        group_id: The ID of the group to delete.
        group_field_name: The database column name for the group ID 
                          (e.g., 'installment_group_id' or 'recurring_group_id').

    Returns:
        A tuple (success: bool, num_deleted: int).
    """
    if group_field_name not in ["installment_group_id", "recurring_group_id"]:
        print(f"Error: Invalid group_field_name: {group_field_name}")
        return False, 0

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # Ensure group_field_name is safe for direct use in SQL (already checked against whitelist)
        query = f"DELETE FROM transactions WHERE {group_field_name} = ?"
        cursor.execute(query, (group_id,))
        conn.commit()
        num_deleted = cursor.rowcount
        return True, num_deleted
    except Exception as e:
        print(f"Error deleting transaction group {group_id} using field {group_field_name}: {e}")
        return False, 0
    finally:
        conn.close()

def update_group_base_description(group_id: str, group_field_name: str, new_base_description: str) -> tuple[bool, int]:
    """Updates the base description for all transactions in a group.
    The (X/Y) part of the description is preserved and reconstructed.
    """
    if group_field_name not in ["installment_group_id", "recurring_group_id"]:
        print(f"Error: Invalid group_field_name for description update: {group_field_name}")
        return False, 0

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    updated_count = 0
    try:
        # First, fetch all transactions in the group to get their individual numbers
        id_field = "id"
        num_field = "installment_number" if group_field_name == "installment_group_id" else "occurrence_number"
        total_field = "total_installments" if group_field_name == "installment_group_id" else "total_occurrences_in_group"
        
        query_select = f"SELECT {id_field}, {num_field}, {total_field} FROM transactions WHERE {group_field_name} = ?"
        cursor.execute(query_select, (group_id,))
        transactions_in_group = cursor.fetchall()

        for t_id, num, total in transactions_in_group:
            if num is not None and total is not None:
                reconstructed_description = f"{new_base_description.strip()} ({num}/{total})"
            else:
                reconstructed_description = new_base_description.strip() # Should not happen for grouped items
            
            cursor.execute("UPDATE transactions SET description = ? WHERE id = ?", (reconstructed_description, t_id))
            updated_count += cursor.rowcount
        
        conn.commit()
        return True, updated_count
    except Exception as e:
        print(f"Error updating base description for group {group_id}: {e}")
        conn.rollback() # Rollback on error
        return False, 0
    finally:
        conn.close()

def update_recurring_group_future_amounts(recurring_group_id: str, from_date_str: str, new_amount: float) -> tuple[bool, int]:
    """Updates amounts for transactions in a recurring group on or after from_date.
    Assumes date_str is in 'YYYY-MM-DD' format.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        query = """
            UPDATE transactions 
            SET amount = ? 
            WHERE recurring_group_id = ? AND date >= ?
        """
        cursor.execute(query, (new_amount, recurring_group_id, from_date_str))
        conn.commit()
        return True, cursor.rowcount
    except Exception as e:
        print(f"Error updating future amounts for recurring group {recurring_group_id}: {e}")
        return False, 0
    finally:
        conn.close()

# Initialize the database when this module is imported
# initialize_db() # Call this explicitly from main.py or similar entry point if issues arise with tests or multiple initializations