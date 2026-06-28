from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QLabel,
    QComboBox,
    QInputDialog,
    QMessageBox,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QCompleter
from src.database.db_manager import GuardDB
import os
import sys


def get_asset_path(relative_path):
    """Dynamically route paths for PyInstaller _MEIPASS or local dev"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class HistoryWindow(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("היסטוריית שיבוצים (50 אחרונים)")
        self.setMinimumSize(450, 300)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.db = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Build the table grid
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["שם מאבטח/ת", "עמדה", "זמן שיבוץ"])

        # Make the columns stretch to fill the window
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.load_table_data()
        layout.addWidget(self.table)

        self.clear_btn = QPushButton("נקה את כל ההיסטוריה")
        self.clear_btn.setStyleSheet("""
            background-color: #f8d7da; 
            color: red; 
            border-radius: 8px; 
            border: 1px solid #f5c6cb;
            padding: 6px;
            font-weight: bold;
        """)
        self.clear_btn.clicked.connect(self.clear_history_safely)
        layout.addWidget(self.clear_btn)

        self.setLayout(layout)

    def load_table_data(self):
        # Fetch the data and inject it
        history_data = self.db.get_shift_history()
        self.table.setRowCount(len(history_data))

        for row_idx, row_data in enumerate(history_data):
            name, post, timestamp = row_data
            self.table.setItem(row_idx, 0, QTableWidgetItem(name))
            self.table.setItem(row_idx, 1, QTableWidgetItem(post))
            self.table.setItem(row_idx, 2, QTableWidgetItem(timestamp))

    def clear_history_safely(self):
        # Safety prompt
        reply = QMessageBox.question(
            self,
            "אזהרה חמורה",
            "האם אתה בטוח שברצונך למחוק את כל היסטוריית השיבוצים? לא ניתן לשחזר פעולה זו",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.clear_history()
            self.load_table_data()

            msg = QMessageBox(self)
            msg.setWindowTitle("הצלחה")
            msg.setText("כל היסטוריית השיבוצים נמחקה בהצלחה")
            msg.setIcon(QMessageBox.Icon.NoIcon)
            msg.exec()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Window title
        self.setWindowTitle("מערכת שיבוץ מאבטחים")
        self.setMinimumSize(500, 400)

        # Logo
        logo_path = get_asset_path("assets/guard_logo.jpg")
        self.setWindowIcon(QIcon(logo_path))

        self.setMinimumSize(500, 400)

        # Connecting the database
        self.db = GuardDB()

        self.setup_ui()

    def setup_ui(self):
        self.central_widget = QWidget()
        main_layout = QVBoxLayout()

        db_management_layout = QHBoxLayout()

        # Add guard to the DB button
        self.add_to_db_btn = QPushButton("הוסף מאבטח/ת למאגר")
        self.add_to_db_btn.setStyleSheet("""
            background-color: #d4edda; 
            color: green; 
            border-radius: 8px; 
            border: 1px solid #c3e6cb;
            padding: 6px;
            font-weight: bold;
        """)

        # Delete guard from the DB button
        self.remove_from_db_btn = QPushButton("מחק מאבטח/ת מהמאגר")
        self.remove_from_db_btn.setStyleSheet("""
            background-color: #f8d7da; 
            color: red; 
            border-radius: 8px; 
            border: 1px solid #f5c6cb;
            padding: 6px;
            font-weight: bold;
        """)

        self.add_to_db_btn.clicked.connect(self.hire_guard)
        self.remove_from_db_btn.clicked.connect(self.fire_guard)

        db_management_layout.addWidget(self.add_to_db_btn)
        db_management_layout.addWidget(self.remove_from_db_btn)
        main_layout.addLayout(db_management_layout)

        # View history button
        self.history_btn = QPushButton("היסטוריית שיבוצים")
        self.history_btn.setStyleSheet("""
            background-color: #e2e3e5; 
            color: black; 
            border-radius: 8px; 
            border: 1px solid #d6d8db;
            padding: 6px;
            font-weight: bold;
        """)
        self.history_btn.clicked.connect(self.show_history)
        main_layout.addWidget(self.history_btn)

        # Search bar and Auto complete
        search_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("הקלד שם מאבטח/ת")
        self.refresh_autocomplete()

        # Assign to shift button
        self.add_guard_btn = QPushButton("שבץ למשמרת")
        self.add_guard_btn.setStyleSheet("""
            background-color: #d1ecf1; 
            color: #0c5460; 
            border-radius: 8px; 
            border: 1px solid #bee5eb;
            padding: 6px;
            font-weight: bold;
        """)

        self.search_bar.returnPressed.connect(self.add_guard_to_list)
        self.add_guard_btn.clicked.connect(self.add_guard_to_list)

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.add_guard_btn)

        main_layout.addLayout(search_layout)

        # Visual guards list
        self.active_guards_list = QListWidget()
        main_layout.addWidget(self.active_guards_list)

        shift_management_layout = QHBoxLayout()

        # Assign to post
        self.assign_btn = QPushButton("שבץ לעמדה")
        self.assign_btn.setStyleSheet("""
            background-color: #cce5ff; 
            color: #004085; 
            border-radius: 8px; 
            border: 1px solid #b8daff;
            padding: 6px;
            font-weight: bold;
        """)
        self.assign_btn.clicked.connect(self.assign_shift)

        # Remove a guard from the shift
        self.remove_from_shift_btn = QPushButton("הסר מהמשמרת")
        self.remove_from_shift_btn.setStyleSheet("""
            background-color: #fff3cd; 
            color: #856404; 
            border-radius: 8px; 
            border: 1px solid #ffeeba;
            padding: 6px;
            font-weight: bold;
        """)
        self.remove_from_shift_btn.clicked.connect(self.remove_guard_from_list)

        shift_management_layout.addWidget(self.assign_btn)
        shift_management_layout.addWidget(self.remove_from_shift_btn)

        main_layout.addLayout(shift_management_layout)

        # Post selection drop down
        self.post_selector = QComboBox()
        self.post_selector.addItems(["סריקה", "אנטולי"])
        main_layout.addWidget(self.post_selector)

        # Output text
        self.result_label = QLabel("השיבוץ יוצג כאן")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #cce5ff;"
        )
        main_layout.addWidget(self.result_label)

        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

        self.signature_label = QLabel("Made by Kiril Shamis")
        self.signature_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.signature_label.setStyleSheet(
            "font-size: 11px; color: gray; font-style: italic;"
        )
        main_layout.addWidget(self.signature_label)

        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

    def refresh_autocomplete(self):
        all_guards = self.db.get_all()
        completer = QCompleter(all_guards)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_bar.setCompleter(completer)

    def show_history(self):
        dialog = HistoryWindow(self.db, self)
        dialog.exec()

    def hire_guard(self):

        name, ok = QInputDialog.getText(self, "הוספת מאבטח", "הכנס שם מאבטח/ת חדש/ה:")

        if ok and name.strip():
            name = name.strip()

            # Check if they already exist
            if name in self.db.get_all():
                # Warning box
                QMessageBox.warning(self, "שגיאה", f"המאבטח/ת '{name}' כבר קיים במאגר!")
                return

            self.db.add_guard(name)
            self.refresh_autocomplete()

            QMessageBox.information(
                self, "הצלחה", f"המאבטח/ת '{name}' נוסף/ה בהצלחה למאגר!"
            )

    def fire_guard(self):

        name, ok = QInputDialog.getText(self, "מחיקת מאבטח", "הכנס שם מאבטח/ת למחיקה:")

        if ok and name.strip():
            name = name.strip()

            # Checking if name exists
            if name not in self.db.get_all():
                # Warning box
                QMessageBox.warning(
                    self, "שגיאה", f"לא נמצא מאבטח/ת בשם '{name}' במאגר!"
                )
                return  # Stop the function here

            self.db.remove_guard(name)
            self.refresh_autocomplete()

            QMessageBox.information(
                self, "הצלחה", f"המאבטח/ת '{name}' נמחק/ה בהצלחה מהמאגר!"
            )

    def add_guard_to_list(self):
        typed_name = self.search_bar.text().strip()

        # If search bar empty do nothing
        if not typed_name:
            return

        # Pull master list names
        all_guards = self.db.get_all()

        # Setting the chosen guards name
        matched_full_name = None

        for full_name in all_guards:
            if typed_name == full_name or typed_name in full_name:
                matched_full_name = full_name
                break

        if matched_full_name:
            current_items = [
                self.active_guards_list.item(i).text()
                for i in range(self.active_guards_list.count())
            ]

            if matched_full_name not in current_items:
                self.active_guards_list.addItem(matched_full_name)
                self.result_label.setText("השיבוץ יוצג כאן")

            self.search_bar.clear()

        else:
            self.result_label.setText(f"שגיאה: לא נמצא מאבטח בשם '{typed_name}'")

    def remove_guard_from_list(self):
        # Find higlightened name
        selected_items = self.active_guards_list.selectedItems()

        # In case nothing was
        if not selected_items:
            self.result_label.setText("שגיאה: סמן מאבטח ברשימה כדי להסיר")
            return

        # Execute the removal
        for item in selected_items:
            row_number = self.active_guards_list.row(item)
            self.active_guards_list.takeItem(row_number)

        self.result_label.setText("המאבטח הוסר מהמשמרת.")

    def assign_shift(self):
        present_guards = [
            self.active_guards_list.item(i).text()
            for i in range(self.active_guards_list.count())
        ]

        if not present_guards:
            self.result_label.setText("שגיאה: הוסף מאבטחים למשמרת תחילה!")
            return

        post_name = self.post_selector.currentText()
        next_guard = self.db.get_next_guard(present_guards, post_name)

        if next_guard:
            self.result_label.setText(f"הבא בתור ל{post_name}: {next_guard}")
            self.db.record_shift(next_guard, post_name)

        else:
            fallback_guard = present_guards[0]
            self.result_label.setText(
                f"הבא בתור ל{post_name}: {fallback_guard} (שיבוץ ראשון)"
            )
            self.db.record_shift(fallback_guard, post_name)
