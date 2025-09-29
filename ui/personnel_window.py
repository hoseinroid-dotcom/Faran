from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QLineEdit, QComboBox, QDateEdit, QSpinBox,
                            QDoubleSpinBox, QCheckBox, QTabWidget,
                            QHeaderView, QMessageBox, QFormLayout, QGroupBox)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QIcon
from .base_window import BaseWindow
from widgets.modern_button import ModernButton
from widgets.modern_input import ModernInput
from widgets.modern_table import ModernTable
from database.database_manager import DatabaseManager
from utils.date_converter import DateConverter
from utils.font_manager import FontManager
import logging

logger = logging.getLogger(__name__)

class PersonnelWindow(QWidget):  # تغییر از BaseWindow به QWidget
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.selected_personnel_id = None
        self.setup_ui()
        self.load_personnel_data()
        
    def setup_ui(self):
        """Setup personnel management UI"""
        main_layout = QVBoxLayout(self)  # این خط تغییر کرد
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("مدیریت پرسنل")
        title_label.setFont(FontManager.get_font(point_size=16, bold=True))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add new personnel button
        self.add_btn = ModernButton("➕ افزودن پرسنل جدید")
        self.add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(header_layout)
        
        # Create tabs
        self.setup_tabs(main_layout)
    
    def setup_tabs(self, main_layout: QVBoxLayout):
        """Setup tabs for personnel management"""
        tabs = QTabWidget()
        
        # Personnel list tab
        self.setup_personnel_list_tab(tabs)
        
        # Add/Edit tab
        self.setup_edit_tab(tabs)
        
        main_layout.addWidget(tabs)
    
    def setup_personnel_list_tab(self, tabs: QTabWidget):
        """Setup personnel list tab"""
        list_tab = QWidget()
        layout = QVBoxLayout(list_tab)
        
        # Search and filter
        self.setup_search_filter(layout)
        
        # Personnel table
        self.setup_personnel_table(layout)
        
        tabs.addTab(list_tab, "لیست پرسنل")
    
    def setup_search_filter(self, layout: QVBoxLayout):
        """Setup search and filter section"""
        search_layout = QHBoxLayout()
        
        # Search input
        self.search_input = ModernInput()
        self.search_input.setPlaceholderText("جستجو بر اساس نام، کد پرسنلی، کد ملی...")
        self.search_input.textChanged.connect(self.filter_personnel)
        search_layout.addWidget(self.search_input)
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItems(["همه", "فعال", "غیرفعال"])
        self.status_filter.currentTextChanged.connect(self.filter_personnel)
        search_layout.addWidget(QLabel("وضعیت:"))
        search_layout.addWidget(self.status_filter)
        
        layout.addLayout(search_layout)
    
    def setup_personnel_table(self, layout: QVBoxLayout):
        """Setup personnel table"""
        self.personnel_table = ModernTable()
        self.personnel_table.setColumnCount(10)
        self.personnel_table.setHorizontalHeaderLabels([
            "عملیات", "کد پرسنلی", "نام و نام خانوادگی", "کد ملی", 
            "تاریخ استخدام", "سمت", "حقوق پایه", "تعداد فرزندان", 
            "وضعیت", "تاریخ ایجاد"
        ])
        
        # Set column widths
        header = self.personnel_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 120)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.personnel_table)
    
    def setup_edit_tab(self, tabs: QTabWidget):
        """Setup add/edit personnel tab"""
        self.edit_tab = QWidget()
        layout = QVBoxLayout(self.edit_tab)
        
        # Personal info group
        personal_group = QGroupBox("اطلاعات فردی")
        personal_layout = QFormLayout(personal_group)
        
        self.employee_code_input = ModernInput()
        self.first_name_input = ModernInput()
        self.last_name_input = ModernInput()
        self.national_id_input = ModernInput()
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate.currentDate().addYears(-25))
        
        personal_layout.addRow("کد پرسنلی:", self.employee_code_input)
        personal_layout.addRow("نام:", self.first_name_input)
        personal_layout.addRow("نام خانوادگی:", self.last_name_input)
        personal_layout.addRow("کد ملی:", self.national_id_input)
        personal_layout.addRow("تاریخ تولد:", self.birth_date_input)
        
        # Employment info group
        employment_group = QGroupBox("اطلاعات استخدام")
        employment_layout = QFormLayout(employment_group)
        
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        self.position_input = ModernInput()
        self.base_salary_input = QDoubleSpinBox()
        self.base_salary_input.setRange(0, 1000000000)
        self.base_salary_input.setValue(56000000)
        self.base_salary_input.setSuffix(" ریال")
        
        employment_layout.addRow("تاریخ استخدام:", self.hire_date_input)
        employment_layout.addRow("سمت:", self.position_input)
        employment_layout.addRow("حقوق پایه:", self.base_salary_input)
        
        # Allowances group
        allowances_group = QGroupBox("حقوق و مزایا")
        allowances_layout = QFormLayout(allowances_group)
        
        self.housing_allowance_input = QDoubleSpinBox()
        self.housing_allowance_input.setRange(0, 1)
        self.housing_allowance_input.setValue(0.25)
        self.housing_allowance_input.setSingleStep(0.05)
        self.housing_allowance_input.setSuffix(" %")
        
        self.family_allowance_input = QDoubleSpinBox()
        self.family_allowance_input.setRange(0, 1)
        self.family_allowance_input.setValue(0.1)
        self.family_allowance_input.setSingleStep(0.05)
        self.family_allowance_input.setSuffix(" %")
        
        self.children_count_input = QSpinBox()
        self.children_count_input.setRange(0, 10)
        
        self.is_active_checkbox = QCheckBox("فعال")
        self.is_active_checkbox.setChecked(True)
        
        allowances_layout.addRow("حق مسکن:", self.housing_allowance_input)
        allowances_layout.addRow("حق عائله:", self.family_allowance_input)
        allowances_layout.addRow("تعداد فرزندان:", self.children_count_input)
        allowances_layout.addRow("", self.is_active_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = ModernButton("💾 ذخیره اطلاعات")
        self.save_btn.clicked.connect(self.save_personnel)
        self.cancel_btn = ModernButton("❌ انصراف")
        self.cancel_btn.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # Add groups to layout
        layout.addWidget(personal_group)
        layout.addWidget(employment_group)
        layout.addWidget(allowances_group)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        tabs.addTab(self.edit_tab, "ثبت / ویرایش")
    
    def load_personnel_data(self):
        """Load personnel data from database"""
        try:
            query = """
                SELECT id, employee_code, first_name, last_name, national_id,
                       hire_date, position, base_salary, children_count, is_active,
                       created_at
                FROM personnel 
                ORDER BY created_at DESC
            """
            results = self.db.fetch_all(query)
            
            self.personnel_table.setRowCount(0)
            
            for row_data in results:
                row_position = self.personnel_table.rowCount()
                self.personnel_table.insertRow(row_position)
                
                # Action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(5, 2, 5, 2)
                
                edit_btn = ModernButton("✏️")
                edit_btn.setFixedSize(30, 30)
                edit_btn.clicked.connect(lambda checked, id=row_data['id']: self.edit_personnel(id))
                
                delete_btn = ModernButton("🗑️")
                delete_btn.setFixedSize(30, 30)
                delete_btn.clicked.connect(lambda checked, id=row_data['id']: self.delete_personnel(id))
                
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(delete_btn)
                action_layout.addStretch()
                
                self.personnel_table.setCellWidget(row_position, 0, action_widget)
                self.personnel_table.setItem(row_position, 1, QTableWidgetItem(str(row_data['employee_code'])))
                self.personnel_table.setItem(row_position, 2, QTableWidgetItem(f"{row_data['first_name']} {row_data['last_name']}"))
                self.personnel_table.setItem(row_position, 3, QTableWidgetItem(str(row_data['national_id'])))
                self.personnel_table.setItem(row_position, 4, QTableWidgetItem(DateConverter.gregorian_to_jalali_str(row_data['hire_date'])))
                self.personnel_table.setItem(row_position, 5, QTableWidgetItem(row_data['position'] or ''))
                self.personnel_table.setItem(row_position, 6, QTableWidgetItem(f"{row_data['base_salary']:,.0f}"))
                self.personnel_table.setItem(row_position, 7, QTableWidgetItem(str(row_data['children_count'])))
                self.personnel_table.setItem(row_position, 8, QTableWidgetItem("فعال" if row_data['is_active'] else "غیرفعال"))
                self.personnel_table.setItem(row_position, 9, QTableWidgetItem(DateConverter.gregorian_to_jalali_str(row_data['created_at'])))
                
        except Exception as e:
            logger.error(f"Error loading personnel data: {e}")
            self.show_error_message("خطا", "خطا در بارگذاری اطلاعات پرسنل")
    
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
    
    def filter_personnel(self):
        """Filter personnel based on search criteria"""
        # Implementation for filtering
        pass
    
    def show_add_dialog(self):
        """Show add personnel dialog"""
        self.clear_form()
        self.edit_tab.parent().setCurrentWidget(self.edit_tab)
    
    def clear_form(self):
        """Clear the form"""
        self.selected_personnel_id = None
        self.employee_code_input.clear()
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.national_id_input.clear()
        self.birth_date_input.setDate(QDate.currentDate().addYears(-25))
        self.hire_date_input.setDate(QDate.currentDate())
        self.position_input.clear()
        self.base_salary_input.setValue(56000000)
        self.housing_allowance_input.setValue(0.25)
        self.family_allowance_input.setValue(0.1)
        self.children_count_input.setValue(0)
        self.is_active_checkbox.setChecked(True)
        
        self.save_btn.setText("💾 ذخیره اطلاعات")
    
    def edit_personnel(self, personnel_id: int):
        """Edit personnel information"""
        try:
            query = "SELECT * FROM personnel WHERE id = %s"
            personnel_data = self.db.fetch_one(query, (personnel_id,))
            
            if personnel_data:
                self.selected_personnel_id = personnel_id
                
                self.employee_code_input.setText(str(personnel_data['employee_code']))
                self.first_name_input.setText(personnel_data['first_name'])
                self.last_name_input.setText(personnel_data['last_name'])
                self.national_id_input.setText(str(personnel_data['national_id']))
                
                if personnel_data['birth_date']:
                    self.birth_date_input.setDate(QDate.fromString(str(personnel_data['birth_date']), Qt.DateFormat.ISODate))
                
                self.hire_date_input.setDate(QDate.fromString(str(personnel_data['hire_date']), Qt.DateFormat.ISODate))
                self.position_input.setText(personnel_data['position'] or '')
                self.base_salary_input.setValue(float(personnel_data['base_salary']))
                self.housing_allowance_input.setValue(float(personnel_data['housing_allowance_rate']))
                self.family_allowance_input.setValue(float(personnel_data['family_allowance_rate']))
                self.children_count_input.setValue(personnel_data['children_count'])
                self.is_active_checkbox.setChecked(personnel_data['is_active'])
                
                self.save_btn.setText("💾 به‌روزرسانی اطلاعات")
                self.edit_tab.parent().setCurrentWidget(self.edit_tab)
                
        except Exception as e:
            logger.error(f"Error editing personnel: {e}")
            self.show_error_message("خطا", "خطا در ویرایش اطلاعات پرسنل")
    
    def save_personnel(self):
        """Save personnel information"""
        try:
            # Validate inputs
            if not self.validate_inputs():
                return
            
            personnel_data = {
                'employee_code': self.employee_code_input.text().strip(),
                'first_name': self.first_name_input.text().strip(),
                'last_name': self.last_name_input.text().strip(),
                'national_id': self.national_id_input.text().strip(),
                'birth_date': self.birth_date_input.date().toString(Qt.DateFormat.ISODate),
                'hire_date': self.hire_date_input.date().toString(Qt.DateFormat.ISODate),
                'position': self.position_input.text().strip(),
                'base_salary': self.base_salary_input.value(),
                'housing_allowance_rate': self.housing_allowance_input.value(),
                'family_allowance_rate': self.family_allowance_input.value(),
                'children_count': self.children_count_input.value(),
                'is_active': self.is_active_checkbox.isChecked()
            }
            
            if self.selected_personnel_id:
                # Update existing personnel
                query = """
                    UPDATE personnel SET 
                    employee_code = %s, first_name = %s, last_name = %s, 
                    national_id = %s, birth_date = %s, hire_date = %s,
                    position = %s, base_salary = %s, housing_allowance_rate = %s,
                    family_allowance_rate = %s, children_count = %s, is_active = %s,
                    updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                params = tuple(personnel_data.values()) + (self.selected_personnel_id,)
            else:
                # Insert new personnel
                query = """
                    INSERT INTO personnel 
                    (employee_code, first_name, last_name, national_id, birth_date,
                     hire_date, position, base_salary, housing_allowance_rate,
                     family_allowance_rate, children_count, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = tuple(personnel_data.values())
            
            if self.db.execute_query(query, params):
                self.show_success_message("موفقیت", "اطلاعات پرسنل با موفقیت ذخیره شد")
                self.clear_form()
                self.load_personnel_data()
            else:
                self.show_error_message("خطا", "خطا در ذخیره‌سازی اطلاعات پرسنل")
                
        except Exception as e:
            logger.error(f"Error saving personnel: {e}")
            self.show_error_message("خطا", "خطا در ذخیره‌سازی اطلاعات پرسنل")
    
    def validate_inputs(self) -> bool:
        """Validate form inputs"""
        if not self.employee_code_input.text().strip():
            self.show_error_message("خطا", "لطفاً کد پرسنلی را وارد کنید")
            return False
        
        if not self.first_name_input.text().strip():
            self.show_error_message("خطا", "لطفاً نام را وارد کنید")
            return False
            
        if not self.last_name_input.text().strip():
            self.show_error_message("خطا", "لطفاً نام خانوادگی را وارد کنید")
            return False
            
        if not self.national_id_input.text().strip():
            self.show_error_message("خطا", "لطفاً کد ملی را وارد کنید")
            return False
            
        if len(self.national_id_input.text().strip()) != 10:
            self.show_error_message("خطا", "کد ملی باید ۱۰ رقمی باشد")
            return False
            
        return True
    
    def delete_personnel(self, personnel_id: int):
        """Delete personnel record"""
        reply = QMessageBox.question(
            self,
            "تأیید حذف",
            "آیا از حذف این پرسنل اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = "DELETE FROM personnel WHERE id = %s"
                if self.db.execute_query(query, (personnel_id,)):
                    self.show_success_message("موفقیت", "پرسنل با موفقیت حذف شد")
                    self.load_personnel_data()
                else:
                    self.show_error_message("خطا", "خطا در حذف پرسنل")
            except Exception as e:
                logger.error(f"Error deleting personnel: {e}")
                self.show_error_message("خطا", "خطا در حذف پرسنل")