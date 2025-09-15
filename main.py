from services import analyze_data, clean_data, load_raw_data, export_to_csv, load_to_postgresql

def main():
    print("🚀 Starting Enterprise Data Processing Pipeline")
    print("=" * 50)
    
    try:
        # 1. EXTRACT: Load the raw data with validation
        print("\n📥 EXTRACT Phase: Loading raw data...")
        raw_df = load_raw_data()
        
        # 2. ANALYZE: Perform initial analysis on the raw data
        print("\n🔍 ANALYZE Phase: Assessing data quality...")
        analyze_data(raw_df)
        
        # 3. TRANSFORM: Clean the data using intelligent algorithms
        print("\n🧹 TRANSFORM Phase: Cleaning and standardizing data...")
        cleaned_df = clean_data(raw_df)
        
        # 4. LOAD: Export the results to multiple destinations
        print("\n💾 LOAD Phase: Exporting cleaned data...")
        export_to_csv(cleaned_df)
        load_to_postgresql(cleaned_df)
        
        print("\n✅ Pipeline execution completed successfully!")
        print(f"📊 Processed {len(cleaned_df)} records")
        print("🌐 Launch web dashboard: python display.py")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        print("🔧 Check logs and configuration before retrying")
        raise

if __name__ == "__main__":
    main()