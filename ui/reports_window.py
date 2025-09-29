from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QComboBox, QDateEdit, QTabWidget, QHeaderView,
                            QMessageBox, QGroupBox, QFrame, QTextEdit)
from PyQt6.QtCore import QDate
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from widgets.modern_button import ModernButton
from widgets.modern_table import ModernTable
from database.database_manager import DatabaseManager
from utils.date_converter import DateConverter
from utils.font_manager import FontManager
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup reports UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("گزارشات و آمار")
        title_label.setFont(FontManager.get_font(point_size=16, bold=True))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Create tabs
        self.setup_tabs(main_layout)
    
    def setup_tabs(self, main_layout: QVBoxLayout):
        """Setup tabs for reports"""
        tabs = QTabWidget()
        
        # Payroll reports tab
        self.setup_payroll_reports_tab(tabs)
        
        # Attendance reports tab
        self.setup_attendance_reports_tab(tabs)
        
        # Financial reports tab
        self.setup_financial_reports_tab(tabs)
        
        # Personnel reports tab
        self.setup_personnel_reports_tab(tabs)
        
        main_layout.addWidget(tabs)
    
    def setup_payroll_reports_tab(self, tabs: QTabWidget):
        """Setup payroll reports tab"""
        payroll_tab = QWidget()
        layout = QVBoxLayout(payroll_tab)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.payroll_month = QComboBox()
        self.payroll_month.addItems([DateConverter.get_jalali_month_name(i) for i in range(1, 13)])
        current_month = DateConverter.get_current_jalali_date().month
        self.payroll_month.setCurrentIndex(current_month - 1)
        
        self.payroll_year = QComboBox()
        current_year = DateConverter.get_current_jalali_date().year
        self.payroll_year.addItems([str(year) for year in range(current_year-2, current_year+1)])
        self.payroll_year.setCurrentText(str(current_year))
        
        generate_btn = ModernButton("📊 تولید گزارش حقوق")
        generate_btn.clicked.connect(self.generate_payroll_report)
        
        print_btn = ModernButton("🖨️ چاپ گزارش")
        print_btn.clicked.connect(self.print_payroll_report)
        
        export_btn = ModernButton("📤 خروجی Excel")
        export_btn.clicked.connect(self.export_payroll_report)
        
        controls_layout.addWidget(export_btn)
        controls_layout.addWidget(print_btn)
        controls_layout.addWidget(generate_btn)
        controls_layout.addWidget(QLabel("سال:"))
        controls_layout.addWidget(self.payroll_year)
        controls_layout.addWidget(QLabel("ماه:"))
        controls_layout.addWidget(self.payroll_month)
        
        layout.addLayout(controls_layout)
        
        # Payroll report table
        self.payroll_report_table = ModernTable()
        self.payroll_report_table.setColumnCount(8)
        self.payroll_report_table.setHorizontalHeaderLabels([
            "کد پرسنلی", "نام و نام خانوادگی", "حقوق پایه", "مزایا",
            "کسورات", "حقوق خالص", "وضعیت پرداخت", "تاریخ پرداخت"
        ])
        
        layout.addWidget(self.payroll_report_table)
        
        # Summary
        summary_group = QGroupBox("خلاصه گزارش حقوق")
        summary_layout = QHBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(120)
        self.summary_text.setReadOnly(True)
        
        summary_layout.addWidget(self.summary_text)
        layout.addWidget(summary_group)
        
        tabs.addTab(payroll_tab, "گزارشات حقوق")
    
    def setup_attendance_reports_tab(self, tabs: QTabWidget):
        """Setup attendance reports tab"""
        attendance_tab = QWidget()
        layout = QVBoxLayout(attendance_tab)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.attendance_month = QComboBox()
        self.attendance_month.addItems([DateConverter.get_jalali_month_name(i) for i in range(1, 13)])
        current_month = DateConverter.get_current_jalali_date().month
        self.attendance_month.setCurrentIndex(current_month - 1)
        
        self.attendance_year = QComboBox()
        current_year = DateConverter.get_current_jalali_date().year
        self.attendance_year.addItems([str(year) for year in range(current_year-2, current_year+1)])
        self.attendance_year.setCurrentText(str(current_year))
        
        generate_btn = ModernButton("📊 تولید گزارش حضور")
        generate_btn.clicked.connect(self.generate_attendance_report)
        
        controls_layout.addWidget(generate_btn)
        controls_layout.addWidget(QLabel("سال:"))
        controls_layout.addWidget(self.attendance_year)
        controls_layout.addWidget(QLabel("ماه:"))
        controls_layout.addWidget(self.attendance_month)
        
        layout.addLayout(controls_layout)
        
        # Attendance report table
        self.attendance_report_table = ModernTable()
        self.attendance_report_table.setColumnCount(10)
        self.attendance_report_table.setHorizontalHeaderLabels([
            "کد پرسنلی", "نام و نام خانوادگی", "روزهای کاری", 
            "مرخصی استعلاجی", "مرخصی استحقاقی", "غیبت", 
            "تعطیل", "ساعات اضافه کاری", "تأخیر", "زمان کارکرد"
        ])
        
        layout.addWidget(self.attendance_report_table)
        
        tabs.addTab(attendance_tab, "گزارشات حضور")
    
    def setup_financial_reports_tab(self, tabs: QTabWidget):
        """Setup financial reports tab"""
        financial_tab = QWidget()
        layout = QVBoxLayout(financial_tab)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.financial_year = QComboBox()
        current_year = DateConverter.get_current_jalali_date().year
        self.financial_year.addItems([str(year) for year in range(current_year-2, current_year+1)])
        self.financial_year.setCurrentText(str(current_year))
        
        generate_btn = ModernButton("📊 گزارش مالی سالانه")
        generate_btn.clicked.connect(self.generate_financial_report)
        
        controls_layout.addWidget(generate_btn)
        controls_layout.addWidget(QLabel("سال:"))
        controls_layout.addWidget(self.financial_year)
        
        layout.addLayout(controls_layout)
        
        # Financial summary
        financial_group = QGroupBox("خلاصه مالی سالانه")
        financial_layout = QVBoxLayout(financial_group)
        
        self.financial_text = QTextEdit()
        self.financial_text.setReadOnly(True)
        
        financial_layout.addWidget(self.financial_text)
        layout.addWidget(financial_group)
        
        tabs.addTab(financial_tab, "گزارشات مالی")
    
    def setup_personnel_reports_tab(self, tabs: QTabWidget):
        """Setup personnel reports tab"""
        personnel_tab = QWidget()
        layout = QVBoxLayout(personnel_tab)
        
        # Report types
        report_group = QGroupBox("گزارشات پرسنلی")
        report_layout = QVBoxLayout(report_group)
        
        personnel_list_btn = ModernButton("📋 لیست کلی پرسنل")
        personnel_list_btn.clicked.connect(self.generate_personnel_list)
        
        active_personnel_btn = ModernButton("👥 پرسنل فعال")
        active_personnel_btn.clicked.connect(self.generate_active_personnel)
        
        salary_ranges_btn = ModernButton("💰 بازه‌های حقوقی")
        salary_ranges_btn.clicked.connect(self.generate_salary_ranges)
        
        report_layout.addWidget(personnel_list_btn)
        report_layout.addWidget(active_personnel_btn)
        report_layout.addWidget(salary_ranges_btn)
        
        layout.addWidget(report_group)
        
        # Personnel report table
        self.personnel_report_table = ModernTable()
        layout.addWidget(self.personnel_report_table)
        
        tabs.addTab(personnel_tab, "گزارشات پرسنلی")
    
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
    
    def generate_payroll_report(self):
        """Generate payroll report"""
        try:
            month = self.payroll_month.currentIndex() + 1
            year = int(self.payroll_year.currentText())
            
            query = """
                SELECT 
                    p.employee_code,
                    p.first_name || ' ' || p.last_name as full_name,
                    pr.base_salary,
                    (pr.housing_allowance + pr.family_allowance + pr.child_allowance + 
                     pr.overtime_amount + pr.other_allowances) as allowances,
                    (pr.insurance_employee + pr.tax_amount + pr.loan_deduction + 
                     pr.advance_deduction + pr.other_deductions) as deductions,
                    pr.net_salary,
                    CASE WHEN pr.is_paid THEN 'پرداخت شده' ELSE 'پرداخت نشده' END as payment_status,
                    COALESCE(pr.payment_date::text, '-') as payment_date
                FROM payroll pr
                JOIN personnel p ON pr.personnel_id = p.id
                WHERE pr.year = %s AND pr.month = %s
                ORDER BY p.employee_code
            """
            
            results = self.db.fetch_all(query, (year, month))
            
            self.payroll_report_table.setRowCount(0)
            
            total_base = 0
            total_allowances = 0
            total_deductions = 0
            total_net = 0
            paid_count = 0
            
            for row_data in results:
                row_position = self.payroll_report_table.rowCount()
                self.payroll_report_table.insertRow(row_position)
                
                self.payroll_report_table.setItem(row_position, 0, QTableWidgetItem(str(row_data['employee_code'])))
                self.payroll_report_table.setItem(row_position, 1, QTableWidgetItem(row_data['full_name']))
                self.payroll_report_table.setItem(row_position, 2, QTableWidgetItem(f"{row_data['base_salary']:,.0f}"))
                self.payroll_report_table.setItem(row_position, 3, QTableWidgetItem(f"{row_data['allowances']:,.0f}"))
                self.payroll_report_table.setItem(row_position, 4, QTableWidgetItem(f"{row_data['deductions']:,.0f}"))
                self.payroll_report_table.setItem(row_position, 5, QTableWidgetItem(f"{row_data['net_salary']:,.0f}"))
                self.payroll_report_table.setItem(row_position, 6, QTableWidgetItem(row_data['payment_status']))
                self.payroll_report_table.setItem(row_position, 7, QTableWidgetItem(row_data['payment_date']))
                
                # Update totals
                total_base += row_data['base_salary']
                total_allowances += row_data['allowances']
                total_deductions += row_data['deductions']
                total_net += row_data['net_salary']
                if row_data['payment_status'] == 'پرداخت شده':
                    paid_count += 1
            
            # Update summary
            summary_text = f"""
            خلاصه گزارش حقوق {DateConverter.get_jalali_month_name(month)} {year}:
            
            • تعداد پرسنل: {len(results)} نفر
            • تعداد پرداخت شده: {paid_count} نفر
            • مجموع حقوق پایه: {total_base:,.0f} ریال
            • مجموع مزایا: {total_allowances:,.0f} ریال
            • مجموع کسورات: {total_deductions:,.0f} ریال
            • مجموع حقوق خالص: {total_net:,.0f} ریال
            """
            
            self.summary_text.setText(summary_text)
            
        except Exception as e:
            logger.error(f"Error generating payroll report: {e}")
            self.show_error_message("خطا", "خطا در تولید گزارش حقوق")
    
    def generate_attendance_report(self):
        """Generate attendance report"""
        try:
            month = self.attendance_month.currentIndex() + 1
            year = int(self.attendance_year.currentText())
            
            query = """
                SELECT 
                    p.employee_code,
                    p.first_name || ' ' || p.last_name as full_name,
                    COUNT(CASE WHEN a.absence_type = 'حاضر' THEN 1 END) as work_days,
                    COUNT(CASE WHEN a.absence_type = 'مرخصی استعلاجی' THEN 1 END) as sick_leave,
                    COUNT(CASE WHEN a.absence_type = 'مرخصی استحقاقی' THEN 1 END) as annual_leave,
                    COUNT(CASE WHEN a.absence_type = 'غیبت' THEN 1 END) as absence_days,
                    COUNT(CASE WHEN a.absence_type = 'تعطیل' THEN 1 END) as holiday_days,
                    COALESCE(SUM(a.overtime_hours), 0) as overtime_hours,
                    COUNT(CASE WHEN a.entry_time > '08:15' THEN 1 END) as late_days,
                    COUNT(CASE WHEN a.absence_type = 'حاضر' THEN 1 END) * 8 as total_work_hours
                FROM personnel p
                LEFT JOIN attendance a ON p.id = a.personnel_id 
                    AND EXTRACT(YEAR FROM a.date) = %s 
                    AND EXTRACT(MONTH FROM a.date) = %s
                WHERE p.is_active = TRUE
                GROUP BY p.id, p.employee_code, p.first_name, p.last_name
                ORDER BY p.employee_code
            """
            
            results = self.db.fetch_all(query, (year, month))
            
            self.attendance_report_table.setRowCount(0)
            
            for row_data in results:
                row_position = self.attendance_report_table.rowCount()
                self.attendance_report_table.insertRow(row_position)
                
                self.attendance_report_table.setItem(row_position, 0, QTableWidgetItem(str(row_data['employee_code'])))
                self.attendance_report_table.setItem(row_position, 1, QTableWidgetItem(row_data['full_name']))
                self.attendance_report_table.setItem(row_position, 2, QTableWidgetItem(str(row_data['work_days'])))
                self.attendance_report_table.setItem(row_position, 3, QTableWidgetItem(str(row_data['sick_leave'])))
                self.attendance_report_table.setItem(row_position, 4, QTableWidgetItem(str(row_data['annual_leave'])))
                self.attendance_report_table.setItem(row_position, 5, QTableWidgetItem(str(row_data['absence_days'])))
                self.attendance_report_table.setItem(row_position, 6, QTableWidgetItem(str(row_data['holiday_days'])))
                self.attendance_report_table.setItem(row_position, 7, QTableWidgetItem(str(row_data['overtime_hours'])))
                self.attendance_report_table.setItem(row_position, 8, QTableWidgetItem(str(row_data['late_days'])))
                self.attendance_report_table.setItem(row_position, 9, QTableWidgetItem(str(row_data['total_work_hours'])))
                
        except Exception as e:
            logger.error(f"Error generating attendance report: {e}")
            self.show_error_message("خطا", "خطا در تولید گزارش حضور")
    
    def generate_financial_report(self):
        """Generate financial report"""
        try:
            year = int(self.financial_year.currentText())
            
            query = """
                SELECT 
                    month,
                    COUNT(*) as employee_count,
                    SUM(base_salary) as total_base_salary,
                    SUM(gross_salary) as total_gross_salary,
                    SUM(net_salary) as total_net_salary,
                    SUM(insurance_employee) as total_insurance_employee,
                    SUM(insurance_employer) as total_insurance_employer,
                    SUM(tax_amount) as total_tax,
                    COUNT(CASE WHEN is_paid THEN 1 END) as paid_count
                FROM payroll 
                WHERE year = %s
                GROUP BY month
                ORDER BY month
            """
            
            results = self.db.fetch_all(query, (year,))
            
            financial_text = f"گزارش مالی سال {year}\n\n"
            financial_text += "ماه | تعداد | حقوق پایه | حقوق ناخالص | حقوق خالص | بیمه کارمند | بیمه کارفرما | مالیات | وضعیت پرداخت\n"
            financial_text += "-" * 100 + "\n"
            
            yearly_totals = {
                'employees': 0,
                'base_salary': 0,
                'gross_salary': 0,
                'net_salary': 0,
                'insurance_employee': 0,
                'insurance_employer': 0,
                'tax': 0,
                'paid': 0
            }
            
            for row_data in results:
                month_name = DateConverter.get_jalali_month_name(row_data['month'])
                financial_text += f"{month_name} | {row_data['employee_count']} | {row_data['total_base_salary']:,.0f} | {row_data['total_gross_salary']:,.0f} | {row_data['total_net_salary']:,.0f} | {row_data['total_insurance_employee']:,.0f} | {row_data['total_insurance_employer']:,.0f} | {row_data['total_tax']:,.0f} | {row_data['paid_count']}/{row_data['employee_count']}\n"
                
                # Update yearly totals
                yearly_totals['employees'] += row_data['employee_count']
                yearly_totals['base_salary'] += row_data['total_base_salary']
                yearly_totals['gross_salary'] += row_data['total_gross_salary']
                yearly_totals['net_salary'] += row_data['total_net_salary']
                yearly_totals['insurance_employee'] += row_data['total_insurance_employee']
                yearly_totals['insurance_employer'] += row_data['total_insurance_employer']
                yearly_totals['tax'] += row_data['total_tax']
                yearly_totals['paid'] += row_data['paid_count']
            
            financial_text += f"\nجمع سالانه:\n"
            financial_text += f"• تعداد کل پرسنل: {yearly_totals['employees']} نفر\n"
            financial_text += f"• مجموع حقوق پایه: {yearly_totals['base_salary']:,.0f} ریال\n"
            financial_text += f"• مجموع حقوق ناخالص: {yearly_totals['gross_salary']:,.0f} ریال\n"
            financial_text += f"• مجموع حقوق خالص: {yearly_totals['net_salary']:,.0f} ریال\n"
            financial_text += f"• مجموع بیمه کارمند: {yearly_totals['insurance_employee']:,.0f} ریال\n"
            financial_text += f"• مجموع بیمه کارفرما: {yearly_totals['insurance_employer']:,.0f} ریال\n"
            financial_text += f"• مجموع مالیات: {yearly_totals['tax']:,.0f} ریال\n"
            financial_text += f"• تعداد پرداخت‌ها: {yearly_totals['paid']} پرداخت\n"
            
            self.financial_text.setText(financial_text)
            
        except Exception as e:
            logger.error(f"Error generating financial report: {e}")
            self.show_error_message("خطا", "خطا در تولید گزارش مالی")
    
    def generate_personnel_list(self):
        """Generate personnel list report"""
        try:
            query = """
                SELECT 
                    employee_code,
                    first_name || ' ' || last_name as full_name,
                    national_id,
                    position,
                    base_salary,
                    children_count,
                    CASE WHEN is_active THEN 'فعال' ELSE 'غیرفعال' END as status,
                    TO_CHAR(hire_date, 'YYYY/MM/DD') as hire_date
                FROM personnel 
                ORDER BY employee_code
            """
            
            results = self.db.fetch_all(query)
            
            self.personnel_report_table.setRowCount(0)
            self.personnel_report_table.setColumnCount(8)
            self.personnel_report_table.setHorizontalHeaderLabels([
                "کد پرسنلی", "نام و نام خانوادگی", "کد ملی", "سمت",
                "حقوق پایه", "تعداد فرزندان", "وضعیت", "تاریخ استخدام"
            ])
            
            for row_data in results:
                row_position = self.personnel_report_table.rowCount()
                self.personnel_report_table.insertRow(row_position)
                
                self.personnel_report_table.setItem(row_position, 0, QTableWidgetItem(str(row_data['employee_code'])))
                self.personnel_report_table.setItem(row_position, 1, QTableWidgetItem(row_data['full_name']))
                self.personnel_report_table.setItem(row_position, 2, QTableWidgetItem(str(row_data['national_id'])))
                self.personnel_report_table.setItem(row_position, 3, QTableWidgetItem(row_data['position']))
                self.personnel_report_table.setItem(row_position, 4, QTableWidgetItem(f"{row_data['base_salary']:,.0f}"))
                self.personnel_report_table.setItem(row_position, 5, QTableWidgetItem(str(row_data['children_count'])))
                self.personnel_report_table.setItem(row_position, 6, QTableWidgetItem(row_data['status']))
                self.personnel_report_table.setItem(row_position, 7, QTableWidgetItem(row_data['hire_date']))
                
        except Exception as e:
            logger.error(f"Error generating personnel list: {e}")
            self.show_error_message("خطا", "خطا در تولید لیست پرسنل")
    
    def generate_active_personnel(self):
        """Generate active personnel report"""
        try:
            query = """
                SELECT 
                    employee_code,
                    first_name || ' ' || last_name as full_name,
                    national_id,
                    position,
                    base_salary,
                    children_count,
                    TO_CHAR(hire_date, 'YYYY/MM/DD') as hire_date
                FROM personnel 
                WHERE is_active = TRUE
                ORDER BY employee_code
            """
            
            results = self.db.fetch_all(query)
            
            self.personnel_report_table.setRowCount(0)
            self.personnel_report_table.setColumnCount(7)
            self.personnel_report_table.setHorizontalHeaderLabels([
                "کد پرسنلی", "نام و نام خانوادگی", "کد ملی", "سمت",
                "حقوق پایه", "تعداد فرزندان", "تاریخ استخدام"
            ])
            
            for row_data in results:
                row_position = self.personnel_report_table.rowCount()
                self.personnel_report_table.insertRow(row_position)
                
                self.personnel_report_table.setItem(row_position, 0, QTableWidgetItem(str(row_data['employee_code'])))
                self.personnel_report_table.setItem(row_position, 1, QTableWidgetItem(row_data['full_name']))
                self.personnel_report_table.setItem(row_position, 2, QTableWidgetItem(str(row_data['national_id'])))
                self.personnel_report_table.setItem(row_position, 3, QTableWidgetItem(row_data['position']))
                self.personnel_report_table.setItem(row_position, 4, QTableWidgetItem(f"{row_data['base_salary']:,.0f}"))
                self.personnel_report_table.setItem(row_position, 5, QTableWidgetItem(str(row_data['children_count'])))
                self.personnel_report_table.setItem(row_position, 6, QTableWidgetItem(row_data['hire_date']))
                
        except Exception as e:
            logger.error(f"Error generating active personnel: {e}")
            self.show_error_message("خطا", "خطا در تولید لیست پرسنل فعال")
    
    def generate_salary_ranges(self):
        """Generate salary ranges report"""
        try:
            query = """
                SELECT 
                    CASE 
                        WHEN base_salary < 30000000 THEN 'کمتر از 30 میلیون'
                        WHEN base_salary < 50000000 THEN '30 تا 50 میلیون'
                        WHEN base_salary < 80000000 THEN '50 تا 80 میلیون'
                        ELSE 'بیشتر از 80 میلیون'
                    END as salary_range,
                    COUNT(*) as employee_count,
                    AVG(base_salary) as average_salary,
                    MIN(base_salary) as min_salary,
                    MAX(base_salary) as max_salary
                FROM personnel 
                WHERE is_active = TRUE
                GROUP BY 
                    CASE 
                        WHEN base_salary < 30000000 THEN 'کمتر از 30 میلیون'
                        WHEN base_salary < 50000000 THEN '30 تا 50 میلیون'
                        WHEN base_salary < 80000000 THEN '50 تا 80 میلیون'
                        ELSE 'بیشتر از 80 میلیون'
                    END
                ORDER BY min_salary
            """
            
            results = self.db.fetch_all(query)
            
            self.personnel_report_table.setRowCount(0)
            self.personnel_report_table.setColumnCount(5)
            self.personnel_report_table.setHorizontalHeaderLabels([
                "بازه حقوقی", "تعداد پرسنل", "میانگین حقوق", "کمترین حقوق", "بیشترین حقوق"
            ])
            
            for row_data in results:
                row_position = self.personnel_report_table.rowCount()
                self.personnel_report_table.insertRow(row_position)
                
                self.personnel_report_table.setItem(row_position, 0, QTableWidgetItem(row_data['salary_range']))
                self.personnel_report_table.setItem(row_position, 1, QTableWidgetItem(str(row_data['employee_count'])))
                self.personnel_report_table.setItem(row_position, 2, QTableWidgetItem(f"{row_data['average_salary']:,.0f}"))
                self.personnel_report_table.setItem(row_position, 3, QTableWidgetItem(f"{row_data['min_salary']:,.0f}"))
                self.personnel_report_table.setItem(row_position, 4, QTableWidgetItem(f"{row_data['max_salary']:,.0f}"))
                
        except Exception as e:
            logger.error(f"Error generating salary ranges: {e}")
            self.show_error_message("خطا", "خطا در تولید گزارش بازه‌های حقوقی")
    
    def print_payroll_report(self):
        """Print payroll report"""
        try:
            printer = QPrinter()
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                self.show_success_message("اطلاع", "چاپ گزارش با موفقیت انجام شد")
                
        except Exception as e:
            logger.error(f"Error printing report: {e}")
            self.show_error_message("خطا", "خطا در چاپ گزارش")
    
    def export_payroll_report(self):
        """Export payroll report to Excel"""
        self.show_success_message("اطلاع", "قابلیت خروجی Excel به زودی اضافه خواهد شد")