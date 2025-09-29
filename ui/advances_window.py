from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox,
                            QCheckBox, QTabWidget, QHeaderView, QMessageBox,
                            QFormLayout, QGroupBox)
from PyQt6.QtCore import QDate, Qt
from widgets.modern_button import ModernButton
from widgets.modern_input import ModernInput
from widgets.modern_table import ModernTable
from database.database_manager import DatabaseManager
from utils.date_converter import DateConverter
from utils.font_manager import FontManager
import logging

logger = logging.getLogger(__name__)

class AdvancesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.selected_advance_id = None
        self.setup_ui()
        self.load_advances_data()
        
    def setup_ui(self):
        """Setup advances management UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("مدیریت مساعده‌ها")
        title_label.setFont(FontManager.get_font(point_size=16, bold=True))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add new advance button
        self.add_btn = ModernButton("➕ ثبت مساعده جدید")
        self.add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(header_layout)
        
        # Create tabs
        self.setup_tabs(main_layout)
    
    def setup_tabs(self, main_layout: QVBoxLayout):
        """Setup tabs for advances management"""
        tabs = QTabWidget()
        
        # Advances list tab
        self.setup_advances_list_tab(tabs)
        
        # Add/Edit tab
        self.setup_edit_tab(tabs)
        
        main_layout.addWidget(tabs)
    
    def setup_advances_list_tab(self, tabs: QTabWidget):
        """Setup advances list tab"""
        list_tab = QWidget()
        layout = QVBoxLayout(list_tab)
        
        # Filter section
        self.setup_filters(layout)
        
        # Advances table
        self.setup_advances_table(layout)
        
        tabs.addTab(list_tab, "لیست مساعده‌ها")
    
    def setup_filters(self, layout: QVBoxLayout):
        """Setup filter section"""
        filter_layout = QHBoxLayout()
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItems(["همه", "تسویه نشده", "تسویه شده"])
        self.status_filter.currentTextChanged.connect(self.filter_advances)
        filter_layout.addWidget(QLabel("وضعیت:"))
        filter_layout.addWidget(self.status_filter)
        
        # Personnel filter
        self.personnel_filter = QComboBox()
        self.personnel_filter.addItem("همه پرسنل")
        self.load_personnel_filter()
        self.personnel_filter.currentTextChanged.connect(self.filter_advances)
        filter_layout.addWidget(QLabel("پرسنل:"))
        filter_layout.addWidget(self.personnel_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
    
    def setup_advances_table(self, layout: QVBoxLayout):
        """Setup advances table"""
        self.advances_table = ModernTable()
        self.advances_table.setColumnCount(8)
        self.advances_table.setHorizontalHeaderLabels([
            "عملیات", "کد پرسنلی", "نام و نام خانوادگی", "مبلغ مساعده", 
            "تاریخ مساعده", "وضعیت تسویه", "توضیحات", "تاریخ ثبت"
        ])
        
        # Set column widths
        header = self.advances_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 100)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.advances_table)
    
    def setup_edit_tab(self, tabs: QTabWidget):
        """Setup add/edit advance tab"""
        self.edit_tab = QWidget()
        layout = QVBoxLayout(self.edit_tab)
        
        # Advance form
        form_group = QGroupBox("ثبت مساعده")
        form_layout = QFormLayout(form_group)
        
        # Personnel selection
        self.personnel_combo = QComboBox()
        self.load_personnel_combo()
        form_layout.addRow("پرسنل:", self.personnel_combo)
        
        # Advance amount
        self.advance_amount_input = QDoubleSpinBox()
        self.advance_amount_input.setRange(0, 1000000000)
        self.advance_amount_input.setValue(1000000)
        self.advance_amount_input.setSuffix(" ریال")
        form_layout.addRow("مبلغ مساعده:", self.advance_amount_input)
        
        # Advance date
        self.advance_date_input = QDateEdit()
        self.advance_date_input.setCalendarPopup(True)
        self.advance_date_input.setDate(QDate.currentDate())
        self.advance_date_input.setDisplayFormat("yyyy/MM/dd")
        form_layout.addRow("تاریخ مساعده:", self.advance_date_input)
        
        # Description
        self.description_input = ModernInput()
        self.description_input.setPlaceholderText("توضیحات اختیاری...")
        form_layout.addRow("توضیحات:", self.description_input)
        
        # Settlement status
        self.is_settled_checkbox = QCheckBox("مساعده تسویه شده")
        form_layout.addRow("", self.is_settled_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = ModernButton("💾 ذخیره مساعده")
        self.save_btn.clicked.connect(self.save_advance)
        self.cancel_btn = ModernButton("❌ انصراف")
        self.cancel_btn.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(form_group)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        tabs.addTab(self.edit_tab, "ثبت / ویرایش")
    
    def load_personnel_filter(self):
        """Load personnel for filter"""
        try:
            query = "SELECT id, employee_code, first_name, last_name FROM personnel WHERE is_active = TRUE"
            results = self.db.fetch_all(query)
            
            for personnel in results:
                display_text = f"{personnel['employee_code']} - {personnel['first_name']} {personnel['last_name']}"
                self.personnel_filter.addItem(display_text, personnel['id'])
                
        except Exception as e:
            logger.error(f"Error loading personnel filter: {e}")
    
    def load_personnel_combo(self):
        """Load personnel for combo box"""
        try:
            query = "SELECT id, employee_code, first_name, last_name FROM personnel WHERE is_active = TRUE"
            results = self.db.fetch_all(query)
            
            for personnel in results:
                display_text = f"{personnel['employee_code']} - {personnel['first_name']} {personnel['last_name']}"
                self.personnel_combo.addItem(display_text, personnel['id'])
                
        except Exception as e:
            logger.error(f"Error loading personnel combo: {e}")
    
    def load_advances_data(self):
        """Load advances data from database"""
        try:
            query = """
                SELECT a.*, p.employee_code, p.first_name, p.last_name
                FROM advances a
                JOIN personnel p ON a.personnel_id = p.id
                ORDER BY a.created_at DESC
            """
            results = self.db.fetch_all(query)
            
            self.advances_table.setRowCount(0)
            
            for row_data in results:
                row_position = self.advances_table.rowCount()
                self.advances_table.insertRow(row_position)
                
                # Action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(5, 2, 5, 2)
                
                edit_btn = ModernButton("✏️")
                edit_btn.setFixedSize(30, 30)
                edit_btn.clicked.connect(lambda checked, id=row_data['id']: self.edit_advance(id))
                
                delete_btn = ModernButton("🗑️")
                delete_btn.setFixedSize(30, 30)
                delete_btn.clicked.connect(lambda checked, id=row_data['id']: self.delete_advance(id))
                
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(delete_btn)
                action_layout.addStretch()
                
                self.advances_table.setCellWidget(row_position, 0, action_widget)
                self.advances_table.setItem(row_position, 1, QTableWidgetItem(str(row_data['employee_code'])))
                self.advances_table.setItem(row_position, 2, QTableWidgetItem(f"{row_data['first_name']} {row_data['last_name']}"))
                self.advances_table.setItem(row_position, 3, QTableWidgetItem(f"{row_data['advance_amount']:,.0f}"))
                
                # Handle date conversion safely
                try:
                    if row_data['advance_date']:
                        date_str = DateConverter.gregorian_to_jalali_str(row_data['advance_date'])
                    else:
                        date_str = ''
                except:
                    date_str = str(row_data['advance_date']) if row_data['advance_date'] else ''
                
                self.advances_table.setItem(row_position, 4, QTableWidgetItem(date_str))
                self.advances_table.setItem(row_position, 5, QTableWidgetItem("تسویه شده" if row_data['is_settled'] else "تسویه نشده"))
                self.advances_table.setItem(row_position, 6, QTableWidgetItem(row_data['description'] or ''))
                
                # Handle created_at date
                try:
                    if row_data['created_at']:
                        created_str = DateConverter.gregorian_to_jalali_str(row_data['created_at'])
                    else:
                        created_str = ''
                except:
                    created_str = str(row_data['created_at']) if row_data['created_at'] else ''
                
                self.advances_table.setItem(row_position, 7, QTableWidgetItem(created_str))
                
        except Exception as e:
            logger.error(f"Error loading advances data: {e}")
            self.show_error_message("خطا", "خطا در بارگذاری اطلاعات مساعده‌ها")
    
    def show_error_message(self, title: str, message: str):
        """Show error message"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()
    
    def show_success_message(self, title: str, message: str):
        """Show success message"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()
    
    def filter_advances(self):
        """Filter advances based on criteria"""
        # Implementation for filtering
        pass
    
    def show_add_dialog(self):
        """Show add advance dialog"""
        self.clear_form()
        self.edit_tab.parent().setCurrentWidget(self.edit_tab)
    
    def clear_form(self):
        """Clear the form"""
        self.selected_advance_id = None
        if self.personnel_combo.count() > 0:
            self.personnel_combo.setCurrentIndex(0)
        self.advance_amount_input.setValue(1000000)
        self.advance_date_input.setDate(QDate.currentDate())
        self.description_input.clear()
        self.is_settled_checkbox.setChecked(False)
        
        self.save_btn.setText("💾 ذخیره مساعده")
    
    def edit_advance(self, advance_id: int):
        """Edit advance information"""
        try:
            query = "SELECT * FROM advances WHERE id = %s"
            advance_data = self.db.fetch_one(query, (advance_id,))
            
            if advance_data:
                self.selected_advance_id = advance_id
                
                # Find and set personnel in combo
                personnel_index = -1
                for i in range(self.personnel_combo.count()):
                    if self.personnel_combo.itemData(i) == advance_data['personnel_id']:
                        personnel_index = i
                        break
                if personnel_index >= 0:
                    self.personnel_combo.setCurrentIndex(personnel_index)
                
                self.advance_amount_input.setValue(float(advance_data['advance_amount']))
                
                if advance_data['advance_date']:
                    self.advance_date_input.setDate(QDate.fromString(str(advance_data['advance_date']), Qt.DateFormat.ISODate))
                
                self.description_input.setText(advance_data['description'] or '')
                self.is_settled_checkbox.setChecked(advance_data['is_settled'])
                
                self.save_btn.setText("💾 به‌روزرسانی مساعده")
                self.edit_tab.parent().setCurrentWidget(self.edit_tab)
                
        except Exception as e:
            logger.error(f"Error editing advance: {e}")
            self.show_error_message("خطا", "خطا در ویرایش اطلاعات مساعده")
    
    def save_advance(self):
        """Save advance information"""
        try:
            if not self.validate_advance_inputs():
                return
            
            personnel_id = self.personnel_combo.currentData()
            
            advance_data = {
                'personnel_id': personnel_id,
                'advance_amount': self.advance_amount_input.value(),
                'advance_date': self.advance_date_input.date().toString(Qt.DateFormat.ISODate),
                'description': self.description_input.text().strip(),
                'is_settled': self.is_settled_checkbox.isChecked()
            }
            
            if self.selected_advance_id:
                # Update existing advance
                query = """
                    UPDATE advances SET 
                    personnel_id = %s, advance_amount = %s, advance_date = %s,
                    description = %s, is_settled = %s
                    WHERE id = %s
                """
                params = tuple(advance_data.values()) + (self.selected_advance_id,)
            else:
                # Insert new advance
                query = """
                    INSERT INTO advances 
                    (personnel_id, advance_amount, advance_date, description, is_settled)
                    VALUES (%s, %s, %s, %s, %s)
                """
                params = tuple(advance_data.values())
            
            if self.db.execute_query(query, params):
                self.show_success_message("موفقیت", "اطلاعات مساعده با موفقیت ذخیره شد")
                self.clear_form()
                self.load_advances_data()
            else:
                self.show_error_message("خطا", "خطا در ذخیره‌سازی اطلاعات مساعده")
                
        except Exception as e:
            logger.error(f"Error saving advance: {e}")
            self.show_error_message("خطا", "خطا در ذخیره‌سازی اطلاعات مساعده")
    
    def validate_advance_inputs(self) -> bool:
        """Validate advance form inputs"""
        if self.personnel_combo.currentIndex() == -1:
            self.show_error_message("خطا", "لطفاً پرسنل را انتخاب کنید")
            return False
            
        if self.advance_amount_input.value() <= 0:
            self.show_error_message("خطا", "مبلغ مساعده باید بیشتر از صفر باشد")
            return False
            
        return True
    
    def delete_advance(self, advance_id: int):
        """Delete advance record"""
        reply = QMessageBox.question(
            self,
            "تأیید حذف",
            "آیا از حذف این مساعده اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = "DELETE FROM advances WHERE id = %s"
                if self.db.execute_query(query, (advance_id,)):
                    self.show_success_message("موفقیت", "مساعده با موفقیت حذف شد")
                    self.load_advances_data()
                else:
                    self.show_error_message("خطا", "خطا در حذف مساعده")
            except Exception as e:
                logger.error(f"Error deleting advance: {e}")
                self.show_error_message("خطا", "خطا در حذف مساعده")