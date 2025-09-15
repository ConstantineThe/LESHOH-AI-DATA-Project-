# database_loader.py
import pandas as pd
from sqlalchemy import create_engine, text
from .config import DATABASE_URL, CLEANED_DATA_PATH

def load_raw_data():
    """Loads the raw data from CSV into a Pandas DataFrame."""
    print(f"Loading raw data from sales_transactions.csv...")
    df = pd.read_csv('sales_transactions.csv')
    print(f"Success. Loaded {len(df)} rows.")
    return df

def export_to_csv(df, filepath=CLEANED_DATA_PATH):
    """Exports a DataFrame to a CSV file."""
    print(f"\nExporting cleaned data to {filepath}...")
    df.to_csv(filepath, index=False)
    print("Export successful.")

def load_to_postgresql(df, table_name='cleaned_sales'):
    """
    Loads a DataFrame into a PostgreSQL table using SQLAlchemy.
    Replaces the table if it already exists.
    """
    try:
        print(f"\nConnecting to database and loading into table '{table_name}'...")
        engine = create_engine(DATABASE_URL)

        df.to_sql(
            table_name,
            engine,
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=1000
        )
        print(f"Success! Loaded {len(df)} rows into PostgreSQL.")
        return True

    except Exception as e:
        print(f"Error loading data to PostgreSQL: {e}")
        return False

def create_relational_tables(engine):
    """Create the relational database tables"""
    schema_sql = """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id VARCHAR(50) PRIMARY KEY,
        customer_name VARCHAR(100),
        email VARCHAR(100),
        created_date DATE
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id VARCHAR(50) PRIMARY KEY,
        product_name VARCHAR(100) NOT NULL,
        category VARCHAR(50),
        standard_price DECIMAL(10, 2)
    );

    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id VARCHAR(50) PRIMARY KEY,
        customer_id VARCHAR(50) NOT NULL,
        transaction_date DATE NOT NULL,
        total_amount DECIMAL(10, 2),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE IF NOT EXISTS transaction_items (
        item_id SERIAL PRIMARY KEY,
        transaction_id VARCHAR(50) NOT NULL,
        product_id VARCHAR(50) NOT NULL,
        quantity INTEGER NOT NULL,
        price_per_unit DECIMAL(10, 2) NOT NULL,
        total_price DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """

    with engine.connect() as conn:
        conn.execute(text(schema_sql))
        conn.commit()

def transform_to_relational(df):
    """Transform flat data to relational format"""
    # Extract unique customers
    customers = df[['customer_id']].drop_duplicates()
    customers['customer_name'] = 'Customer ' + customers['customer_id']
    customers['email'] = customers['customer_id'].str.lower() + '@example.com'
    customers['created_date'] = pd.to_datetime('2023-01-01')

    # Extract unique products
    products = df[['product_id', 'product_name']].drop_duplicates()
    products['category'] = 'Electronics'
    products['standard_price'] = df.groupby('product_id')['price_per_unit'].transform('mean')

    # Create transactions
    transactions = df[['transaction_id', 'customer_id', 'transaction_date']].drop_duplicates()
    transactions['total_amount'] = df.groupby('transaction_id')['total_price'].transform('sum')

    # Create transaction items
    transaction_items = df[['transaction_id', 'product_id', 'quantity', 'price_per_unit', 'total_price']].copy()

    return customers, products, transactions, transaction_items

def load_to_postgresql_relational(df, table_name_prefix=''):
    """
    Loads data into PostgreSQL using relational schema
    """
    try:
        print(f"\nCreating relational database structure...")
        engine = create_engine(DATABASE_URL)

        # Create tables
        create_relational_tables(engine)

        # Transform data
        customers, products, transactions, transaction_items = transform_to_relational(df)

        # Load data
        print("Loading customers...")
        customers.to_sql('customers', engine, if_exists='append', index=False)

        print("Loading products...")
        products.to_sql('products', engine, if_exists='append', index=False)

        print("Loading transactions...")
        transactions.to_sql('transactions', engine, if_exists='append', index=False)

        print("Loading transaction items...")
        transaction_items.to_sql('transaction_items', engine, if_exists='append', index=False)

        print(f"Success! Loaded data into relational schema.")
        return True

    except Exception as e:
        print(f"Error loading data to PostgreSQL: {e}")
        return False

def execute_sql_query(query, params=None):
    """Execute a SQL query and return results"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            if params:
                result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))

            if result.returns_rows:
                return pd.DataFrame(result.fetchall(), columns=result.keys())
            else:
                return pd.DataFrame()

    except Exception as e:
        print(f"Error executing query: {e}")
        return pd.DataFrame()

def run_sql_file(file_path):
    """Execute all SQL queries from a file"""
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()

        # Split into individual queries
        queries = [q.strip() for q in sql_content.split(';') if q.strip()]

        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            for query in queries:
                if query:  # Skip empty queries
                    conn.execute(text(query))
            conn.commit()

        print(f"Successfully executed {len(queries)} queries from {file_path}")
        return True

    except Exception as e:
        print(f"Error running SQL file: {e}")
        return False