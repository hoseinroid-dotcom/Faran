import logging
import json
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2 import sql
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger.warning("psycopg2 not available, running in demo mode")

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.config = self.load_config()
        self.demo_data = self.load_demo_data()
        
    def load_config(self) -> Dict[str, Any]:
        """Load database configuration from settings file"""
        try:
            with open('config/settings.json', 'r', encoding='utf-8') as file:
                config = json.load(file)
                return config.get('database', {})
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def load_demo_data(self) -> Dict[str, Any]:
        """Load demo data for offline mode"""
        return {
            'personnel': [
                {
                    'id': 1, 'employee_code': '1001', 
                    'first_name': 'علی', 'last_name': 'رضایی',
                    'national_id': '1234567890', 'position': 'برنامه نویس',
                    'base_salary': 56000000, 'is_active': True,
                    'hire_date': '2023-01-15', 'children_count': 2,
                    'housing_allowance_rate': 0.25, 'family_allowance_rate': 0.1,
                    'created_at': '2023-01-15 10:00:00'
                },
                {
                    'id': 2, 'employee_code': '1002', 
                    'first_name': 'فاطمه', 'last_name': 'محمدی',
                    'national_id': '0987654321', 'position': 'منابع انسانی',
                    'base_salary': 48000000, 'is_active': True,
                    'hire_date': '2023-02-20', 'children_count': 1,
                    'housing_allowance_rate': 0.25, 'family_allowance_rate': 0.1,
                    'created_at': '2023-02-20 09:30:00'
                },
                {
                    'id': 3, 'employee_code': '1003', 
                    'first_name': 'محمد', 'last_name': 'کریمی',
                    'national_id': '1122334455', 'position': 'مدیر مالی',
                    'base_salary': 75000000, 'is_active': True,
                    'hire_date': '2023-03-10', 'children_count': 3,
                    'housing_allowance_rate': 0.25, 'family_allowance_rate': 0.1,
                    'created_at': '2023-03-10 08:45:00'
                }
            ],
            'attendance': [
                {
                    'id': 1, 'personnel_id': 1, 'date': '2024-01-15',
                    'entry_time': '08:00', 'exit_time': '16:30',
                    'overtime_hours': 2.5, 'absence_type': 'حاضر',
                    'description': 'کار عادی'
                }
            ],
            'loans': [
                {
                    'id': 1, 'personnel_id': 1, 'loan_amount': 10000000,
                    'installment_amount': 500000, 'remaining_installments': 18,
                    'total_installments': 20, 'start_date': '2024-01-01',
                    'description': 'وام مسکن', 'is_active': True
                }
            ],
            'advances': [
                {
                    'id': 1, 'personnel_id': 2, 'advance_amount': 2000000,
                    'advance_date': '2024-01-10', 'description': 'مساعده درمان',
                    'is_settled': False
                }
            ],
            'payroll': [
                {
                    'id': 1, 'personnel_id': 1, 'year': 2024, 'month': 1,
                    'base_salary': 56000000, 'housing_allowance': 14000000,
                    'family_allowance': 5600000, 'child_allowance': 1000000,
                    'overtime_amount': 3500000, 'other_allowances': 0,
                    'gross_salary': 80100000, 'insurance_employee': 5607000,
                    'insurance_employer': 18423000, 'tax_amount': 2450000,
                    'loan_deduction': 500000, 'advance_deduction': 0,
                    'other_deductions': 0, 'net_salary': 71443000,
                    'is_paid': True, 'payment_date': '2024-02-01'
                }
            ]
        }
    
    def connect(self) -> bool:
        """Establish database connection"""
        if not PSYCOPG2_AVAILABLE:
            logger.info("Running in demo mode (no database connection)")
            return True
            
        try:
            self.connection = psycopg2.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5432),
                database=self.config.get('database', 'faran_payroll'),
                user=self.config.get('username', 'postgres'),
                password=self.config.get('password', 'password')
            )
            logger.info("Database connected successfully")
            return True
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            logger.info("Falling back to demo mode")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database disconnected")
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Execute a query (INSERT, UPDATE, DELETE)"""
        if not PSYCOPG2_AVAILABLE or not self.connection:
            logger.info("Demo mode: Query execution simulated")
            return True
            
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                return True
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Fetch all results from query"""
        if not PSYCOPG2_AVAILABLE or not self.connection:
            # Return demo data based on query type
            query_lower = query.lower()
            
            if 'personnel' in query_lower:
                return self.demo_data['personnel']
            elif 'attendance' in query_lower:
                return self.demo_data['attendance']
            elif 'loans' in query_lower:
                return self.demo_data['loans']
            elif 'advances' in query_lower:
                return self.demo_data['advances']
            elif 'payroll' in query_lower:
                return self.demo_data['payroll']
            else:
                return []
            
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
        except Exception as e:
            logger.error(f"Fetch all error: {e}")
            return []
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Fetch single result from query"""
        results = self.fetch_all(query, params)
        return results[0] if results else None
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        if not PSYCOPG2_AVAILABLE or not self.connection:
            logger.info("Demo mode: Table creation simulated")
            return True
            
        tables = {
            'personnel': """
                CREATE TABLE IF NOT EXISTS personnel (
                    id SERIAL PRIMARY KEY,
                    employee_code VARCHAR(20) UNIQUE NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    national_id VARCHAR(10) UNIQUE NOT NULL,
                    birth_date DATE,
                    hire_date DATE NOT NULL,
                    position VARCHAR(100),
                    base_salary DECIMAL(15,2) NOT NULL,
                    housing_allowance_rate DECIMAL(5,2) DEFAULT 0.25,
                    family_allowance_rate DECIMAL(5,2) DEFAULT 0.1,
                    children_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'attendance': """
                CREATE TABLE IF NOT EXISTS attendance (
                    id SERIAL PRIMARY KEY,
                    personnel_id INTEGER REFERENCES personnel(id),
                    date DATE NOT NULL,
                    entry_time TIME,
                    exit_time TIME,
                    overtime_hours DECIMAL(4,2) DEFAULT 0,
                    absence_type VARCHAR(20) DEFAULT 'present',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'loans': """
                CREATE TABLE IF NOT EXISTS loans (
                    id SERIAL PRIMARY KEY,
                    personnel_id INTEGER REFERENCES personnel(id),
                    loan_amount DECIMAL(15,2) NOT NULL,
                    installment_amount DECIMAL(15,2) NOT NULL,
                    remaining_installments INTEGER NOT NULL,
                    total_installments INTEGER NOT NULL,
                    start_date DATE NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'advances': """
                CREATE TABLE IF NOT EXISTS advances (
                    id SERIAL PRIMARY KEY,
                    personnel_id INTEGER REFERENCES personnel(id),
                    advance_amount DECIMAL(15,2) NOT NULL,
                    advance_date DATE NOT NULL,
                    description TEXT,
                    is_settled BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'payroll': """
                CREATE TABLE IF NOT EXISTS payroll (
                    id SERIAL PRIMARY KEY,
                    personnel_id INTEGER REFERENCES personnel(id),
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    base_salary DECIMAL(15,2) NOT NULL,
                    housing_allowance DECIMAL(15,2) DEFAULT 0,
                    family_allowance DECIMAL(15,2) DEFAULT 0,
                    child_allowance DECIMAL(15,2) DEFAULT 0,
                    overtime_amount DECIMAL(15,2) DEFAULT 0,
                    other_allowances DECIMAL(15,2) DEFAULT 0,
                    gross_salary DECIMAL(15,2) NOT NULL,
                    insurance_employee DECIMAL(15,2) DEFAULT 0,
                    insurance_employer DECIMAL(15,2) DEFAULT 0,
                    tax_amount DECIMAL(15,2) DEFAULT 0,
                    loan_deduction DECIMAL(15,2) DEFAULT 0,
                    advance_deduction DECIMAL(15,2) DEFAULT 0,
                    other_deductions DECIMAL(15,2) DEFAULT 0,
                    net_salary DECIMAL(15,2) NOT NULL,
                    payment_date DATE,
                    is_paid BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(personnel_id, year, month)
                )
            """
        }
        
        for table_name, table_query in tables.items():
            if not self.execute_query(table_query):
                logger.error(f"Failed to create table: {table_name}")
                return False
        
        logger.info("All tables created successfully")
        return True