import os

# Database connection details - use environment variables with fallbacks
DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '01010')  # Default for development only
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'eshop_db')

# Construct the database URL for SQLAlchemy
DATABASE_URL = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# File paths
RAW_DATA_PATH = 'sales_transactions.csv'
CLEANED_DATA_PATH = 'cleaned_sales_transactions.csv'

# Product normalization mapping
PRODUCT_MAPPING = {
    r'usb[-\s]?c': 'USB-C Cable',
    r'usbc': 'USB-C Cable',
    r'webcam': 'Webcam',
    r'mouse': 'Mouse',
    r'keyboard': 'Keyboard',
    r'laptop': 'Laptop',
    r'monitor': 'Monitor',
    r'tablet': 'Tablet',
    r'printer': 'Printer',
    r'headphones': 'Headphones',
    r'charger': 'Charger',
    r'smartphone': 'Smartphone'
}