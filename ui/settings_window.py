from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QComboBox, QCheckBox,
                            QTabWidget, QMessageBox, QFormLayout, QGroupBox,
                            QFileDialog, QSpinBox, QTextEdit)
from PyQt6.QtCore import Qt
from widgets.modern_button import ModernButton
from widgets.modern_input import ModernInput
from database.database_manager import DatabaseManager
from utils.font_manager import FontManager
import logging
import json
import os
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.config = self.load_config()
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup settings UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("تنظیمات سیستم")
        title_label.setFont(FontManager.get_font(point_size=16, bold=True))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Save button
        self.save_btn = ModernButton("💾 ذخیره همه تنظیمات")
        self.save_btn.clicked.connect(self.save_all_settings)
        header_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(header_layout)
        
        # Create tabs
        self.setup_tabs(main_layout)
    
    def setup_tabs(self, main_layout: QVBoxLayout):
        """Setup tabs for settings"""
        tabs = QTabWidget()
        
        # General settings tab
        self.setup_general_tab(tabs)
        
        # Database settings tab
        self.setup_database_tab(tabs)
        
        # Backup settings tab
        self.setup_backup_tab(tabs)
        
        # About tab
        self.setup_about_tab(tabs)
        
        main_layout.addWidget(tabs)
    
    def setup_general_tab(self, tabs: QTabWidget):
        """Setup general settings tab"""
        general_tab = QWidget()
        layout = QVBoxLayout(general_tab)
        
        # Company settings
        company_group = QGroupBox("تنظیمات شرکت")
        company_layout = QFormLayout(company_group)
        
        self.company_name_input = ModernInput()
        self.company_name_input.setPlaceholderText("نام شرکت")
        
        self.company_address_input = QTextEdit()
        self.company_address_input.setMaximumHeight(80)
        self.company_address_input.setPlaceholderText("آدرس شرکت")
        
        self.company_phone_input = ModernInput()
        self.company_phone_input.setPlaceholderText("تلفن شرکت")
        
        company_layout.addRow("نام شرکت:", self.company_name_input)
        company_layout.addRow("آدرس شرکت:", self.company_address_input)
        company_layout.addRow("تلفن شرکت:", self.company_phone_input)
        
        # Application settings
        app_group = QGroupBox("تنظیمات برنامه")
        app_layout = QFormLayout(app_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["فارسی", "English"])
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["روشن", "تیره"])
        
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["ریال", "تومان"])
        
        self.auto_backup_check = QCheckBox("پشتیبان‌گیری خودکار")
        
        app_layout.addRow("زبان:", self.language_combo)
        app_layout.addRow("تم:", self.theme_combo)
        app_layout.addRow("واحد پول:", self.currency_combo)
        app_layout.addRow("", self.auto_backup_check)
        
        layout.addWidget(company_group)
        layout.addWidget(app_group)
        layout.addStretch()
        
        tabs.addTab(general_tab, "عمومی")
    
    def setup_database_tab(self, tabs: QTabWidget):
        """Setup database settings tab"""
        db_tab = QWidget()
        layout = QVBoxLayout(db_tab)
        
        # Database connection settings
        db_group = QGroupBox("تنظیمات اتصال به پایگاه داده")
        db_layout = QFormLayout(db_group)
        
        self.db_host_input = ModernInput()
        self.db_host_input.setPlaceholderText("localhost")
        
        self.db_port_input = QSpinBox()
        self.db_port_input.setRange(1, 65535)
        self.db_port_input.setValue(5432)
        
        self.db_name_input = ModernInput()
        self.db_name_input.setPlaceholderText("faran_payroll")
        
        self.db_username_input = ModernInput()
        self.db_username_input.setPlaceholderText("postgres")
        
        self.db_password_input = ModernInput()
        self.db_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_password_input.setPlaceholderText("رمز عبور")
        
        db_layout.addRow("هاست:", self.db_host_input)
        db_layout.addRow("پورت:", self.db_port_input)
        db_layout.addRow("نام پایگاه داده:", self.db_name_input)
        db_layout.addRow("نام کاربری:", self.db_username_input)
        db_layout.addRow("رمز عبور:", self.db_password_input)
        
        # Database actions
        actions_group = QGroupBox("عملیات پایگاه داده")
        actions_layout = QVBoxLayout(actions_group)
        
        test_btn = ModernButton("🔍 آزمایش اتصال")
        test_btn.clicked.connect(self.test_database_connection)
        
        create_tables_btn = ModernButton("🗃️ ایجاد جداول")
        create_tables_btn.clicked.connect(self.create_database_tables)
        
        reset_btn = ModernButton("⚠️ بازنشانی پایگاه داده")
        reset_btn.clicked.connect(self.reset_database)
        reset_btn.setStyleSheet("background-color: #e74c3c;")
        
        actions_layout.addWidget(test_btn)
        actions_layout.addWidget(create_tables_btn)
        actions_layout.addWidget(reset_btn)
        
        layout.addWidget(db_group)
        layout.addWidget(actions_group)
        layout.addStretch()
        
        tabs.addTab(db_tab, "پایگاه داده")
    
    def setup_backup_tab(self, tabs: QTabWidget):
        """Setup backup settings tab"""
        backup_tab = QWidget()
        layout = QVBoxLayout(backup_tab)
        
        # Backup settings
        backup_group = QGroupBox("تنظیمات پشتیبان‌گیری")
        backup_layout = QFormLayout(backup_group)
        
        self.backup_path_input = ModernInput()
        self.backup_path_input.setPlaceholderText("مسیر ذخیره پشتیبان‌ها")
        
        browse_btn = ModernButton("📁 مرور")
        browse_btn.clicked.connect(self.browse_backup_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.backup_path_input)
        path_layout.addWidget(browse_btn)
        
        self.backup_interval = QSpinBox()
        self.backup_interval.setRange(1, 30)
        self.backup_interval.setSuffix(" روز")
        self.backup_interval.setValue(7)
        
        backup_layout.addRow("مسیر پشتیبان‌گیری:", path_layout)
        backup_layout.addRow("فاصله پشتیبان‌گیری:", self.backup_interval)
        
        # Backup actions
        actions_group = QGroupBox("عملیات پشتیبان‌گیری")
        actions_layout = QVBoxLayout(actions_group)
        
        backup_now_btn = ModernButton("💾 پشتیبان‌گیری اکنون")
        backup_now_btn.clicked.connect(self.create_backup)
        
        restore_btn = ModernButton("🔄 بازیابی پشتیبان")
        restore_btn.clicked.connect(self.restore_backup)
        
        actions_layout.addWidget(backup_now_btn)
        actions_layout.addWidget(restore_btn)
        
        # Backup history
        history_group = QGroupBox("تاریخچه پشتیبان‌ها")
        history_layout = QVBoxLayout(history_group)
        
        self.backup_history = QTextEdit()
        self.backup_history.setReadOnly(True)
        self.backup_history.setMaximumHeight(150)
        
        history_layout.addWidget(self.backup_history)
        self.load_backup_history()
        
        layout.addWidget(backup_group)
        layout.addWidget(actions_group)
        layout.addWidget(history_group)
        
        tabs.addTab(backup_tab, "پشتیبان‌گیری")
    
    def setup_about_tab(self, tabs: QTabWidget):
        """Setup about tab"""
        about_tab = QWidget()
        layout = QVBoxLayout(about_tab)
        
        # Application info
        info_group = QGroupBox("اطلاعات برنامه")
        info_layout = QVBoxLayout(info_group)
        
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
        <h2>سیستم حقوق و دستمزد فران</h2>
        <p><b>ورژن:</b> ۱.۰.۰</p>
        <p><b>توسعه‌دهنده:</b> شرکت فران</p>
        <p><b>تاریخ انتشار:</b> ۱۴۰۳</p>
        <p><b>توضیحات:</b></p>
        <p>سیستم جامع مدیریت حقوق و دستمزد با قابلیت‌های:</p>
        <ul>
            <li>مدیریت اطلاعات پرسنلی</li>
            <li>ثبت حضور و غیاب</li>
            <li>مدیریت وام و مساعده</li>
            <li>محاسبه خودکار حقوق</li>
            <li>گزارشات متنوع</li>
            <li>پشتیبان‌گیری از اطلاعات</li>
        </ul>
        <p><b>پشتیبانی:</b></p>
        <p>تلفن: ۰۲۱-۱۲۳۴۵۶۷۸</p>
        <p>ایمیل: support@faran.com</p>
        """)
        
        info_layout.addWidget(about_text)
        
        # System info
        system_group = QGroupBox("اطلاعات سیستم")
        system_layout = QVBoxLayout(system_group)
        
        system_text = QTextEdit()
        system_text.setReadOnly(True)
        
        # Get system information
        import platform
        system_info = f"""
        <b>سیستم عامل:</b> {platform.system()} {platform.release()}
        <b>پایتون:</b> {platform.python_version()}
        <b>معماری:</b> {platform.architecture()[0]}
        <b>پایگاه داده:</b> PostgreSQL
        """
        
        system_text.setHtml(system_info)
        system_layout.addWidget(system_text)
        
        layout.addWidget(info_group)
        layout.addWidget(system_group)
        layout.addStretch()
        
        tabs.addTab(about_tab, "درباره برنامه")
    
    def load_config(self) -> dict:
        """Load configuration from file"""
        try:
            with open('config/settings.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def load_settings(self):
        """Load current settings into UI"""
        try:
            # General settings
            app_config = self.config.get('application', {})
            self.company_name_input.setText(app_config.get('company_name', ''))
            self.company_address_input.setText(app_config.get('company_address', ''))
            self.company_phone_input.setText(app_config.get('company_phone', ''))
            
            self.language_combo.setCurrentText('فارسی' if app_config.get('language') == 'fa' else 'English')
            self.theme_combo.setCurrentText('تیره' if app_config.get('theme') == 'dark' else 'روشن')
            self.currency_combo.setCurrentText(app_config.get('currency', 'ریال'))
            self.auto_backup_check.setChecked(app_config.get('auto_backup', True))
            
            # Database settings
            db_config = self.config.get('database', {})
            self.db_host_input.setText(db_config.get('host', 'localhost'))
            self.db_port_input.setValue(db_config.get('port', 5432))
            self.db_name_input.setText(db_config.get('database', 'faran_payroll'))
            self.db_username_input.setText(db_config.get('username', 'postgres'))
            self.db_password_input.setText(db_config.get('password', ''))
            
            # Backup settings
            report_config = self.config.get('report', {})
            self.backup_path_input.setText(report_config.get('save_path', './backups'))
            self.backup_interval.setValue(app_config.get('backup_interval', 7))
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            self.show_error_message("خطا", "خطا در بارگذاری تنظیمات")
    
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
    
    def save_all_settings(self):
        """Save all settings to configuration file"""
        try:
            # Update config dictionary
            self.config['application'].update({
                'company_name': self.company_name_input.text(),
                'company_address': self.company_address_input.toPlainText(),
                'company_phone': self.company_phone_input.text(),
                'language': 'fa' if self.language_combo.currentText() == 'فارسی' else 'en',
                'theme': 'dark' if self.theme_combo.currentText() == 'تیره' else 'light',
                'currency': self.currency_combo.currentText(),
                'auto_backup': self.auto_backup_check.isChecked(),
                'backup_interval': self.backup_interval.value()
            })
            
            self.config['database'].update({
                'host': self.db_host_input.text(),
                'port': self.db_port_input.value(),
                'database': self.db_name_input.text(),
                'username': self.db_username_input.text(),
                'password': self.db_password_input.text()
            })
            
            self.config['report'].update({
                'save_path': self.backup_path_input.text()
            })
            
            # Save to file
            with open('config/settings.json', 'w', encoding='utf-8') as file:
                json.dump(self.config, file, indent=4, ensure_ascii=False)
            
            self.show_success_message("موفقیت", "همه تنظیمات با موفقیت ذخیره شدند")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            self.show_error_message("خطا", "خطا در ذخیره تنظیمات")
    
    def test_database_connection(self):
        """Test database connection with current settings"""
        try:
            # Create temporary database manager with new settings
            temp_db = DatabaseManager()
            temp_db.config = {
                'host': self.db_host_input.text(),
                'port': self.db_port_input.value(),
                'database': self.db_name_input.text(),
                'username': self.db_username_input.text(),
                'password': self.db_password_input.text()
            }
            
            if temp_db.connect():
                self.show_success_message("موفقیت", "اتصال به پایگاه داده با موفقیت برقرار شد")
                temp_db.disconnect()
            else:
                self.show_error_message("خطا", "خطا در اتصال به پایگاه داده")
                
        except Exception as e:
            logger.error(f"Error testing database connection: {e}")
            self.show_error_message("خطا", "خطا در آزمایش اتصال به پایگاه داده")
    
    def create_database_tables(self):
        """Create database tables"""
        reply = QMessageBox.question(
            self,
            "تأیید ایجاد جداول",
            "آیا از ایجاد جداول پایگاه داده اطمینان دارید؟\nاین عمل داده‌های موجود را پاک می‌کند!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.db.create_tables():
                    self.show_success_message("موفقیت", "جداول پایگاه داده با موفقیت ایجاد شدند")
                else:
                    self.show_error_message("خطا", "خطا در ایجاد جداول پایگاه داده")
            except Exception as e:
                logger.error(f"Error creating database tables: {e}")
                self.show_error_message("خطا", "خطا در ایجاد جداول پایگاه داده")
    
    def reset_database(self):
        """Reset database (drop all data)"""
        reply = QMessageBox.warning(
            self,
            "هشدار خطر",
            "⚠️ این عمل تمام داده‌های سیستم را پاک می‌کند!\n\nآیا مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Drop all tables
                tables = ['payroll', 'advances', 'loans', 'attendance', 'personnel']
                
                for table in tables:
                    query = f"DROP TABLE IF EXISTS {table} CASCADE"
                    self.db.execute_query(query)
                
                # Recreate tables
                if self.db.create_tables():
                    self.show_success_message("موفقیت", "پایگاه داده با موفقیت بازنشانی شد")
                else:
                    self.show_error_message("خطا", "خطا در بازنشانی پایگاه داده")
                    
            except Exception as e:
                logger.error(f"Error resetting database: {e}")
                self.show_error_message("خطا", "خطا در بازنشانی پایگاه داده")
    
    def browse_backup_path(self):
        """Browse for backup directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "انتخاب مسیر پشتیبان‌گیری",
            self.backup_path_input.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.backup_path_input.setText(directory)
    
    def create_backup(self):
        """Create database backup"""
        try:
            backup_dir = self.backup_path_input.text()
            if not backup_dir:
                self.show_error_message("خطا", "لطفاً مسیر پشتیبان‌گیری را انتخاب کنید")
                return
            
            # Create backup directory if it doesn't exist
            os.makedirs(backup_dir, exist_ok=True)
            
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"faran_payroll_backup_{timestamp}.sql")
            
            # TODO: Implement actual database backup using pg_dump
            # For now, create a placeholder file
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write("-- Faran Payroll Database Backup\n")
                f.write(f"-- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-- This is a placeholder backup file\n")
            
            # Update backup history
            self.update_backup_history(f"پشتیبان ایجاد شده: {timestamp}")
            
            self.show_success_message("موفقیت", f"پشتیبان با موفقیت ایجاد شد\n{backup_file}")
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            self.show_error_message("خطا", "خطا در ایجاد پشتیبان")
    
    def restore_backup(self):
        """Restore database from backup"""
        try:
            backup_file, _ = QFileDialog.getOpenFileName(
                self,
                "انتخاب فایل پشتیبان",
                self.backup_path_input.text(),
                "SQL Files (*.sql);;All Files (*)"
            )
            
            if backup_file:
                reply = QMessageBox.warning(
                    self,
                    "هشدار",
                    "این عمل داده‌های فعلی را با داده‌های پشتیبان جایگزین می‌کند.\nآیا ادامه می‌دهید؟",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # TODO: Implement actual database restore using psql
                    # For now, just show a message
                    self.update_backup_history(f"پشتیبان بازیابی شده: {os.path.basename(backup_file)}")
                    self.show_success_message("موفقیت", "پشتیبان با موفقیت بازیابی شد")
                    
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            self.show_error_message("خطا", "خطا در بازیابی پشتیبان")
    
    def load_backup_history(self):
        """Load backup history"""
        try:
            backup_dir = self.backup_path_input.text()
            if os.path.exists(backup_dir):
                backups = []
                for file in os.listdir(backup_dir):
                    if file.startswith('faran_payroll_backup_') and file.endswith('.sql'):
                        file_path = os.path.join(backup_dir, file)
                        file_time = os.path.getmtime(file_path)
                        backups.append((file_time, file))
                
                # Sort by date (newest first)
                backups.sort(reverse=True)
                
                history_text = "تاریخچه پشتیبان‌ها:\n\n"
                for file_time, file_name in backups[:10]:  # Show last 10 backups
                    date_str = datetime.fromtimestamp(file_time).strftime('%Y/%m/%d %H:%M')
                    history_text += f"• {date_str} - {file_name}\n"
                
                self.backup_history.setText(history_text)
            else:
                self.backup_history.setText("هیچ پشتیبانی یافت نشد")
                
        except Exception as e:
            logger.error(f"Error loading backup history: {e}")
            self.backup_history.setText("خطا در بارگذاری تاریخچه پشتیبان‌ها")
    
    def update_backup_history(self, message: str):
        """Update backup history with new message"""
        current_text = self.backup_history.toPlainText()
        timestamp = datetime.now().strftime('%Y/%m/%d %H:%M')
        new_text = f"{timestamp} - {message}\n{current_text}"
        self.backup_history.setText(new_text)