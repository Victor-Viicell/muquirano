from PySide6.QtCore import QDate

# Helper to convert YYYY-MM-DD to dd/MM/yyyy for display
def format_date_for_display(date_str_db):
    if not date_str_db:
        return ""
    try:
        date_obj = QDate.fromString(date_str_db, "yyyy-MM-dd")
        return date_obj.toString("dd/MM/yyyy")
    except Exception:
        return date_str_db # Fallback to original if parsing fails 