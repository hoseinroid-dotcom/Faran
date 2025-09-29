from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from utils.font_manager import FontManager
import logging

logger = logging.getLogger(__name__)

class BaseWindow(QMainWindow):
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.apply_fonts()
        
    def setup_window(self):
        """Setup basic window properties"""
        self.setMinimumSize(1000, 700)
        self.center_window()
        
    def center_window(self):
        """Center window on screen"""
        screen = self.screen().availableGeometry()
        size = self.frameGeometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def apply_fonts(self):
        """Apply fonts to window"""
        self.setFont(FontManager.get_font(point_size=9))
    
    def show_message(self, title: str, message: str, icon=QMessageBox.Icon.Information):
        """Show message box"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        msg.setFont(FontManager.get_font())
        msg.exec()
    
    def show_error(self, title: str, message: str):
        """Show error message"""
        self.show_message(title, message, QMessageBox.Icon.Critical)
    
    def show_warning(self, title: str, message: str):
        """Show warning message"""
        self.show_message(title, message, QMessageBox.Icon.Warning)
    
    def show_success(self, title: str, message: str):
        """Show success message"""
        self.show_message(title, message, QMessageBox.Icon.Information)
    
    def create_central_widget(self) -> QWidget:
        """Create central widget with layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        return central_widget
    
    def create_layout(self, central_widget: QWidget, layout_type=QVBoxLayout) -> QVBoxLayout:
        """Create layout for central widget"""
        layout = layout_type(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        return layout