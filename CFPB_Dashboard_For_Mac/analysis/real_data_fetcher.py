"""
Real CFPB Data Fetcher and Processor
Downloads and processes actual CFPB complaint data from the official website
"""

import requests
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import zipfile
import io
from urllib.parse import urljoin
import time

class CFPBRealDataFetcher:
    def __init__(self):
        # Ensure Unicode output works on Windows consoles (prevents 'charmap' codec errors)
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        self.base_url = "https://www.consumerfinance.gov/data-research/consumer-complaints/"
        self.data_url = "https://files.consumerfinance.gov/ccdb/complaints.csv.zip"
        self.data_dir = "data/"
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Date range for analysis (last 6 months) - use relative dates
        # Try to get MONTHS_WINDOW from environment, default to 6 months
        try:
            months = int(os.environ.get("MONTHS_WINDOW", "6"))
        except ValueError:
            months = 6
        months = max(1, min(months, 12))
        
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=30 * months)
        
        # Credit reporting categories to exclude (both checkboxes)
        self.credit_exclusions = [
            "Credit reporting, credit repair services, or other personal consumer reports",
            "Credit reporting",
            "Credit repair services", 
            "Other personal consumer reports"
        ]
        
    def download_latest_data(self, force_download=False):
        """
        Download the latest CFPB complaint data
        """
        csv_path = os.path.join(self.data_dir, "complaints.csv")
        zip_path = os.path.join(self.data_dir, "complaints.csv.zip")
        
        # Check if we already have recent data
        if os.path.exists(csv_path) and not force_download:
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(csv_path))
            if file_age.days < 7:  # Data is less than a week old
                print(f"✅ Using existing data file (age: {file_age.days} days)")
                return csv_path
        
        print("📥 Downloading latest CFPB complaint data...")
        print(f"🌐 Source: {self.data_url}")
        
        try:
            # Download the ZIP file
            response = requests.get(self.data_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            print(f"📦 File size: {total_size / (1024*1024):.1f} MB")
            
            # Save ZIP file with progress
            with open(zip_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r⬇️  Progress: {progress:.1f}%", end="", flush=True)
            
            print("\n🗜️  Extracting CSV file...")
            
            # Extract CSV from ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.data_dir)
            
            # Clean up ZIP file
            os.remove(zip_path)
            
            print("✅ Download and extraction complete!")
            return csv_path
            
        except requests.RequestException as e:
            print(f"❌ Error downloading data: {e}")
            print("🔗 Please manually download from: https://www.consumerfinance.gov/data-research/consumer-complaints/#download-the-data")
            return None
        except Exception as e:
            print(f"❌ Error processing data: {e}")
            return None
    
    def load_and_filter_data(self, csv_path=None):
        """
        Load real CFPB data and apply filters as specified
        """
        # Use months-specific cache file
        months = int((self.end_date - self.start_date).days / 30)
        fast_file = f"data/complaints_filtered_{months}months.csv"
        
        if os.path.exists(fast_file):
            print(f"📊 Loading pre-filtered CFPB data for {months} months...")
            try:
                # Check cache age - accept files up to 7 days old
                cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(fast_file))
                if cache_age.days < 7:
                    print(f"📁 Using cached file (age: {cache_age.days} days)")
                    df = pd.read_csv(fast_file, low_memory=False)
                    
                    # Convert date columns
                    df['Date received'] = pd.to_datetime(df['Date received'])
                    df['Date sent to company'] = pd.to_datetime(df['Date sent to company'], errors='coerce')
                    
                    # Verify cache covers our date range
                    cache_start = df['Date received'].min()
                    cache_end = df['Date received'].max()
                    
                    # Check if cache covers requested range (with some tolerance)
                    if cache_start <= self.start_date and cache_end >= (self.end_date - timedelta(days=7)):
                        print(f"✅ Loaded {len(df):,} real CFPB complaints for {months} months")
                        return df
                    else:
                        print(f"⚠️ Cache date range insufficient. Need: {self.start_date:%Y-%m-%d} to {self.end_date:%Y-%m-%d}")
                        print(f"📅 Cache has: {cache_start:%Y-%m-%d} to {cache_end:%Y-%m-%d}")
                        print("🔄 Regenerating from full dataset...")
                else:
                    print(f"⚠️ Cache is {cache_age.days} days old, regenerating...")
            except Exception as e:
                print(f"⚠️ Error loading cache: {e}")
                print("📊 Falling back to full dataset...")
        
        # Skip Socrata API - use local files only

        # Use local data only - no downloads
        csv_path = os.path.join(self.data_dir, "complaints.csv")
        
        if not os.path.exists(csv_path):
            print("❌ No data file available. Please download manually.")
            return None
        
        print("📊 Loading CFPB complaint data...")
        
        try:
            # Load data in chunks to handle large file
            chunk_size = 50000
            chunks = []
            
            for chunk in pd.read_csv(csv_path, chunksize=chunk_size, low_memory=False):
                chunks.append(chunk)
                print(f"📈 Loaded {len(chunks) * chunk_size:,} rows...", end="\r")
            
            df = pd.concat(chunks, ignore_index=True)
            print(f"\n✅ Total complaints loaded: {len(df):,}")
            
            # Convert date columns
            df['Date received'] = pd.to_datetime(df['Date received'])
            df['Date sent to company'] = pd.to_datetime(df['Date sent to company'], errors='coerce')
            
            print("🔍 Applying filters...")
            
            # Debug: Print date range being used
            print(f"📅 Looking for complaints between: {self.start_date.strftime('%Y-%m-%d')} and {self.end_date.strftime('%Y-%m-%d')}")
            print(f"📅 Data has complaints from: {df['Date received'].min()} to {df['Date received'].max()}")
            
            # 1. Date range filter (last 6 months)
            date_mask = (
                (df['Date received'] >= self.start_date) & 
                (df['Date received'] <= self.end_date)
            )
            print(f"📅 Date range filter: {date_mask.sum():,} complaints match date range")
            
            # 2. Has narrative filter (must have consumer complaint narrative)
            narrative_mask = (
                df['Consumer complaint narrative'].notna() & 
                (df['Consumer complaint narrative'].str.strip() != '')
            )
            print(f"📝 Narrative filter: {narrative_mask.sum():,} complaints with narratives")
            
            # 3. Exclude credit reporting categories (both checkboxes)
            product_mask = ~df['Product'].isin(self.credit_exclusions)
            print(f"🚫 Excluding credit reporting: {(~product_mask).sum():,} credit complaints excluded")
            
            # Apply all filters
            filtered_df = df[date_mask & narrative_mask & product_mask].copy()
            
            print(f"\n🎯 Final filtered dataset: {len(filtered_df):,} complaints")
            print(f"📊 Date range: {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
            print(f"📋 Criteria: Narratives only, excluding credit reporting, last 6 months")
            
            # Add some summary stats
            print(f"\n📈 Quick Stats:")
            print(f"   • Unique companies: {filtered_df['Company'].nunique():,}")
            print(f"   • Unique products: {filtered_df['Product'].nunique()}")
            print(f"   • States covered: {filtered_df['State'].nunique()}")
            print(f"   • Date range span: {(filtered_df['Date received'].max() - filtered_df['Date received'].min()).days} days")
            
            # Cache the filtered file for faster future loads
            try:
                filtered_df.to_csv(fast_file, index=False)
                print(f"💾 Cached filtered data to {fast_file}")
            except Exception as cache_error:
                print(f"⚠️ Could not save cache: {cache_error}")
            
            return filtered_df
            
        except Exception as e:
            print(f"❌ Error processing data: {e}")
            return None
    
    def get_top_trends(self, df, top_n=10):
        """
        Get top complaint trends by product and issue
        """
        if df is None or len(df) == 0:
            return None
        
        print(f"📊 Analyzing top {top_n} trends...")
        
        # Top products (excluding credit reporting)
        top_products = df['Product'].value_counts().head(top_n)
        
        # Top issues
        top_issues = df['Issue'].value_counts().head(top_n)
        
        # Product-Issue combinations
        product_issue_combos = (
            df.groupby(['Product', 'Issue'])
            .size()
            .reset_index(name='Count')
            .sort_values('Count', ascending=False)
            .head(top_n)
        )
        
        return {
            'top_products': top_products,
            'top_issues': top_issues,
            'product_issue_combinations': product_issue_combos
        }
    
    def get_sub_trends(self, df, product, top_n=5):
        """
        Get sub-trends (issues) for a specific product with sample complaints
        """
        if df is None or len(df) == 0:
            return None
        
        product_data = df[df['Product'] == product].copy()
        
        if len(product_data) == 0:
            return None
        
        sub_issues = product_data['Issue'].value_counts().head(top_n)
        
        sub_trend_details = {}
        for issue in sub_issues.index:
            issue_data = product_data[product_data['Issue'] == issue]
            
            # Get sample complaints with IDs and narratives
            sample_complaints = issue_data[
                ['Complaint ID', 'Consumer complaint narrative', 'Company', 'State', 'Date received']
            ].head(3)
            
            sub_trend_details[issue] = {
                'count': sub_issues[issue],
                'percentage': (sub_issues[issue] / len(product_data)) * 100,
                'sample_complaints': sample_complaints.to_dict('records')
            }
        
        return sub_trend_details
    
    def get_top_companies(self, df, top_n=10):
        """
        Get most complained about companies (excluding credit reporting agencies)
        """
        if df is None or len(df) == 0:
            return None
        
        # Credit reporting agencies to exclude
        credit_agencies = [
            'EQUIFAX, INC.',
            'Experian Information Solutions Inc.',
            'TRANSUNION INTERMEDIATE HOLDINGS, INC.',
            'TransUnion Intermediate Holdings, Inc.',
            'EXPERIAN INFORMATION SOLUTIONS INC.',
            'Equifax Information Services LLC',
            'EXPERIAN',
            'EQUIFAX'
        ]
        
        # Filter out credit agencies
        df_companies = df[~df['Company'].isin(credit_agencies)].copy()
        
        top_companies = df_companies['Company'].value_counts().head(top_n)
        
        company_details = {}
        for company in top_companies.index:
            company_data = df_companies[df_companies['Company'] == company]
            
            # Top issues for this company
            top_issues = company_data['Issue'].value_counts().head(5)
            
            # Sample complaints for this company
            sample_complaints = company_data[
                ['Complaint ID', 'Consumer complaint narrative', 'Issue', 'Product', 'Date received']
            ].head(5)
            
            company_details[company] = {
                'total_complaints': top_companies[company],
                'top_issues': top_issues.to_dict(),
                'sample_complaints': sample_complaints.to_dict('records')
            }
        
        return company_details
    
    def generate_complaint_links(self, complaint_ids):
        """
        Generate clickable CFPB complaint detail links
        """
        base_url = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/detail/"
        return [f"{base_url}{complaint_id}" for complaint_id in complaint_ids]
    
    def export_analysis_data(self, df, output_path):
        """
        Export processed data for further analysis
        """
        if df is None or len(df) == 0:
            print("❌ No data to export")
            return
        
        print(f"💾 Exporting analysis data to {output_path}...")
        
        # Create summary statistics
        summary = {
            'total_complaints': len(df),
            'date_range': f"{self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}",
            'unique_companies': df['Company'].nunique(),
            'unique_products': df['Product'].nunique(),
            'unique_states': df['State'].nunique(),
            'data_exported': datetime.now().isoformat()
        }
        
        # Export to Excel with multiple sheets
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            pd.DataFrame([summary]).to_excel(writer, sheet_name='Summary', index=False)
            
            # Full filtered data (first 10,000 rows due to Excel limits)
            df.head(10000).to_excel(writer, sheet_name='Filtered_Data', index=False)
            
            # Top products
            top_products = df['Product'].value_counts().head(20)
            pd.DataFrame({'Product': top_products.index, 'Count': top_products.values}).to_excel(
                writer, sheet_name='Top_Products', index=False
            )
            
            # Top companies
            companies = self.get_top_companies(df, 20)
            if companies:
                company_list = []
                for company, data in companies.items():
                    company_list.append({
                        'Company': company,
                        'Total_Complaints': data['total_complaints'],
                        'Top_Issue': list(data['top_issues'].keys())[0] if data['top_issues'] else 'N/A'
                    })
                pd.DataFrame(company_list).to_excel(writer, sheet_name='Top_Companies', index=False)
        
        print(f"✅ Data exported successfully to {output_path}")

if __name__ == "__main__":
    print("🏛️  CFPB Real Data Fetcher and Processor")
    print("=========================================")
    
    fetcher = CFPBRealDataFetcher()
    
    # Download and process real data
    filtered_data = fetcher.load_and_filter_data()
    
    if filtered_data is not None:
        print("\n📊 Generating analysis...")
        
        # Get top trends
        trends = fetcher.get_top_trends(filtered_data)
        if trends:
            print("\n🔥 Top 10 Product Categories (Excluding Credit Reporting):")
            for i, (product, count) in enumerate(trends['top_products'].items(), 1):
                pct = (count / len(filtered_data)) * 100
                print(f"   {i:2d}. {product:<50} {count:>8,} ({pct:>5.1f}%)")
        
        # Get top companies
        companies = fetcher.get_top_companies(filtered_data)
        if companies:
            print("\n🏢 Top 10 Most Complained About Companies:")
            for i, (company, data) in enumerate(companies.items(), 1):
                print(f"   {i:2d}. {company:<50} {data['total_complaints']:>8,}")
        
        # Export data
        fetcher.export_analysis_data(filtered_data, "outputs/cfpb_real_analysis.xlsx")
        
        print("\n✅ Real data analysis complete!")
        print("📁 Check outputs/cfpb_real_analysis.xlsx for detailed results")
    else:
        print("❌ Unable to process data. Please check your connection and try again.")
