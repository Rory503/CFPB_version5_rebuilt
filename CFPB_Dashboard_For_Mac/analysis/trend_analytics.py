"""
Trend Analytics Module
Provides real-time analysis for consumer complaint trend questions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TrendAnalytics:
    """Compute real answers to trend analysis questions"""
    
    def __init__(self, analyzer):
        """Initialize with analyzer that has loaded data"""
        self.analyzer = analyzer
        self.df = analyzer.filtered_df if hasattr(analyzer, 'filtered_df') and analyzer.filtered_df is not None else None
        
        if self.df is None:
            self.df = analyzer.df if hasattr(analyzer, 'df') else None
    
    def top_five_categories_last_30_days(self):
        """Get top 5 complaint categories in last 30 days"""
        if self.df is None or self.df.empty:
            return None
        
        try:
            # Ensure date column is datetime
            df = self.df.copy()
            if 'Date received' in df.columns:
                df['Date received'] = pd.to_datetime(df['Date received'], errors='coerce')
                
                # Filter last 30 days
                thirty_days_ago = datetime.now() - timedelta(days=30)
                recent_df = df[df['Date received'] >= thirty_days_ago]
                
                # Group by product
                if 'Product' in recent_df.columns:
                    top_products = recent_df['Product'].value_counts().head(5)
                    
                    return {
                        'title': 'Top 5 Complaint Categories (Last 30 Days)',
                        'data': top_products.to_dict(),
                        'total_complaints': len(recent_df),
                        'date_range': f"{thirty_days_ago.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}"
                    }
        except Exception as e:
            print(f"Error in top_five_categories_last_30_days: {e}")
        
        return None
    
    def companies_with_most_recent_complaints(self, days=30):
        """Companies with most complaints in last N days"""
        if self.df is None or self.df.empty:
            return None
        
        try:
            df = self.df.copy()
            if 'Date received' in df.columns and 'Company' in df.columns:
                df['Date received'] = pd.to_datetime(df['Date received'], errors='coerce')
                
                # Filter recent
                cutoff_date = datetime.now() - timedelta(days=days)
                recent_df = df[df['Date received'] >= cutoff_date]
                
                # Group by company
                top_companies = recent_df['Company'].value_counts().head(10)
                
                return {
                    'title': f'Companies with Most Complaints (Last {days} Days)',
                    'data': top_companies.to_dict(),
                    'total_complaints': len(recent_df),
                    'date_range': f"{cutoff_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}"
                }
        except Exception as e:
            print(f"Error in companies_with_most_recent_complaints: {e}")
        
        return None
    
    def mortgage_complaints_vs_last_quarter(self):
        """Compare mortgage complaints: current quarter vs previous quarter"""
        if self.df is None or self.df.empty:
            return None
        
        try:
            df = self.df.copy()
            if 'Date received' in df.columns and 'Product' in df.columns:
                df['Date received'] = pd.to_datetime(df['Date received'], errors='coerce')
                
                # Define quarters
                now = datetime.now()
                current_quarter_start = now - timedelta(days=90)
                previous_quarter_start = now - timedelta(days=180)
                previous_quarter_end = current_quarter_start
                
                # Filter mortgage complaints
                mortgage_df = df[df['Product'].str.contains('Mortgage', case=False, na=False)]
                
                # Current quarter
                current_quarter = mortgage_df[mortgage_df['Date received'] >= current_quarter_start]
                current_count = len(current_quarter)
                
                # Previous quarter
                previous_quarter = mortgage_df[
                    (mortgage_df['Date received'] >= previous_quarter_start) & 
                    (mortgage_df['Date received'] < previous_quarter_end)
                ]
                previous_count = len(previous_quarter)
                
                # Calculate change
                if previous_count > 0:
                    pct_change = ((current_count - previous_count) / previous_count) * 100
                else:
                    pct_change = 0
                
                return {
                    'title': 'Mortgage Complaints: Current vs Previous Quarter',
                    'current_quarter': {
                        'count': current_count,
                        'period': f"Last 90 days ({current_quarter_start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')})"
                    },
                    'previous_quarter': {
                        'count': previous_count,
                        'period': f"Prior 90 days ({previous_quarter_start.strftime('%Y-%m-%d')} to {previous_quarter_end.strftime('%Y-%m-%d')})"
                    },
                    'change': {
                        'absolute': current_count - previous_count,
                        'percentage': round(pct_change, 2),
                        'direction': 'increase' if pct_change > 0 else 'decrease' if pct_change < 0 else 'no change'
                    }
                }
        except Exception as e:
            print(f"Error in mortgage_complaints_vs_last_quarter: {e}")
        
        return None
    
    def complaints_percentage_with_narratives(self):
        """Calculate what percentage of complaints include narratives"""
        if self.df is None or self.df.empty:
            return None
        
        try:
            df = self.df.copy()
            
            # Find narrative column
            narrative_col = None
            for col in df.columns:
                if 'narrative' in col.lower() or 'complaint' in col.lower():
                    if 'what happened' in col.lower() or 'consumer complaint' in col.lower():
                        narrative_col = col
                        break
            
            if narrative_col:
                # Count non-empty narratives
                total_complaints = len(df)
                with_narrative = df[df[narrative_col].notna() & (df[narrative_col].astype(str).str.strip() != '')].shape[0]
                
                pct = (with_narrative / total_complaints * 100) if total_complaints > 0 else 0
                
                return {
                    'title': 'Complaints with Consumer Narratives',
                    'total_complaints': total_complaints,
                    'with_narratives': with_narrative,
                    'without_narratives': total_complaints - with_narrative,
                    'percentage': round(pct, 2)
                }
        except Exception as e:
            print(f"Error in complaints_percentage_with_narratives: {e}")
        
        return None
    
    def fastest_growing_products(self, months=6):
        """Products showing fastest growth in complaint volume"""
        if self.df is None or self.df.empty:
            return None
        
        try:
            df = self.df.copy()
            if 'Date received' in df.columns and 'Product' in df.columns:
                df['Date received'] = pd.to_datetime(df['Date received'], errors='coerce')
                
                # Split into two periods
                now = datetime.now()
                mid_point = now - timedelta(days=30 * months // 2)
                start_point = now - timedelta(days=30 * months)
                
                # Recent period
                recent = df[df['Date received'] >= mid_point]
                recent_counts = recent['Product'].value_counts()
                
                # Earlier period
                earlier = df[(df['Date received'] >= start_point) & (df['Date received'] < mid_point)]
                earlier_counts = earlier['Product'].value_counts()
                
                # Calculate growth
                growth_data = []
                for product in recent_counts.index:
                    recent_count = recent_counts[product]
                    earlier_count = earlier_counts.get(product, 0)
                    
                    if earlier_count > 0:
                        growth_pct = ((recent_count - earlier_count) / earlier_count) * 100
                        growth_data.append({
                            'product': product,
                            'recent_count': recent_count,
                            'earlier_count': earlier_count,
                            'growth_pct': growth_pct
                        })
                
                # Sort by growth percentage
                growth_data.sort(key=lambda x: x['growth_pct'], reverse=True)
                
                return {
                    'title': f'Fastest Growing Products (Last {months} Months)',
                    'data': growth_data[:10],  # Top 10
                    'period_recent': f"{mid_point.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}",
                    'period_earlier': f"{start_point.strftime('%Y-%m-%d')} to {mid_point.strftime('%Y-%m-%d')}"
                }
        except Exception as e:
            print(f"Error in fastest_growing_products: {e}")
        
        return None
    
    def auto_finance_common_issues(self):
        """Most common issues in auto-finance/vehicle loan complaints"""
        if self.df is None or self.df.empty:
            return None
        
        try:
            df = self.df.copy()
            if 'Product' in df.columns and 'Issue' in df.columns:
                # Filter auto/vehicle related products
                auto_df = df[df['Product'].str.contains('Vehicle|Auto', case=False, na=False)]
                
                if len(auto_df) > 0:
                    # Get top issues
                    top_issues = auto_df['Issue'].value_counts().head(10)
                    
                    return {
                        'title': 'Most Common Auto-Finance Issues',
                        'data': top_issues.to_dict(),
                        'total_auto_complaints': len(auto_df)
                    }
        except Exception as e:
            print(f"Error in auto_finance_common_issues: {e}")
        
        return None
    
    def company_monetary_relief_rate(self, top_n=15):
        """How often companies respond with monetary relief"""
        if self.df is None or self.df.empty:
            return None
        
        try:
            df = self.df.copy()
            if 'Company' in df.columns and 'Company response to consumer' in df.columns:
                # Get top companies
                top_companies = df['Company'].value_counts().head(top_n).index
                
                relief_data = []
                for company in top_companies:
                    company_df = df[df['Company'] == company]
                    total = len(company_df)
                    
                    # Count monetary relief responses
                    relief_responses = company_df[
                        company_df['Company response to consumer'].str.contains(
                            'monetary|relief', case=False, na=False
                        )
                    ]
                    relief_count = len(relief_responses)
                    relief_pct = (relief_count / total * 100) if total > 0 else 0
                    
                    relief_data.append({
                        'company': company,
                        'total_complaints': total,
                        'with_monetary_relief': relief_count,
                        'relief_percentage': round(relief_pct, 2)
                    })
                
                return {
                    'title': f'Monetary Relief Rates (Top {top_n} Companies)',
                    'data': relief_data
                }
        except Exception as e:
            print(f"Error in company_monetary_relief_rate: {e}")
        
        return None


class CompanyAnalytics:
    """Compute answers to company-specific investigation questions"""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.df = analyzer.filtered_df if hasattr(analyzer, 'filtered_df') and analyzer.filtered_df is not None else None
        
        if self.df is None:
            self.df = analyzer.df if hasattr(analyzer, 'df') else None
    
    def company_recent_complaints_summary(self, company_name, days=90):
        """Get recent complaints for a specific company and summarize issues"""
        if self.df is None or self.df.empty:
            return None
        
        try:
            df = self.df.copy()
            if 'Company' in df.columns and 'Date received' in df.columns:
                df['Date received'] = pd.to_datetime(df['Date received'], errors='coerce')
                
                # Filter by company
                company_df = df[df['Company'].str.contains(company_name, case=False, na=False)]
                
                # Filter recent
                cutoff_date = datetime.now() - timedelta(days=days)
                recent_df = company_df[company_df['Date received'] >= cutoff_date]
                
                if len(recent_df) > 0:
                    # Get top issues
                    top_issues = recent_df['Issue'].value_counts().head(5).to_dict() if 'Issue' in recent_df.columns else {}
                    
                    # Get top products
                    top_products = recent_df['Product'].value_counts().head(3).to_dict() if 'Product' in recent_df.columns else {}
                    
                    return {
                        'title': f'Recent Complaints: {company_name}',
                        'company': company_name,
                        'total_complaints': len(recent_df),
                        'date_range': f"Last {days} days ({cutoff_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')})",
                        'top_issues': top_issues,
                        'top_products': top_products
                    }
        except Exception as e:
            print(f"Error in company_recent_complaints_summary: {e}")
        
        return None
    
    def compare_companies(self, company_a, company_b):
        """Compare complaint volumes and issues for two companies"""
        if self.df is None or self.df.empty:
            return None
        
        try:
            df = self.df.copy()
            if 'Company' in df.columns:
                # Get data for both companies
                company_a_df = df[df['Company'].str.contains(company_a, case=False, na=False)]
                company_b_df = df[df['Company'].str.contains(company_b, case=False, na=False)]
                
                # Get top issues for each
                a_issues = company_a_df['Issue'].value_counts().head(5).to_dict() if 'Issue' in company_a_df.columns else {}
                b_issues = company_b_df['Issue'].value_counts().head(5).to_dict() if 'Issue' in company_b_df.columns else {}
                
                return {
                    'title': f'Company Comparison: {company_a} vs {company_b}',
                    'company_a': {
                        'name': company_a,
                        'total_complaints': len(company_a_df),
                        'top_issues': a_issues
                    },
                    'company_b': {
                        'name': company_b,
                        'total_complaints': len(company_b_df),
                        'top_issues': b_issues
                    },
                    'difference': len(company_a_df) - len(company_b_df)
                }
        except Exception as e:
            print(f"Error in compare_companies: {e}")
        
        return None
    
    def company_unresolved_ratio(self, company_name):
        """Calculate unresolved complaint ratio for a company"""
        if self.df is None or self.df.empty:
            return None
        
        try:
            df = self.df.copy()
            if 'Company' in df.columns and 'Company response to consumer' in df.columns:
                company_df = df[df['Company'].str.contains(company_name, case=False, na=False)]
                
                total = len(company_df)
                
                # Count resolved/closed
                resolved = company_df[
                    company_df['Company response to consumer'].str.contains(
                        'Closed|relief', case=False, na=False
                    )
                ]
                resolved_count = len(resolved)
                
                # Unresolved
                unresolved_count = total - resolved_count
                unresolved_pct = (unresolved_count / total * 100) if total > 0 else 0
                
                return {
                    'title': f'Unresolved Complaint Ratio: {company_name}',
                    'company': company_name,
                    'total_complaints': total,
                    'resolved': resolved_count,
                    'unresolved': unresolved_count,
                    'unresolved_percentage': round(unresolved_pct, 2)
                }
        except Exception as e:
            print(f"Error in company_unresolved_ratio: {e}")
        
        return None






