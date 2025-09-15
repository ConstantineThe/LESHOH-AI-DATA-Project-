def analyze_data(df):
    """
    Analyzes a DataFrame and prints a report on data quality issues.
    Does not modify the input DataFrame.
    """
    print("Original data shape:", df.shape)
    print("\nInitial data preview:")
    print(df.head())

    print("\n=== MISSING VALUES ===")
    missing_values = df.isnull().sum()
    print(missing_values)

    print("\n=== DATA TYPES ===")
    print(df.dtypes)

    print("\n=== DUPLICATE ROWS ===")
    duplicates = df.duplicated().sum()
    print(f"Total duplicate rows: {duplicates}")

    print("\n=== PRODUCT NAME INCONSISTENCIES ===")
    print("Unique product names:")
    print(df['product_name'].unique())

    print("\n=== DATE FORMAT ISSUES ===")
    print("Sample dates:")
    print(df['transaction_date'].head(10))

    print("\n=== OUTLIER ANALYSIS ===")
    print("Quantity stats:")
    print(df['quantity'].describe())
    print("\nTotal price stats:")
    print(df['total_price'].describe())
    print("\nPrice per unit stats:")
    print(df['price_per_unit'].describe())