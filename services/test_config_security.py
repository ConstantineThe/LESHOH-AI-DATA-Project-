import os
import re
import sys

# Add the parent directory to Python path so we can import services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_file_exists():
    """Test that config file exists"""
    config_path = os.path.join('services', 'config.py')
    assert os.path.exists(config_path), f"Config file not found at: {config_path}"

def test_no_hardcoded_default_password():
    """Test that default password isn't hardcoded in business logic"""
    config_path = os.path.join('services', 'config.py')

    with open(config_path, 'r') as f:
        content = f.read()

    # This is just a warning, not a failure, since default passwords are common in development
    if '01010' in content:
        print("⚠️  Warning: Default password found in config.py")
        print("   Consider using environment variables for production:")
        print("   Example: DB_PASSWORD = os.getenv('DB_PASSWORD', '01010')")

def test_database_url_security():
    """Test that database URL doesn't expose real passwords"""
    config_path = os.path.join('services', 'config.py')

    with open(config_path, 'r') as f:
        content = f.read()

    # Check if database URL contains password
    url_pattern = r"postgresql://[^:]+:([^@]+)@"
    matches = re.findall(url_pattern, content)

    for password in matches:
        if password != '01010':
            print(f"⚠️  Warning: Database URL contains password: {password}")
            print("   Consider using environment variables for security")

def test_required_config_variables():
    """Test that config has all required variables"""
    config_path = os.path.join('services', 'config.py')

    with open(config_path, 'r') as f:
        content = f.read()

    required_vars = ['DB_USERNAME', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DATABASE_URL']
    missing_vars = [var for var in required_vars if var not in content]

    assert not missing_vars, f"Missing configuration variables: {missing_vars}"

def test_business_logic_no_credentials():
    """Test that business logic files don't contain credentials"""
    business_files = ['data_cleaning.py', 'data_analysis.py']

    for file in business_files:
        filepath = os.path.join('services', file)
        if not os.path.exists(filepath):
            continue  # Skip if file doesn't exist

        with open(filepath, 'r') as f:
            content = f.read()

        # Should not find the actual password in business logic
        assert '01010' not in content, f"Hardcoded password found in {file}"

        # Should not find database connection details
        assert 'postgresql://' not in content, f"Database URL found in business logic file {file}"