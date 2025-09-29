from PyQt6.QtWidgets import QTableWidget
from PyQt6.QtCore import Qt
from utils.font_manager import FontManager

class ModernTable(QTableWidget):
    """Modern styled table with Persian font support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()
    
    def setup_table(self):
        """Setup table styling"""
        self.setFont(FontManager.get_font(point_size=9))
        
        # Base style
        self.setStyleSheet("""
            ModernTable {
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #3498db;
                selection-color: white;
                gridline-color: #dee2e6;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }
            ModernTable::item {
                padding: 5px;
                border-bottom: 1px solid #dee2e6;
            }
            ModernTable::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Table properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)