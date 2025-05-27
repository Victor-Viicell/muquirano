import sys
import re # For parsing description
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QDialogButtonBox, QFormLayout, QDateEdit, QGroupBox,
    QSpinBox, QCheckBox
)
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtCore import Qt, QDate
from src.db import database
from src.db.data_models import TransactionType, User, Transaction
from src.app.analysis import ReportPredictionDialog
from src.app.utils import format_date_for_display

class LoginWindow(QWidget):
    def __init__(self, main_app_controller):
        super().__init__()
        self.main_app_controller = main_app_controller
        self.setWindowTitle("Muquirano - Login")
        self.setMinimumWidth(350)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.username_combo = QComboBox()
        self.load_usernames() # Load usernames into combobox
        form_layout.addRow("Selecionar Usuário:", self.username_combo)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Senha:", self.password_input)
        
        main_layout.addLayout(form_layout)

        # Registration specific inputs (kept separate for now)
        registration_group = QGroupBox("Novo Registro")
        registration_form_layout = QFormLayout()
        self.new_username_input = QLineEdit()
        self.new_username_input.setPlaceholderText("Digite o nome para novo usuário")
        registration_form_layout.addRow("Novo Usuário:", self.new_username_input)
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Digite a senha para novo usuário")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        registration_form_layout.addRow("Nova Senha:", self.new_password_input)
        self.register_button = QPushButton("Registrar Novo Usuário")
        self.register_button.clicked.connect(self.handle_register)
        registration_form_layout.addWidget(self.register_button)
        registration_group.setLayout(registration_form_layout)


        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        button_layout.addWidget(self.login_button)

        # self.register_button = QPushButton("Registrar") # Original register button
        # self.register_button.clicked.connect(self.handle_register)
        # button_layout.addWidget(self.register_button)

        main_layout.addLayout(button_layout)
        main_layout.addWidget(registration_group) # Add registration group to layout
        self.setLayout(main_layout)
        
        self.username_combo.setFocus()

    def load_usernames(self):
        self.username_combo.clear()
        usernames = database.get_all_usernames()
        if usernames:
            self.username_combo.addItems(usernames)
        else:
            self.username_combo.addItem("Nenhum usuário registrado")
            self.username_combo.setEnabled(False)
            self.login_button.setEnabled(False) # Disable login if no users

    def handle_login(self):
        username = self.username_combo.currentText()
        password = self.password_input.text()

        if self.username_combo.currentIndex() == -1 or username == "Nenhum usuário registrado":
            QMessageBox.warning(self, "Login Falhou", "Por favor, selecione um usuário válido.")
            return

        if not password:
            QMessageBox.warning(self, "Login Falhou", "Senha é obrigatória.")
            return

        user = database.check_user_password(username, password)

        if user:
            self.main_app_controller.show_main_window(user)
            self.close()
        else:
            QMessageBox.warning(self, "Login Falhou", "Usuário ou senha inválidos.")
            self.password_input.clear()
            self.password_input.setFocus()


    def handle_register(self):
        username = self.new_username_input.text().strip()
        password = self.new_password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Registro Falhou", "Nome de usuário e senha não podem estar vazios.")
            return

        if len(password) < 4:
            QMessageBox.warning(self, "Registro Falhou", "A senha deve ter pelo menos 4 caracteres.")
            return

        user = database.add_user(username, password)
        if user:
            QMessageBox.information(self, "Registro Bem-sucedido", f"Usuário '{username}' registrado com sucesso! Agora você pode selecioná-lo na lista para fazer login.")
            self.new_username_input.clear()
            self.new_password_input.clear()
            self.load_usernames() # Refresh the usernames combobox
            self.username_combo.setEnabled(True) # Ensure combo is enabled
            self.login_button.setEnabled(True) # Ensure login button is enabled
            # Find and set current item to the newly registered user
            index = self.username_combo.findText(username)
            if index >= 0:
                 self.username_combo.setCurrentIndex(index)
            self.password_input.setFocus()
        else:
            QMessageBox.warning(self, "Registro Falhou", "Nome de usuário já existe ou ocorreu um erro.")

class AddTransactionDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Adicionar Nova Transação")
        self.setMinimumWidth(350)

        self.layout = QFormLayout(self)

        self.type_combo = QComboBox()
        self.type_combo.addItems([TransactionType.INCOME.value.capitalize(), TransactionType.EXPENSE.value.capitalize()])
        self.layout.addRow("Tipo:", self.type_combo)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Ex: 150.00 (valor total ou por ocorrência)")
        double_validator = QDoubleValidator(0.01, 9999999.99, 2)
        double_validator.setNotation(QDoubleValidator.StandardNotation)
        self.amount_input.setValidator(double_validator)
        self.amount_label = QLabel("Valor Total (R$):")
        self.layout.addRow(self.amount_label, self.amount_input)

        self.installments_input = QSpinBox()
        self.installments_input.setMinimum(1)
        self.installments_input.setMaximum(120)
        self.installments_input.setValue(1)
        self.layout.addRow("Número de Parcelas:", self.installments_input)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.layout.addRow("Data (Primeira Ocorrência/Parcela):", self.date_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Ex: Salário, Compra de pão")
        self.layout.addRow("Descrição:", self.description_input)

        # Recurring Transaction Inputs
        self.recurring_checkbox = QCheckBox("Repetir Transação?")
        self.recurring_checkbox.toggled.connect(self.toggle_recurring_inputs)
        self.layout.addRow(self.recurring_checkbox)

        self.recurring_frequency_label = QLabel("Frequência da Repetição:")
        self.recurring_frequency_combo = QComboBox()
        self.recurring_frequency_combo.addItems(["Mensal", "Semanal", "Anual"])
        self.layout.addRow(self.recurring_frequency_label, self.recurring_frequency_combo)

        self.recurring_occurrences_label = QLabel("Gerar para X Ocorrências:")
        self.recurring_occurrences_input = QSpinBox()
        self.recurring_occurrences_input.setMinimum(1)
        self.recurring_occurrences_input.setMaximum(60)
        self.recurring_occurrences_input.setValue(1)
        self.layout.addRow(self.recurring_occurrences_label, self.recurring_occurrences_input)

        # Initially hide recurring inputs
        self.toggle_recurring_inputs(False)

        # Ensure installments and recurring are mutually exclusive in UI logic for now
        self.recurring_checkbox.toggled.connect(lambda checked: self.installments_input.setEnabled(not checked))
        self.installments_input.valueChanged.connect(lambda value: self.recurring_checkbox.setEnabled(value <= 1))

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        
        self.type_combo.setFocus()

    def toggle_recurring_inputs(self, checked):
        self.recurring_frequency_label.setVisible(checked)
        self.recurring_frequency_combo.setVisible(checked)
        self.recurring_occurrences_label.setVisible(checked)
        self.recurring_occurrences_input.setVisible(checked)
        if checked:
            self.amount_label.setText("Valor por Ocorrência (R$):")
            self.installments_input.setValue(1)
            self.installments_input.setEnabled(False)
        else:
            self.amount_label.setText("Valor Total (R$):")
            self.installments_input.setEnabled(True)

    def validate_and_accept(self):
        amount_text = self.amount_input.text().replace(',', '.')
        
        is_recurring = self.recurring_checkbox.isChecked()
        field_name_for_error = "Valor por Ocorrência" if is_recurring else "Valor Total"

        if not amount_text:
            QMessageBox.warning(self, "Erro de Validação", f"O campo '{field_name_for_error}' é obrigatório.")
            self.amount_input.setFocus()
            return

        try:
            total_or_per_occurrence_amount = float(amount_text)
            if total_or_per_occurrence_amount <= 0:
                QMessageBox.warning(self, "Erro de Validação", f"O '{field_name_for_error}' da transação deve ser positivo.")
                self.amount_input.setFocus()
                return
        except ValueError:
            QMessageBox.warning(self, "Erro de Validação", f"'{field_name_for_error}' inválido. Use números (ex: 123.45).")
            self.amount_input.setFocus()
            return

        num_installments = self.installments_input.value()
        date_str_db = self.date_input.date().toString("yyyy-MM-dd") 
        description = self.description_input.text().strip()
        transaction_type_str = self.type_combo.currentText().lower()
        transaction_type = TransactionType(transaction_type_str) 

        if not description:
            QMessageBox.warning(self, "Erro de Validação", "O campo 'Descrição' é obrigatório.")
            self.description_input.setFocus()
            return

        # Parameters for add_transaction
        db_total_amount = total_or_per_occurrence_amount
        db_num_installments = 1
        db_is_recurring = False
        db_recurrence_frequency = None
        db_num_occurrences = 0

        if is_recurring:
            db_is_recurring = True
            db_recurrence_frequency = self.recurring_frequency_combo.currentText().lower()
            db_num_occurrences = self.recurring_occurrences_input.value()
            # total_amount for add_transaction in recurring case is per_occurrence_amount
        elif num_installments > 1:
            db_num_installments = num_installments
            # total_amount for add_transaction in installment case is the grand total
        
        created_transactions = database.add_transaction(
            user_id=self.user_id, 
            type=transaction_type, 
            total_amount=db_total_amount, 
            date_str=date_str_db, 
            description=description,
            num_installments=db_num_installments,
            is_recurring_input=db_is_recurring,
            recurrence_frequency_input=db_recurrence_frequency,
            num_occurrences_to_generate_input=db_num_occurrences
        )

        if created_transactions:
            num_created = len(created_transactions)
            if db_is_recurring and num_created > 0:
                QMessageBox.information(self, "Sucesso", f"{num_created} ocorrências da transação recorrente foram adicionadas!")
            elif db_num_installments > 1 and num_created > 0:
                QMessageBox.information(self, "Sucesso", f"{num_created} parcelas da transação foram adicionadas!")
            elif num_created == 1:
                QMessageBox.information(self, "Sucesso", "Transação adicionada!")
            else: # Should not happen if created_transactions is not empty
                 QMessageBox.information(self, "Sucesso", "Transações processadas.")
            self.accept()
        else:
            QMessageBox.warning(self, "Erro no Banco", "Falha ao adicionar transação(ões) ao banco de dados.")

class EditTransactionDialog(QDialog):
    def __init__(self, transaction: Transaction, parent=None):
        super().__init__(parent)
        self.transaction = transaction
        self.setWindowTitle("Editar Transação")
        self.setMinimumWidth(400) # Increased width for more options

        self.layout = QFormLayout(self)
        self.base_description = self.transaction.description # Store original base description
        self.is_part_of_group = bool(self.transaction.installment_group_id or self.transaction.recurring_group_id)
        self.is_recurring_item = bool(self.transaction.recurring_group_id)

        # Type ComboBox
        self.type_combo = QComboBox()
        self.type_combo.addItems([TransactionType.INCOME.value.capitalize(), TransactionType.EXPENSE.value.capitalize()])
        current_type_index = 0
        if self.transaction.type == TransactionType.EXPENSE:
            current_type_index = 1
        self.type_combo.setCurrentIndex(current_type_index)
        self.layout.addRow("Tipo:", self.type_combo)

        self.amount_input = QLineEdit()
        self.amount_input.setText(f"{self.transaction.amount:.2f}")
        double_validator = QDoubleValidator(0.01, 9999999.99, 2)
        double_validator.setNotation(QDoubleValidator.StandardNotation)
        self.amount_input.setValidator(double_validator)
        # Label depends on whether it's an installment/recurring part
        amount_label_text = "Valor (R$):"
        if self.transaction.installment_group_id:
            amount_label_text = f"Valor da Parcela {self.transaction.installment_number}/{self.transaction.total_installments} (R$):"
        elif self.transaction.is_recurring:
            amount_label_text = f"Valor da Ocorrência {self.transaction.occurrence_number}/{self.transaction.total_occurrences_in_group} (R$):"
        self.layout.addRow(amount_label_text, self.amount_input)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.fromString(self.transaction.date, "yyyy-MM-dd"))
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.layout.addRow("Data:", self.date_input)

        self.description_input = QLineEdit()
        self.base_description_for_edit = self.transaction.description
        if self.is_part_of_group:
            # Try to parse out the base description, e.g., "Salary" from "Salary (1/12)"
            match = re.match(r"^(.*?)\s*\(\d+/\d+\)$", self.transaction.description)
            if match:
                self.base_description_for_edit = match.group(1).strip()
        self.description_input.setText(self.base_description_for_edit)
        self.layout.addRow("Descrição Base:", self.description_input)

        # Options for group edits
        self.apply_desc_to_group_checkbox = QCheckBox("Aplicar alteração de descrição a todo o grupo?")
        if self.is_part_of_group:
            self.layout.addRow(self.apply_desc_to_group_checkbox)
        else:
            self.apply_desc_to_group_checkbox.setVisible(False)

        self.apply_amount_to_future_checkbox = QCheckBox("Aplicar valor a esta e futuras ocorrências recorrentes?")
        if self.is_recurring_item:
            self.layout.addRow(self.apply_amount_to_future_checkbox)
        else:
            self.apply_amount_to_future_checkbox.setVisible(False)

        # Original Info Label (slightly modified)
        if self.is_part_of_group:
            info_text = "Nota: Editando uma transação de grupo. Use as caixas acima para aplicar a todo o grupo."
        else:
            info_text = "Editando transação individual."
        info_label = QLabel(info_text)
        self.layout.addRow(info_label)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        
        self.type_combo.setFocus()

    def validate_and_accept(self):
        amount_text = self.amount_input.text().replace(',', '.')
        
        if not amount_text:
            QMessageBox.warning(self, "Erro de Validação", "O campo 'Valor' é obrigatório.")
            self.amount_input.setFocus()
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                QMessageBox.warning(self, "Erro de Validação", "O valor da transação deve ser positivo.")
                self.amount_input.setFocus()
                return
        except ValueError:
            QMessageBox.warning(self, "Erro de Validação", "Valor inválido. Use números (ex: 123.45).")
            self.amount_input.setFocus()
            return

        date_str_db = self.date_input.date().toString("yyyy-MM-dd") 
        description_to_save = self.description_input.text().strip() # This is the base description
        transaction_type_str = self.type_combo.currentText().lower()
        transaction_type = TransactionType(transaction_type_str)

        if not description_to_save:
            QMessageBox.warning(self, "Erro de Validação", "O campo 'Descrição Base' é obrigatório.")
            self.description_input.setFocus()
            return

        # --- Individual Transaction Update (always happens for the current item) ---
        # Reconstruct the full description for the current item if it was part of a group
        final_description_for_current_item = description_to_save
        if self.transaction.installment_group_id and self.transaction.installment_number and self.transaction.total_installments:
            final_description_for_current_item = f"{description_to_save} ({self.transaction.installment_number}/{self.transaction.total_installments})"
        elif self.transaction.recurring_group_id and self.transaction.occurrence_number and self.transaction.total_occurrences_in_group:
            final_description_for_current_item = f"{description_to_save} ({self.transaction.occurrence_number}/{self.transaction.total_occurrences_in_group})"

        individual_update_success = database.update_transaction(
            self.transaction.id, 
            transaction_type, 
            amount, 
            date_str_db, 
            final_description_for_current_item
        )

        if not individual_update_success:
            QMessageBox.warning(self, "Erro no Banco", "Falha ao atualizar a transação individual selecionada.")
            return # Stop if individual update fails
        
        # --- Group Update Logic ---
        group_update_messages = []

        # 1. Apply description change to group if checked
        if self.is_part_of_group and self.apply_desc_to_group_checkbox.isChecked():
            group_id = self.transaction.installment_group_id or self.transaction.recurring_group_id
            group_field = "installment_group_id" if self.transaction.installment_group_id else "recurring_group_id"
            if group_id:
                desc_success, desc_count = database.update_group_base_description(group_id, group_field, description_to_save)
                if desc_success:
                    group_update_messages.append(f"{desc_count} descrições no grupo atualizadas.")
                else:
                    group_update_messages.append("Falha ao atualizar descrições do grupo.")
        
        # 2. Apply amount change to this and future recurring occurrences if checked
        if self.is_recurring_item and self.apply_amount_to_future_checkbox.isChecked():
            if self.transaction.recurring_group_id:
                # The date from which to update is the date of the current transaction being edited
                amount_success, amount_count = database.update_recurring_group_future_amounts(
                    self.transaction.recurring_group_id, 
                    self.transaction.date, # Use original date of current item as from_date
                    amount
                )
                if amount_success:
                    group_update_messages.append(f"{amount_count} valores recorrentes futuros atualizados.")
                else:
                    group_update_messages.append("Falha ao atualizar valores recorrentes futuros.")

        if group_update_messages:
            QMessageBox.information(self, "Sucesso com Atualizações de Grupo", 
                                    "Transação individual atualizada.\n" + "\n".join(group_update_messages))
        else:
            QMessageBox.information(self, "Sucesso", "Transação atualizada!")
        
        self.accept()

class MainWindow(QWidget):
    def __init__(self, user, main_app_controller):
        super().__init__()
        self.user = user
        self.main_app_controller = main_app_controller
        self.setWindowTitle(f"Muquirano - Olá, {self.user.name}!")
        self.setGeometry(100, 100, 850, 600)

        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        self.welcome_label = QLabel(f"Logado como: <b>{self.user.name}</b>")
        top_layout.addWidget(self.welcome_label, alignment=Qt.AlignLeft)
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.handle_logout)
        top_layout.addWidget(self.logout_button, alignment=Qt.AlignRight)
        main_layout.addLayout(top_layout)

        controls_group = QGroupBox("Filtros e Ordenação")
        controls_layout = QHBoxLayout()

        search_sub_layout = QVBoxLayout()
        search_sub_layout.addWidget(QLabel("Buscar na Descrição:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Termo da busca...")
        self.search_input.returnPressed.connect(self.apply_filters_and_sort)
        search_sub_layout.addWidget(self.search_input)
        controls_layout.addLayout(search_sub_layout)

        filter_type_sub_layout = QVBoxLayout()
        filter_type_sub_layout.addWidget(QLabel("Filtrar por Tipo:"))
        self.filter_type_combo = QComboBox()
        self.filter_type_combo.addItems(["Todas", TransactionType.INCOME.value.capitalize(), TransactionType.EXPENSE.value.capitalize()])
        self.filter_type_combo.currentIndexChanged.connect(self.apply_filters_and_sort)
        filter_type_sub_layout.addWidget(self.filter_type_combo)
        controls_layout.addLayout(filter_type_sub_layout)

        sort_col_sub_layout = QVBoxLayout()
        sort_col_sub_layout.addWidget(QLabel("Ordenar por:"))
        self.sort_column_combo = QComboBox()
        self.sort_column_combo.addItems(["Data", "Descrição", "Valor"])
        self.sort_column_combo.currentIndexChanged.connect(self.apply_filters_and_sort)
        sort_col_sub_layout.addWidget(self.sort_column_combo)
        controls_layout.addLayout(sort_col_sub_layout)

        sort_order_sub_layout = QVBoxLayout()
        sort_order_sub_layout.addWidget(QLabel("Ordem:"))
        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItems(["Decrescente", "Crescente"])
        self.sort_order_combo.currentIndexChanged.connect(self.apply_filters_and_sort)
        sort_order_sub_layout.addWidget(self.sort_order_combo)
        controls_layout.addLayout(sort_order_sub_layout)
        
        self.apply_filters_button = QPushButton("Aplicar Filtros/Busca")
        self.apply_filters_button.clicked.connect(self.apply_filters_and_sort)
        controls_layout.addWidget(self.apply_filters_button, alignment=Qt.AlignBottom)

        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)

        action_button_layout = QHBoxLayout()
        self.add_transaction_button = QPushButton("Nova Transação")
        self.add_transaction_button.clicked.connect(self.open_add_transaction_dialog)
        action_button_layout.addWidget(self.add_transaction_button)

        self.edit_transaction_button = QPushButton("Editar Selecionada")
        self.edit_transaction_button.clicked.connect(self.open_edit_transaction_dialog)
        action_button_layout.addWidget(self.edit_transaction_button)

        self.delete_transaction_button = QPushButton("Remover Selecionada")
        self.delete_transaction_button.clicked.connect(self.handle_delete_transaction)
        action_button_layout.addWidget(self.delete_transaction_button)

        self.delete_group_button = QPushButton("Remover Grupo")
        self.delete_group_button.clicked.connect(self.handle_delete_group)
        action_button_layout.addWidget(self.delete_group_button)

        self.reports_button = QPushButton("Relatórios e Gráficos")
        self.reports_button.clicked.connect(self.open_reports_dialog)
        action_button_layout.addWidget(self.reports_button)

        main_layout.addLayout(action_button_layout)

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels(["ID", "Tipo", "Valor (R$)", "Data", "Descrição"])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transactions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transactions_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.transactions_table)
        
        self.setLayout(main_layout)
        self.apply_filters_and_sort()

    def apply_filters_and_sort(self):
        search_term = self.search_input.text().strip() or None
        
        filter_type_text = self.filter_type_combo.currentText()
        filter_type: TransactionType | None = None
        if filter_type_text == TransactionType.INCOME.value.capitalize():
            filter_type = TransactionType.INCOME
        elif filter_type_text == TransactionType.EXPENSE.value.capitalize():
            filter_type = TransactionType.EXPENSE

        sort_column_text = self.sort_column_combo.currentText().lower()
        db_sort_column_map = {"data": "date", "descrição": "description", "valor": "amount"}
        sort_by = db_sort_column_map.get(sort_column_text, "date")

        sort_order_text = self.sort_order_combo.currentText().lower()
        sort_order = "ASC" if sort_order_text == "crescente" else "DESC"

        self.show_transactions(search_term=search_term, filter_type=filter_type, sort_by=sort_by, sort_order=sort_order)

    def open_add_transaction_dialog(self):
        dialog = AddTransactionDialog(self.user.id, self)
        if dialog.exec(): 
            self.apply_filters_and_sort() 

    def open_edit_transaction_dialog(self):
        selected_rows = self.transactions_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Nenhuma Seleção", "Por favor, selecione uma transação da tabela para editar.")
            return

        selected_row_index = selected_rows[0].row()
        transaction_id_item = self.transactions_table.item(selected_row_index, 0)
        
        if not transaction_id_item:
            QMessageBox.critical(self, "Erro", "Não foi possível obter o ID da transação selecionada para edição.")
            return
        
        transaction_id = int(transaction_id_item.text())
        transaction_to_edit = database.get_transaction_by_id(transaction_id)

        if not transaction_to_edit:
            QMessageBox.critical(self, "Erro", f"Transação com ID {transaction_id} não encontrada no banco de dados.")
            return

        dialog = EditTransactionDialog(transaction_to_edit, self)
        if dialog.exec():
            self.apply_filters_and_sort()

    def handle_delete_transaction(self):
        selected_rows = self.transactions_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Nenhuma Seleção", "Por favor, selecione uma transação da tabela para remover.")
            return

        selected_row_index = selected_rows[0].row()
        transaction_id_item = self.transactions_table.item(selected_row_index, 0)
        
        if not transaction_id_item:
            QMessageBox.critical(self, "Erro", "Não foi possível obter o ID da transação selecionada.")
            return
        
        transaction_id = int(transaction_id_item.text())
        # Fetch the transaction to check if it's part of a group for a more informative message
        transaction_details = database.get_transaction_by_id(transaction_id)
        description_for_confirm = f"transação ID: {transaction_id}"
        if transaction_details and (transaction_details.installment_group_id or transaction_details.is_recurring):
            description_for_confirm = f"transação ID: {transaction_id} (esta é parte de um grupo. Use 'Remover Grupo' para remover todas as transações relacionadas)"


        reply = QMessageBox.question(self, "Confirmar Remoção Individual", 
                                     f"Tem certeza que deseja remover APENAS a {description_for_confirm}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if database.delete_transaction(transaction_id):
                QMessageBox.information(self, "Sucesso", f"Transação ID: {transaction_id} removida com sucesso.")
                self.apply_filters_and_sort()
            else:
                QMessageBox.warning(self, "Erro", f"Falha ao remover a transação ID: {transaction_id}.")

    def handle_delete_group(self):
        selected_rows = self.transactions_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Nenhuma Seleção", "Por favor, selecione uma transação da tabela para identificar o grupo a ser removido.")
            return

        selected_row_index = selected_rows[0].row()
        transaction_id_item = self.transactions_table.item(selected_row_index, 0)
        if not transaction_id_item:
            QMessageBox.critical(self, "Erro", "Não foi possível obter o ID da transação selecionada.")
            return
        transaction_id = int(transaction_id_item.text())

        selected_transaction = database.get_transaction_by_id(transaction_id)
        if not selected_transaction:
            QMessageBox.critical(self, "Erro", f"Transação com ID {transaction_id} não encontrada.")
            return

        group_id_to_delete = None
        group_field_name = None
        group_type_message = ""
        num_in_group_approx = 0 # For message, actual count comes from delete function

        if selected_transaction.installment_group_id:
            group_id_to_delete = selected_transaction.installment_group_id
            group_field_name = "installment_group_id"
            group_type_message = f"grupo de parcelamento (originalmente {selected_transaction.total_installments} parcelas)"
            num_in_group_approx = selected_transaction.total_installments or 0
        elif selected_transaction.recurring_group_id:
            group_id_to_delete = selected_transaction.recurring_group_id
            group_field_name = "recurring_group_id"
            group_type_message = f"grupo de recorrência (originalmente {selected_transaction.total_occurrences_in_group} ocorrências)"
            num_in_group_approx = selected_transaction.total_occurrences_in_group or 0
        else:
            QMessageBox.information(self, "Nenhum Grupo", "A transação selecionada não pertence a um grupo de parcelamento ou recorrência.")
            return

        if not group_id_to_delete: # Should not happen if logic above is correct
            QMessageBox.warning(self, "Erro", "Não foi possível identificar o ID do grupo.")
            return

        reply = QMessageBox.question(self, f"Confirmar Remoção de Grupo", 
                                     f"Tem certeza que deseja remover TODAS as transações do {group_type_message} associado à transação ID {transaction_id}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            success, num_deleted = database.delete_transaction_group(group_id_to_delete, group_field_name)
            if success:
                QMessageBox.information(self, "Sucesso", f"{num_deleted} transações do grupo foram removidas com sucesso.")
                self.apply_filters_and_sort()
            else:
                QMessageBox.warning(self, "Erro", f"Falha ao remover o grupo de transações.")
        
    def open_reports_dialog(self):
        dialog = ReportPredictionDialog(user_id=self.user.id, parent=self)
        dialog.exec()

    def show_transactions(self, search_term: str | None = None, 
                          filter_type: TransactionType | None = None, 
                          sort_by: str = "date", 
                          sort_order: str = "DESC"):
        self.transactions_table.setRowCount(0) 
        transactions = database.get_transactions_by_user(self.user.id, 
                                                       search_term=search_term, 
                                                       filter_type=filter_type, 
                                                       sort_by=sort_by, 
                                                       sort_order=sort_order)
        for row_num, t in enumerate(transactions):
            self.transactions_table.insertRow(row_num)
            self.transactions_table.setItem(row_num, 0, QTableWidgetItem(str(t.id)))
            
            item_type = QTableWidgetItem(t.type.value.capitalize())
            if t.type == TransactionType.INCOME:
                item_type.setForeground(Qt.darkGreen)
            else:
                item_type.setForeground(Qt.red)
            self.transactions_table.setItem(row_num, 1, item_type)
            self.transactions_table.setItem(row_num, 2, QTableWidgetItem(f"{t.amount:.2f}"))
            self.transactions_table.setItem(row_num, 3, QTableWidgetItem(format_date_for_display(t.date)))
            self.transactions_table.setItem(row_num, 4, QTableWidgetItem(t.description))
            
    def handle_logout(self):
        reply = QMessageBox.question(self, "Logout", "Tem certeza que deseja sair?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.main_app_controller.show_login_window()
            self.close()

class MainAppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        try:
            if "Fusion" in QApplication.style().objectName() or "WindowsVista" in QApplication.style().objectName():
                 self.app.setStyle(QApplication.style())
            elif "Fusion" in QApplication.styleFactoryKeys():
                 self.app.setStyle("Fusion")
        except Exception:
            pass 

        self.login_window = None
        self.main_window = None
        database.initialize_db()

    def start(self):
        self.show_login_window()
        sys.exit(self.app.exec())

    def show_login_window(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        self.login_window = LoginWindow(self)
        self.login_window.show()

    def show_main_window(self, user: User):
        if self.login_window:
            self.login_window.close()
            self.login_window = None
        self.main_window = MainWindow(user, self)
        self.main_window.show()

if __name__ == '__main__':
    controller = MainAppController()
    controller.start() 