from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QListWidget, QPushButton, QLabel,
                             QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCompleter
from src.database.db_manager import GuardDB

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        # Window title
        self.setWindowTitle("מערכת שיבוץ מאבטחים")
        self.setMinimumSize(500, 400)
        
        # Connecting the database
        self.db = GuardDB()
        
        self.setup_ui()


    def setup_ui(self):
        self.central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Search bar and Auto complete
        search_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("שבץ מאבטח/ת")
        
        # Get all the guards from DB
        all_guards = self.db.get_all()
        completer = QCompleter(all_guards)
        
        self.search_bar.setCompleter(completer)
        self.add_guard_btn = QPushButton("הוסף")
        self.search_bar.returnPressed.connect(self.add_guard_to_list)
        self.add_guard_btn.clicked.connect(self.add_guard_to_list)
        
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.add_guard_btn)
        
        main_layout.addLayout(search_layout)
        
        # Visual guards list
        self.active_guards_list = QListWidget()
        main_layout.addWidget(self.active_guards_list)
        
        # "Assign" Button widget
        self.assign_btn = QPushButton("שבץ לעמדה")
        self.assign_btn.clicked.connect(self.assign_shift)
        main_layout.addWidget(self.assign_btn)
        
        # Post selection drop down
        self.post_selector = QComboBox()
        self.post_selector.addItems(["סריקה", "אנטולי"])
        main_layout.addWidget(self.post_selector)
        
        # Output text
        self.result_label = QLabel("השיבוץ יוצג כאן")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("font-size: 18px; font-weight: bold; color: blue;")
        main_layout.addWidget(self.result_label)
        
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)
        
        
    
    def add_guard_to_list(self):
        typed_name = self.search_bar.text().strip()
        
        # If search bar empty do nothing
        if not typed_name:
            return
            
        # 1Pull master list names
        all_guards = self.db.get_all() 
        
        # Setting the chosen guards name
        matched_full_name = None
        
        for full_name in all_guards:
            if typed_name == full_name or typed_name in full_name:
                matched_full_name = full_name
                break 
                
        if matched_full_name:
            current_items = [self.active_guards_list.item(i).text() for i in range(self.active_guards_list.count())]
            
            if matched_full_name not in current_items:
                self.active_guards_list.addItem(matched_full_name)
                self.result_label.setText("השיבוץ יוצג כאן") 
            
            self.search_bar.clear()
            
        else:
            self.result_label.setText(f"שגיאה: לא נמצא מאבטח בשם '{typed_name}'")
            
    def assign_shift(self):
        present_guards = [self.active_guards_list.item(i).text() for i in range(self.active_guards_list.count())]
        
        if not present_guards:
            self.result_label.setText("שגיאה: הוסף מאבטחים למשמרת תחילה!")
            return
            
        post_name = self.post_selector.currentText()
        next_guard = self.db.get_next_guard(present_guards, post_name)
        
        if next_guard:
            self.result_label.setText(f"הבא בתור ל{post_name}: {next_guard}")
            self.db.record_shift(next_guard, post_name)