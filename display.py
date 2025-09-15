from flask import Flask, render_template
import csv
import os

app = Flask(__name__)

# Define the expected column structure for e-commerce transaction data
COLUMNS = [
    "transaction_id",    # Unique identifier for each transaction
    "customer_id",       # Customer identifier for relationship tracking
    "product_id",        # Product SKU or identifier
    "product_name",      # Human-readable product name
    "quantity",          # Number of items purchased
    "price_per_unit",    # Individual item price
    "total_price",       # Total transaction value (quantity × price_per_unit)
    "transaction_date",  # Date of purchase (standardized to YYYY-MM-DD)
]

def read_csv(filename):
    """Read CSV file and return list of dictionaries"""
    try:
        with open(filename, newline="", encoding="utf-8") as f:
            # Use DictReader with actual header
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return []

def format_currency(value):
    """
    Example:
        format_currency(1234.5) -> "$1,234.50"
        format_currency("invalid") -> "invalid"
    """
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return value

@app.route("/")
def compare_csv():
    """Main comparison page"""
    original = read_csv("sales_transactions.csv")
    cleaned = read_csv("cleaned_sales_transactions.csv")
    
    # Get some stats for the header
    stats = {
        'original_count': len(original),
        'cleaned_count': len(cleaned),
        'rows_removed': len(original) - len(cleaned),
        'cleaning_percentage': round((1 - len(cleaned)/len(original)) * 100, 1) if original else 0
    }

    max_len = max(len(original), len(cleaned))
    rows_to_display = []

    for i in range(min(max_len, 108)):  # Limit to first 108 rows for performance
        orig_row = original[i] if i < len(original) else None
        clean_row = cleaned[i] if i < len(cleaned) else None

        diffs = set()
        if orig_row and clean_row:
            # Compare normalized values
            for col in COLUMNS:
                orig_val = str(orig_row.get(col, '')).strip()
                clean_val = str(clean_row.get(col, '')).strip()

                # Handle numeric comparison for quantity, price fields
                if col in ['quantity', 'price_per_unit', 'total_price']:
                    try:
                        if float(orig_val) != float(clean_val):
                            diffs.add(col)
                    except (ValueError, TypeError):
                        if orig_val != clean_val:
                            diffs.add(col)
                else:
                    if orig_val != clean_val:
                        diffs.add(col)

        rows_to_display.append({
            "original": orig_row,
            "cleaned": clean_row,
            "diffs": diffs,
            "is_dropped": orig_row is not None and clean_row is None,
            "is_new": clean_row is not None and orig_row is None,
            "row_number": i + 1
        })

    return render_template(
        "index.html",
        columns=COLUMNS,
        rows=rows_to_display,
        stats=stats,
        format_currency=format_currency
    )

@app.route("/stats")
def show_stats():
    """Simple statistics page"""
    cleaned = read_csv("cleaned_sales_transactions.csv")
    
    if not cleaned:
        return "No data available"
    
    # Basic statistics
    total_revenue = sum(float(row.get('total_price', 0)) for row in cleaned)
    avg_order_value = total_revenue / len(cleaned) if cleaned else 0
    
    # Product counts by quantity
    product_counts = {}
    for row in cleaned:
        product = row.get('product_name', 'Unknown')
        qty = int(row.get('quantity', 0))
        product_counts[product] = product_counts.get(product, 0) + qty

    return render_template(
        "stats.html",
        total_records=len(cleaned),
        total_revenue=total_revenue,
        avg_order_value=avg_order_value,
        total_quantity=sum(product_counts.values()),
        product_counts=sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    )

if __name__ == "__main__":
    
    # Check if running in production mode
    is_production = os.getenv('FLASK_ENV') == 'production'
    
    if is_production:
        print("⚠️  Production mode detected!")
        print("🚀 Use a proper WSGI server like Gunicorn for production deployment")
        print("📖 Example: gunicorn -w 4 -b 0.0.0.0:5000 display:app")
    else:
        # Development server configuration
        print("🌐 Starting Data Visualization Dashboard...")
        print("📊 Access your dashboard at: http://localhost:5000")
        print("🔄 Press Ctrl+C to stop the server")
        print("-" * 50)
    
    app.run(
        debug=not is_production,    # Disable debug in production
        host='127.0.0.1' if not is_production else '0.0.0.0',  # Localhost for dev, all interfaces for prod
        port=int(os.getenv('PORT', 5000)),  # Allow port configuration via environment
        use_reloader=not is_production      # Disable reloader in production
    )