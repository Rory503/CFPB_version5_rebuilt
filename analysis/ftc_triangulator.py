"""
FTC Consumer Sentinel Data Triangulation Module
Compares CFPB trends with FTC Consumer Sentinel data for cross-validation
"""

import pandas as pd
import requests
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

class FTCTriangulator:
    def __init__(self, cfpb_analyzer):
        self.cfpb_analyzer = cfpb_analyzer
        self.ftc_data = None
        
        # Mapping between CFPB products and FTC categories
        self.category_mapping = {
            'Debt collection': ['Debt Management/Credit Services', 'Credit/Debt', 'Debt Collection'],
            'Credit card or prepaid card': ['Credit Cards', 'Prepaid Cards'],
            'Checking or savings account': ['Banking/Credit', 'Online/Mobile Banking'],
            'Mortgage': ['Mortgage/Real Estate', 'Home Improvement', 'Mortgage Lending'],
            'Credit reporting': ['Credit Monitoring/Repair', 'Credit Services'],
            'Money transfer, virtual currency, or money service': ['Wire Transfers', 'Virtual Currency', 'Money Services'],
            'Auto loan': ['Auto-Related', 'Vehicle Sales/Leasing'],
            'Student loan': ['Education/Training', 'Student Loans'],
            'Personal loan': ['Personal Loans', 'Payday Loans'],
            'Payday loan': ['Payday Loans', 'Short-term Lending']
        }
        
        # Keywords for cross-category analysis
        self.fraud_keywords = [
            'fraud', 'scam', 'identity theft', 'phishing', 'wire fraud',
            'unauthorized charges', 'account takeover', 'cybercrime'
        ]
        
        self.digital_keywords = [
            'mobile app', 'online banking', 'digital wallet', 'zelle',
            'venmo', 'cashapp', 'paypal', 'cryptocurrency', 'bitcoin'
        ]
    
    def load_ftc_data(self, csv_path=None, auto_download=False):
        """
        Load FTC Consumer Sentinel data
        Note: FTC data requires manual download from https://www.ftc.gov/exploredata
        """
        if auto_download:
            print("Note: FTC Consumer Sentinel data requires manual download.")
            print("Please visit: https://www.ftc.gov/exploredata")
            print("Download the Consumer Sentinel Network Data Book or raw data files")
            return None
        
        if csv_path:
            try:
                self.ftc_data = pd.read_csv(csv_path, low_memory=False)
                print(f"FTC data loaded: {len(self.ftc_data):,} records")
                
                # Standardize date format if present
                if 'Date Received' in self.ftc_data.columns:
                    self.ftc_data['Date Received'] = pd.to_datetime(self.ftc_data['Date Received'])
                elif 'date_received' in self.ftc_data.columns:
                    self.ftc_data['date_received'] = pd.to_datetime(self.ftc_data['date_received'])
                
                return self.ftc_data
            except Exception as e:
                print(f"Error loading FTC data: {e}")
                return None
        else:
            print("No FTC data path provided. Using simulated data for demonstration.")
            return self._generate_simulated_ftc_data()
    
    def _generate_simulated_ftc_data(self):
        """
        Generate simulated FTC data for demonstration purposes
        Based on typical FTC Consumer Sentinel trends
        """
        np.random.seed(42)
        
        # Simulated data based on real FTC trends
        categories = [
            'Identity Theft', 'Imposter Scams', 'Online Shopping', 'Debt Collection',
            'Credit/Debt', 'Auto-Related', 'Investment Related', 'Banking/Credit',
            'Health Care/Pharmaceutical', 'Mortgage/Real Estate', 'Tech Support',
            'Government/Military', 'Sweepstakes/Lottery', 'Travel/Vacations'
        ]
        
        # Generate date range for last 6 months
        start_date = datetime(2025, 4, 19)
        end_date = datetime(2025, 10, 19)
        date_range = pd.date_range(start_date, end_date, freq='D')
        
        # Generate simulated complaints
        simulated_data = []
        for _ in range(50000):  # Simulate 50k complaints
            category = np.random.choice(categories, p=[0.25, 0.15, 0.12, 0.08, 0.07, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03, 0.02, 0.01])
            date = np.random.choice(date_range)
            amount_lost = np.random.exponential(1000) if np.random.random() < 0.3 else 0
            
            # Add fraud keywords based on category
            has_fraud_keywords = category in ['Identity Theft', 'Imposter Scams', 'Tech Support'] or np.random.random() < 0.1
            has_digital_keywords = category in ['Online Shopping', 'Banking/Credit'] or np.random.random() < 0.2
            
            simulated_data.append({
                'Date Received': date,
                'Category': category,
                'Amount Lost': amount_lost,
                'Has Fraud Keywords': has_fraud_keywords,
                'Has Digital Keywords': has_digital_keywords,
                'State': np.random.choice(['CA', 'TX', 'FL', 'NY', 'PA', 'OH', 'IL', 'GA'], p=[0.12, 0.09, 0.07, 0.06, 0.04, 0.04, 0.04, 0.03])
            })
        
        self.ftc_data = pd.DataFrame(simulated_data)
        print(f"Simulated FTC data generated: {len(self.ftc_data):,} records")
        return self.ftc_data
    
    def compare_trends(self):
        """
        Compare CFPB and FTC trends for overlapping categories
        """
        if self.ftc_data is None:
            self.load_ftc_data()
        
        if self.cfpb_analyzer.filtered_df is None:
            print("CFPB data not loaded. Please load CFPB data first.")
            return None
        
        # Get CFPB trends
        cfpb_trends = self.cfpb_analyzer.get_top_trends()
        cfpb_products = cfpb_trends['products']
        
        # Get FTC trends (simulated or real)
        if self.ftc_data is not None and 'Category' in self.ftc_data.columns:
            ftc_categories = self.ftc_data['Category'].value_counts()
        else:
            ftc_categories = pd.Series()
        
        # Find overlapping categories
        comparisons = {}
        
        for cfpb_product, cfpb_count in cfpb_products.items():
            # Find matching FTC categories
            ftc_matches = []
            if cfpb_product in self.category_mapping:
                for ftc_category in self.category_mapping[cfpb_product]:
                    if ftc_category in ftc_categories.index:
                        ftc_matches.append((ftc_category, ftc_categories[ftc_category]))
            
            if ftc_matches:
                total_ftc_count = sum([count for _, count in ftc_matches])
                comparisons[cfpb_product] = {
                    'cfpb_count': cfpb_count,
                    'ftc_count': total_ftc_count,
                    'ftc_categories': ftc_matches,
                    'ratio': cfpb_count / total_ftc_count if total_ftc_count > 0 else float('inf')
                }
        
        return comparisons
    
    def analyze_fraud_trends(self):
        """
        Analyze fraud trends across both CFPB and FTC data
        """
        results = {}
        
        # CFPB fraud analysis
        if self.cfpb_analyzer.filtered_df is not None:
            cfpb_special = self.cfpb_analyzer.analyze_special_categories()
            cfpb_fraud = cfpb_special['fraud_digital_complaints']
            
            results['cfpb_fraud'] = {
                'total_complaints': len(cfpb_fraud),
                'top_products': cfpb_fraud['product'].value_counts().head(5),
                'percentage_of_total': (len(cfpb_fraud) / len(self.cfpb_analyzer.filtered_df)) * 100
            }
        
        # FTC fraud analysis (simulated or real)
        if self.ftc_data is not None:
            fraud_categories = ['Identity Theft', 'Imposter Scams', 'Tech Support']
            
            if 'Category' in self.ftc_data.columns:
                ftc_fraud = self.ftc_data[self.ftc_data['Category'].isin(fraud_categories)]
            elif 'Has Fraud Keywords' in self.ftc_data.columns:
                ftc_fraud = self.ftc_data[self.ftc_data['Has Fraud Keywords'] == True]
            else:
                ftc_fraud = pd.DataFrame()
            
            if len(ftc_fraud) > 0:
                results['ftc_fraud'] = {
                    'total_complaints': len(ftc_fraud),
                    'top_categories': ftc_fraud['Category'].value_counts().head(5) if 'Category' in ftc_fraud.columns else pd.Series(),
                    'percentage_of_total': (len(ftc_fraud) / len(self.ftc_data)) * 100,
                    'total_losses': ftc_fraud['Amount Lost'].sum() if 'Amount Lost' in ftc_fraud.columns else 0
                }
        
        return results
    
    def create_comparison_chart(self, comparison_data):
        """
        Create visual comparison between CFPB and FTC trends
        """
        if not comparison_data:
            return None
        
        categories = list(comparison_data.keys())
        cfpb_counts = [comparison_data[cat]['cfpb_count'] for cat in categories]
        ftc_counts = [comparison_data[cat]['ftc_count'] for cat in categories]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Side-by-side comparison
        x = np.arange(len(categories))
        width = 0.35
        
        ax1.bar(x - width/2, cfpb_counts, width, label='CFPB', alpha=0.8, color='#1f77b4')
        ax1.bar(x + width/2, ftc_counts, width, label='FTC', alpha=0.8, color='#ff7f0e')
        
        ax1.set_xlabel('Product/Category')
        ax1.set_ylabel('Number of Complaints')
        ax1.set_title('CFPB vs FTC Complaint Volume Comparison')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Ratio analysis
        ratios = [comparison_data[cat]['ratio'] for cat in categories]
        colors = ['green' if r < 1 else 'red' if r > 1 else 'gray' for r in ratios]
        
        ax2.barh(categories, ratios, color=colors, alpha=0.7)
        ax2.set_xlabel('CFPB/FTC Ratio')
        ax2.set_title('CFPB to FTC Complaint Ratio\n(>1 = More CFPB complaints)')
        ax2.axvline(x=1, color='black', linestyle='--', alpha=0.5)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def generate_cross_trend_insights(self):
        """
        Generate insights from cross-platform trend analysis
        """
        insights = []
        
        # Compare trends
        comparisons = self.compare_trends()
        if comparisons:
            # Find categories with high CFPB/FTC ratios
            high_ratio_categories = {k: v for k, v in comparisons.items() if v['ratio'] > 2}
            if high_ratio_categories:
                insights.append({
                    'type': 'high_cfpb_ratio',
                    'title': 'Categories with Disproportionately High CFPB Complaints',
                    'description': f"These categories show >2x more complaints in CFPB vs FTC: {', '.join(high_ratio_categories.keys())}",
                    'data': high_ratio_categories
                })
            
            # Find categories with low ratios
            low_ratio_categories = {k: v for k, v in comparisons.items() if v['ratio'] < 0.5}
            if low_ratio_categories:
                insights.append({
                    'type': 'low_cfpb_ratio',
                    'title': 'Categories with Higher FTC Activity',
                    'description': f"These categories show more FTC complaints: {', '.join(low_ratio_categories.keys())}",
                    'data': low_ratio_categories
                })
        
        # Fraud analysis
        fraud_analysis = self.analyze_fraud_trends()
        if fraud_analysis:
            if 'cfpb_fraud' in fraud_analysis and 'ftc_fraud' in fraud_analysis:
                cfpb_fraud_pct = fraud_analysis['cfpb_fraud']['percentage_of_total']
                ftc_fraud_pct = fraud_analysis['ftc_fraud']['percentage_of_total']
                
                insights.append({
                    'type': 'fraud_comparison',
                    'title': 'Fraud Complaint Distribution',
                    'description': f"Fraud represents {cfpb_fraud_pct:.1f}% of CFPB complaints vs {ftc_fraud_pct:.1f}% of FTC complaints",
                    'data': fraud_analysis
                })
        
        return insights
    
    def export_triangulation_report(self, output_path):
        """
        Export comprehensive triangulation report
        """
        report = {
            'comparison_data': self.compare_trends(),
            'fraud_analysis': self.analyze_fraud_trends(),
            'insights': self.generate_cross_trend_insights(),
            'data_sources': {
                'cfpb_complaints': len(self.cfpb_analyzer.filtered_df) if self.cfpb_analyzer.filtered_df is not None else 0,
                'ftc_reports': len(self.ftc_data) if self.ftc_data is not None else 0,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        # Save as JSON for structured access
        import json
        with open(f"{output_path}.json", 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Triangulation report exported to {output_path}.json")
        return report

if __name__ == "__main__":
    print("FTC Triangulation Module for CFPB Analysis")
    print("==========================================")
    print("This module compares CFPB trends with FTC Consumer Sentinel data")
    print("Note: FTC data requires manual download from https://www.ftc.gov/exploredata")
    print("For demonstration, simulated FTC data will be used if no real data is provided.")