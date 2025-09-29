from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFrame, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
from .base_window import BaseWindow
from utils.font_manager import FontManager
import logging

logger = logging.getLogger(__name__)

class LoginWindow(BaseWindow):
    login_successful = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup login window UI"""
        self.setWindowTitle("ورود به سیستم حقوق و دستمزد فاران")
        self.setFixedSize(400, 500)
        
        central_widget = self.create_central_widget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Logo
        self.setup_logo(layout)
        
        # Title
        self.setup_title(layout)
        
        # Login form
        self.setup_login_form(layout)
        
        # Buttons
        self.setup_buttons(layout)
    
    def setup_logo(self, layout: QVBoxLayout):
        """Setup logo section"""
        logo_label = QLabel()
        logo_pixmap = QPixmap("icons/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            logo_label.setText("LOGO")
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
    
    def setup_title(self, layout: QVBoxLayout):
        """Setup title section"""
        title_label = QLabel("سیستم حقوق و دستمزد فاران")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(FontManager.get_font(point_size=16, bold=True))
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Faran Payroll System")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(FontManager.get_font(point_size=12))
        layout.addWidget(subtitle_label)
    
    def setup_login_form(self, layout: QVBoxLayout):
        """Setup login form"""
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Username
        username_layout = QVBoxLayout()
        username_label = QLabel("نام کاربری:")
        username_label.setFont(FontManager.get_font(bold=True))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری خود را وارد کنید")
        self.username_input.setMinimumHeight(35)
        
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        form_layout.addLayout(username_layout)
        
        # Password
        password_layout = QVBoxLayout()
        password_label = QLabel("کلمه عبور:")
        password_label.setFont(FontManager.get_font(bold=True))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("کلمه عبور خود را وارد کنید")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)
        
        # Remember me
        self.remember_checkbox = QCheckBox("مرا به خاطر بسپار")
        self.remember_checkbox.setFont(FontManager.get_font())
        form_layout.addWidget(self.remember_checkbox)
        
        layout.addWidget(form_frame)
    
    def setup_buttons(self, layout: QVBoxLayout):
        """Setup login buttons"""
        # Login button
        self.login_button = QPushButton("ورود به سیستم")
        self.login_button.setMinimumHeight(40)
        self.login_button.setFont(FontManager.get_font(point_size=12, bold=True))
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        self.login_button.clicked.connect(self.attempt_login)
        layout.addWidget(self.login_button)
        
        # Forgot password
        forgot_button = QPushButton("کلمه عبور را فراموش کرده‌ام")
        forgot_button.setFont(FontManager.get_font(point_size=9))
        forgot_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
            }
            QPushButton:hover {
                color: #2980b9;
                text-decoration: underline;
            }
        """)
        layout.addWidget(forgot_button)
    
    def attempt_login(self):
        """Attempt to login"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_error("خطا", "لطفاً نام کاربری و کلمه عبور را وارد کنید")
            return
        
        # TODO: Implement actual authentication
        # For now, accept any non-empty credentials
        if username and password:
            logger.info(f"User {username} logged in successfully")
            self.login_successful.emit()
        else:
            self.show_error("خطا", "نام کاربری یا کلمه عبور اشتباه است")