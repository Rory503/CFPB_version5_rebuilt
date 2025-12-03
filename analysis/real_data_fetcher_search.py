"""
Fetcher that uses the official CFPB Search API (consumerfinance.gov)
instead of the Socrata Open Data API. This matches the API docs you
shared and avoids needing a Socrata token.

Docs base: https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/

We page using `frm` and `size`, and return a normalized DataFrame with
columns compatible with the rest of the app.
"""

import os
from datetime import datetime, timedelta
import requests
import pandas as pd

try:
    from analysis.supabase_data_manager import SupabaseDataManager
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


class SearchAPIRealDataFetcher:
    def __init__(self, months=4, max_records=5000, use_cache=True):
        base = os.environ.get(
            "CFPB_SEARCH_API_BASE",
            "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/",
        )
        self.base_url = base.rstrip("/") + "/"
        # Rolling window in months (default 4 for snappy loads, max 3 for web)
        months = max(1, min(int(months), 3))  # Limit to 3 months max for web deployment
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=30 * months)
        # Lite mode: do not retain long narratives (default enabled for memory efficiency)
        self.lite_mode = str(os.environ.get("LITE_MODE", "1")).lower() in ("1", "true", "yes")
        # Maximum records to load (prevent memory overflow)
        self.max_records = int(os.environ.get("MAX_RECORDS", max_records))
        # Exclude credit reporting product family
        self.credit_exclusions = {
            "Credit reporting, credit repair services, or other personal consumer reports",
            "Credit reporting",
            "Credit repair services",
            "Other personal consumer reports",
        }
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize Supabase caching if credentials are available
        self.use_cache = use_cache and SUPABASE_AVAILABLE
        self.supabase_manager = None
        if self.use_cache:
            try:
                self.supabase_manager = SupabaseDataManager()
                print("✅ Supabase caching enabled")
            except Exception as e:
                print(f"⚠️  Supabase unavailable ({e}), using direct API mode")
                self.use_cache = False

    def _page(self, size=1000):
        """Yield pages of results from the Search API, respecting API paging limits and max_records."""
        frm = 0
        max_offset = min(10000, self.max_records)  # Limit to max_records or API max, whichever is smaller
        warned = False
        total_yielded = 0
        while True:
            if frm >= max_offset or total_yielded >= self.max_records:
                if not warned:
                    print(f"⚠️  API paging stopped at frm={frm} (reached max_records limit: {self.max_records})")
                    warned = True
                break
            params = {
                "date_received_min": f"{self.start_date:%Y-%m-%d}",
                "date_received_max": f"{self.end_date:%Y-%m-%d}",
                "no_aggs": "true",
                "no_highlight": "true",
                "size": min(size, self.max_records - total_yielded),  # Adjust size to not exceed max
                "frm": frm,
            }
            if not self.lite_mode:
                params["has_narrative"] = "yes"

            r = requests.get(self.base_url, params=params, timeout=90)
            if r.status_code == 400:
                print(f"Search API paging stopped at frm={frm} (400 Bad Request, likely offset/size too high)")
                break
            r.raise_for_status()
            data = r.json()
            hits = (data or {}).get("hits", {}).get("hits", [])
            if not hits:
                break
            yield hits
            total_yielded += len(hits)
            if len(hits) < size or total_yielded >= self.max_records:
                break
            frm += size

    def load_and_filter_data(self, company=None):
        """
        Load via Search API or Supabase cache.
        
        Args:
            company: Optional company filter for targeted loading
        
        Returns:
            DataFrame with complaint data
        """
        # Try loading from Supabase cache first
        if self.use_cache and self.supabase_manager:
            print(f"\n💾 Checking Supabase cache...")
            cached_df = self.supabase_manager.get_cached_complaints(
                company=company,
                start_date=self.start_date.strftime("%Y-%m-%d"),
                end_date=self.end_date.strftime("%Y-%m-%d"),
                limit=self.max_records
            )
            
            if not cached_df.empty:
                print(f"✅ Loaded {len(cached_df)} complaints from cache (instant!)")
                return self._apply_filters(cached_df)
            else:
                print("⚠️  No cached data found, fetching from CFPB API...")
        
        # Fallback to API loading
        print(
            f"\n🏛️  Loading Real CFPB Complaint Data\n{'='*35}\nSearch API load (lite={self.lite_mode}, max={self.max_records}) window: {self.start_date:%Y-%m-%d}..{self.end_date:%Y-%m-%d}"
        )
        rows = []
        truncated = False
        try:
            for hits in self._page():
                for h in hits:
                    if len(rows) >= self.max_records:
                        truncated = True
                        break
                    s = h.get("_source", {})
                    # Only include narrative if not in lite mode (saves memory)
                    row_data = {
                        "Complaint ID": s.get("complaint_id"),
                        "Date received": s.get("date_received"),
                        "Date sent to company": s.get("date_sent_to_company"),
                        "Product": s.get("product"),
                        "Issue": s.get("issue"),
                        "Company": s.get("company"),
                        "State": s.get("state"),
                    }
                    if not self.lite_mode:
                        row_data["Consumer complaint narrative"] = s.get("complaint_what_happened")
                    rows.append(row_data)
                if truncated:
                    break
            if truncated:
                print(f"⚠️  Reached max_records limit ({self.max_records}). Data truncated.")
        except requests.HTTPError as e:
            print(f"Search API error: {e}")
            return None
        except Exception as e:
            print(f"Search API exception: {e}")
            import traceback
            print(traceback.format_exc())
            return None

        if not rows:
            print("⚠️  No complaint data loaded from API.")
            return None

        # Limit rows before creating DataFrame to save memory
        if len(rows) > self.max_records:
            rows = rows[:self.max_records]
            truncated = True

        df = pd.DataFrame(rows)
        print(f"✅ Loaded {len(df):,} complaints from API")
        
        if truncated:
            print(f"⚠️  Data truncated to {self.max_records} records for memory efficiency.")
        
        # Parse dates
        df["Date received"] = pd.to_datetime(df["Date received"], errors="coerce")
        df["Date sent to company"] = pd.to_datetime(
            df["Date sent to company"], errors="coerce"
        )

        # Cache to Supabase in the background
        if self.use_cache and self.supabase_manager and not df.empty:
            try:
                cached_count = self.supabase_manager.cache_complaints(df)
                print(f"💾 Cached {cached_count} complaints to Supabase")
            except Exception as e:
                print(f"⚠️  Failed to cache to Supabase: {e}")

        # Apply filters and return
        return self._apply_filters(df)
    
    def _apply_filters(self, df):
        """Apply common filters to DataFrame."""
        if df.empty:
            return df
        
        # Filter window (defense-in-depth) and narrative presence only when not in lite mode
        mask = (df["Date received"] >= self.start_date) & (
            df["Date received"] <= self.end_date
        )
        if not self.lite_mode and "Consumer complaint narrative" in df.columns:
            mask &= df["Consumer complaint narrative"].notna() & (
                df["Consumer complaint narrative"].str.strip() != ""
            )
        df = df[mask].copy()

        # Exclude credit reporting families
        df = df[~df["Product"].isin(self.credit_exclusions)].copy()

        # Drop narrative when lite mode is on (if it somehow got added)
        if self.lite_mode and "Consumer complaint narrative" in df.columns:
            df.drop(columns=["Consumer complaint narrative"], inplace=True)

        # Downcast to categories to minimize memory
        for col in ["Product", "Issue", "Company", "State"]:
            if col in df.columns:
                df[col] = df[col].astype("category")

        # Clear rows list to free memory
        rows = None
        
        # Cache for quick re-use (only if reasonable size)
        try:
            if len(df) < 10000:  # Only cache if not too large
                df.to_csv(os.path.join(self.data_dir, "complaints_filtered.csv"), index=False)
        except Exception:
            pass

        return df

    # The rest of the interface mirrors other fetchers
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
                    "Consumer complaint narrative"
                    if "Consumer complaint narrative" in sub.columns
                    else None,
                    "Company",
                    "State",
                    "Date received",
                ]
            ]
            sample = sample.dropna(how="all", axis=1).head(3)
            details[issue] = {
                "count": counts[issue],
                "percentage": (counts[issue] / len(sub)) * 100,
                "sample_complaints": sample.to_dict("records"),
            }
        return details

    def get_top_companies(self, df, top_n=10):
        if df is None or len(df) == 0:
            return None
        exclude = {
            "EQUIFAX, INC.",
            "Experian Information Solutions Inc.",
            "TRANSUNION INTERMEDIATE HOLDINGS, INC.",
            "TransUnion Intermediate Holdings, Inc.",
            "EXPERIAN INFORMATION SOLUTIONS INC.",
            "Equifax Information Services LLC",
            "EXPERIAN",
            "EQUIFAX",
        }
        base = df[~df["Company"].isin(exclude)]
        top = base["Company"].value_counts().head(top_n)
        out = {}
        for company in top.index:
            cdf = base[base["Company"] == company]
            out[company] = {
                "total_complaints": top[company],
                "top_issues": cdf["Issue"].value_counts().head(5).to_dict(),
                "sample_complaints": cdf[[
                    "Complaint ID",
                    "Consumer complaint narrative"
                    if "Consumer complaint narrative" in cdf.columns
                    else None,
                    "Issue",
                    "Product",
                    "Date received",
                ]].dropna(how="all", axis=1).head(5).to_dict("records"),
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

