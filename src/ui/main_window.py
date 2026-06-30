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
    QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QCompleter
from src.database.db_manager import GuardDB


class HistoryWindow(QDialog):
    def __init__(self, db_manager, is_dark_mode, parent=None):
        super().__init__(parent)
        self.setWindowTitle("היסטוריית שיבוצים (50 אחרונים)")
        self.setMinimumSize(500, 350)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.db = db_manager
        self.is_dark_mode = is_dark_mode
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["שם מאבטח/ת", "עמדה", "זמן שיבוץ"])

        # Force the user to select the entire row, not just one cell
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.load_table_data()
        layout.addWidget(self.table)

        # Buttons layout
        btn_layout = QHBoxLayout()

        self.del_selected_btn = QPushButton("מחק רשומה נבחרת")
        self.del_selected_btn.setStyleSheet("""
            background-color: #fff3cd; 
            color: #856404; 
            border-radius: 8px; 
            border: 1px solid #ffeeba;
            padding: 6px;
            font-weight: bold;
        """)
        self.del_selected_btn.clicked.connect(self.delete_selected_record)

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

        btn_layout.addWidget(self.del_selected_btn)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_table_data(self):
        self.table.setRowCount(0)  # Clear existing rows
        history_data = self.db.get_shift_history()
        self.table.setRowCount(len(history_data))

        for row_idx, row_data in enumerate(history_data):
            name, post, timestamp = row_data
            self.table.setItem(row_idx, 0, QTableWidgetItem(name))
            self.table.setItem(row_idx, 1, QTableWidgetItem(post))
            self.table.setItem(row_idx, 2, QTableWidgetItem(timestamp))

    def delete_selected_record(self):
        current_row = self.table.currentRow()

        if current_row < 0:
            QMessageBox.warning(self, "שגיאה", "אנא בחר רשומה מהרשימה תחילה! ❌")
            return

        name = self.table.item(current_row, 0).text()
        post = self.table.item(current_row, 1).text()
        timestamp = self.table.item(current_row, 2).text()

        # Confirm targeted deletion
        reply = QMessageBox.question(
            self,
            "אישור מחיקה",
            f"האם למחוק את השיבוץ של {name} לעמדת {post}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_specific_history(name, post, timestamp)
            self.load_table_data()

    def clear_history_safely(self):
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
            msg.setText("כל היסטוריית השיבוצים נמחקה בהצלחה ✅")
            msg.setIcon(QMessageBox.Icon.NoIcon)
            msg.exec()

    def apply_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet("""
                QDialog { background-color: #2b2b2b; }
                QTableWidget { background-color: #3b3b3b; color: #ffffff; gridline-color: #555555; }
                QHeaderView::section { background-color: #444444; color: white; border: 1px solid #555555; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #f0f0f0; }
                QTableWidget { background-color: #ffffff; color: #000000; gridline-color: #cccccc; }
                QHeaderView::section { background-color: #e0e0e0; color: black; border: 1px solid #cccccc; }
            """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("מערכת שיבוץ מאבטחים")
        self.setMinimumSize(500, 450)
        self.setWindowIcon(QIcon("assets/guard_logo.jpg"))

        self.db = GuardDB()
        self.is_dark_mode = True  # Default to Dark Mode

        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        self.central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Top Bar: Theme Toggle + DB Management
        top_bar_layout = QHBoxLayout()

        self.theme_btn = QPushButton("☀️ מצב יום")
        self.theme_btn.setStyleSheet("""
            background-color: #f8f9fa; 
            color: #212529; 
            border-radius: 8px; 
            border: 1px solid #dae0e5;
            padding: 6px;
            font-weight: bold;
        """)
        self.theme_btn.clicked.connect(self.toggle_theme)

        self.add_to_db_btn = QPushButton("הוסף למאגר")
        self.add_to_db_btn.setStyleSheet("""
            background-color: #d4edda; 
            color: green; 
            border-radius: 8px; 
            border: 1px solid #c3e6cb;
            padding: 6px;
            font-weight: bold;
        """)

        self.remove_from_db_btn = QPushButton("מחק מהמאגר")
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

        top_bar_layout.addWidget(self.theme_btn)
        top_bar_layout.addWidget(self.add_to_db_btn)
        top_bar_layout.addWidget(self.remove_from_db_btn)
        main_layout.addLayout(top_bar_layout)

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

        search_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("הקלד שם מאבטח/ת")
        self.refresh_autocomplete()

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

        self.active_guards_list = QListWidget()
        main_layout.addWidget(self.active_guards_list)

        shift_management_layout = QHBoxLayout()

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

        self.post_selector = QComboBox()
        self.post_selector.addItems(["סריקה", "אנטולי"])
        main_layout.addWidget(self.post_selector)

        self.result_label = QLabel("השיבוץ יוצג כאן")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.result_label)

        self.signature_label = QLabel("Made by Kiril Shamis")
        self.signature_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.signature_label)

        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

    def apply_theme(self):
        """Mathematically switches the UI colors based on the current mode."""
        if self.is_dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget#central_widget { background-color: #2b2b2b; }
                QLabel { color: #ffffff; }
                QLineEdit, QListWidget, QComboBox { 
                    background-color: #3b3b3b; 
                    color: #ffffff; 
                    border: 1px solid #555555; 
                }
            """)
            self.result_label.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #66b3ff;"
            )  # Light Blue
            self.signature_label.setStyleSheet(
                "font-size: 11px; color: #aaaaaa; font-style: italic;"
            )

            self.theme_btn.setText("☀️ מצב יום")
            self.theme_btn.setStyleSheet("""
                background-color: #f8f9fa; color: #212529; border-radius: 8px; border: 1px solid #dae0e5; padding: 6px; font-weight: bold;
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget#central_widget { background-color: #f0f0f0; }
                QLabel { color: #000000; }
                QLineEdit, QListWidget, QComboBox { 
                    background-color: #ffffff; 
                    color: #000000; 
                    border: 1px solid #cccccc; 
                }
            """)
            self.result_label.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #004085;"
            )  # Dark Blue
            self.signature_label.setStyleSheet(
                "font-size: 11px; color: #666666; font-style: italic;"
            )

            self.theme_btn.setText("🌙 מצב לילה")
            self.theme_btn.setStyleSheet("""
                background-color: #343a40; color: white; border-radius: 8px; border: 1px solid #23272b; padding: 6px; font-weight: bold;
            """)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def refresh_autocomplete(self):
        all_guards = self.db.get_all()
        completer = QCompleter(all_guards)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_bar.setCompleter(completer)

    def show_history(self):
        # We pass the current theme state to the history window so it matches instantly!
        dialog = HistoryWindow(self.db, self.is_dark_mode, self)
        dialog.exec()

    def hire_guard(self):
        name, ok = QInputDialog.getText(self, "הוספת מאבטח", "הכנס שם מאבטח/ת חדש/ה:")
        if ok and name.strip():
            name = name.strip()
            if name in self.db.get_all():
                msg = QMessageBox(self)
                msg.setWindowTitle("שגיאה")
                msg.setText(f"המאבטח/ת '{name}' כבר קיים במאגר! ❌")
                msg.setIcon(QMessageBox.Icon.NoIcon)
                msg.exec()
                return

            self.db.add_guard(name)
            self.refresh_autocomplete()

            msg = QMessageBox(self)
            msg.setWindowTitle("הצלחה")
            msg.setText(f"המאבטח/ת '{name}' נוסף/ה בהצלחה למאגר! ✅")
            msg.setIcon(QMessageBox.Icon.NoIcon)
            msg.exec()

    def fire_guard(self):
        name, ok = QInputDialog.getText(self, "מחיקת מאבטח", "הכנס שם מאבטח/ת למחיקה:")
        if ok and name.strip():
            name = name.strip()
            if name not in self.db.get_all():
                msg = QMessageBox(self)
                msg.setWindowTitle("שגיאה")
                msg.setText(f"לא נמצא מאבטח/ת בשם '{name}' במאגר! ❌")
                msg.setIcon(QMessageBox.Icon.NoIcon)
                msg.exec()
                return

            self.db.remove_guard(name)
            self.refresh_autocomplete()

            msg = QMessageBox(self)
            msg.setWindowTitle("הצלחה")
            msg.setText(f"המאבטח/ת '{name}' נמחק/ה בהצלחה מהמאגר! ✅")
            msg.setIcon(QMessageBox.Icon.NoIcon)
            msg.exec()

    def add_guard_to_list(self):
        typed_name = self.search_bar.text().strip()
        if not typed_name:
            return

        all_guards = self.db.get_all()
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
        selected_items = self.active_guards_list.selectedItems()
        if not selected_items:
            self.result_label.setText("שגיאה: סמן מאבטח ברשימה כדי להסיר!")
            return

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
