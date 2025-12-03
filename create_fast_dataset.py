"""
Fast CFPB Data Loader - Pre-filtered Real Data
Creates a smaller file with ONLY the data we need for faster loading
"""

import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Fix Windows encoding issues
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def create_fast_dataset(months=6):
    """Create pre-filtered dataset with real CFPB data matching your requirements"""
    
    print(f"🏛️  Creating Fast CFPB Dataset ({months} months)")
    print("============================")
    
    # Load the full dataset
    data_file = "data/complaints.csv"
    if not os.path.exists(data_file):
        print("❌ Main data file not found")
        return False
    
    print("📊 Loading full CFPB data...")
    df = pd.read_csv(data_file, low_memory=False)
    print(f"✅ Loaded {len(df):,} total complaints")
    
    # Apply your exact filters
    print("🔍 Applying filters...")
    
    # 1. Last N months filter
    cutoff_date = datetime.now() - timedelta(days=30 * months)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d')
    df['Date received'] = pd.to_datetime(df['Date received'])
    df_recent = df[df['Date received'] >= cutoff_str]
    print(f"📅 Last {months} months: {len(df_recent):,} complaints")
    
    # 2. Only complaints with narratives (consumers)
    df_narratives = df_recent[df_recent['Consumer complaint narrative'].notna()]
    print(f"📝 With narratives: {len(df_narratives):,} complaints")
    
    # 3. Exclude credit reporting
    credit_products = [
        'Credit reporting, credit repair services, or other personal consumer reports',
        'Credit reporting',
        'Credit repair services',
        'Other personal consumer reports'
    ]
    df_filtered = df_narratives[~df_narratives['Product'].isin(credit_products)]
    print(f"🚫 Excluding credit reporting: {len(df_filtered):,} complaints")
    
    # Save the pre-filtered dataset with months in filename
    output_file = f"data/complaints_filtered_{months}months.csv"
    df_filtered.to_csv(output_file, index=False)
    print(f"💾 Saved filtered dataset to: {output_file}")
    print(f"📊 Final dataset: {len(df_filtered):,} real CFPB complaints")
    
    return True

if __name__ == "__main__":
    import sys
    months = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    create_fast_dataset(months)