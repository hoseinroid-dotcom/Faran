from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import QFile, QIODevice
import os
import logging

logger = logging.getLogger(__name__)

class FontManager:
    _fonts_loaded = False
    
    @classmethod
    def load_fonts(cls):
        """Load IRAN Sans font"""
        if cls._fonts_loaded:
            return
            
        try:
            # Load IRAN Sans font from different possible locations
            font_paths = [
                "fonts/IRANSans.ttf",
                "fonts/IRANSans-web.ttf", 
                "fonts/IRANSansFaNum.ttf",
                "../fonts/IRANSans.ttf",
                "./IRANSans.ttf"
            ]
            
            font_loaded = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    if font_id != -1:
                        logger.info(f"IRAN Sans font loaded successfully from {font_path}")
                        font_loaded = True
                        break
            
            if not font_loaded:
                logger.warning("IRAN Sans font not found. Using system default font.")
                # Try to use system font that supports Persian
                system_fonts = ["Segoe UI", "Tahoma", "Arial"]
                for font_name in system_fonts:
                    if font_name in QFontDatabase.families():
                        logger.info(f"Using system font: {font_name}")
                        break
            
            cls._fonts_loaded = True
            
        except Exception as e:
            logger.error(f"Error loading fonts: {e}")
    
    @classmethod
    def get_font(cls, font_family: str = "IRAN Sans", point_size: int = 10, bold: bool = False):
        """Get configured font"""
        cls.load_fonts()
        
        # Check if IRAN Sans is available
        available_fonts = QFontDatabase.families()
        if "IRAN Sans" not in available_fonts:
            # Fallback to fonts that support Persian
            for font in ["Segoe UI", "Tahoma", "Arial"]:
                if font in available_fonts:
                    font_family = font
                    break
        
        font = QFont(font_family, point_size)
        font.setBold(bold)
        return font
    
    @classmethod
    def set_application_font(cls, app, font_family: str = "IRAN Sans", point_size: int = 9):
        """Set default application font"""
        cls.load_fonts()
        app_font = cls.get_font(font_family, point_size)
        app.setFont(app_font)
    
    @classmethod
    def get_available_fonts(cls):
        """Get list of available font families"""
        return QFontDatabase.families()