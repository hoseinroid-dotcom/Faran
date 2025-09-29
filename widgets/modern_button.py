from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.font_manager import FontManager

class ModernButton(QPushButton):
    """Modern styled button with Persian font support"""
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setup_button()
    
    def setup_button(self):
        """Setup button styling"""
        self.setFont(FontManager.get_font(point_size=10))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(35)
        
        # Base style
        self.setStyleSheet("""
            ModernButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            ModernButton:hover {
                background-color: #2980b9;
            }
            ModernButton:pressed {
                background-color: #21618c;
            }
            ModernButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)