"""
Sistema Muquirano - Interface Gráfica do Usuário

Este módulo contém todas as classes e componentes da interface gráfica do sistema
de controle financeiro Muquirano. Utiliza PySide6 para criar uma interface moderna
e intuitiva para gerenciamento de transações financeiras.

Principais componentes:
- LoginWindow: Tela de autenticação de usuário
- MainWindow: Janela principal com listagem de transações
- AddTransactionDialog: Diálogo para adicionar novas transações
- EditTransactionDialog: Diálogo para editar transações existentes
- MainAppController: Controlador principal da aplicação

Autor: Viicell
Data: 2025
"""

import sys
import re # Para análise de descrições
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QDialogButtonBox, QFormLayout, QDateEdit, QGroupBox,
    QSpinBox, QCheckBox, QFrame, QScrollArea, QSplitter
)
from PySide6.QtGui import QDoubleValidator, QIntValidator, QFont, QIcon, QPalette, QPixmap
from PySide6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve
from src.db import database
from src.db.data_models import TransactionType, User, Transaction
from src.app.analysis import ReportPredictionDialog
from src.app.utils import format_date_for_display

# Folha de estilo moderna para a aplicação
MODERN_STYLESHEET = """
/* Estilização Base da Aplicação */
QApplication {
    font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
    font-size: 9pt;
}

/* Estilização da Janela Principal */
QWidget {
    background-color: #f8f9fa;
    color: #2c3e50;
}

/* Estilização dos Botões */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 9pt;
    min-height: 16px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #21618c;
}

QPushButton:disabled {
    background-color: #bdc3c7;
    color: #7f8c8d;
}

/* Variante de Botão Primário */
QPushButton#primary {
    background-color: #2ecc71;
}

QPushButton#primary:hover {
    background-color: #27ae60;
}

/* Variante de Botão de Perigo */
QPushButton#danger {
    background-color: #e74c3c;
}

QPushButton#danger:hover {
    background-color: #c0392b;
}

/* Variante de Botão Secundário */
QPushButton#secondary {
    background-color: #95a5a6;
}

QPushButton#secondary:hover {
    background-color: #7f8c8d;
}

/* Estilização dos Campos de Entrada */
QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox {
    background-color: white;
    border: 2px solid #ecf0f1;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 9pt;
    min-height: 20px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
    border-color: #3498db;
    outline: none;
}

QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QDateEdit:hover, QComboBox:hover {
    border-color: #bdc3c7;
}

/* Menu Suspenso do ComboBox */
QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #7f8c8d;
    margin-right: 5px;
}

/* Estilização da Tabela */
QTableWidget {
    background-color: white;
    border: 1px solid #ecf0f1;
    border-radius: 8px;
    gridline-color: #ecf0f1;
    selection-background-color: #ebf3fd;
    alternate-background-color: #f8f9fa;
    font-size: 9pt;
}

QTableWidget::item {
    padding: 15px 8px;  /* Padding aumentado de 12px para 15px para melhor visibilidade */
    border: none;
    min-height: 25px;   /* Altura mínima adicionada para garantir que o conteúdo seja totalmente visível */
}

QTableWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QHeaderView::section {
    background-color: #34495e;
    color: white;
    padding: 12px 8px;
    border: none;
    font-weight: 600;
    font-size: 9pt;
}

QHeaderView::section:first {
    border-top-left-radius: 8px;
}

QHeaderView::section:last {
    border-top-right-radius: 8px;
}

/* Estilização do Group Box */
QGroupBox {
    background-color: white;
    border: 1px solid #ecf0f1;
    border-radius: 8px;
    margin-top: 20px;
    padding-top: 15px;
    font-weight: 600;
    font-size: 10pt;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 5px 10px;
    background-color: #3498db;
    color: white;
    border-radius: 4px;
}

/* Estilização dos Labels */
QLabel {
    color: #2c3e50;
    font-size: 9pt;
}

QLabel#title {
    font-size: 18pt;
    font-weight: 700;
    color: #2c3e50;
    margin: 10px 0;
}

QLabel#subtitle {
    font-size: 12pt;
    font-weight: 600;
    color: #34495e;
    margin: 5px 0;
}

QLabel#welcome {
    font-size: 11pt;
    font-weight: 600;
    color: #27ae60;
}

/* Estilização do Checkbox */
QCheckBox {
    spacing: 8px;
    font-size: 9pt;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #bdc3c7;
    border-radius: 3px;
    background-color: white;
}

QCheckBox::indicator:checked {
    background-color: #3498db;
    border-color: #3498db;
}

QCheckBox::indicator:checked:hover {
    background-color: #2980b9;
    border-color: #2980b9;
}

/* Estilização de Diálogos */
QDialog {
    background-color: #f8f9fa;
    border-radius: 12px;
}

/* Estilização de Caixas de Mensagem */
QMessageBox {
    background-color: white;
    color: #2c3e50;
}

QMessageBox QPushButton {
    min-width: 80px;
    margin: 4px;
}

/* Área de Rolagem */
QScrollArea {
    border: none;
    background-color: transparent;
}

/* Estilização de Frames */
QFrame#card {
    background-color: white;
    border: 1px solid #ecf0f1;
    border-radius: 8px;
    margin: 4px;
    padding: 8px;
}

/* Indicadores de Status */
QLabel#income {
    color: #27ae60;
    font-weight: 600;
}

QLabel#expense {
    color: #e74c3c;
    font-weight: 600;
}
"""

class LoginWindow(QWidget):
    """
    Janela de Login do Sistema Muquirano
    
    Esta classe representa a tela inicial do sistema onde os usuários podem
    fazer login com credenciais existentes ou criar novos usuários.
    
    Funcionalidades:
    - Autenticação de usuário existente
    - Registro de novo usuário com validação de senha
    - Interface moderna com formulários separados
    - Validação de entrada de dados
    
    Attributes:
        main_app_controller: Referência ao controlador principal da aplicação
        username_combo: ComboBox para seleção de usuário existente
        password_input: Campo de entrada para senha
        new_username_input: Campo para nome de novo usuário
        new_password_input: Campo para senha de novo usuário
    """
    
    def __init__(self, main_app_controller):
        """
        Inicializa a janela de login
        
        Args:
            main_app_controller: Instância do controlador principal da aplicação
        """
        super().__init__()
        self.main_app_controller = main_app_controller
        self.setWindowTitle("Muquirano - Sistema de Controle Financeiro")
        self.setFixedSize(480, 650)
        self.setStyleSheet(MODERN_STYLESHEET)

        # Container principal com layout moderno
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Seção do Cabeçalho
        header_frame = QFrame()
        header_frame.setObjectName("card")
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("Muquirano")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Sistema de Controle Financeiro")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        main_layout.addWidget(header_frame)

        # Seção de Login
        login_group = QGroupBox("Login")
        login_layout = QFormLayout(login_group)
        login_layout.setSpacing(15)  # Corresponde ao espaçamento da seção de registro
        login_layout.setContentsMargins(20, 30, 20, 20)

        # Seleção de usuário
        user_label = QLabel("Usuário:")
        user_label.setStyleSheet("font-weight: 600;")
        self.username_combo = QComboBox()
        self.username_combo.setMinimumHeight(40)
        login_layout.addRow(user_label, self.username_combo)

        # Campo de entrada de senha
        password_label = QLabel("Senha:")
        password_label.setStyleSheet("font-weight: 600;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        login_layout.addRow(password_label, self.password_input)

        # Botão de login
        self.login_button = QPushButton("Entrar")
        self.login_button.setObjectName("primary")
        self.login_button.setMinimumHeight(45)
        self.login_button.clicked.connect(self.handle_login)
        login_layout.addRow("", self.login_button)

        main_layout.addWidget(login_group)

        # Seção de Registro
        registration_group = QGroupBox("Novo Usuário")
        registration_layout = QFormLayout(registration_group)
        registration_layout.setSpacing(15)
        registration_layout.setContentsMargins(20, 30, 20, 20)

        # Novo nome de usuário
        new_user_label = QLabel("Nome de Usuário:")
        new_user_label.setStyleSheet("font-weight: 600;")
        self.new_username_input = QLineEdit()
        self.new_username_input.setPlaceholderText("Digite o nome do novo usuário")
        self.new_username_input.setMinimumHeight(40)
        registration_layout.addRow(new_user_label, self.new_username_input)

        # Nova senha
        new_password_label = QLabel("Senha:")
        new_password_label.setStyleSheet("font-weight: 600;")
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Digite a senha (mín. 4 caracteres)")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setMinimumHeight(40)
        registration_layout.addRow(new_password_label, self.new_password_input)

        # Botão de registro
        self.register_button = QPushButton("Registrar")
        self.register_button.setObjectName("secondary")
        self.register_button.setMinimumHeight(45)
        self.register_button.clicked.connect(self.handle_register)
        registration_layout.addRow("", self.register_button)

        main_layout.addWidget(registration_group)

        # Carrega nomes de usuário após todos os elementos da UI serem criados
        self.load_usernames()

        # Define foco e manipulação da tecla Enter
        self.username_combo.setFocus()
        self.password_input.returnPressed.connect(self.handle_login)
        self.new_password_input.returnPressed.connect(self.handle_register)

    def load_usernames(self):
        """
        Carrega a lista de nomes de usuário disponíveis do banco de dados
        
        Atualiza o ComboBox com todos os usuários registrados no sistema.
        Se não houver usuários, desabilita o botão de login.
        """
        self.username_combo.clear()
        usernames = database.get_all_usernames()
        if usernames:
            self.username_combo.addItems(usernames)
        else:
            self.username_combo.addItem("Nenhum usuário registrado")
            self.username_combo.setEnabled(False)
            self.login_button.setEnabled(False)

    def handle_login(self):
        """
        Processa a tentativa de login do usuário
        
        Valida as credenciais fornecidas e redireciona para a janela principal
        se a autenticação for bem-sucedida. Exibe mensagens de erro apropriadas
        em caso de falha na validação ou autenticação.
        """
        username = self.username_combo.currentText()
        password = self.password_input.text()

        if self.username_combo.currentIndex() == -1 or username == "Nenhum usuário registrado":
            self.show_message("Erro de Login", "Por favor, selecione um usuário válido.", "warning")
            return

        if not password:
            self.show_message("Erro de Login", "Senha é obrigatória.", "warning")
            return

        user = database.check_user_password(username, password)

        if user:
            self.main_app_controller.show_main_window(user)
            self.close()
        else:
            self.show_message("Erro de Login", "Usuário ou senha inválidos.", "warning")
            self.password_input.clear()
            self.password_input.setFocus()

    def handle_register(self):
        """
        Processa o registro de um novo usuário
        
        Valida os dados de entrada (nome de usuário e senha), cria um novo
        usuário no banco de dados e atualiza a interface. Inclui validação
        de senha mínima e verificação de duplicidade de nome de usuário.
        """
        username = self.new_username_input.text().strip()
        password = self.new_password_input.text()

        if not username or not password:
            self.show_message("Erro de Registro", "Nome de usuário e senha não podem estar vazios.", "warning")
            return

        if len(password) < 4:
            self.show_message("Erro de Registro", "A senha deve ter pelo menos 4 caracteres.", "warning")
            return

        user = database.add_user(username, password)
        if user:
            self.show_message("Sucesso", f"Usuário '{username}' registrado com sucesso!", "info")
            self.new_username_input.clear()
            self.new_password_input.clear()
            self.load_usernames()
            self.username_combo.setEnabled(True)
            self.login_button.setEnabled(True)
            
            index = self.username_combo.findText(username)
            if index >= 0:
                self.username_combo.setCurrentIndex(index)
            self.password_input.setFocus()
        else:
            self.show_message("Erro de Registro", "Nome de usuário já existe ou ocorreu um erro.", "warning")

    def show_message(self, title, message, msg_type="info"):
        """
        Exibe uma caixa de mensagem para o usuário
        
        Args:
            title (str): Título da mensagem
            message (str): Texto da mensagem
            msg_type (str): Tipo da mensagem ('info' ou 'warning')
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        if msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == "info":
            msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()

class AddTransactionDialog(QDialog):
    """
    Diálogo para Adicionar Nova Transação
    
    Esta classe fornece uma interface para adicionar novas transações financeiras
    ao sistema. Suporta transações simples, parceladas e recorrentes com validação
    completa de dados de entrada.
    
    Funcionalidades:
    - Transações de receita e despesa
    - Parcelamento em múltiplas parcelas
    - Transações recorrentes (mensal, semanal, anual)
    - Validação de campos obrigatórios
    - Cálculo automático de datas para parcelas e recorrências
    
    Attributes:
        user_id (int): ID do usuário proprietário da transação
        type_combo: ComboBox para seleção do tipo de transação
        amount_input: Campo para entrada do valor
        installments_input: SpinBox para número de parcelas
        date_input: DateEdit para seleção da data
        description_input: Campo para descrição da transação
        recurring_checkbox: Checkbox para ativar modo recorrente
        recurring_options: Frame com opções de recorrência
    """
    
    def __init__(self, user_id, parent=None):
        """
        Inicializa o diálogo de nova transação
        
        Args:
            user_id (int): ID do usuário para o qual a transação será criada
            parent: Widget pai do diálogo
        """
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Nova Transação")
        self.setFixedSize(500, 700)
        self.setStyleSheet(MODERN_STYLESHEET)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Cabeçalho
        header_frame = QFrame()
        header_frame.setObjectName("card")
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("Adicionar Nova Transação")
        title.setObjectName("subtitle")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        main_layout.addWidget(header_frame)

        # Container do formulário
        form_frame = QFrame()
        form_frame.setObjectName("card")
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        # Tipo de transação
        type_label = QLabel("Tipo de Transação:")
        type_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["💰 " + TransactionType.INCOME.value.capitalize(), "💸 " + TransactionType.EXPENSE.value.capitalize()])
        self.type_combo.setMinimumHeight(40)
        form_layout.addRow(type_label, self.type_combo)

        # Campo de entrada de valor
        self.amount_label = QLabel("Valor Total (R$):")
        self.amount_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Ex: 150.00")
        self.amount_input.setMinimumHeight(40)
        double_validator = QDoubleValidator(0.01, 9999999.99, 2)
        double_validator.setNotation(QDoubleValidator.StandardNotation)
        self.amount_input.setValidator(double_validator)
        form_layout.addRow(self.amount_label, self.amount_input)

        # Parcelas
        installments_label = QLabel("Número de Parcelas:")
        installments_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        self.installments_input = QSpinBox()
        self.installments_input.setMinimum(1)
        self.installments_input.setMaximum(120)
        self.installments_input.setValue(1)
        self.installments_input.setMinimumHeight(40)
        form_layout.addRow(installments_label, self.installments_input)

        # Campo de entrada de data
        date_label = QLabel("Data (Primeira Ocorrência):")
        date_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setMinimumHeight(40)
        form_layout.addRow(date_label, self.date_input)

        # Descrição
        description_label = QLabel("Descrição:")
        description_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Ex: Salário, Compra de mercado")
        self.description_input.setMinimumHeight(40)
        form_layout.addRow(description_label, self.description_input)

        main_layout.addWidget(form_frame)

        # Seção de recorrência
        recurring_frame = QFrame()
        recurring_frame.setObjectName("card")
        recurring_layout = QVBoxLayout(recurring_frame)
        recurring_layout.setContentsMargins(20, 20, 20, 20)

        self.recurring_checkbox = QCheckBox("🔄 Configurar como Transação Recorrente")
        self.recurring_checkbox.setStyleSheet("font-weight: 600; font-size: 10pt;")
        self.recurring_checkbox.toggled.connect(self.toggle_recurring_inputs)
        recurring_layout.addWidget(self.recurring_checkbox)

        # Opções de recorrência (inicialmente ocultas)
        self.recurring_options = QFrame()
        recurring_options_layout = QFormLayout(self.recurring_options)
        recurring_options_layout.setSpacing(10)

        self.recurring_frequency_label = QLabel("Frequência:")
        self.recurring_frequency_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        self.recurring_frequency_combo = QComboBox()
        self.recurring_frequency_combo.addItems(["📅 Mensal", "📆 Semanal", "🗓️ Anual"])
        self.recurring_frequency_combo.setMinimumHeight(35)
        recurring_options_layout.addRow(self.recurring_frequency_label, self.recurring_frequency_combo)

        self.recurring_occurrences_label = QLabel("Número de Ocorrências:")
        self.recurring_occurrences_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        self.recurring_occurrences_input = QSpinBox()
        self.recurring_occurrences_input.setMinimum(1)
        self.recurring_occurrences_input.setMaximum(60)
        self.recurring_occurrences_input.setValue(12)
        self.recurring_occurrences_input.setMinimumHeight(35)
        recurring_options_layout.addRow(self.recurring_occurrences_label, self.recurring_occurrences_input)

        recurring_layout.addWidget(self.recurring_options)
        self.toggle_recurring_inputs(False)

        main_layout.addWidget(recurring_frame)

        # Botões
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("secondary")
        cancel_button.setMinimumHeight(45)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        save_button = QPushButton("💾 Salvar Transação")
        save_button.setObjectName("primary")
        save_button.setMinimumHeight(45)
        save_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(save_button)

        main_layout.addLayout(button_layout)

        # Conecta exclusividade mútua
        self.recurring_checkbox.toggled.connect(lambda checked: self.installments_input.setEnabled(not checked))
        self.installments_input.valueChanged.connect(lambda value: self.recurring_checkbox.setEnabled(value <= 1))

        self.type_combo.setFocus()

    def toggle_recurring_inputs(self, checked):
        """
        Alterna a visibilidade e estado dos controles de recorrência
        
        Args:
            checked (bool): Estado do checkbox de recorrência
        """
        self.recurring_options.setVisible(checked)
        if checked:
            self.amount_label.setText("Valor por Ocorrência (R$):")
            self.installments_input.setValue(1)
            self.installments_input.setEnabled(False)
        else:
            self.amount_label.setText("Valor Total (R$):")
            self.installments_input.setEnabled(True)

    def validate_and_accept(self):
        """
        Valida os dados do formulário e processa a criação da transação
        
        Executa validação completa dos campos, calcula valores para parcelas
        ou recorrências, e chama a função do banco de dados para criar as
        transações. Exibe mensagens de sucesso ou erro conforme apropriado.
        """
        amount_text = self.amount_input.text().replace(',', '.')
        
        is_recurring = self.recurring_checkbox.isChecked()
        field_name_for_error = "Valor por Ocorrência" if is_recurring else "Valor Total"

        if not amount_text:
            self.show_message("Erro de Validação", f"O campo '{field_name_for_error}' é obrigatório.", "warning")
            self.amount_input.setFocus()
            return

        try:
            total_or_per_occurrence_amount = float(amount_text)
            if total_or_per_occurrence_amount <= 0:
                self.show_message("Erro de Validação", f"O '{field_name_for_error}' da transação deve ser positivo.", "warning")
                self.amount_input.setFocus()
                return
        except ValueError:
            self.show_message("Erro de Validação", f"'{field_name_for_error}' inválido. Use números (ex: 123.45).", "warning")
            self.amount_input.setFocus()
            return

        num_installments = self.installments_input.value()
        date_str_db = self.date_input.date().toString("yyyy-MM-dd") 
        description = self.description_input.text().strip()
        transaction_type_str = self.type_combo.currentText().split(" ", 1)[1].lower()  # Remove emoji
        transaction_type = TransactionType(transaction_type_str) 

        if not description:
            self.show_message("Erro de Validação", "O campo 'Descrição' é obrigatório.", "warning")
            self.description_input.setFocus()
            return

        # Parâmetros para add_transaction
        db_total_amount = total_or_per_occurrence_amount
        db_num_installments = 1
        db_is_recurring = False
        db_recurrence_frequency = None
        db_num_occurrences = 0

        if is_recurring:
            db_is_recurring = True
            freq_text = self.recurring_frequency_combo.currentText().split(" ", 1)[1].lower()  # Remove emoji
            # Mapeia texto português para frequência do banco de dados
            db_recurrence_frequency = freq_text  # Agora será "mensal", "semanal" ou "anual"
            db_num_occurrences = self.recurring_occurrences_input.value()
        elif num_installments > 1:
            db_num_installments = num_installments
        
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
                self.show_message("Sucesso", f"✅ {num_created} ocorrências da transação recorrente foram adicionadas!", "info")
            elif db_num_installments > 1 and num_created > 0:
                self.show_message("Sucesso", f"✅ {num_created} parcelas da transação foram adicionadas!", "info")
            elif num_created == 1:
                self.show_message("Sucesso", "✅ Transação adicionada com sucesso!", "info")
            else:
                self.show_message("Sucesso", "✅ Transações processadas.", "info")
            self.accept()
        else:
            self.show_message("Erro", "❌ Falha ao adicionar transação(ões) ao banco de dados.", "warning")

    def show_message(self, title, message, msg_type="info"):
        """
        Exibe uma caixa de mensagem para o usuário
        
        Args:
            title (str): Título da mensagem
            message (str): Texto da mensagem
            msg_type (str): Tipo da mensagem ('info' ou 'warning')
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        if msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == "info":
            msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()

class EditTransactionDialog(QDialog):
    def __init__(self, transaction: Transaction, parent=None):
        super().__init__(parent)
        self.transaction = transaction
        self.setWindowTitle("Editar Transação")
        self.setFixedSize(550, 650)
        self.setStyleSheet(MODERN_STYLESHEET)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header with transaction info
        header_frame = QFrame()
        header_frame.setObjectName("card")
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("✏️ Editar Transação")
        title.setObjectName("subtitle")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        # Transaction ID info
        id_info = QLabel(f"ID: {self.transaction.id}")
        id_info.setAlignment(Qt.AlignCenter)
        id_info.setStyleSheet("color: #7f8c8d; font-size: 8pt;")
        header_layout.addWidget(id_info)
        
        main_layout.addWidget(header_frame)

        self.base_description = self.transaction.description
        self.is_part_of_group = bool(self.transaction.installment_group_id or self.transaction.recurring_group_id)
        self.is_recurring_item = bool(self.transaction.recurring_group_id)

        # Main form
        form_frame = QFrame()
        form_frame.setObjectName("card")
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        # Type ComboBox
        type_label = QLabel("Tipo:")
        type_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["💰 " + TransactionType.INCOME.value.capitalize(), "💸 " + TransactionType.EXPENSE.value.capitalize()])
        self.type_combo.setMinimumHeight(40)
        current_type_index = 0 if self.transaction.type == TransactionType.INCOME else 1
        self.type_combo.setCurrentIndex(current_type_index)
        form_layout.addRow(type_label, self.type_combo)

        # Amount input
        amount_label_text = "Valor (R$):"
        if self.transaction.installment_group_id:
            amount_label_text = f"Valor da Parcela {self.transaction.installment_number}/{self.transaction.total_installments} (R$):"
        elif self.transaction.is_recurring:
            amount_label_text = f"Valor da Ocorrência {self.transaction.occurrence_number}/{self.transaction.total_occurrences_in_group} (R$):"
        
        amount_label = QLabel(amount_label_text)
        amount_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        self.amount_input = QLineEdit()
        self.amount_input.setText(f"{self.transaction.amount:.2f}")
        self.amount_input.setMinimumHeight(40)
        double_validator = QDoubleValidator(0.01, 9999999.99, 2)
        double_validator.setNotation(QDoubleValidator.StandardNotation)
        self.amount_input.setValidator(double_validator)
        form_layout.addRow(amount_label, self.amount_input)

        # Date input
        date_label = QLabel("Data:")
        date_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.fromString(self.transaction.date, "yyyy-MM-dd"))
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setMinimumHeight(40)
        form_layout.addRow(date_label, self.date_input)

        # Description
        description_label = QLabel("Descrição Base:")
        description_label.setStyleSheet("font-weight: 600; color: #2c3e50;")
        self.description_input = QLineEdit()
        self.description_input.setMinimumHeight(40)
        
        self.base_description_for_edit = self.transaction.description
        if self.is_part_of_group:
            # Try to parse out the base description
            match = re.match(r"^(.*?)\s*\(\d+/\d+\)$", self.transaction.description)
            if match:
                self.base_description_for_edit = match.group(1).strip()
        self.description_input.setText(self.base_description_for_edit)
        form_layout.addRow(description_label, self.description_input)

        main_layout.addWidget(form_frame)

        # Group options (if applicable)
        if self.is_part_of_group or self.is_recurring_item:
            options_frame = QFrame()
            options_frame.setObjectName("card")
            options_layout = QVBoxLayout(options_frame)
            options_layout.setContentsMargins(20, 20, 20, 20)
            options_layout.setSpacing(15)
            
            options_title = QLabel("🔧 Opções de Grupo")
            options_title.setStyleSheet("font-weight: 600; font-size: 11pt; color: #34495e;")
            options_layout.addWidget(options_title)

            if self.is_part_of_group:
                self.apply_desc_to_group_checkbox = QCheckBox("📝 Aplicar alteração de descrição a todo o grupo")
                self.apply_desc_to_group_checkbox.setStyleSheet("font-size: 9pt;")
                options_layout.addWidget(self.apply_desc_to_group_checkbox)
            else:
                self.apply_desc_to_group_checkbox = QCheckBox()
                self.apply_desc_to_group_checkbox.setVisible(False)

            if self.is_recurring_item:
                self.apply_amount_to_future_checkbox = QCheckBox("🔄 Aplicar valor a esta e futuras ocorrências recorrentes")
                self.apply_amount_to_future_checkbox.setStyleSheet("font-size: 9pt;")
                options_layout.addWidget(self.apply_amount_to_future_checkbox)
            else:
                self.apply_amount_to_future_checkbox = QCheckBox()
                self.apply_amount_to_future_checkbox.setVisible(False)

            # Info text
            if self.is_part_of_group:
                info_text = "💡 Esta transação faz parte de um grupo. Use as opções acima para aplicar alterações a todo o grupo."
            else:
                info_text = "💡 Editando transação individual."
            
            info_label = QLabel(info_text)
            info_label.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 8pt;")
            info_label.setWordWrap(True)
            options_layout.addWidget(info_label)

            main_layout.addWidget(options_frame)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("secondary")
        cancel_button.setMinimumHeight(45)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        save_button = QPushButton("💾 Salvar Alterações")
        save_button.setObjectName("primary")
        save_button.setMinimumHeight(45)
        save_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(save_button)

        main_layout.addLayout(button_layout)
        
        self.type_combo.setFocus()

    def validate_and_accept(self):
        amount_text = self.amount_input.text().replace(',', '.')
        
        if not amount_text:
            self.show_message("Erro de Validação", "O campo 'Valor' é obrigatório.", "warning")
            self.amount_input.setFocus()
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                self.show_message("Erro de Validação", "O valor da transação deve ser positivo.", "warning")
                self.amount_input.setFocus()
                return
        except ValueError:
            self.show_message("Erro de Validação", "Valor inválido. Use números (ex: 123.45).", "warning")
            self.amount_input.setFocus()
            return

        date_str_db = self.date_input.date().toString("yyyy-MM-dd") 
        description_to_save = self.description_input.text().strip()
        transaction_type_str = self.type_combo.currentText().split(" ", 1)[1].lower()  # Remove emoji
        transaction_type = TransactionType(transaction_type_str)

        if not description_to_save:
            self.show_message("Erro de Validação", "O campo 'Descrição Base' é obrigatório.", "warning")
            self.description_input.setFocus()
            return

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
            self.show_message("Erro", "Falha ao atualizar a transação individual selecionada.", "warning")
            return
        
        # Group Update Logic
        group_update_messages = []

        # Apply description change to group if checked
        if self.is_part_of_group and self.apply_desc_to_group_checkbox.isChecked():
            group_id = self.transaction.installment_group_id or self.transaction.recurring_group_id
            group_field = "installment_group_id" if self.transaction.installment_group_id else "recurring_group_id"
            if group_id:
                desc_success, desc_count = database.update_group_base_description(group_id, group_field, description_to_save)
                if desc_success:
                    group_update_messages.append(f"✅ {desc_count} descrições no grupo atualizadas.")
                else:
                    group_update_messages.append("❌ Falha ao atualizar descrições do grupo.")
        
        # Apply amount change to this and future recurring occurrences if checked
        if self.is_recurring_item and self.apply_amount_to_future_checkbox.isChecked():
            if self.transaction.recurring_group_id:
                amount_success, amount_count = database.update_recurring_group_future_amounts(
                    self.transaction.recurring_group_id, 
                    self.transaction.date,
                    amount
                )
                if amount_success:
                    group_update_messages.append(f"✅ {amount_count} valores recorrentes futuros atualizados.")
                else:
                    group_update_messages.append("❌ Falha ao atualizar valores recorrentes futuros.")

        if group_update_messages:
            message = "✅ Transação individual atualizada.\n\n" + "\n".join(group_update_messages)
            self.show_message("Sucesso com Atualizações de Grupo", message, "info")
        else:
            self.show_message("Sucesso", "✅ Transação atualizada com sucesso!", "info")
        
        self.accept()

    def show_message(self, title, message, msg_type="info"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        if msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == "info":
            msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()

class MainWindow(QWidget):
    def __init__(self, user, main_app_controller):
        super().__init__()
        self.user = user
        self.main_app_controller = main_app_controller
        self.setWindowTitle(f"Muquirano - {self.user.name}")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(MODERN_STYLESHEET)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        # Welcome section
        welcome_section = QVBoxLayout()
        welcome_title = QLabel("💰 Muquirano")
        welcome_title.setObjectName("title")
        welcome_title.setStyleSheet("color: #2c3e50; font-size: 16pt;")
        welcome_section.addWidget(welcome_title)
        
        self.welcome_label = QLabel(f"Olá, {self.user.name}! 👋")
        self.welcome_label.setObjectName("welcome")
        welcome_section.addWidget(self.welcome_label)
        
        header_layout.addLayout(welcome_section)
        header_layout.addStretch()

        # Logout button
        self.logout_button = QPushButton("🚪 Sair")
        self.logout_button.setObjectName("secondary")
        self.logout_button.setMinimumHeight(40)
        self.logout_button.setFixedWidth(100)
        self.logout_button.clicked.connect(self.handle_logout)
        header_layout.addWidget(self.logout_button)

        main_layout.addWidget(header_frame)

        # Action buttons section
        actions_frame = QFrame()
        actions_frame.setObjectName("card")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(20, 15, 20, 15)
        actions_layout.setSpacing(15)

        self.add_transaction_button = QPushButton("➕ Nova Transação")
        self.add_transaction_button.setObjectName("primary")
        self.add_transaction_button.setMinimumHeight(45)
        self.add_transaction_button.clicked.connect(self.open_add_transaction_dialog)
        actions_layout.addWidget(self.add_transaction_button)

        self.edit_transaction_button = QPushButton("✏️ Editar")
        self.edit_transaction_button.setMinimumHeight(45)
        self.edit_transaction_button.clicked.connect(self.open_edit_transaction_dialog)
        actions_layout.addWidget(self.edit_transaction_button)

        self.delete_transaction_button = QPushButton("🗑️ Remover")
        self.delete_transaction_button.setObjectName("danger")
        self.delete_transaction_button.setMinimumHeight(45)
        self.delete_transaction_button.clicked.connect(self.handle_delete_transaction)
        actions_layout.addWidget(self.delete_transaction_button)

        self.delete_group_button = QPushButton("🗂️ Remover Grupo")
        self.delete_group_button.setObjectName("danger")
        self.delete_group_button.setMinimumHeight(45)
        self.delete_group_button.clicked.connect(self.handle_delete_group)
        actions_layout.addWidget(self.delete_group_button)

        self.reports_button = QPushButton("📊 Relatórios")
        self.reports_button.setObjectName("secondary")
        self.reports_button.setMinimumHeight(45)
        self.reports_button.clicked.connect(self.open_reports_dialog)
        actions_layout.addWidget(self.reports_button)

        main_layout.addWidget(actions_frame)

        # Filters section
        filters_frame = QFrame()
        filters_frame.setObjectName("card")
        filters_layout = QVBoxLayout(filters_frame)
        filters_layout.setContentsMargins(20, 15, 20, 15)

        filters_title = QLabel("🔍 Filtros e Busca")
        filters_title.setStyleSheet("font-weight: 600; font-size: 11pt; color: #34495e; margin-bottom: 10px;")
        filters_layout.addWidget(filters_title)

        filters_controls = QHBoxLayout()
        filters_controls.setSpacing(15)

        # Search input
        search_section = QVBoxLayout()
        search_label = QLabel("Buscar:")
        search_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 9pt;")
        search_section.addWidget(search_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para buscar na descrição...")
        self.search_input.setMinimumHeight(35)
        self.search_input.returnPressed.connect(self.apply_filters_and_sort)
        search_section.addWidget(self.search_input)
        filters_controls.addLayout(search_section)

        # Type filter
        type_section = QVBoxLayout()
        type_label = QLabel("Tipo:")
        type_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 9pt;")
        type_section.addWidget(type_label)
        self.filter_type_combo = QComboBox()
        self.filter_type_combo.addItems(["Todas", "💰 " + TransactionType.INCOME.value.capitalize(), "💸 " + TransactionType.EXPENSE.value.capitalize()])
        self.filter_type_combo.setMinimumHeight(35)
        self.filter_type_combo.currentIndexChanged.connect(self.apply_filters_and_sort)
        type_section.addWidget(self.filter_type_combo)
        filters_controls.addLayout(type_section)

        # Sort by
        sort_section = QVBoxLayout()
        sort_label = QLabel("Ordenar por:")
        sort_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 9pt;")
        sort_section.addWidget(sort_label)
        self.sort_column_combo = QComboBox()
        self.sort_column_combo.addItems(["📅 Data", "📝 Descrição", "💰 Valor"])
        self.sort_column_combo.setMinimumHeight(35)
        self.sort_column_combo.currentIndexChanged.connect(self.apply_filters_and_sort)
        sort_section.addWidget(self.sort_column_combo)
        filters_controls.addLayout(sort_section)

        # Sort order
        order_section = QVBoxLayout()
        order_label = QLabel("Ordem:")
        order_label.setStyleSheet("font-weight: 600; color: #2c3e50; font-size: 9pt;")
        order_section.addWidget(order_label)
        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItems(["⬇️ Decrescente", "⬆️ Crescente"])
        self.sort_order_combo.setMinimumHeight(35)
        self.sort_order_combo.currentIndexChanged.connect(self.apply_filters_and_sort)
        order_section.addWidget(self.sort_order_combo)
        filters_controls.addLayout(order_section)

        # Apply button
        apply_section = QVBoxLayout()
        apply_section.addWidget(QLabel(""))  # Spacer
        self.apply_filters_button = QPushButton("🔍 Aplicar")
        self.apply_filters_button.setMinimumHeight(35)
        self.apply_filters_button.clicked.connect(self.apply_filters_and_sort)
        apply_section.addWidget(self.apply_filters_button)
        filters_controls.addLayout(apply_section)

        filters_layout.addLayout(filters_controls)
        main_layout.addWidget(filters_frame)

        # Transactions table
        table_frame = QFrame()
        table_frame.setObjectName("card")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 15, 15, 15)

        table_title = QLabel("📋 Suas Transações")
        table_title.setStyleSheet("font-weight: 600; font-size: 11pt; color: #34495e; margin-bottom: 10px;")
        table_layout.addWidget(table_title)

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels(["ID", "Tipo", "Valor (R$)", "Data", "Descrição"])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transactions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setMinimumHeight(300)
        
        # Set default row height to ensure content is fully visible
        self.transactions_table.verticalHeader().setDefaultSectionSize(45)  # Increased row height
        self.transactions_table.verticalHeader().setMinimumSectionSize(40)  # Minimum row height
        
        table_layout.addWidget(self.transactions_table)

        main_layout.addWidget(table_frame)
        
        self.apply_filters_and_sort()

    def apply_filters_and_sort(self):
        search_term = self.search_input.text().strip() or None
        
        filter_type_text = self.filter_type_combo.currentText()
        filter_type: TransactionType | None = None
        if "receita" in filter_type_text.lower():
            filter_type = TransactionType.INCOME
        elif "despesa" in filter_type_text.lower():
            filter_type = TransactionType.EXPENSE

        sort_column_text = self.sort_column_combo.currentText().lower()
        db_sort_column_map = {"data": "date", "descrição": "description", "valor": "amount"}
        
        for key in db_sort_column_map:
            if key in sort_column_text:
                sort_by = db_sort_column_map[key]
                break
        else:
            sort_by = "date"

        sort_order_text = self.sort_order_combo.currentText().lower()
        sort_order = "ASC" if "crescente" in sort_order_text else "DESC"

        self.show_transactions(search_term=search_term, filter_type=filter_type, sort_by=sort_by, sort_order=sort_order)

    def open_add_transaction_dialog(self):
        dialog = AddTransactionDialog(self.user.id, self)
        if dialog.exec(): 
            self.apply_filters_and_sort() 

    def open_edit_transaction_dialog(self):
        selected_rows = self.transactions_table.selectionModel().selectedRows()
        if not selected_rows:
            self.show_message("Nenhuma Seleção", "Por favor, selecione uma transação da tabela para editar.", "info")
            return

        selected_row_index = selected_rows[0].row()
        transaction_id_item = self.transactions_table.item(selected_row_index, 0)
        
        if not transaction_id_item:
            self.show_message("Erro", "Não foi possível obter o ID da transação selecionada para edição.", "warning")
            return
        
        transaction_id = int(transaction_id_item.text())
        transaction_to_edit = database.get_transaction_by_id(transaction_id)

        if not transaction_to_edit:
            self.show_message("Erro", f"Transação com ID {transaction_id} não encontrada no banco de dados.", "warning")
            return

        dialog = EditTransactionDialog(transaction_to_edit, self)
        if dialog.exec():
            self.apply_filters_and_sort()

    def handle_delete_transaction(self):
        selected_rows = self.transactions_table.selectionModel().selectedRows()
        if not selected_rows:
            self.show_message("Nenhuma Seleção", "Por favor, selecione uma transação da tabela para remover.", "info")
            return

        selected_row_index = selected_rows[0].row()
        transaction_id_item = self.transactions_table.item(selected_row_index, 0)
        
        if not transaction_id_item:
            self.show_message("Erro", "Não foi possível obter o ID da transação selecionada.", "warning")
            return
        
        transaction_id = int(transaction_id_item.text())
        transaction_details = database.get_transaction_by_id(transaction_id)
        description_for_confirm = f"transação ID: {transaction_id}"
        if transaction_details and (transaction_details.installment_group_id or transaction_details.is_recurring):
            description_for_confirm = f"transação ID: {transaction_id}\n\n⚠️ Esta é parte de um grupo. Use 'Remover Grupo' para remover todas as transações relacionadas."

        reply = QMessageBox.question(self, "🗑️ Confirmar Remoção Individual", 
                                     f"Tem certeza que deseja remover APENAS a {description_for_confirm}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if database.delete_transaction(transaction_id):
                self.show_message("Sucesso", f"✅ Transação ID: {transaction_id} removida com sucesso.", "info")
                self.apply_filters_and_sort()
            else:
                self.show_message("Erro", f"❌ Falha ao remover a transação ID: {transaction_id}.", "warning")

    def handle_delete_group(self):
        selected_rows = self.transactions_table.selectionModel().selectedRows()
        if not selected_rows:
            self.show_message("Nenhuma Seleção", "Por favor, selecione uma transação da tabela para identificar o grupo a ser removido.", "info")
            return

        selected_row_index = selected_rows[0].row()
        transaction_id_item = self.transactions_table.item(selected_row_index, 0)
        if not transaction_id_item:
            self.show_message("Erro", "Não foi possível obter o ID da transação selecionada.", "warning")
            return
        transaction_id = int(transaction_id_item.text())

        selected_transaction = database.get_transaction_by_id(transaction_id)
        if not selected_transaction:
            self.show_message("Erro", f"Transação com ID {transaction_id} não encontrada.", "warning")
            return

        group_id_to_delete = None
        group_field_name = None
        group_type_message = ""

        if selected_transaction.installment_group_id:
            group_id_to_delete = selected_transaction.installment_group_id
            group_field_name = "installment_group_id"
            group_type_message = f"grupo de parcelamento (originalmente {selected_transaction.total_installments} parcelas)"
        elif selected_transaction.recurring_group_id:
            group_id_to_delete = selected_transaction.recurring_group_id
            group_field_name = "recurring_group_id"
            group_type_message = f"grupo de recorrência (originalmente {selected_transaction.total_occurrences_in_group} ocorrências)"
        else:
            self.show_message("Nenhum Grupo", "A transação selecionada não pertence a um grupo de parcelamento ou recorrência.", "info")
            return

        if not group_id_to_delete:
            self.show_message("Erro", "Não foi possível identificar o ID do grupo.", "warning")
            return

        reply = QMessageBox.question(self, f"🗂️ Confirmar Remoção de Grupo", 
                                     f"Tem certeza que deseja remover TODAS as transações do {group_type_message} associado à transação ID {transaction_id}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            success, num_deleted = database.delete_transaction_group(group_id_to_delete, group_field_name)
            if success:
                self.show_message("Sucesso", f"✅ {num_deleted} transações do grupo foram removidas com sucesso.", "info")
                self.apply_filters_and_sort()
            else:
                self.show_message("Erro", "❌ Falha ao remover o grupo de transações.", "warning")
        
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
            
            # Type with emoji and color
            type_text = "💰 " + t.type.value.capitalize() if t.type == TransactionType.INCOME else "💸 " + t.type.value.capitalize()
            item_type = QTableWidgetItem(type_text)
            if t.type == TransactionType.INCOME:
                item_type.setForeground(Qt.darkGreen)
            else:
                item_type.setForeground(Qt.red)
            self.transactions_table.setItem(row_num, 1, item_type)
            
            # Amount with formatting
            amount_item = QTableWidgetItem(f"R$ {t.amount:.2f}")
            if t.type == TransactionType.INCOME:
                amount_item.setForeground(Qt.darkGreen)
            else:
                amount_item.setForeground(Qt.red)
            self.transactions_table.setItem(row_num, 2, amount_item)
            
            self.transactions_table.setItem(row_num, 3, QTableWidgetItem(format_date_for_display(t.date)))
            self.transactions_table.setItem(row_num, 4, QTableWidgetItem(t.description))
            
    def handle_logout(self):
        reply = QMessageBox.question(self, "🚪 Logout", "Tem certeza que deseja sair?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.main_app_controller.show_login_window()
            self.close()

    def show_message(self, title, message, msg_type="info"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        if msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == "info":
            msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()

class MainAppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # Set application-wide style
        self.app.setStyleSheet(MODERN_STYLESHEET)
        
        # Set modern font
        font = QFont("Segoe UI", 9)
        self.app.setFont(font)
        
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