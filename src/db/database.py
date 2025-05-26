import sqlite3
from typing import Optional, List
import bcrypt # Added for password hashing
import uuid # For generating unique installment group IDs
from datetime import datetime, date # ensure date is imported
from dateutil.relativedelta import relativedelta # For date calculations
from .data_models import User, Transaction, TransactionType

DB_NAME = "muquirano.db"

def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    # Create transactions table
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
            is_recurring INTEGER DEFAULT 0,      -- SQLite uses INTEGER for BOOLEAN (0 or 1)
            recurring_group_id TEXT,
            recurrence_frequency TEXT,         -- e.g., 'monthly', 'weekly', 'yearly'
            occurrence_number INTEGER,         -- e.g., 1, 2, 3 for the current occurrence in the group
            total_occurrences_in_group INTEGER,-- Total number of occurrences planned for this group at creation
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

def add_user(name: str, password: str) -> Optional[User]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # Hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, hashed_password))
        conn.commit()
        user_id = cursor.lastrowid
        if user_id is not None:
            # Return user with plain password for immediate use if needed, though it's not stored plain
            # For this application structure, returning the hashed password is not useful for the User object
            return User(id=user_id, name=name, password=password) # Or consider not returning password at all
        return None
    except sqlite3.IntegrityError: # Username already exists
        return None
    finally:
        conn.close()

def get_user(name: str) -> Optional[User]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, password FROM users WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        user_id, user_name, stored_hashed_password_bytes = row
        # The User object returned here does not need the password to be the plain text one
        # The check happens here. If successful, the UI knows.
        # We are returning a User object that still has a password field,
        # but for a logged-in user, its value isn't directly used for re-authentication typically.
        # For now, let's keep it simple and not store the plain password in the User object after login.
        # We will need to adjust handle_login in ui.py because it compares user.password == password
        return User(id=user_id, name=user_name, password=stored_hashed_password_bytes.decode('utf-8', errors='ignore')) # Store hash as string
    return None

def check_user_password(username: str, password_to_check: str) -> Optional[User]:
    """
    Checks user credentials. Returns User object if valid, None otherwise.
    This function is intended to replace the password check in LoginWindow.handle_login.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, password FROM users WHERE name = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        user_id, user_name, stored_hashed_password_bytes = row
        if bcrypt.checkpw(password_to_check.encode('utf-8'), stored_hashed_password_bytes):
            return User(id=user_id, name=user_name, password='') # Don't return hash or plain password
        else:
            return None # Password mismatch
    return None # User not found

def add_transaction(
    user_id: int,
    type: TransactionType,
    total_amount: float, 
    date_str: str, 
    description: str,
    num_installments: int = 1,
    is_recurring_input: bool = False, # New: if this transaction is part of a recurring series
    recurrence_frequency_input: Optional[str] = None, # New: e.g., 'monthly', 'weekly'
    num_occurrences_to_generate_input: int = 0 # New: How many future occurrences to auto-generate
) -> List[Transaction]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    created_transactions: List[Transaction] = []
    
    base_start_date = datetime.strptime(date_str, "%Y-%m-%d").date() # Use .date() for date objects

    # Determine loop iterations: 1 for simple, N for installments, M for recurring batch
    # If it's recurring, num_installments is implicitly 1 for each generated occurrence.
    # If it's an installment, is_recurring_input should be False for the initial call from UI for that group.

    # For recurring transactions, we generate a batch based on num_occurrences_to_generate_input
    if is_recurring_input and num_occurrences_to_generate_input > 0:
        current_recurring_group_id = str(uuid.uuid4())
        amount_per_occurrence = total_amount # For recurring, total_amount is the amount for EACH occurrence
        
        for occurrence_idx in range(num_occurrences_to_generate_input):
            occurrence_num = occurrence_idx + 1
            occurrence_date = base_start_date
            if recurrence_frequency_input == 'monthly':
                occurrence_date = base_start_date + relativedelta(months=occurrence_idx)
            elif recurrence_frequency_input == 'weekly':
                occurrence_date = base_start_date + relativedelta(weeks=occurrence_idx)
            elif recurrence_frequency_input == 'yearly':
                occurrence_date = base_start_date + relativedelta(years=occurrence_idx)
            else: # Default to base_start_date if frequency is unknown or not applicable for batch generation
                if occurrence_idx > 0: # only advance if not the first one and frequency is weird
                    # Potentially log a warning or handle this case as an error
                    print(f"Warning: Unknown recurrence frequency '{recurrence_frequency_input}' for batch generation of {description}")
                    occurrence_date = base_start_date + relativedelta(months=occurrence_idx) # fallback to monthly for safety
            
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
                else: print(f"Error: Failed to get lastrowid for recurring transaction: {occurrence_description}")
            except Exception as e:
                print(f"Error adding recurring transaction: {occurrence_description}: {e}")
                conn.close(); return []
    
    # For installment transactions (can't be simultaneously batch-recurring from one UI call like this)
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
                else: print(f"Error: Failed to get lastrowid for installment: {installment_description}")
            except Exception as e:
                print(f"Error adding installment transaction: {installment_description}: {e}")
                conn.close(); return []

    # For simple, non-installment, non-batch-recurring transactions
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
            else: print(f"Error: Failed to get lastrowid for simple transaction: {description}")
        except Exception as e:
            print(f"Error adding simple transaction: {description}: {e}")
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