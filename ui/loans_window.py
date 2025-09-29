from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox,
                            QSpinBox, QCheckBox, QTabWidget, QHeaderView, 
                            QMessageBox, QFormLayout, QGroupBox)
from PyQt6.QtCore import QDate, Qt
from widgets.modern_button import ModernButton
from widgets.modern_input import ModernInput
from widgets.modern_table import ModernTable
from database.database_manager import DatabaseManager
from utils.date_converter import DateConverter
from utils.font_manager import FontManager
import logging

logger = logging.getLogger(__name__)

class LoansWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.selected_loan_id = None
        self.setup_ui()
        self.load_loans_data()
        
    def setup_ui(self):
        """Setup loans management UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("مدیریت وام‌ها")
        title_label.setFont(FontManager.get_font(point_size=16, bold=True))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add new loan button
        self.add_btn = ModernButton("➕ ثبت وام جدید")
        self.add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(header_layout)
        
        # Create tabs
        self.setup_tabs(main_layout)
    
    def setup_tabs(self, main_layout: QVBoxLayout):
        """Setup tabs for loans management"""
        tabs = QTabWidget()
        
        # Loans list tab
        self.setup_loans_list_tab(tabs)
        
        # Add/Edit tab
        self.setup_edit_tab(tabs)
        
        main_layout.addWidget(tabs)
    
    def setup_loans_list_tab(self, tabs: QTabWidget):
        """Setup loans list tab"""
        list_tab = QWidget()
        layout = QVBoxLayout(list_tab)
        
        # Filter section
        self.setup_filters(layout)
        
        # Loans table
        self.setup_loans_table(layout)
        
        tabs.addTab(list_tab, "لیست وام‌ها")
    
    def setup_filters(self, layout: QVBoxLayout):
        """Setup filter section"""
        filter_layout = QHBoxLayout()
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItems(["همه", "فعال", "تسویه شده"])
        self.status_filter.currentTextChanged.connect(self.filter_loans)
        filter_layout.addWidget(QLabel("وضعیت:"))
        filter_layout.addWidget(self.status_filter)
        
        # Personnel filter
        self.personnel_filter = QComboBox()
        self.personnel_filter.addItem("همه پرسنل")
        self.load_personnel_filter()
        self.personnel_filter.currentTextChanged.connect(self.filter_loans)
        filter_layout.addWidget(QLabel("پرسنل:"))
        filter_layout.addWidget(self.personnel_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
    
    def setup_loans_table(self, layout: QVBoxLayout):
        """Setup loans table"""
        self.loans_table = ModernTable()
        self.loans_table.setColumnCount(10)
        self.loans_table.setHorizontalHeaderLabels([
            "عملیات", "کد پرسنلی", "نام و نام خانوادگی", "مبلغ وام", 
            "تعداد اقساط", "اقساط باقیمانده", "مبلغ قسط", 
            "تاریخ شروع", "وضعیت", "توضیحات"
        ])
        
        # Set column widths
        header = self.loans_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 100)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.loans_table)
    
    def setup_edit_tab(self, tabs: QTabWidget):
        """Setup add/edit loan tab"""
        self.edit_tab = QWidget()
        layout = QVBoxLayout(self.edit_tab)
        
        # Loan form
        form_group = QGroupBox("ثبت وام")
        form_layout = QFormLayout(form_group)
        
        # Personnel selection
        self.personnel_combo = QComboBox()
        self.load_personnel_combo()
        form_layout.addRow("پرسنل:", self.personnel_combo)
        
        # Loan amount
        self.loan_amount_input = QDoubleSpinBox()
        self.loan_amount_input.setRange(0, 1000000000)
        self.loan_amount_input.setValue(10000000)
        self.loan_amount_input.setSuffix(" ریال")
        form_layout.addRow("مبلغ وام:", self.loan_amount_input)
        
        # Installments
        installments_layout = QHBoxLayout()
        
        self.installment_count_input = QSpinBox()
        self.installment_count_input.setRange(1, 120)
        self.installment_count_input.setValue(12)
        self.installment_count_input.valueChanged.connect(self.calculate_installment)
        
        self.installment_amount_input = QDoubleSpinBox()
        self.installment_amount_input.setRange(0, 100000000)
        self.installment_amount_input.setSuffix(" ریال")
        self.installment_amount_input.setReadOnly(True)
        
        installments_layout.addWidget(QLabel("مبلغ قسط:"))
        installments_layout.addWidget(self.installment_amount_input)
        installments_layout.addWidget(QLabel("تعداد اقساط:"))
        installments_layout.addWidget(self.installment_count_input)
        
        form_layout.addRow("اقساط:", installments_layout)
        
        # Start date
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setDisplayFormat("yyyy/MM/dd")
        form_layout.addRow("تاریخ شروع:", self.start_date_input)
        
        # Description
        self.description_input = ModernInput()
        self.description_input.setPlaceholderText("توضیحات اختیاری...")
        form_layout.addRow("توضیحات:", self.description_input)
        
        # Active status
        self.is_active_checkbox = QCheckBox("وام فعال")
        self.is_active_checkbox.setChecked(True)
        form_layout.addRow("", self.is_active_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = ModernButton("💾 ذخیره وام")
        self.save_btn.clicked.connect(self.save_loan)
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
    
    def load_loans_data(self):
        """Load loans data from database"""
        try:
            query = """
                SELECT l.*, p.employee_code, p.first_name, p.last_name
                FROM loans l
                JOIN personnel p ON l.personnel_id = p.id
                ORDER BY l.created_at DESC
            """
            results = self.db.fetch_all(query)
            
            self.loans_table.setRowCount(0)
            
            for row_data in results:
                row_position = self.loans_table.rowCount()
                self.loans_table.insertRow(row_position)
                
                # Action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(5, 2, 5, 2)
                
                edit_btn = ModernButton("✏️")
                edit_btn.setFixedSize(30, 30)
                edit_btn.clicked.connect(lambda checked, id=row_data['id']: self.edit_loan(id))
                
                delete_btn = ModernButton("🗑️")
                delete_btn.setFixedSize(30, 30)
                delete_btn.clicked.connect(lambda checked, id=row_data['id']: self.delete_loan(id))
                
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(delete_btn)
                action_layout.addStretch()
                
                self.loans_table.setCellWidget(row_position, 0, action_widget)
                self.loans_table.setItem(row_position, 1, QTableWidgetItem(str(row_data['employee_code'])))
                self.loans_table.setItem(row_position, 2, QTableWidgetItem(f"{row_data['first_name']} {row_data['last_name']}"))
                self.loans_table.setItem(row_position, 3, QTableWidgetItem(f"{row_data['loan_amount']:,.0f}"))
                self.loans_table.setItem(row_position, 4, QTableWidgetItem(str(row_data['total_installments'])))
                self.loans_table.setItem(row_position, 5, QTableWidgetItem(str(row_data['remaining_installments'])))
                self.loans_table.setItem(row_position, 6, QTableWidgetItem(f"{row_data['installment_amount']:,.0f}"))
                
                # Handle date conversion safely
                try:
                    if row_data['start_date']:
                        date_str = DateConverter.gregorian_to_jalali_str(row_data['start_date'])
                    else:
                        date_str = ''
                except:
                    date_str = str(row_data['start_date']) if row_data['start_date'] else ''
                
                self.loans_table.setItem(row_position, 7, QTableWidgetItem(date_str))
                self.loans_table.setItem(row_position, 8, QTableWidgetItem("فعال" if row_data['is_active'] else "تسویه شده"))
                self.loans_table.setItem(row_position, 9, QTableWidgetItem(row_data['description'] or ''))
                
        except Exception as e:
            logger.error(f"Error loading loans data: {e}")
            self.show_error_message("خطا", "خطا در بارگذاری اطلاعات وام‌ها")
    
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
    
    def filter_loans(self):
        """Filter loans based on criteria"""
        # Implementation for filtering
        pass
    
    def show_add_dialog(self):
        """Show add loan dialog"""
        self.clear_form()
        self.edit_tab.parent().setCurrentWidget(self.edit_tab)
    
    def clear_form(self):
        """Clear the form"""
        self.selected_loan_id = None
        if self.personnel_combo.count() > 0:
            self.personnel_combo.setCurrentIndex(0)
        self.loan_amount_input.setValue(10000000)
        self.installment_count_input.setValue(12)
        self.start_date_input.setDate(QDate.currentDate())
        self.description_input.clear()
        self.is_active_checkbox.setChecked(True)
        
        self.calculate_installment()
        self.save_btn.setText("💾 ذخیره وام")
    
    def calculate_installment(self):
        """Calculate installment amount"""
        loan_amount = self.loan_amount_input.value()
        installment_count = self.installment_count_input.value()
        
        if installment_count > 0:
            installment_amount = loan_amount / installment_count
            self.installment_amount_input.setValue(installment_amount)
    
    def edit_loan(self, loan_id: int):
        """Edit loan information"""
        try:
            query = "SELECT * FROM loans WHERE id = %s"
            loan_data = self.db.fetch_one(query, (loan_id,))
            
            if loan_data:
                self.selected_loan_id = loan_id
                
                # Find and set personnel in combo
                personnel_index = -1
                for i in range(self.personnel_combo.count()):
                    if self.personnel_combo.itemData(i) == loan_data['personnel_id']:
                        personnel_index = i
                        break
                if personnel_index >= 0:
                    self.personnel_combo.setCurrentIndex(personnel_index)
                
                self.loan_amount_input.setValue(float(loan_data['loan_amount']))
                self.installment_count_input.setValue(loan_data['total_installments'])
                
                if loan_data['start_date']:
                    self.start_date_input.setDate(QDate.fromString(str(loan_data['start_date']), Qt.DateFormat.ISODate))
                
                self.description_input.setText(loan_data['description'] or '')
                self.is_active_checkbox.setChecked(loan_data['is_active'])
                
                self.calculate_installment()
                self.save_btn.setText("💾 به‌روزرسانی وام")
                self.edit_tab.parent().setCurrentWidget(self.edit_tab)
                
        except Exception as e:
            logger.error(f"Error editing loan: {e}")
            self.show_error_message("خطا", "خطا در ویرایش اطلاعات وام")
    
    def save_loan(self):
        """Save loan information"""
        try:
            if not self.validate_loan_inputs():
                return
            
            personnel_id = self.personnel_combo.currentData()
            
            loan_data = {
                'personnel_id': personnel_id,
                'loan_amount': self.loan_amount_input.value(),
                'installment_amount': self.installment_amount_input.value(),
                'remaining_installments': self.installment_count_input.value(),
                'total_installments': self.installment_count_input.value(),
                'start_date': self.start_date_input.date().toString(Qt.DateFormat.ISODate),
                'description': self.description_input.text().strip(),
                'is_active': self.is_active_checkbox.isChecked()
            }
            
            if self.selected_loan_id:
                # Update existing loan
                query = """
                    UPDATE loans SET 
                    personnel_id = %s, loan_amount = %s, installment_amount = %s,
                    remaining_installments = %s, total_installments = %s, start_date = %s,
                    description = %s, is_active = %s
                    WHERE id = %s
                """
                params = tuple(loan_data.values()) + (self.selected_loan_id,)
            else:
                # Insert new loan
                query = """
                    INSERT INTO loans 
                    (personnel_id, loan_amount, installment_amount, remaining_installments,
                     total_installments, start_date, description, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = tuple(loan_data.values())
            
            if self.db.execute_query(query, params):
                self.show_success_message("موفقیت", "اطلاعات وام با موفقیت ذخیره شد")
                self.clear_form()
                self.load_loans_data()
            else:
                self.show_error_message("خطا", "خطا در ذخیره‌سازی اطلاعات وام")
                
        except Exception as e:
            logger.error(f"Error saving loan: {e}")
            self.show_error_message("خطا", "خطا در ذخیره‌سازی اطلاعات وام")
    
    def validate_loan_inputs(self) -> bool:
        """Validate loan form inputs"""
        if self.personnel_combo.currentIndex() == -1:
            self.show_error_message("خطا", "لطفاً پرسنل را انتخاب کنید")
            return False
            
        if self.loan_amount_input.value() <= 0:
            self.show_error_message("خطا", "مبلغ وام باید بیشتر از صفر باشد")
            return False
            
        if self.installment_count_input.value() <= 0:
            self.show_error_message("خطا", "تعداد اقساط باید بیشتر از صفر باشد")
            return False
            
        return True
    
    def delete_loan(self, loan_id: int):
        """Delete loan record"""
        reply = QMessageBox.question(
            self,
            "تأیید حذف",
            "آیا از حذف این وام اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = "DELETE FROM loans WHERE id = %s"
                if self.db.execute_query(query, (loan_id,)):
                    self.show_success_message("موفقیت", "وام با موفقیت حذف شد")
                    self.load_loans_data()
                else:
                    self.show_error_message("خطا", "خطا در حذف وام")
            except Exception as e:
                logger.error(f"Error deleting loan: {e}")
                self.show_error_message("خطا", "خطا در حذف وام")