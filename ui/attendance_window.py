from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox,
                            QCheckBox, QTabWidget, QHeaderView, QMessageBox,
                            QFormLayout, QGroupBox, QCalendarWidget)
from PyQt6.QtCore import QDate, Qt
from widgets.modern_button import ModernButton
from widgets.modern_input import ModernInput
from widgets.modern_table import ModernTable
from database.database_manager import DatabaseManager
from utils.date_converter import DateConverter
from utils.font_manager import FontManager
import logging

logger = logging.getLogger(__name__)

class AttendanceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.selected_attendance_id = None
        self.setup_ui()
        self.load_attendance_data()
        
    def setup_ui(self):
        """Setup attendance management UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("مدیریت حضور و غیاب")
        title_label.setFont(FontManager.get_font(point_size=16, bold=True))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add new attendance button
        self.add_btn = ModernButton("➕ ثبت حضور و غیاب")
        self.add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(self.add_btn)
        
        # Import button
        self.import_btn = ModernButton("📤 وارد کردن از فایل")
        self.import_btn.clicked.connect(self.import_attendance)
        header_layout.addWidget(self.import_btn)
        
        main_layout.addLayout(header_layout)
        
        # Create tabs
        self.setup_tabs(main_layout)
    
    def setup_tabs(self, main_layout: QVBoxLayout):
        """Setup tabs for attendance management"""
        tabs = QTabWidget()
        
        # Attendance list tab
        self.setup_attendance_list_tab(tabs)
        
        # Add/Edit tab
        self.setup_edit_tab(tabs)
        
        # Monthly report tab
        self.setup_report_tab(tabs)
        
        main_layout.addWidget(tabs)
    
    def setup_attendance_list_tab(self, tabs: QTabWidget):
        """Setup attendance list tab"""
        list_tab = QWidget()
        layout = QVBoxLayout(list_tab)
        
        # Filter section
        self.setup_filters(layout)
        
        # Attendance table
        self.setup_attendance_table(layout)
        
        tabs.addTab(list_tab, "لیست حضور و غیاب")
    
    def setup_filters(self, layout: QVBoxLayout):
        """Setup filter section"""
        filter_layout = QHBoxLayout()
        
        # Month filter
        self.month_filter = QComboBox()
        months = ["همه ماه‌ها"] + [f"{i} - {DateConverter.get_jalali_month_name(i)}" for i in range(1, 13)]
        self.month_filter.addItems(months)
        self.month_filter.currentTextChanged.connect(self.filter_attendance)
        filter_layout.addWidget(QLabel("ماه:"))
        filter_layout.addWidget(self.month_filter)
        
        # Year filter
        self.year_filter = QComboBox()
        current_year = DateConverter.get_current_jalali_date().year
        years = ["همه سال‌ها"] + [str(year) for year in range(current_year-2, current_year+1)]
        self.year_filter.addItems(years)
        self.year_filter.currentTextChanged.connect(self.filter_attendance)
        filter_layout.addWidget(QLabel("سال:"))
        filter_layout.addWidget(self.year_filter)
        
        # Personnel filter
        self.personnel_filter = QComboBox()
        self.personnel_filter.addItem("همه پرسنل")
        self.load_personnel_filter()
        self.personnel_filter.currentTextChanged.connect(self.filter_attendance)
        filter_layout.addWidget(QLabel("پرسنل:"))
        filter_layout.addWidget(self.personnel_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
    
    def setup_attendance_table(self, layout: QVBoxLayout):
        """Setup attendance table"""
        self.attendance_table = ModernTable()
        self.attendance_table.setColumnCount(9)
        self.attendance_table.setHorizontalHeaderLabels([
            "عملیات", "کد پرسنلی", "نام و نام خانوادگی", "تاریخ", 
            "ساعت ورود", "ساعت خروج", "اضافه کاری (ساعت)", 
            "نوع حضور", "توضیحات"
        ])
        
        # Set column widths
        header = self.attendance_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 100)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.attendance_table)
    
    def setup_edit_tab(self, tabs: QTabWidget):
        """Setup add/edit attendance tab"""
        self.edit_tab = QWidget()
        layout = QVBoxLayout(self.edit_tab)
        
        # Attendance form
        form_group = QGroupBox("ثبت حضور و غیاب")
        form_layout = QFormLayout(form_group)
        
        # Personnel selection
        self.personnel_combo = QComboBox()
        self.load_personnel_combo()
        form_layout.addRow("پرسنل:", self.personnel_combo)
        
        # Date
        self.attendance_date = QDateEdit()
        self.attendance_date.setCalendarPopup(True)
        self.attendance_date.setDate(QDate.currentDate())
        self.attendance_date.setDisplayFormat("yyyy/MM/dd")
        form_layout.addRow("تاریخ:", self.attendance_date)
        
        # Time inputs
        time_layout = QHBoxLayout()
        
        self.entry_time = QComboBox()
        self.exit_time = QComboBox()
        
        # Generate time options
        times = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 30]]
        self.entry_time.addItems(times)
        self.exit_time.addItems(times)
        
        self.entry_time.setCurrentText("08:00")
        self.exit_time.setCurrentText("16:30")
        
        time_layout.addWidget(QLabel("خروج:"))
        time_layout.addWidget(self.exit_time)
        time_layout.addWidget(QLabel("ورود:"))
        time_layout.addWidget(self.entry_time)
        
        form_layout.addRow("ساعت کار:", time_layout)
        
        # Overtime
        self.overtime_input = QDoubleSpinBox()
        self.overtime_input.setRange(0, 24)
        self.overtime_input.setSuffix(" ساعت")
        self.overtime_input.setSingleStep(0.5)
        form_layout.addRow("اضافه کاری:", self.overtime_input)
        
        # Attendance type
        self.attendance_type = QComboBox()
        self.attendance_type.addItems(["حاضر", "مرخصی استعلاجی", "مرخصی استحقاقی", "غیبت", "تعطیل"])
        form_layout.addRow("نوع حضور:", self.attendance_type)
        
        # Description
        self.description_input = ModernInput()
        self.description_input.setPlaceholderText("توضیحات اختیاری...")
        form_layout.addRow("توضیحات:", self.description_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = ModernButton("💾 ذخیره حضور و غیاب")
        self.save_btn.clicked.connect(self.save_attendance)
        self.cancel_btn = ModernButton("❌ انصراف")
        self.cancel_btn.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(form_group)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        tabs.addTab(self.edit_tab, "ثبت / ویرایش")
    
    def setup_report_tab(self, tabs: QTabWidget):
        """Setup monthly report tab"""
        report_tab = QWidget()
        layout = QVBoxLayout(report_tab)
        
        # Report controls
        controls_layout = QHBoxLayout()
        
        self.report_month = QComboBox()
        self.report_month.addItems([DateConverter.get_jalali_month_name(i) for i in range(1, 13)])
        self.report_month.setCurrentIndex(DateConverter.get_current_jalali_date().month - 1)
        
        self.report_year = QComboBox()
        current_year = DateConverter.get_current_jalali_date().year
        self.report_year.addItems([str(year) for year in range(current_year-2, current_year+1)])
        self.report_year.setCurrentText(str(current_year))
        
        generate_btn = ModernButton("📊 تولید گزارش")
        generate_btn.clicked.connect(self.generate_report)
        
        export_btn = ModernButton("📤 خروجی Excel")
        export_btn.clicked.connect(self.export_report)
        
        controls_layout.addWidget(export_btn)
        controls_layout.addWidget(generate_btn)
        controls_layout.addWidget(QLabel("سال:"))
        controls_layout.addWidget(self.report_year)
        controls_layout.addWidget(QLabel("ماه:"))
        controls_layout.addWidget(self.report_month)
        
        layout.addLayout(controls_layout)
        
        # Report table
        self.report_table = ModernTable()
        self.report_table.setColumnCount(8)
        self.report_table.setHorizontalHeaderLabels([
            "کد پرسنلی", "نام و نام خانوادگی", "روزهای کاری", 
            "مرخصی استعلاجی", "مرخصی استحقاقی", "غیبت", 
            "ساعات اضافه کاری", "مجموع حقوق"
        ])
        
        layout.addWidget(self.report_table)
        tabs.addTab(report_tab, "گزارش ماهانه")
    
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
    
    def load_attendance_data(self):
        """Load attendance data from database"""
        try:
            query = """
                SELECT a.*, p.employee_code, p.first_name, p.last_name
                FROM attendance a
                JOIN personnel p ON a.personnel_id = p.id
                ORDER BY a.date DESC
            """
            results = self.db.fetch_all(query)
            
            self.attendance_table.setRowCount(0)
            
            for row_data in results:
                row_position = self.attendance_table.rowCount()
                self.attendance_table.insertRow(row_position)
                
                # Action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(5, 2, 5, 2)
                
                edit_btn = ModernButton("✏️")
                edit_btn.setFixedSize(30, 30)
                edit_btn.clicked.connect(lambda checked, id=row_data['id']: self.edit_attendance(id))
                
                delete_btn = ModernButton("🗑️")
                delete_btn.setFixedSize(30, 30)
                delete_btn.clicked.connect(lambda checked, id=row_data['id']: self.delete_attendance(id))
                
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(delete_btn)
                action_layout.addStretch()
                
                self.attendance_table.setCellWidget(row_position, 0, action_widget)
                self.attendance_table.setItem(row_position, 1, QTableWidgetItem(str(row_data['employee_code'])))
                self.attendance_table.setItem(row_position, 2, QTableWidgetItem(f"{row_data['first_name']} {row_data['last_name']}"))
                
                # Handle date conversion safely
                try:
                    if row_data['date']:
                        date_str = DateConverter.gregorian_to_jalali_str(row_data['date'])
                    else:
                        date_str = ''
                except:
                    date_str = str(row_data['date']) if row_data['date'] else ''
                
                self.attendance_table.setItem(row_position, 3, QTableWidgetItem(date_str))
                self.attendance_table.setItem(row_position, 4, QTableWidgetItem(str(row_data['entry_time'] or '')))
                self.attendance_table.setItem(row_position, 5, QTableWidgetItem(str(row_data['exit_time'] or '')))
                self.attendance_table.setItem(row_position, 6, QTableWidgetItem(str(row_data['overtime_hours'])))
                self.attendance_table.setItem(row_position, 7, QTableWidgetItem(row_data['absence_type']))
                self.attendance_table.setItem(row_position, 8, QTableWidgetItem(row_data['description'] or ''))
                
        except Exception as e:
            logger.error(f"Error loading attendance data: {e}")
            self.show_error_message("خطا", "خطا در بارگذاری اطلاعات حضور و غیاب")
    
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
    
    def filter_attendance(self):
        """Filter attendance based on criteria"""
        # Implementation for filtering
        pass
    
    def show_add_dialog(self):
        """Show add attendance dialog"""
        self.clear_form()
        self.edit_tab.parent().setCurrentWidget(self.edit_tab)
    
    def clear_form(self):
        """Clear the form"""
        self.selected_attendance_id = None
        if self.personnel_combo.count() > 0:
            self.personnel_combo.setCurrentIndex(0)
        self.attendance_date.setDate(QDate.currentDate())
        self.entry_time.setCurrentText("08:00")
        self.exit_time.setCurrentText("16:30")
        self.overtime_input.setValue(0)
        self.attendance_type.setCurrentText("حاضر")
        self.description_input.clear()
        
        self.save_btn.setText("💾 ذخیره حضور و غیاب")
    
    def edit_attendance(self, attendance_id: int):
        """Edit attendance information"""
        try:
            query = "SELECT * FROM attendance WHERE id = %s"
            attendance_data = self.db.fetch_one(query, (attendance_id,))
            
            if attendance_data:
                self.selected_attendance_id = attendance_id
                
                # Find and set personnel in combo
                personnel_index = -1
                for i in range(self.personnel_combo.count()):
                    if self.personnel_combo.itemData(i) == attendance_data['personnel_id']:
                        personnel_index = i
                        break
                if personnel_index >= 0:
                    self.personnel_combo.setCurrentIndex(personnel_index)
                
                # Set date
                if attendance_data['date']:
                    self.attendance_date.setDate(QDate.fromString(str(attendance_data['date']), Qt.DateFormat.ISODate))
                
                # Set times
                if attendance_data['entry_time']:
                    self.entry_time.setCurrentText(str(attendance_data['entry_time']))
                if attendance_data['exit_time']:
                    self.exit_time.setCurrentText(str(attendance_data['exit_time']))
                
                self.overtime_input.setValue(float(attendance_data['overtime_hours']))
                self.attendance_type.setCurrentText(attendance_data['absence_type'])
                self.description_input.setText(attendance_data['description'] or '')
                
                self.save_btn.setText("💾 به‌روزرسانی حضور و غیاب")
                self.edit_tab.parent().setCurrentWidget(self.edit_tab)
                
        except Exception as e:
            logger.error(f"Error editing attendance: {e}")
            self.show_error_message("خطا", "خطا در ویرایش اطلاعات حضور و غیاب")
    
    def save_attendance(self):
        """Save attendance information"""
        try:
            if not self.validate_attendance_inputs():
                return
            
            personnel_id = self.personnel_combo.currentData()
            
            attendance_data = {
                'personnel_id': personnel_id,
                'date': self.attendance_date.date().toString(Qt.DateFormat.ISODate),
                'entry_time': self.entry_time.currentText(),
                'exit_time': self.exit_time.currentText(),
                'overtime_hours': self.overtime_input.value(),
                'absence_type': self.attendance_type.currentText(),
                'description': self.description_input.text().strip()
            }
            
            if self.selected_attendance_id:
                # Update existing attendance
                query = """
                    UPDATE attendance SET 
                    personnel_id = %s, date = %s, entry_time = %s, exit_time = %s,
                    overtime_hours = %s, absence_type = %s, description = %s
                    WHERE id = %s
                """
                params = tuple(attendance_data.values()) + (self.selected_attendance_id,)
            else:
                # Insert new attendance
                query = """
                    INSERT INTO attendance 
                    (personnel_id, date, entry_time, exit_time, overtime_hours, absence_type, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                params = tuple(attendance_data.values())
            
            if self.db.execute_query(query, params):
                self.show_success_message("موفقیت", "اطلاعات حضور و غیاب با موفقیت ذخیره شد")
                self.clear_form()
                self.load_attendance_data()
            else:
                self.show_error_message("خطا", "خطا در ذخیره‌سازی اطلاعات حضور و غیاب")
                
        except Exception as e:
            logger.error(f"Error saving attendance: {e}")
            self.show_error_message("خطا", "خطا در ذخیره‌سازی اطلاعات حضور و غیاب")
    
    def validate_attendance_inputs(self) -> bool:
        """Validate attendance form inputs"""
        if self.personnel_combo.currentIndex() == -1:
            self.show_error_message("خطا", "لطفاً پرسنل را انتخاب کنید")
            return False
            
        return True
    
    def delete_attendance(self, attendance_id: int):
        """Delete attendance record"""
        reply = QMessageBox.question(
            self,
            "تأیید حذف",
            "آیا از حذف این رکورد حضور و غیاب اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                query = "DELETE FROM attendance WHERE id = %s"
                if self.db.execute_query(query, (attendance_id,)):
                    self.show_success_message("موفقیت", "رکورد حضور و غیاب با موفقیت حذف شد")
                    self.load_attendance_data()
                else:
                    self.show_error_message("خطا", "خطا در حذف رکورد حضور و غیاب")
            except Exception as e:
                logger.error(f"Error deleting attendance: {e}")
                self.show_error_message("خطا", "خطا در حذف رکورد حضور و غیاب")
    
    def import_attendance(self):
        """Import attendance from file"""
        # Implementation for file import
        self.show_success_message("اطلاع", "قابلیت وارد کردن از فایل به زودی اضافه خواهد شد")
    
    def generate_report(self):
        """Generate monthly report"""
        try:
            month = self.report_month.currentIndex() + 1
            year = int(self.report_year.currentText())
            
            query = """
                SELECT 
                    p.employee_code,
                    p.first_name || ' ' || p.last_name as full_name,
                    COUNT(CASE WHEN a.absence_type = 'حاضر' THEN 1 END) as work_days,
                    COUNT(CASE WHEN a.absence_type = 'مرخصی استعلاجی' THEN 1 END) as sick_leave,
                    COUNT(CASE WHEN a.absence_type = 'مرخصی استحقاقی' THEN 1 END) as annual_leave,
                    COUNT(CASE WHEN a.absence_type = 'غیبت' THEN 1 END) as absence_days,
                    COALESCE(SUM(a.overtime_hours), 0) as total_overtime
                FROM personnel p
                LEFT JOIN attendance a ON p.id = a.personnel_id 
                    AND EXTRACT(YEAR FROM a.date) = %s 
                    AND EXTRACT(MONTH FROM a.date) = %s
                WHERE p.is_active = TRUE
                GROUP BY p.id, p.employee_code, p.first_name, p.last_name
                ORDER BY p.employee_code
            """
            
            results = self.db.fetch_all(query, (year, month))
            
            self.report_table.setRowCount(0)
            
            for row_data in results:
                row_position = self.report_table.rowCount()
                self.report_table.insertRow(row_position)
                
                self.report_table.setItem(row_position, 0, QTableWidgetItem(str(row_data['employee_code'])))
                self.report_table.setItem(row_position, 1, QTableWidgetItem(row_data['full_name']))
                self.report_table.setItem(row_position, 2, QTableWidgetItem(str(row_data['work_days'])))
                self.report_table.setItem(row_position, 3, QTableWidgetItem(str(row_data['sick_leave'])))
                self.report_table.setItem(row_position, 4, QTableWidgetItem(str(row_data['annual_leave'])))
                self.report_table.setItem(row_position, 5, QTableWidgetItem(str(row_data['absence_days'])))
                self.report_table.setItem(row_position, 6, QTableWidgetItem(str(row_data['total_overtime'])))
                self.report_table.setItem(row_position, 7, QTableWidgetItem("محاسبه شود"))
                
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            self.show_error_message("خطا", "خطا در تولید گزارش")
    
    def export_report(self):
        """Export report to Excel"""
        # Implementation for Excel export
        self.show_success_message("اطلاع", "قابلیت خروجی Excel به زودی اضافه خواهد شد")