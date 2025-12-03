"""
Supabase Data Manager for CFPB Complaints
Caches complaint data in Supabase for fast loading and historical tracking.
"""

import os
from datetime import datetime, timedelta
import pandas as pd
from supabase import create_client, Client
import streamlit as st


class SupabaseDataManager:
    def __init__(self):
        """Initialize Supabase client with credentials from environment variables."""
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY environment variables."
            )
        
        self.client: Client = create_client(supabase_url, supabase_key)
        self.table_name = "cfpb_complaints"
    
    def setup_table(self):
        """
        Create the complaints table if it doesn't exist.
        Run this once during initial setup.
        
        Table schema:
        - complaint_id (text, primary key)
        - date_received (date)
        - product (text)
        - sub_product (text)
        - issue (text)
        - sub_issue (text)
        - company (text)
        - state (text)
        - zip_code (text)
        - submitted_via (text)
        - company_response (text)
        - timely_response (text)
        - consumer_disputed (text)
        - complaint_text (text, nullable for lite mode)
        - created_at (timestamp)
        - updated_at (timestamp)
        """
        # Note: You'll need to create this table in Supabase dashboard
        # or run SQL directly. This is a reference schema.
        pass
    
    def cache_complaints(self, df: pd.DataFrame) -> int:
        """
        Cache complaints DataFrame to Supabase.
        Uses upsert to avoid duplicates.
        
        Args:
            df: DataFrame with complaint data
            
        Returns:
            Number of records cached
        """
        if df.empty:
            return 0
        
        # Prepare records for Supabase
        records = []
        for _, row in df.iterrows():
            record = {
                "complaint_id": str(row.get("Complaint ID", "")),
                "date_received": row.get("Date received", ""),
                "product": row.get("Product", ""),
                "sub_product": row.get("Sub-product", ""),
                "issue": row.get("Issue", ""),
                "sub_issue": row.get("Sub-issue", ""),
                "company": row.get("Company", ""),
                "state": row.get("State", ""),
                "zip_code": str(row.get("ZIP code", "")),
                "submitted_via": row.get("Submitted via", ""),
                "company_response": row.get("Company response to consumer", ""),
                "timely_response": row.get("Timely response?", ""),
                "consumer_disputed": row.get("Consumer disputed?", ""),
                "complaint_text": row.get("Consumer complaint narrative", ""),
                "updated_at": datetime.now().isoformat(),
            }
            records.append(record)
        
        # Batch upsert (Supabase handles duplicates by complaint_id)
        try:
            response = self.client.table(self.table_name).upsert(records).execute()
            return len(records)
        except Exception as e:
            st.error(f"Error caching to Supabase: {e}")
            return 0
    
    def get_cached_complaints(
        self,
        company: str = None,
        start_date: str = None,
        end_date: str = None,
        product: str = None,
        limit: int = 5000,
    ) -> pd.DataFrame:
        """
        Retrieve cached complaints from Supabase with filters.
        
        Args:
            company: Filter by company name (case-insensitive partial match)
            start_date: Filter by date >= start_date (YYYY-MM-DD)
            end_date: Filter by date <= end_date (YYYY-MM-DD)
            product: Filter by product name
            limit: Maximum records to return
            
        Returns:
            DataFrame with cached complaint data
        """
        try:
            query = self.client.table(self.table_name).select("*")
            
            # Apply filters
            if company:
                query = query.ilike("company", f"%{company}%")
            
            if start_date:
                query = query.gte("date_received", start_date)
            
            if end_date:
                query = query.lte("date_received", end_date)
            
            if product:
                query = query.eq("product", product)
            
            # Execute query with limit
            response = query.limit(limit).execute()
            
            if not response.data:
                return pd.DataFrame()
            
            # Convert to DataFrame and rename columns to match existing format
            df = pd.DataFrame(response.data)
            df = df.rename(columns={
                "complaint_id": "Complaint ID",
                "date_received": "Date received",
                "product": "Product",
                "sub_product": "Sub-product",
                "issue": "Issue",
                "sub_issue": "Sub-issue",
                "company": "Company",
                "state": "State",
                "zip_code": "ZIP code",
                "submitted_via": "Submitted via",
                "company_response": "Company response to consumer",
                "timely_response": "Timely response?",
                "consumer_disputed": "Consumer disputed?",
                "complaint_text": "Consumer complaint narrative",
            })
            
            # Convert date column to datetime
            df["Date received"] = pd.to_datetime(df["Date received"])
            
            return df
        
        except Exception as e:
            st.error(f"Error loading from Supabase: {e}")
            return pd.DataFrame()
    
    def get_cache_stats(self) -> dict:
        """
        Get statistics about cached data.
        
        Returns:
            Dict with cache statistics
        """
        try:
            # Total count
            response = self.client.table(self.table_name).select("complaint_id", count="exact").execute()
            total_count = response.count if hasattr(response, 'count') else 0
            
            # Date range
            date_response = self.client.table(self.table_name)\
                .select("date_received")\
                .order("date_received", desc=False)\
                .limit(1)\
                .execute()
            
            oldest_date = date_response.data[0]["date_received"] if date_response.data else None
            
            date_response = self.client.table(self.table_name)\
                .select("date_received")\
                .order("date_received", desc=True)\
                .limit(1)\
                .execute()
            
            newest_date = date_response.data[0]["date_received"] if date_response.data else None
            
            return {
                "total_complaints": total_count,
                "oldest_complaint": oldest_date,
                "newest_complaint": newest_date,
            }
        
        except Exception as e:
            st.error(f"Error getting cache stats: {e}")
            return {"total_complaints": 0, "oldest_complaint": None, "newest_complaint": None}
    
    def clear_old_data(self, days: int = 90):
        """
        Clear complaints older than specified days to manage storage.
        
        Args:
            days: Delete complaints older than this many days
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        try:
            response = self.client.table(self.table_name)\
                .delete()\
                .lt("date_received", cutoff_date)\
                .execute()
            return True
        except Exception as e:
            st.error(f"Error clearing old data: {e}")
            return False
