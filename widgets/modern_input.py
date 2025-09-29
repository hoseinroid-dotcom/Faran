from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt
from utils.font_manager import FontManager

class ModernInput(QLineEdit):
    """Modern styled input field with Persian font support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_input()
    
    def setup_input(self):
        """Setup input styling"""
        self.setFont(FontManager.get_font(point_size=10))
        self.setMinimumHeight(35)
        
        # Base style
        self.setStyleSheet("""
            ModernInput {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: white;
                selection-background-color: #3498db;
            }
            ModernInput:focus {
                border-color: #3498db;
            }
            ModernInput:disabled {
                background-color: #ecf0f1;
                color: #7f8c8d;
            }
        """)
        
        # Set text alignment for RTL
        self.setAlignment(Qt.AlignmentFlag.AlignRight)