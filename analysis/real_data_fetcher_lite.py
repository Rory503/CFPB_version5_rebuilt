"""
Lightweight real-data fetcher optimized for small memory instances.
Downloads full CFPB ZIP file and filters for narratives only.
"""

import os
import io
from datetime import datetime, timedelta
import requests
import pandas as pd
import zipfile


class RealDataFetcher:
    def __init__(self):
        # Configure rolling window (months)
        try:
            months = int(os.environ.get("MONTHS_WINDOW", "4"))
        except ValueError:
            months = 4
        months = max(1, min(months, 12))
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=30 * months)

        # Lite mode: exclude long narratives to reduce memory
        self.lite_mode = str(os.environ.get("LITE_MODE", "0")).lower() in ("1", "true", "yes")
        self.include_narratives = not self.lite_mode

        # Exclusions (credit reporting)
        self.credit_exclusions = [
            "Credit reporting, credit repair services, or other personal consumer reports",
            "Credit reporting",
            "Credit repair services",
            "Other personal consumer reports",
        ]

        self.data_dir = "data"
        self.zip_url = "https://files.consumerfinance.gov/ccdb/complaints.csv.zip"
        os.makedirs(self.data_dir, exist_ok=True)

    def _download_zip(self):
        """Download the full CFPB complaints ZIP file"""
        csv_path = os.path.join(self.data_dir, "complaints.csv")
        zip_path = os.path.join(self.data_dir, "complaints.csv.zip")
        
        # Check if we already have recent data
        if os.path.exists(csv_path):
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(csv_path))
            if file_age.days < 7:  # Data is less than a week old
                print(f"Using existing data file (age: {file_age.days} days)")
                return csv_path
        
        print(f"Downloading latest CFPB complaint data from {self.zip_url}...")
        
        try:
            # Download the ZIP file
            response = requests.get(self.zip_url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            print(f"File size: {total_size / (1024*1024):.1f} MB")
            
            # Save ZIP file
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print("Extracting CSV file...")
            
            # Extract CSV from ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.data_dir)
            
            # Clean up ZIP file
            os.remove(zip_path)
            
            print("Download and extraction complete!")
            return csv_path
            
        except Exception as e:
            print(f"Error downloading ZIP: {e}")
            return None

    def load_and_filter_data(self):
        print(
            f"Loading CFPB data (lite={self.lite_mode}) for window: {self.start_date:%Y-%m-%d} to {self.end_date:%Y-%m-%d}"
        )
        
        # Use months-specific cache file
        months = int((self.end_date - self.start_date).days / 30)
        cache = os.path.join(self.data_dir, f"complaints_filtered_{months}months.csv")
        
        if os.path.exists(cache):
            try:
                cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache))
                if cache_age.days < 7:  # Use cache if less than 7 days old
                    print(f"Using cached file for {months} months (age: {cache_age.days} days)")
                    df = pd.read_csv(cache, low_memory=False)
                    df["Date received"] = pd.to_datetime(df["Date received"]) 
                    df["Date sent to company"] = pd.to_datetime(df["Date sent to company"], errors="coerce")
                    
                    # Verify cache covers our date range
                    cache_start = df["Date received"].min()
                    cache_end = df["Date received"].max()
                    
                    # Check if cache covers requested range (with some tolerance)
                    if cache_start <= self.start_date and cache_end >= (self.end_date - timedelta(days=7)):
                        print(f"Cache covers date range. Loaded {len(df):,} complaints")
                        return df
                    else:
                        print(f"Cache date range insufficient. Need: {self.start_date:%Y-%m-%d} to {self.end_date:%Y-%m-%d}")
                        print(f"Cache has: {cache_start:%Y-%m-%d} to {cache_end:%Y-%m-%d}")
                else:
                    print(f"Cache is {cache_age.days} days old, regenerating...")
            except Exception as e:
                print(f"Error loading cache: {e}")
                pass

        # Download ZIP file and process
        csv_path = self._download_zip()
        if not csv_path or not os.path.exists(csv_path):
            print("Failed to download data file")
            return None
        
        print("Loading CFPB complaint data...")
        
        try:
            # Load data in chunks to handle large file
            chunk_size = 50000
            chunks = []
            
            for chunk in pd.read_csv(csv_path, chunksize=chunk_size, low_memory=False):
                chunks.append(chunk)
                print(f"Loaded {len(chunks) * chunk_size:,} rows...", end="\r")
            
            df = pd.concat(chunks, ignore_index=True)
            print(f"\nTotal complaints loaded: {len(df):,}")
            
            # Convert date columns
            df['Date received'] = pd.to_datetime(df['Date received'])
            df['Date sent to company'] = pd.to_datetime(df['Date sent to company'], errors='coerce')
            
            print("Applying filters...")
            
            # 1. Date range filter
            date_mask = (df['Date received'] >= self.start_date) & (df['Date received'] <= self.end_date)
            print(f"Date range filter: {date_mask.sum():,} complaints match")
            
            # 2. Has narrative filter - check both column name variations
            narrative_col = None
            for col in ['Consumer complaint narrative', 'consumer_complaint_narrative']:
                if col in df.columns:
                    narrative_col = col
                    break
            
            if narrative_col:
                narrative_mask = (
                    df[narrative_col].notna() & 
                    (df[narrative_col].str.strip() != '')
                )
                print(f"Narrative filter: {narrative_mask.sum():,} complaints with narratives")
            else:
                print("WARNING: No narrative column found")
                narrative_mask = pd.Series([True] * len(df))
            
            # 3. Exclude credit reporting - check both column name variations
            product_col = None
            for col in ['Product', 'product']:
                if col in df.columns:
                    product_col = col
                    break
            
            if product_col:
                product_mask = ~df[product_col].isin(self.credit_exclusions)
                print(f"Excluding credit reporting: {(~product_mask).sum():,} excluded")
            else:
                product_mask = pd.Series([True] * len(df))
            
            # Apply all filters
            filtered_df = df[date_mask & narrative_mask & product_mask].copy()
            
            print(f"\nFinal filtered dataset: {len(filtered_df):,} complaints")
            
            # Rename columns for consistency
            col_map = {
                'consumer_complaint_narrative': 'Consumer complaint narrative',
                'complaint_id': 'Complaint ID',
                'date_received': 'Date received',
                'date_sent_to_company': 'Date sent to company',
                'product': 'Product',
                'issue': 'Issue',
                'company': 'Company',
                'state': 'State',
            }
            for old, new in col_map.items():
                if old in filtered_df.columns and new not in filtered_df.columns:
                    filtered_df = filtered_df.rename(columns={old: new})
            
            # Cache the filtered file
            try:
                filtered_df.to_csv(cache, index=False)
                print(f"Cached filtered data to {cache}")
            except Exception:
                pass
            
            return filtered_df
            
        except Exception as e:
            print(f"Error processing data: {e}")
            import traceback
            traceback.print_exc()
            return None

    # The following helpers mirror the original fetcher API
    def get_top_trends(self, df, top_n=10):
        if df is None or len(df) == 0:
            return None
        top_products = df["Product"].value_counts().head(top_n)
        top_issues = df["Issue"].value_counts().head(top_n)
        combos = (
            df.groupby(["Product", "Issue"]).size().reset_index(name="Count").sort_values("Count", ascending=False).head(top_n)
        )
        return {"top_products": top_products, "top_issues": top_issues, "product_issue_combinations": combos}

    def get_sub_trends(self, df, product, top_n=5):
        if df is None or len(df) == 0:
            return None
        sub = df[df["Product"] == product]
        if sub.empty:
            return None
        counts = sub["Issue"].value_counts().head(top_n)
        details = {}
        for issue in counts.index:
            sample = sub[sub["Issue"] == issue][
                [
                    "Complaint ID",
                    "Consumer complaint narrative",
                    "Company",
                    "State",
                    "Date received",
                ]
            ].head(3)
            details[issue] = {
                "count": counts[issue],
                "percentage": (counts[issue] / len(sub)) * 100,
                "sample_complaints": sample.to_dict("records"),
            }
        return details

    def get_top_companies(self, df, top_n=10):
        if df is None or len(df) == 0:
            return None
        credit_agencies = [
            "EQUIFAX, INC.",
            "Experian Information Solutions Inc.",
            "TRANSUNION INTERMEDIATE HOLDINGS, INC.",
            "TransUnion Intermediate Holdings, Inc.",
            "EXPERIAN INFORMATION SOLUTIONS INC.",
            "Equifax Information Services LLC",
            "EXPERIAN",
            "EQUIFAX",
        ]
        base = df[~df["Company"].isin(credit_agencies)]
        top = base["Company"].value_counts().head(top_n)
        out = {}
        for company in top.index:
            cdf = base[base["Company"] == company]
            out[company] = {
                "total_complaints": top[company],
                "top_issues": cdf["Issue"].value_counts().head(5).to_dict(),
                "sample_complaints": cdf[[
                    "Complaint ID",
                    "Consumer complaint narrative",
                    "Issue",
                    "Product",
                    "Date received",
                ]].head(5).to_dict("records"),
            }
        return out

    def generate_complaint_links(self, complaint_ids):
        base = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/detail/"
        return [f"{base}{cid}" for cid in complaint_ids]

    def export_analysis_data(self, df, output_path):
        if df is None or len(df) == 0:
            return
        summary = {
            "total_complaints": len(df),
            "date_range": f"{self.start_date:%Y-%m-%d} to {self.end_date:%Y-%m-%d}",
            "unique_companies": df["Company"].nunique(),
            "unique_products": df["Product"].nunique(),
            "unique_states": df["State"].nunique(),
            "data_exported": datetime.now().isoformat(),
        }
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            pd.DataFrame([summary]).to_excel(writer, sheet_name="Summary", index=False)
            df.head(10000).to_excel(writer, sheet_name="Filtered_Data", index=False)
            tp = df["Product"].value_counts().head(20)
            pd.DataFrame({"Product": tp.index, "Count": tp.values}).to_excel(writer, sheet_name="Top_Products", index=False)
