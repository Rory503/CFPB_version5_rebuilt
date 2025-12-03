"""
CFPB Real Data Analyzer - Version 5.0
Processes real CFPB complaint data with no simulated data
"""

import pandas as pd
import sys
import numpy as np
from datetime import datetime, timedelta
import re
import os
import warnings

# Prefer the lightweight fetcher if available. The web app adds the
# 'analysis' folder to sys.path, so we import modules without the prefix.
try:
    from real_data_fetcher_lite import RealDataFetcher as CFPBRealDataFetcher
except Exception:
    from real_data_fetcher import CFPBRealDataFetcher

warnings.filterwarnings('ignore')

class CFPBRealAnalyzer:
    def __init__(self):
        # Ensure Unicode output works on Windows consoles to avoid 'charmap' codec errors
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        self.data_dir = "data/"
        self.output_dir = "outputs/"
        self.viz_dir = "visualizations/"
        
        # Initialize real data fetcher
        self.data_fetcher = CFPBRealDataFetcher()
        
        # Data will be loaded from real CFPB source
        self.df = None
        self.filtered_df = None
        
        # Special keyword filters for analysis - refined for precision
        self.ai_keywords = [
            "artificial intelligence", "AI decision", "AI algorithm", "algorithmic decision", 
            "algorithmic bias", "machine learning model", "automated decision making",
            "chatbot", "robo-advisor", "automated underwriting", "algorithm denied",
            "AI system", "intelligent automation", "predictive model", "credit scoring algorithm"
        ]
        
        self.lep_keywords = [
            "Spanish language", "LEP", "limited English proficiency", "language barrier",
            "interpreter", "translation service", "bilingual support", "Spanish-speaking",
            "language assistance", "non-English speaker", "Spanish documents",
            "language discrimination", "English proficiency"
        ]
        
        self.fraud_digital_keywords = [
            "unauthorized transaction", "fraudulent charge", "identity theft", "phishing scam",
            "account takeover", "Zelle fraud", "digital wallet fraud", "wire fraud",
            "ACH fraud", "synthetic identity", "cybercrime", "online banking fraud",
            "mobile banking fraud", "unauthorized transfer", "fraudulent account"
        ]
        
        # Ensure output directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.viz_dir, exist_ok=True)
    
    def load_real_data(self, force_download=False):
        """
        Load real CFPB complaint data from official source
        """
        print("🏛️  Loading Real CFPB Complaint Data")
        print("====================================")
        
        # Use the real data fetcher to get filtered data
        self.filtered_df = self.data_fetcher.load_and_filter_data()
        
        if self.filtered_df is None:
            print("❌ Failed to load real CFPB data")
            return False
        
        print(f"✅ Successfully loaded {len(self.filtered_df):,} real complaints")
        return True
    
    def get_top_trends(self, top_n=10):
        """
        Get top complaint trends from real data
        """
        if self.filtered_df is None:
            print("❌ No data loaded. Call load_real_data() first.")
            return None
        
        return self.data_fetcher.get_top_trends(self.filtered_df, top_n)
    
    def get_top_companies(self, top_n=10):
        """
        Get most complained about companies from real data
        """
        if self.filtered_df is None:
            print("❌ No data loaded. Call load_real_data() first.")
            return None
        
        return self.data_fetcher.get_top_companies(self.filtered_df, top_n)
    
    def get_sub_trends(self, product, top_n=5):
        """
        Get sub-trends for a specific product from real data
        """
        if self.filtered_df is None:
            print("❌ No data loaded. Call load_real_data() first.")
            return None
        
        return self.data_fetcher.get_sub_trends(self.filtered_df, product, top_n)
    
    def analyze_special_categories(self):
        """
        Analyze AI, LEP/Spanish, and fraud/digital complaint categories from real data
        """
        if self.filtered_df is None:
            print("❌ No data loaded. Call load_real_data() first.")
            return None
        
        results = {}
        
        # AI-related complaints - using word boundaries for precision
        ai_pattern = r'\b(?:' + '|'.join(self.ai_keywords) + r')\b'
        ai_mask = self.filtered_df['Consumer complaint narrative'].str.contains(
            ai_pattern, case=False, na=False, regex=True
        )
        results['ai_complaints'] = self.filtered_df[ai_mask].copy()
        
        # LEP/Spanish complaints - using word boundaries for precision
        lep_pattern = r'\b(?:' + '|'.join(self.lep_keywords) + r')\b'
        lep_mask = self.filtered_df['Consumer complaint narrative'].str.contains(
            lep_pattern, case=False, na=False, regex=True
        )
        results['lep_complaints'] = self.filtered_df[lep_mask].copy()
        
        # Fraud/Digital complaints - using word boundaries for precision
        fraud_pattern = r'\b(?:' + '|'.join(self.fraud_digital_keywords) + r')\b'
        fraud_mask = self.filtered_df['Consumer complaint narrative'].str.contains(
            fraud_pattern, case=False, na=False, regex=True
        )
        results['fraud_digital_complaints'] = self.filtered_df[fraud_mask].copy()
        
        print(f"🤖 AI-related complaints: {len(results['ai_complaints']):,}")
        print(f"🌐 LEP/Spanish complaints: {len(results['lep_complaints']):,}")
        print(f"🚨 Fraud/Digital complaints: {len(results['fraud_digital_complaints']):,}")
        
        return results
    
    def generate_complaint_links(self, complaint_ids):
        """
        Generate clickable CFPB complaint links
        """
        return self.data_fetcher.generate_complaint_links(complaint_ids)
    
    def export_summary_stats(self):
        """
        Export summary statistics from real data
        """
        if self.filtered_df is None:
            return None
        
        summary = {
            'total_complaints': len(self.filtered_df),
            'date_range': f"{self.data_fetcher.start_date.strftime('%Y-%m-%d')} to {self.data_fetcher.end_date.strftime('%Y-%m-%d')}",
            'unique_companies': self.filtered_df['Company'].nunique(),
            'unique_products': self.filtered_df['Product'].nunique(),
            'unique_states': self.filtered_df['State'].nunique(),
            'avg_complaints_per_day': len(self.filtered_df) / ((self.data_fetcher.end_date - self.data_fetcher.start_date).days + 1),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': 'Real CFPB Consumer Complaint Database'
        }
        
        return summary
    
    def create_detailed_report(self):
        """
        Create comprehensive report with real data analysis
        """
        if self.filtered_df is None:
            print("❌ No data loaded. Call load_real_data() first.")
            return None
        
        print("📊 Generating detailed analysis report...")
        
        # Get all analysis components
        summary_stats = self.export_summary_stats()
        trends = self.get_top_trends(10)
        companies = self.get_top_companies(10)
        special_categories = self.analyze_special_categories()
        
        # Generate report
        report = self._generate_markdown_report(summary_stats, trends, companies, special_categories)
        
        # Save report
        report_path = os.path.join(self.output_dir, "cfpb_real_analysis_report.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Detailed report saved to: {report_path}")
        
        return {
            'summary': summary_stats,
            'trends': trends,
            'companies': companies,
            'special_categories': special_categories,
            'report_path': report_path
        }
    
    def _generate_markdown_report(self, summary_stats, trends, companies, special_categories):
        """
        Generate comprehensive markdown report with real data
        """
        report = f"""# 🏛️ CFPB Consumer Complaint Analysis - Real Data Report

**Analysis Period:** {summary_stats['date_range']}  
**Generated:** {summary_stats['analysis_date']}  
**Data Source:** {summary_stats['data_source']}

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Total Non-Credit Complaints** | {summary_stats['total_complaints']:,} |
| **Unique Companies** | {summary_stats['unique_companies']:,} |
| **Product Categories** | {summary_stats['unique_products']:,} |
| **States Covered** | {summary_stats['unique_states']:,} |
| **Avg. Daily Complaints** | {summary_stats['avg_complaints_per_day']:.1f} |

> 🎯 **Analysis Focus**: Last 6 months, narrative complaints only, excluding credit reporting categories

---

## 🔥 Top 10 Complaint Trends (Excluding Credit Reporting)

| Rank | Product Category | Complaints | % of Total |
|------|------------------|------------|------------|
"""
        
        # Add top products table
        total_complaints = summary_stats['total_complaints']
        for i, (product, count) in enumerate(trends['top_products'].items(), 1):
            percentage = (count / total_complaints) * 100
            report += f"| {i} | {product} | {count:,} | {percentage:.1f}% |\n"
        
        report += f"""

### Sub-Trends Analysis

"""
        
        # Add sub-trends for top 5 products
        for i, product in enumerate(list(trends['top_products'].index)[:5], 1):
            sub_trends = self.get_sub_trends(product, 5)
            if sub_trends:
                report += f"#### {i}. {product}\n\n"
                report += "| Issue | Complaints | % of Category | Real Complaint Links |\n"
                report += "|-------|------------|---------------|-----------------------|\n"
                
                for issue, data in sub_trends.items():
                    sample_ids = [str(complaint['Complaint ID']) for complaint in data['sample_complaints'][:2]]
                    links = self.generate_complaint_links(sample_ids)
                    link_text = " • ".join([f"[{id}]({link})" for id, link in zip(sample_ids, links)])
                    
                    report += f"| {issue} | {data['count']:,} | {data['percentage']:.1f}% | {link_text} |\n"
                
                report += "\n"
        
        report += f"""---

## 🏢 Top 10 Most Complained About Companies

*Excluding credit reporting agencies*

| Rank | Company | Complaints | Top Issue | Real Links |
|------|---------|------------|-----------|--------------|
"""
        
        # Add top companies table with clickable links
        for i, (company, data) in enumerate(companies.items(), 1):
            top_issue = list(data['top_issues'].keys())[0] if data['top_issues'] else "N/A"
            
            # Get real complaint links
            sample_ids = [str(complaint['Complaint ID']) for complaint in data['sample_complaints'][:2]]
            links = self.generate_complaint_links(sample_ids)
            link_text = " • ".join([f"[{id}]({link})" for id, link in zip(sample_ids, links)])
            
            report += f"| {i} | {company} | {data['total_complaints']:,} | {top_issue} | {link_text} |\n"
        
        report += f"""

---

## 🎯 Special Category Analysis

### 🤖 AI & Algorithmic Decision Making
- **Total AI-Related Complaints**: {len(special_categories['ai_complaints']):,}
- **Percentage of Total**: {(len(special_categories['ai_complaints']) / total_complaints) * 100:.2f}%

**Top AI Complaint Products:**
"""
        
        if len(special_categories['ai_complaints']) > 0:
            ai_products = special_categories['ai_complaints']['Product'].value_counts().head(5)
            for product, count in ai_products.items():
                report += f"- {product}: {count} complaints\n"
        else:
            report += "- No AI-related complaints detected with current keywords\n"
        
        report += f"""

### 🌐 LEP/Spanish Language Issues  
- **Total LEP-Related Complaints**: {len(special_categories['lep_complaints']):,}
- **Percentage of Total**: {(len(special_categories['lep_complaints']) / total_complaints) * 100:.2f}%

**Top LEP Complaint Products:**
"""
        
        if len(special_categories['lep_complaints']) > 0:
            lep_products = special_categories['lep_complaints']['Product'].value_counts().head(5)
            for product, count in lep_products.items():
                report += f"- {product}: {count} complaints\n"
        else:
            report += "- No LEP-related complaints detected with current keywords\n"
        
        report += f"""

### 🚨 Fraud & Digital Banking
- **Total Fraud/Digital Complaints**: {len(special_categories['fraud_digital_complaints']):,}
- **Percentage of Total**: {(len(special_categories['fraud_digital_complaints']) / total_complaints) * 100:.2f}%

**Top Fraud/Digital Complaint Products:**
"""
        
        if len(special_categories['fraud_digital_complaints']) > 0:
            fraud_products = special_categories['fraud_digital_complaints']['Product'].value_counts().head(5)
            for product, count in fraud_products.items():
                report += f"- {product}: {count} complaints\n"
        else:
            report += "- No fraud/digital complaints detected with current keywords\n"
        
        report += f"""

---

## 🔍 Key Insights & Recommendations

### Regulatory Focus Areas
1. **Most Active Complaint Categories**: {', '.join(list(trends['top_products'].index)[:3])}
2. **Highest Volume Companies**: {', '.join(list(companies.keys())[:3])}
3. **Emerging Digital Trends**: {len(special_categories['fraud_digital_complaints']):,} fraud/digital complaints identified

### Data Quality Notes
- All data sourced directly from CFPB Consumer Complaint Database
- Analysis excludes credit reporting categories to focus on actionable trends
- Only complaints with consumer narratives included for detailed analysis
- Complaint links provided for drill-down investigation

---

## 📋 Methodology

**Data Source**: [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/)  
**Analysis Period**: April 19, 2025 - October 19, 2025 (Last 6 Months)  
**Filters Applied**:
- Has consumer complaint narrative: Yes
- Exclude credit reporting categories: Both checkboxes
- Date range: Last 6 months only

**Special Category Keywords**:
- AI/Algorithmic: {', '.join(self.ai_keywords[:5])}...
- LEP/Spanish: {', '.join(self.lep_keywords[:5])}...  
- Fraud/Digital: {', '.join(self.fraud_digital_keywords[:5])}...

---

*Report generated by CFPB Real Data Analyzer v5.0 - No simulated data used*
"""
        
        return report

if __name__ == "__main__":
    print("🏛️  CFPB Real Data Analyzer v5.0")
    print("=================================")
    print("📡 Fetching and analyzing real CFPB complaint data...")
    print()
    
    analyzer = CFPBRealAnalyzer()
    
    # Load real data
    if analyzer.load_real_data():
        # Generate comprehensive analysis
        results = analyzer.create_detailed_report()
        
        if results:
            print("\n✅ Real data analysis complete!")
            print(f"📄 Report: {results['report_path']}")
            print(f"📊 Total complaints analyzed: {results['summary']['total_complaints']:,}")
            print("\n🔍 Top 3 complaint categories:")
            for i, (product, count) in enumerate(list(results['trends']['top_products'].items())[:3], 1):
                print(f"   {i}. {product}: {count:,} complaints")
    else:
        print("❌ Failed to load real CFPB data. Please check your internet connection.")
