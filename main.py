import sys
import os
import json
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTranslator, QLocale
from PyQt6.QtGui import QFontDatabase, QIcon
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from utils.font_manager import FontManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('noor_gosteran_faran_payroll.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class NoorGosteranFaranPayroll:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.translator = QTranslator()
        self.login_window = None
        self.main_window = None
        self.setup_application()
        
    def setup_application(self):
        """Setup application configuration"""
        try:
            # Set application properties
            self.app.setApplicationName("نور گستران فاران - سیستم حقوق و دستمزد")
            self.app.setApplicationVersion("۱.۰.۰")
            self.app.setOrganizationName("نور گستران فاران")
            
            # Set application icon
            self.set_application_icon()
            
            # Load fonts
            FontManager.load_fonts()
            
            # Set default application font
            FontManager.set_application_font(self.app, "IRAN Sans", 9)
            
            # Set dark theme
            self.apply_theme('dark')
            
            # Setup translator
            self.setup_translator()
            
            # Initialize database
            self.initialize_database()
            
            logger.info("Application setup completed for Noor Gosteran Faran")
            
        except Exception as e:
            logger.error(f"Error in application setup: {e}")
            self.show_critical_error("خطا در راه‌اندازی برنامه", str(e))
    
    def set_application_icon(self):
        """Set application icon"""
        icon_paths = [
            "icons/logo.png",
            "icons/logo.ico",
            "icons/app_icon.png",
            "../icons/logo.png"
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                self.app.setWindowIcon(QIcon(icon_path))
                logger.info(f"Application icon set from {icon_path}")
                return
        
        logger.warning("Application icon not found")
    
    def apply_theme(self, theme='dark'):
        """Apply theme to application"""
        try:
            theme_file = f"themes/{theme}.qss"
            if os.path.exists(theme_file):
                with open(theme_file, 'r', encoding='utf-8') as file:
                    self.app.setStyleSheet(file.read())
                logger.info(f"Theme {theme} applied successfully")
            else:
                logger.warning(f"Theme file {theme_file} not found, using default theme")
        except Exception as e:
            logger.error(f"Error applying theme: {e}")
    
    def setup_translator(self):
        """Setup application translator"""
        try:
            # Load Persian translation if available
            if self.translator.load('translations/faran_payroll_fa.qm'):
                self.app.installTranslator(self.translator)
                logger.info("Persian translator loaded successfully")
            else:
                logger.info("No translation file found, using default language")
        except Exception as e:
            logger.error(f"Error setting up translator: {e}")
    
    def initialize_database(self):
        """Initialize database connection and tables"""
        try:
            from database.database_manager import DatabaseManager
            db = DatabaseManager()
            
            if db.connect():
                logger.info("Database connected successfully")
                
                # Create tables if they don't exist
                if db.create_tables():
                    logger.info("Database tables created/verified successfully")
                else:
                    logger.error("Failed to create database tables")
                
                db.disconnect()
            else:
                logger.warning("Running in demo mode - no database connection")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            logger.warning("Running in demo mode due to database error")
    
    def show_login_window(self):
        """Show login window"""
        try:
            self.login_window = LoginWindow()
            self.login_window.login_successful.connect(self.show_main_window)
            self.login_window.show()
            logger.info("Login window displayed successfully")
        except Exception as e:
            logger.error(f"Error showing login window: {e}")
            self.show_critical_error("خطا در نمایش پنجره ورود", str(e))
    
    def show_main_window(self):
        """Show main window after successful login"""
        try:
            logger.info("Attempting to show main window...")
            
            if self.login_window:
                logger.info("Closing login window...")
                self.login_window.close()
                self.login_window = None
            
            logger.info("Creating main window instance...")
            self.main_window = MainWindow()
            
            logger.info("Showing main window...")
            self.main_window.show()
            
            logger.info("Main window displayed successfully")
            
        except Exception as e:
            logger.error(f"Error showing main window: {e}", exc_info=True)
            self.show_critical_error("خطا در نمایش پنجره اصلی", str(e))
    
    def show_critical_error(self, title: str, message: str):
        """Show critical error message and exit"""
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setWindowTitle(title)
        error_msg.setText(message)
        error_msg.setInformativeText("برنامه خواهد بست.")
        error_msg.exec()
        sys.exit(1)
    
    def show_warning(self, title: str, message: str):
        """Show warning message"""
        warning_msg = QMessageBox()
        warning_msg.setIcon(QMessageBox.Icon.Warning)
        warning_msg.setWindowTitle(title)
        warning_msg.setText(message)
        warning_msg.exec()
    
    def run(self):
        """Run the application"""
        try:
            logger.info("Starting Noor Gosteran Faran Payroll System...")
            
            # Show login window
            self.show_login_window()
            
            # Execute application
            exit_code = self.app.exec()
            
            if exit_code == 0:
                logger.info("Application exited normally")
            else:
                logger.warning(f"Application exited with code: {exit_code}")
            
            return exit_code
            
        except Exception as e:
            logger.error(f"Fatal error running application: {e}")
            self.show_critical_error("خطای بحرانی", f"خطای غیرمنتظره:\n{str(e)}")
            return 1
    
    def cleanup(self):
        """Cleanup resources before exit"""
        try:
            if self.main_window:
                self.main_window.close()
            if self.login_window:
                self.login_window.close()
            
            logger.info("Application cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow keyboard interrupts
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Show error message to user
    error_msg = QMessageBox()
    error_msg.setIcon(QMessageBox.Icon.Critical)
    error_msg.setWindowTitle("خطای غیرمنتظره")
    error_msg.setText("یک خطای غیرمنتظره رخ داده است.")
    error_msg.setInformativeText(f"خطا: {str(exc_value)}")
    error_msg.setDetailedText(f"نوع خطا: {exc_type.__name__}\n\nTraceback:\n{exc_traceback}")
    error_msg.exec()

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import PyQt6
        import jdatetime
        import json
        import logging
        
        # Check for psycopg2 but don't fail if not available
        try:
            import psycopg2
            logger.info("PostgreSQL driver (psycopg2) is available")
        except ImportError:
            logger.warning("PostgreSQL driver (psycopg2) not available - running in demo mode")
        
        logger.info("Core dependencies are available")
        return True
        
    except ImportError as e:
        logger.error(f"Missing core dependency: {e}")
        
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("خطای وابستگی")
        error_msg.setText("کتابخانه‌های اصلی مورد نیاز یافت نشد.")
        error_msg.setInformativeText(f"کتابخانه گمشده: {str(e)}\n\nلطفا requirements.txt را نصب کنید.")
        error_msg.exec()
        
        return False

def create_required_directories():
    """Create required directories if they don't exist"""
    directories = [
        'config',
        'database',
        'fonts',
        'icons',
        'themes',
        'ui',
        'utils',
        'widgets',
        'backups',
        'reports',
        'logs'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Directory created/verified: {directory}")
        except Exception as e:
            logger.warning(f"Could not create directory {directory}: {e}")

def create_default_config():
    """Create default configuration file if it doesn't exist"""
    config_path = 'config/settings.json'
    
    if not os.path.exists(config_path):
        try:
            default_config = {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "noor_gosteran_faran_payroll",
                    "username": "postgres",
                    "password": "password"
                },
                "application": {
                    "language": "fa",
                    "theme": "dark",
                    "auto_backup": True,
                    "backup_path": "./backups",
                    "backup_interval": 7,
                    "company_name": "نور گستران فاران",
                    "company_address": "تهران، خیابان ولیعصر، پلاک ۱۰۰",
                    "company_phone": "۰۲۱-۸۸۵۶۱۲۳۴",
                    "currency": "ریال"
                },
                "calculation": {
                    "base_salary": 56000000,
                    "housing_allowance": 0.25,
                    "family_allowance": 0.1,
                    "child_allowance": 500000,
                    "insurance_employee": 0.07,
                    "insurance_employer": 0.23,
                    "tax_threshold": 56000000
                },
                "report": {
                    "default_format": "pdf",
                    "auto_print": false,
                    "save_path": "./reports"
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            
            logger.info("Default configuration file created")
            
        except Exception as e:
            logger.error(f"Error creating default config: {e}")

def main():
    """Main entry point"""
    try:
        # Set up global exception handler
        sys.excepthook = handle_exception
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Create required directories
        create_required_directories()
        
        # Create default configuration
        create_default_config()
        
        # Create and run application
        app = NoorGosteranFaranPayroll()
        
        # Ensure cleanup on exit
        import atexit
        atexit.register(app.cleanup)
        
        # Run the application
        exit_code = app.run()
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error in main: {e}")
        
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("خطای راه‌اندازی")
        error_msg.setText("برنامه نمی‌تواند راه‌اندازی شود.")
        error_msg.setInformativeText(f"خطا: {str(e)}")
        error_msg.exec()
        
        sys.exit(1)

if __name__ == "__main__":
    main()