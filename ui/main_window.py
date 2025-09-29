from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QStackedWidget, QToolBar, QStatusBar,
                            QMessageBox, QMainWindow, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QPixmap
from .base_window import BaseWindow
from .personnel_window import PersonnelWindow
from .attendance_window import AttendanceWindow
from .loans_window import LoansWindow
from .advances_window import AdvancesWindow
from .payroll_window import PayrollWindow
from .reports_window import ReportsWindow
from .settings_window import SettingsWindow
from utils.font_manager import FontManager
from utils.date_converter import DateConverter
import logging

logger = logging.getLogger(__name__)

class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.setup_ui()
        self.setup_navigation()
        
    def setup_ui(self):
        """Setup main window UI"""
        self.setWindowTitle("سیستم حقوق و دستمزد فران")
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)  # این خط تغییر کرد
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Setup sidebar
        self.setup_sidebar(main_layout)
        
        # Setup main content area
        self.setup_content_area(main_layout)
        
        # Setup status bar
        self.setup_status_bar()
        
    def setup_sidebar(self, main_layout: QHBoxLayout):
        """Setup sidebar navigation"""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: none;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # Company info
        company_label = QLabel("شرکت فران")
        company_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-bottom: 1px solid #34495e;
            }
        """)
        company_label.setFont(FontManager.get_font(point_size=14, bold=True))
        sidebar_layout.addWidget(company_label)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("پرسنل", "personnel", "👥"),
            ("حضور و غیاب", "attendance", "⏰"),
            ("وام‌ها", "loans", "💰"),
            ("مساعده‌ها", "advances", "💳"),
            ("محاسبه حقوق", "payroll", "🧮"),
            ("گزارشات", "reports", "📊"),
            ("تنظیمات", "settings", "⚙️")
        ]
        
        for text, key, icon in nav_items:
            btn = QPushButton(f"{icon} {text}")
            btn.setMinimumHeight(45)
            btn.setFont(FontManager.get_font(point_size=11))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #bdc3c7;
                    border: none;
                    text-align: right;
                    padding: 10px 15px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                    color: #ecf0f1;
                }
                QPushButton:pressed {
                    background-color: #1abc9c;
                }
            """)
            btn.setProperty('nav_key', key)
            btn.clicked.connect(self.on_nav_clicked)
            sidebar_layout.addWidget(btn)
            self.nav_buttons[key] = btn
        
        sidebar_layout.addStretch()
        
        # User info and logout
        user_widget = QFrame()
        user_widget.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        user_layout = QVBoxLayout(user_widget)
        
        user_label = QLabel("کاربر: مدیر سیستم")
        user_label.setStyleSheet("color: #ecf0f1;")
        user_label.setFont(FontManager.get_font(point_size=10))
        
        date_label = QLabel(DateConverter.get_current_jalali_date_str())
        date_label.setStyleSheet("color: #bdc3c7;")
        date_label.setFont(FontManager.get_font(point_size=9))
        
        logout_btn = QPushButton("🚪 خروج")
        logout_btn.setMinimumHeight(35)
        logout_btn.setFont(FontManager.get_font(point_size=10))
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        
        user_layout.addWidget(user_label)
        user_layout.addWidget(date_label)
        user_layout.addWidget(logout_btn)
        
        sidebar_layout.addWidget(user_widget)
        main_layout.addWidget(sidebar)
    
    def setup_content_area(self, main_layout: QHBoxLayout):
        """Setup main content area"""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #ecf0f1;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Header
        header_label = QLabel("داشبورد اصلی")
        header_label.setFont(FontManager.get_font(point_size=18, bold=True))
        header_label.setStyleSheet("color: #2c3e50;")
        content_layout.addWidget(header_label)
        
        # Stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        # Create and add windows
        self.pages = {
            'personnel': PersonnelWindow(),
            'attendance': AttendanceWindow(),
            'loans': LoansWindow(),
            'advances': AdvancesWindow(),
            'payroll': PayrollWindow(),
            'reports': ReportsWindow(),
            'settings': SettingsWindow()
        }
        
        for key, page in self.pages.items():
            self.stacked_widget.addWidget(page)
        
        main_layout.addWidget(content_widget)
    
    def setup_status_bar(self):
        """Setup status bar"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Add status labels
        status_label = QLabel("آماده")
        status_label.setFont(FontManager.get_font(point_size=9))
        status_bar.addWidget(status_label)
        
        # Add version info
        version_label = QLabel("ورژن ۱.۰.۰")
        version_label.setFont(FontManager.get_font(point_size=9))
        status_bar.addPermanentWidget(version_label)
    
    def setup_navigation(self):
        """Setup navigation handlers"""
        # Set default page
        self.show_page('personnel')
    
    def on_nav_clicked(self):
        """Handle navigation button clicks"""
        button = self.sender()
        nav_key = button.property('nav_key')
        self.show_page(nav_key)
    
    def show_page(self, page_key: str):
        """Show specific page"""
        if page_key in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[page_key])
            
            # Update button styles
            for key, btn in self.nav_buttons.items():
                if key == page_key:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #1abc9c;
                            color: white;
                            border: none;
                            text-align: right;
                            padding: 10px 15px;
                            border-radius: 5px;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: transparent;
                            color: #bdc3c7;
                            border: none;
                            text-align: right;
                            padding: 10px 15px;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #34495e;
                            color: #ecf0f1;
                        }
                    """)
    
    def logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self,
            "تأیید خروج",
            "آیا از خروج از سیستم اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("User logged out")
            self.close()
    
    def set_current_user(self, user_data: dict):
        """Set current user data"""
        self.current_user = user_data
        # Update UI with user data if needed
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            "تأیید بسته شدن",
            "آیا از بستن برنامه اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
            logger.info("Application closed by user")
        else:
            event.ignore()