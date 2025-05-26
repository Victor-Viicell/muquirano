import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QDateEdit, QFormLayout, QHBoxLayout, QLabel, QMessageBox
from PySide6.QtCore import QDate
from src.db import database
from src.db.data_models import Transaction, TransactionType
from typing import List, Dict
from src.app.utils import format_date_for_display

def get_transactions_as_dataframe(user_id: int, 
                                  start_date: str | None = None, 
                                  end_date: str | None = None) -> pd.DataFrame:
    """Fetches transactions and returns them as a pandas DataFrame."""
    transactions: List[Transaction] = database.get_transactions_by_user(user_id=user_id, sort_by='date', sort_order='ASC')
    
    if not transactions:
        return pd.DataFrame(columns=['id', 'user_id', 'type', 'amount', 'date', 'description'])

    df = pd.DataFrame([t.__dict__ for t in transactions])
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    df['type'] = df['type'].apply(lambda x: x.value if isinstance(x, TransactionType) else x)

    if start_date:
        df = df[df['date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['date'] <= pd.to_datetime(end_date)]
    return df

def generate_summary_report(df: pd.DataFrame) -> Dict[str, float]:
    """Generates a summary report: total income, total expenses, net balance."""
    summary = {
        "total_receita": df[df['type'] == TransactionType.INCOME.value]['amount'].sum() if not df.empty else 0.0,
        "total_despesa": df[df['type'] == TransactionType.EXPENSE.value]['amount'].sum() if not df.empty else 0.0,
    }
    summary["saldo_liquido"] = summary["total_receita"] - summary["total_despesa"]
    return summary

def create_income_expense_pie_chart(df: pd.DataFrame) -> plt.Figure | None:
    """Generates a pie chart of income vs. expense."""
    if df.empty:
        return None
    
    totals = df.groupby('type')['amount'].sum()
    receita_total = totals.get(TransactionType.INCOME.value, 0)
    despesa_total = totals.get(TransactionType.EXPENSE.value, 0)

    if receita_total == 0 and despesa_total == 0:
        return None

    labels = []
    sizes = []
    colors_pie = [] 

    if receita_total > 0:
        labels.append(TransactionType.INCOME.value.capitalize())
        sizes.append(receita_total)
        colors_pie.append('#77dd77')
    if despesa_total > 0:
        labels.append(TransactionType.EXPENSE.value.capitalize())
        sizes.append(despesa_total)
        colors_pie.append('#ff6961')

    if not sizes:
        return None

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors_pie)
    ax.axis('equal') 
    plt.title("Distribuição de Receitas vs. Despesas")
    return fig

def create_monthly_bar_chart(df: pd.DataFrame) -> plt.Figure | None:
    """Generates a bar chart of monthly income and expenses."""
    if df.empty:
        return None

    df_copy = df.copy()
    df_copy['month_year'] = df_copy['date'].dt.to_period('M').astype(str)
    monthly_summary = df_copy.groupby(['month_year', 'type'])['amount'].sum().unstack(fill_value=0)

    if monthly_summary.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))
    
    if TransactionType.INCOME.value not in monthly_summary:
        monthly_summary[TransactionType.INCOME.value] = 0
    if TransactionType.EXPENSE.value not in monthly_summary:
        monthly_summary[TransactionType.EXPENSE.value] = 0
    
    plot_columns = []
    plot_colors = {}
    if TransactionType.INCOME.value in monthly_summary.columns:
        plot_columns.append(TransactionType.INCOME.value)
        plot_colors[TransactionType.INCOME.value] = '#77dd77'
    if TransactionType.EXPENSE.value in monthly_summary.columns:
        plot_columns.append(TransactionType.EXPENSE.value)
        plot_colors[TransactionType.EXPENSE.value] = '#ff6961'

    if not plot_columns:
        return None
        
    monthly_summary_to_plot = monthly_summary[plot_columns].sort_index()

    monthly_summary_to_plot.plot(kind='bar', ax=ax, color=[plot_colors[col] for col in plot_columns])
    
    ax.set_title("Receitas e Despesas Mensais")
    ax.set_xlabel("Mês-Ano")
    ax.set_ylabel("Valor (R$)")
    legend_labels = [col.capitalize() for col in plot_columns]
    ax.legend(legend_labels)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

def generate_simple_forecast(df_full_history: pd.DataFrame) -> Dict[str, float]:
    """Generates a very simple forecast for next month's expenses and income."""
    forecast = {
        "proxima_receita_estimada": 0.0,
        "proxima_despesa_estimada": 0.0
    }
    if df_full_history.empty:
        return forecast
    
    df_copy = df_full_history.copy()
    df_copy['month_year'] = df_copy['date'].dt.to_period('M')
    unique_months = df_copy['month_year'].unique()

    if len(unique_months) < 1:
        return forecast
        
    last_three_months_periods = sorted(unique_months)[-3:]
    
    if not last_three_months_periods:
        return forecast
        
    recent_df = df_copy[df_copy['month_year'].isin(last_three_months_periods)]

    if recent_df.empty:
        return forecast

    num_months_for_avg = len(last_three_months_periods)

    avg_income = recent_df[recent_df['type'] == TransactionType.INCOME.value]['amount'].sum() / num_months_for_avg
    avg_expense = recent_df[recent_df['type'] == TransactionType.EXPENSE.value]['amount'].sum() / num_months_for_avg

    forecast["proxima_receita_estimada"] = avg_income if pd.notna(avg_income) else 0.0
    forecast["proxima_despesa_estimada"] = avg_expense if pd.notna(avg_expense) else 0.0
    return forecast

class ChartDialog(QDialog):
    """A dialog to display a Matplotlib chart."""
    def __init__(self, figure: plt.Figure, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gráfico")
        self.layout = QVBoxLayout(self)
        self.canvas = FigureCanvas(figure)
        self.layout.addWidget(self.canvas)
        self.setMinimumSize(640, 480)
        # Ensure the figure is closed when the dialog is closed to free memory
        self.finished.connect(lambda: plt.close(figure))


class ReportPredictionDialog(QDialog):
    """Dialog to display reports and predictions with date range selection."""
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Relatórios e Previsões")
        self.setMinimumWidth(500)
        self.current_df_for_report = pd.DataFrame() # Initialize

        layout = QVBoxLayout(self)
        date_range_layout = QFormLayout()
        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-3))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
        date_range_layout.addRow("Data Inicial:", self.start_date_edit)

        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("dd/MM/yyyy")
        date_range_layout.addRow("Data Final:", self.end_date_edit)
        layout.addLayout(date_range_layout)

        self.generate_button = QPushButton("Gerar Relatório/Previsão")
        self.generate_button.clicked.connect(self.generate_report_and_forecast)
        layout.addWidget(self.generate_button)
        
        self.results_text_edit = QTextEdit()
        self.results_text_edit.setReadOnly(True)
        layout.addWidget(self.results_text_edit)
        
        charts_button_layout = QHBoxLayout()
        self.pie_chart_button = QPushButton("Gráfico Pizza (Receita/Despesa)")
        self.pie_chart_button.clicked.connect(self.show_pie_chart)
        self.pie_chart_button.setEnabled(False)
        charts_button_layout.addWidget(self.pie_chart_button)

        self.bar_chart_button = QPushButton("Gráfico Barras (Mensal)")
        self.bar_chart_button.clicked.connect(self.show_bar_chart)
        self.bar_chart_button.setEnabled(False)
        charts_button_layout.addWidget(self.bar_chart_button)
        layout.addLayout(charts_button_layout)

    def generate_report_and_forecast(self):
        start_date_str = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date_str = self.end_date_edit.date().toString("yyyy-MM-dd")

        if self.start_date_edit.date() > self.end_date_edit.date():
            QMessageBox.warning(self, "Data Inválida", "A data inicial não pode ser posterior à data final.")
            self.results_text_edit.setText("Selecione um intervalo de datas válido.")
            self.pie_chart_button.setEnabled(False)
            self.bar_chart_button.setEnabled(False)
            self.current_df_for_report = pd.DataFrame()
            return

        self.current_df_for_report = get_transactions_as_dataframe(self.user_id, start_date_str, end_date_str)

        if self.current_df_for_report.empty:
            self.results_text_edit.setText("Nenhuma transação encontrada para o período selecionado.")
            self.pie_chart_button.setEnabled(False)
            self.bar_chart_button.setEnabled(False)
            return

        summary = generate_summary_report(self.current_df_for_report)
        
        full_history_df = get_transactions_as_dataframe(self.user_id) # For a more stable (but still naive) forecast
        forecast = generate_simple_forecast(full_history_df) 

        report_text = f"--- Relatório Financeiro ({format_date_for_display(start_date_str)} - {format_date_for_display(end_date_str)}) ---\n"
        report_text += f"Total de Receitas: R$ {summary['total_receita']:.2f}\n"
        report_text += f"Total de Despesas: R$ {summary['total_despesa']:.2f}\n"
        report_text += f"Saldo Líquido: R$ {summary['saldo_liquido']:.2f}\n\n"
        report_text += "--- Previsão Simples (Baseado na Média dos Últimos 3 Meses de TODO o Histórico) ---\n"
        report_text += f"Estimativa de Receita Próximo Mês: R$ {forecast['proxima_receita_estimada']:.2f}\n"
        report_text += f"Estimativa de Despesa Próximo Mês: R$ {forecast['proxima_despesa_estimada']:.2f}\n"
        
        self.results_text_edit.setText(report_text)
        self.pie_chart_button.setEnabled(True)
        self.bar_chart_button.setEnabled(True)

    def show_pie_chart(self):
        if not self.current_df_for_report.empty:
            fig = create_income_expense_pie_chart(self.current_df_for_report)
            if fig:
                dialog = ChartDialog(fig, self)
                dialog.exec()
                # Figure is closed by ChartDialog.finished signal
            else:
                QMessageBox.information(self, "Gráfico Pizza", "Não há dados suficientes para gerar o gráfico pizza.")
        else:
            QMessageBox.warning(self, "Gráfico Pizza", "Gere um relatório primeiro para obter os dados do gráfico.")

    def show_bar_chart(self):
        if not self.current_df_for_report.empty:
            fig = create_monthly_bar_chart(self.current_df_for_report) 
            if fig:
                dialog = ChartDialog(fig, self)
                dialog.exec()
                # Figure is closed by ChartDialog.finished signal
            else:
                QMessageBox.information(self, "Gráfico Barras", "Não há dados suficientes para gerar o gráfico de barras mensal.")
        else:
            QMessageBox.warning(self, "Gráfico Barras", "Gere um relatório primeiro para obter os dados do gráfico.")
