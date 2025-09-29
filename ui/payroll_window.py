from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QComboBox, QDoubleSpinBox, QCheckBox, QTabWidget,
                            QHeaderView, QMessageBox, QFormLayout, QGroupBox,
                            QProgressBar, QFrame)
from PyQt6.QtCore import Qt
from widgets.modern_button import ModernButton
from widgets.modern_table import ModernTable
from database.database_manager import DatabaseManager
from utils.date_converter import DateConverter
from utils.font_manager import FontManager
import logging
import json

logger = logging.getLogger(__name__)

class PayrollWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.calculation_config = self.load_calculation_config()
        self.setup_ui()
        self.load_payroll_data()
        
    def setup_ui(self):
        """Setup payroll calculation UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("محاسبه حقوق و دستمزد")
        title_label.setFont(FontManager.get_font(point_size=16, bold=True))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Calculation controls
        controls_layout = QHBoxLayout()
        
        self.month_combo = QComboBox()
        self.month_combo.addItems([DateConverter.get_jalali_month_name(i) for i in range(1, 13)])
        current_month = DateConverter.get_current_jalali_date().month
        self.month_combo.setCurrentIndex(current_month - 1)
        
        self.year_combo = QComboBox()
        current_year = DateConverter.get_current_jalali_date().year
        self.year_combo.addItems([str(year) for year in range(current_year-2, current_year+1)])
        self.year_combo.setCurrentText(str(current_year))
        
        self.calculate_btn = ModernButton("🧮 محاسبه حقوق")
        self.calculate_btn.clicked.connect(self.calculate_payroll)
        
        self.pay_all_btn = ModernButton("💳 پرداخت همه")
        self.pay_all_btn.clicked.connect(self.pay_all_salaries)
        
        controls_layout.addWidget(self.pay_all_btn)
        controls_layout.addWidget(self.calculate_btn)
        controls_layout.addWidget(QLabel("سال:"))
        controls_layout.addWidget(self.year_combo)
        controls_layout.addWidget(QLabel("ماه:"))
        controls_layout.addWidget(self.month_combo)
        
        header_layout.addLayout(controls_layout)
        main_layout.addLayout(header_layout)
        
        # Summary cards
        self.setup_summary_cards(main_layout)
        
        # Create tabs
        self.setup_tabs(main_layout)
    
    def setup_summary_cards(self, main_layout: QVBoxLayout):
        """Setup summary cards"""
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # Total employees card
        total_card = self.create_summary_card("👥 تعداد پرسنل", "0", "#3498db")
        cards_layout.addWidget(total_card)
        
        # Total payroll card
        payroll_card = self.create_summary_card("💰 مجموع حقوق", "0 ریال", "#2ecc71")
        cards_layout.addWidget(payroll_card)
        
        # Paid salaries card
        paid_card = self.create_summary_card("✅ حقوق پرداختی", "0 ریال", "#27ae60")
        cards_layout.addWidget(paid_card)
        
        # Unpaid salaries card
        unpaid_card = self.create_summary_card("⏳ حقوق پرداخت نشده", "0 ریال", "#e74c3c")
        cards_layout.addWidget(unpaid_card)
        
        self.summary_cards = {
            'total': total_card,
            'payroll': payroll_card,
            'paid': paid_card,
            'unpaid': unpaid_card
        }
        
        main_layout.addLayout(cards_layout)
    
    def create_summary_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a summary card"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 12px;")
        title_label.setFont(FontManager.get_font(point_size=10))
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        value_label.setFont(FontManager.get_font(point_size=14, bold=True))
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def setup_tabs(self, main_layout: QVBoxLayout):
        """Setup tabs for payroll management"""
        tabs = QTabWidget()
        
        # Payroll list tab
        self.setup_payroll_list_tab(tabs)
        
        # Calculation settings tab
        self.setup_settings_tab(tabs)
        
        main_layout.addWidget(tabs)
    
    def setup_payroll_list_tab(self, tabs: QTabWidget):
        """Setup payroll list tab"""
        list_tab = QWidget()
        layout = QVBoxLayout(list_tab)
        
        # Payroll table
        self.setup_payroll_table(layout)
        
        tabs.addTab(list_tab, "لیست حقوق‌ها")
    
    def setup_payroll_table(self, layout: QVBoxLayout):
        """Setup payroll table"""
        self.payroll_table = ModernTable()
        self.payroll_table.setColumnCount(15)
        self.payroll_table.setHorizontalHeaderLabels([
            "عملیات", "کد پرسنلی", "نام و نام خانوادگی", "حقوق پایه",
            "حق مسکن", "حق عائله", "حق اولاد", "اضافه کاری", 
            "مزایا", "حقوق ناخالص", "بیمه کارمند", "بیمه کارفرما",
            "مالیات", "کسورات", "حقوق خالص"
        ])
        
        # Set column widths
        header = self.payroll_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 120)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.payroll_table)
    
    def setup_settings_tab(self, tabs: QTabWidget):
        """Setup calculation settings tab"""
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)
        
        # Allowances settings
        allowances_group = QGroupBox("تنظیمات حقوق و مزایا")
        allowances_layout = QFormLayout(allowances_group)
        
        self.base_salary_input = QDoubleSpinBox()
        self.base_salary_input.setRange(0, 1000000000)
        self.base_salary_input.setValue(self.calculation_config.get('base_salary', 56000000))
        self.base_salary_input.setSuffix(" ریال")
        
        self.housing_allowance_rate = QDoubleSpinBox()
        self.housing_allowance_rate.setRange(0, 1)
        self.housing_allowance_rate.setValue(self.calculation_config.get('housing_allowance', 0.25))
        self.housing_allowance_rate.setSingleStep(0.05)
        self.housing_allowance_rate.setSuffix(" %")
        
        self.family_allowance_rate = QDoubleSpinBox()
        self.family_allowance_rate.setRange(0, 1)
        self.family_allowance_rate.setValue(self.calculation_config.get('family_allowance', 0.1))
        self.family_allowance_rate.setSingleStep(0.05)
        self.family_allowance_rate.setSuffix(" %")
        
        self.child_allowance_amount = QDoubleSpinBox()
        self.child_allowance_amount.setRange(0, 10000000)
        self.child_allowance_amount.setValue(self.calculation_config.get('child_allowance', 500000))
        self.child_allowance_amount.setSuffix(" ریال")
        
        allowances_layout.addRow("حقوق پایه:", self.base_salary_input)
        allowances_layout.addRow("نرخ حق مسکن:", self.housing_allowance_rate)
        allowances_layout.addRow("نرخ حق عائله:", self.family_allowance_rate)
        allowances_layout.addRow("مبلغ حق اولاد:", self.child_allowance_amount)
        
        # Insurance settings
        insurance_group = QGroupBox("تنظیمات بیمه و مالیات")
        insurance_layout = QFormLayout(insurance_group)
        
        self.insurance_employee_rate = QDoubleSpinBox()
        self.insurance_employee_rate.setRange(0, 1)
        self.insurance_employee_rate.setValue(self.calculation_config.get('insurance_employee', 0.07))
        self.insurance_employee_rate.setSingleStep(0.01)
        self.insurance_employee_rate.setSuffix(" %")
        
        self.insurance_employer_rate = QDoubleSpinBox()
        self.insurance_employer_rate.setRange(0, 1)
        self.insurance_employer_rate.setValue(self.calculation_config.get('insurance_employer', 0.23))
        self.insurance_employer_rate.setSingleStep(0.01)
        self.insurance_employer_rate.setSuffix(" %")
        
        self.tax_threshold = QDoubleSpinBox()
        self.tax_threshold.setRange(0, 1000000000)
        self.tax_threshold.setValue(self.calculation_config.get('tax_threshold', 56000000))
        self.tax_threshold.setSuffix(" ریال")
        
        insurance_layout.addRow("نرخ بیمه کارمند:", self.insurance_employee_rate)
        insurance_layout.addRow("نرخ بیمه کارفرما:", self.insurance_employer_rate)
        insurance_layout.addRow("آستانه معافیت مالیاتی:", self.tax_threshold)
        
        # Save settings button
        save_btn = ModernButton("💾 ذخیره تنظیمات")
        save_btn.clicked.connect(self.save_calculation_settings)
        
        layout.addWidget(allowances_group)
        layout.addWidget(insurance_group)
        layout.addWidget(save_btn)
        layout.addStretch()
        
        tabs.addTab(settings_tab, "تنظیمات محاسبه")
    
    def load_calculation_config(self) -> dict:
        """Load calculation configuration"""
        try:
            with open('config/settings.json', 'r', encoding='utf-8') as file:
                config = json.load(file)
                return config.get('calculation', {})
        except Exception as e:
            logger.error(f"Error loading calculation config: {e}")
            return {}
    
    def load_payroll_data(self):
        """Load payroll data from database"""
        try:
            month = self.month_combo.currentIndex() + 1
            year = int(self.year_combo.currentText())
            
            query = """
                SELECT pr.*, p.employee_code, p.first_name, p.last_name
                FROM payroll pr
                JOIN personnel p ON pr.personnel_id = p.id
                WHERE pr.year = %s AND pr.month = %s
                ORDER BY p.employee_code
            """
            results = self.db.fetch_all(query, (year, month))
            
            self.payroll_table.setRowCount(0)
            total_payroll = 0
            paid_amount = 0
            unpaid_amount = 0
            
            for row_data in results:
                row_position = self.payroll_table.rowCount()
                self.payroll_table.insertRow(row_position)
                
                # Action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(5, 2, 5, 2)
                
                if not row_data['is_paid']:
                    pay_btn = ModernButton("💳 پرداخت")
                    pay_btn.setFixedSize(60, 30)
                    pay_btn.clicked.connect(lambda checked, id=row_data['id']: self.pay_salary(id))
                    action_layout.addWidget(pay_btn)
                
                detail_btn = ModernButton("📋 جزئیات")
                detail_btn.setFixedSize(60, 30)
                detail_btn.clicked.connect(lambda checked, id=row_data['id']: self.show_payroll_details(id))
                action_layout.addWidget(detail_btn)
                
                action_layout.addStretch()
                
                self.payroll_table.setCellWidget(row_position, 0, action_widget)
                self.payroll_table.setItem(row_position, 1, QTableWidgetItem(str(row_data['employee_code'])))
                self.payroll_table.setItem(row_position, 2, QTableWidgetItem(f"{row_data['first_name']} {row_data['last_name']}"))
                self.payroll_table.setItem(row_position, 3, QTableWidgetItem(f"{row_data['base_salary']:,.0f}"))
                self.payroll_table.setItem(row_position, 4, QTableWidgetItem(f"{row_data['housing_allowance']:,.0f}"))
                self.payroll_table.setItem(row_position, 5, QTableWidgetItem(f"{row_data['family_allowance']:,.0f}"))
                self.payroll_table.setItem(row_position, 6, QTableWidgetItem(f"{row_data['child_allowance']:,.0f}"))
                self.payroll_table.setItem(row_position, 7, QTableWidgetItem(f"{row_data['overtime_amount']:,.0f}"))
                self.payroll_table.setItem(row_position, 8, QTableWidgetItem(f"{row_data['other_allowances']:,.0f}"))
                self.payroll_table.setItem(row_position, 9, QTableWidgetItem(f"{row_data['gross_salary']:,.0f}"))
                self.payroll_table.setItem(row_position, 10, QTableWidgetItem(f"{row_data['insurance_employee']:,.0f}"))
                self.payroll_table.setItem(row_position, 11, QTableWidgetItem(f"{row_data['insurance_employer']:,.0f}"))
                self.payroll_table.setItem(row_position, 12, QTableWidgetItem(f"{row_data['tax_amount']:,.0f}"))
                
                # Calculate total deductions
                total_deductions = (row_data['insurance_employee'] + row_data['tax_amount'] + 
                                  row_data['loan_deduction'] + row_data['advance_deduction'] + 
                                  row_data['other_deductions'])
                self.payroll_table.setItem(row_position, 13, QTableWidgetItem(f"{total_deductions:,.0f}"))
                self.payroll_table.setItem(row_position, 14, QTableWidgetItem(f"{row_data['net_salary']:,.0f}"))
                
                # Update totals
                total_payroll += row_data['net_salary']
                if row_data['is_paid']:
                    paid_amount += row_data['net_salary']
                else:
                    unpaid_amount += row_data['net_salary']
            
            # Update summary cards
            self.update_summary_cards(len(results), total_payroll, paid_amount, unpaid_amount)
            
        except Exception as e:
            logger.error(f"Error loading payroll data: {e}")
            self.show_error_message("خطا", "خطا در بارگذاری اطلاعات حقوق")
    
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
    
    def update_summary_cards(self, total_employees: int, total_payroll: float, 
                           paid_amount: float, unpaid_amount: float):
        """Update summary cards with current data"""
        # Find labels in cards and update them
        for i, card in enumerate(self.summary_cards.values()):
            labels = card.findChildren(QLabel)
            if len(labels) >= 2:
                if i == 0:  # Total employees
                    labels[1].setText(str(total_employees))
                elif i == 1:  # Total payroll
                    labels[1].setText(f"{total_payroll:,.0f} ریال")
                elif i == 2:  # Paid amount
                    labels[1].setText(f"{paid_amount:,.0f} ریال")
                elif i == 3:  # Unpaid amount
                    labels[1].setText(f"{unpaid_amount:,.0f} ریال")
    
    def calculate_payroll(self):
        """Calculate payroll for all active employees"""
        try:
            month = self.month_combo.currentIndex() + 1
            year = int(self.year_combo.currentText())
            
            # Get active personnel
            query = "SELECT * FROM personnel WHERE is_active = TRUE"
            personnel_list = self.db.fetch_all(query)
            
            if not personnel_list:
                self.show_error_message("هشدار", "هیچ پرسنل فعالی برای محاسبه حقوق وجود ندارد")
                return
            
            successful_calculations = 0
            
            for personnel in personnel_list:
                payroll_data = self.calculate_employee_payroll(personnel, year, month)
                
                if payroll_data:
                    # Check if payroll already exists
                    check_query = """
                        SELECT id FROM payroll 
                        WHERE personnel_id = %s AND year = %s AND month = %s
                    """
                    existing = self.db.fetch_one(check_query, (personnel['id'], year, month))
                    
                    if existing:
                        # Update existing payroll
                        update_query = """
                            UPDATE payroll SET 
                            base_salary = %s, housing_allowance = %s, family_allowance = %s,
                            child_allowance = %s, overtime_amount = %s, other_allowances = %s,
                            gross_salary = %s, insurance_employee = %s, insurance_employer = %s,
                            tax_amount = %s, loan_deduction = %s, advance_deduction = %s,
                            other_deductions = %s, net_salary = %s
                            WHERE id = %s
                        """
                        params = tuple(payroll_data.values()) + (existing['id'],)
                    else:
                        # Insert new payroll
                        insert_query = """
                            INSERT INTO payroll 
                            (personnel_id, year, month, base_salary, housing_allowance,
                             family_allowance, child_allowance, overtime_amount, other_allowances,
                             gross_salary, insurance_employee, insurance_employer, tax_amount,
                             loan_deduction, advance_deduction, other_deductions, net_salary)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        params = (personnel['id'], year, month) + tuple(payroll_data.values())
                    
                    if self.db.execute_query(insert_query if not existing else update_query, params):
                        successful_calculations += 1
            
            self.show_success_message("موفقیت", f"حقوق {successful_calculations} نفر از {len(personnel_list)} نفر با موفقیت محاسبه شد")
            self.load_payroll_data()
            
        except Exception as e:
            logger.error(f"Error calculating payroll: {e}")
            self.show_error_message("خطا", "خطا در محاسبه حقوق")
    
    def calculate_employee_payroll(self, personnel: dict, year: int, month: int) -> dict:
        """Calculate payroll for a single employee"""
        try:
            # Base salary
            base_salary = personnel['base_salary']
            
            # Allowances
            housing_allowance = base_salary * personnel['housing_allowance_rate']
            family_allowance = base_salary * personnel['family_allowance_rate']
            child_allowance = self.child_allowance_amount.value() * personnel['children_count']
            
            # Overtime calculation (simplified)
            overtime_amount = self.calculate_overtime(personnel['id'], year, month)
            
            # Other allowances
            other_allowances = 0
            
            # Gross salary
            gross_salary = base_salary + housing_allowance + family_allowance + child_allowance + overtime_amount + other_allowances
            
            # Deductions
            insurance_employee = gross_salary * self.insurance_employee_rate.value()
            insurance_employer = gross_salary * self.insurance_employer_rate.value()
            
            # Tax calculation (simplified)
            tax_amount = self.calculate_tax(gross_salary - insurance_employee)
            
            # Loan deductions
            loan_deduction = self.calculate_loan_deductions(personnel['id'])
            
            # Advance deductions
            advance_deduction = self.calculate_advance_deductions(personnel['id'])
            
            # Other deductions
            other_deductions = 0
            
            # Net salary
            net_salary = gross_salary - insurance_employee - tax_amount - loan_deduction - advance_deduction - other_deductions
            
            return {
                'base_salary': base_salary,
                'housing_allowance': housing_allowance,
                'family_allowance': family_allowance,
                'child_allowance': child_allowance,
                'overtime_amount': overtime_amount,
                'other_allowances': other_allowances,
                'gross_salary': gross_salary,
                'insurance_employee': insurance_employee,
                'insurance_employer': insurance_employer,
                'tax_amount': tax_amount,
                'loan_deduction': loan_deduction,
                'advance_deduction': advance_deduction,
                'other_deductions': other_deductions,
                'net_salary': net_salary
            }
            
        except Exception as e:
            logger.error(f"Error calculating employee payroll: {e}")
            return None
    
    def calculate_overtime(self, personnel_id: int, year: int, month: int) -> float:
        """Calculate overtime amount for employee"""
        try:
            query = """
                SELECT COALESCE(SUM(overtime_hours), 0) as total_overtime
                FROM attendance 
                WHERE personnel_id = %s 
                AND EXTRACT(YEAR FROM date) = %s 
                AND EXTRACT(MONTH FROM date) = %s
            """
            result = self.db.fetch_one(query, (personnel_id, year, month))
            
            if result:
                # Simplified overtime calculation (overtime rate = base hourly rate * 1.4)
                base_hourly_rate = 56000000 / 240  # Assuming 240 working hours per month
                overtime_rate = base_hourly_rate * 1.4
                return result['total_overtime'] * overtime_rate
            
            return 0
        except Exception as e:
            logger.error(f"Error calculating overtime: {e}")
            return 0
    
    def calculate_tax(self, taxable_income: float) -> float:
        """Calculate tax amount based on taxable income"""
        tax_threshold = self.tax_threshold.value()
        
        if taxable_income <= tax_threshold:
            return 0
        
        # Simplified tax calculation
        excess_income = taxable_income - tax_threshold
        tax_rate = 0.1  # 10% for excess income
        return excess_income * tax_rate
    
    def calculate_loan_deductions(self, personnel_id: int) -> float:
        """Calculate total loan deductions for employee"""
        try:
            query = """
                SELECT installment_amount 
                FROM loans 
                WHERE personnel_id = %s AND is_active = TRUE AND remaining_installments > 0
            """
            result = self.db.fetch_one(query, (personnel_id,))
            
            if result:
                return result['installment_amount']
            
            return 0
        except Exception as e:
            logger.error(f"Error calculating loan deductions: {e}")
            return 0
    
    def calculate_advance_deductions(self, personnel_id: int) -> float:
        """Calculate total advance deductions for employee"""
        try:
            query = """
                SELECT advance_amount 
                FROM advances 
                WHERE personnel_id = %s AND is_settled = FALSE
                LIMIT 1
            """
            result = self.db.fetch_one(query, (personnel_id,))
            
            if result:
                return result['advance_amount']
            
            return 0
        except Exception as e:
            logger.error(f"Error calculating advance deductions: {e}")
            return 0
    
    def pay_salary(self, payroll_id: int):
        """Mark salary as paid"""
        try:
            query = """
                UPDATE payroll 
                SET is_paid = TRUE, payment_date = CURRENT_DATE 
                WHERE id = %s
            """
            if self.db.execute_query(query, (payroll_id,)):
                self.show_success_message("موفقیت", "حقوق با موفقیت پرداخت شد")
                self.load_payroll_data()
            else:
                self.show_error_message("خطا", "خطا در پرداخت حقوق")
        except Exception as e:
            logger.error(f"Error paying salary: {e}")
            self.show_error_message("خطا", "خطا در پرداخت حقوق")
    
    def pay_all_salaries(self):
        """Mark all unpaid salaries as paid"""
        reply = QMessageBox.question(
            self,
            "تأیید پرداخت",
            "آیا از پرداخت همه حقوق‌های پرداخت نشده اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                month = self.month_combo.currentIndex() + 1
                year = int(self.year_combo.currentText())
                
                query = """
                    UPDATE payroll 
                    SET is_paid = TRUE, payment_date = CURRENT_DATE 
                    WHERE year = %s AND month = %s AND is_paid = FALSE
                """
                if self.db.execute_query(query, (year, month)):
                    self.show_success_message("موفقیت", "همه حقوق‌ها با موفقیت پرداخت شدند")
                    self.load_payroll_data()
                else:
                    self.show_error_message("خطا", "خطا در پرداخت حقوق‌ها")
            except Exception as e:
                logger.error(f"Error paying all salaries: {e}")
                self.show_error_message("خطا", "خطا در پرداخت حقوق‌ها")
    
    def show_payroll_details(self, payroll_id: int):
        """Show detailed payroll information"""
        try:
            query = """
                SELECT pr.*, p.employee_code, p.first_name, p.last_name
                FROM payroll pr
                JOIN personnel p ON pr.personnel_id = p.id
                WHERE pr.id = %s
            """
            payroll_data = self.db.fetch_one(query, (payroll_id,))
            
            if payroll_data:
                details = f"""
                جزئیات حقوق و دستمزد:
                
                پرسنل: {payroll_data['first_name']} {payroll_data['last_name']}
                کد پرسنلی: {payroll_data['employee_code']}
                دوره: {payroll_data['year']}/{payroll_data['month']}
                
                📈 اقلام مثبت:
                حقوق پایه: {payroll_data['base_salary']:,.0f} ریال
                حق مسکن: {payroll_data['housing_allowance']:,.0f} ریال
                حق عائله: {payroll_data['family_allowance']:,.0f} ریال
                حق اولاد: {payroll_data['child_allowance']:,.0f} ریال
                اضافه کاری: {payroll_data['overtime_amount']:,.0f} ریال
                سایر مزایا: {payroll_data['other_allowances']:,.0f} ریال
                
                📉 اقلام منفی:
                بیمه کارمند: {payroll_data['insurance_employee']:,.0f} ریال
                بیمه کارفرما: {payroll_data['insurance_employer']:,.0f} ریال
                مالیات: {payroll_data['tax_amount']:,.0f} ریال
                کسر وام: {payroll_data['loan_deduction']:,.0f} ریال
                کسر مساعده: {payroll_data['advance_deduction']:,.0f} ریال
                سایر کسورات: {payroll_data['other_deductions']:,.0f} ریال
                
                💰 جمع نهایی:
                حقوق ناخالص: {payroll_data['gross_salary']:,.0f} ریال
                حقوق خالص: {payroll_data['net_salary']:,.0f} ریال
                وضعیت پرداخت: {'پرداخت شده' if payroll_data['is_paid'] else 'پرداخت نشده'}
                """
                
                QMessageBox.information(self, "جزئیات حقوق", details)
                
        except Exception as e:
            logger.error(f"Error showing payroll details: {e}")
            self.show_error_message("خطا", "خطا در نمایش جزئیات حقوق")
    
    def save_calculation_settings(self):
        """Save calculation settings"""
        try:
            # Update local config
            self.calculation_config.update({
                'base_salary': self.base_salary_input.value(),
                'housing_allowance': self.housing_allowance_rate.value(),
                'family_allowance': self.family_allowance_rate.value(),
                'child_allowance': self.child_allowance_amount.value(),
                'insurance_employee': self.insurance_employee_rate.value(),
                'insurance_employer': self.insurance_employer_rate.value(),
                'tax_threshold': self.tax_threshold.value()
            })
            
            # Save to file
            with open('config/settings.json', 'r+', encoding='utf-8') as file:
                config = json.load(file)
                config['calculation'] = self.calculation_config
                file.seek(0)
                json.dump(config, file, indent=4, ensure_ascii=False)
                file.truncate()
            
            self.show_success_message("موفقیت", "تنظیمات محاسبه با موفقیت ذخیره شد")
            
        except Exception as e:
            logger.error(f"Error saving calculation settings: {e}")
            self.show_error_message("خطا", "خطا در ذخیره تنظیمات محاسبه")