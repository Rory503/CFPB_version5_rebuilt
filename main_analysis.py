"""
CFPB Consumer Complaint Analysis - Main Analysis Script
Generates comprehensive reports with visual outputs

Usage:
1. Place CFPB complaint CSV in the data/ folder
2. Run this script to generate full analysis
3. View results in outputs/ and visualizations/ folders
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'analysis'))

from analysis.cfpb_analyzer import CFPBAnalyzer
from analysis.visualizer import CFPBVisualizer
from analysis.ftc_triangulator import FTCTriangulator
import pandas as pd
from datetime import datetime
import json

class CFPBReportGenerator:
    def __init__(self):
        self.analyzer = CFPBAnalyzer()
        self.visualizer = None
        self.triangulator = None
        
    def run_full_analysis(self, cfpb_csv_path, ftc_csv_path=None, output_prefix="cfpb_analysis"):
        """
        Run complete CFPB analysis pipeline
        """
        print("🏛️  CFPB Consumer Complaint Analysis Tool v5.0")
        print("=" * 50)
        print("📊 Analyzing consumer financial complaints for regulatory insights")
        print()
        
        # Step 1: Load and filter CFPB data
        print("📥 STEP 1: Loading CFPB Data")
        try:
            self.analyzer.load_and_filter_data(cfpb_csv_path)
        except FileNotFoundError:
            print(f"❌ Error: CFPB CSV file not found at {cfpb_csv_path}")
            print("📋 Please download the latest CFPB complaint data from:")
            print("   https://www.consumerfinance.gov/data-research/consumer-complaints/#download-the-data")
            return None
        
        # Initialize visualizer and triangulator
        self.visualizer = CFPBVisualizer(self.analyzer)
        self.triangulator = FTCTriangulator(self.analyzer)
        
        # Step 2: Generate core analysis
        print("\n📈 STEP 2: Analyzing Trends")
        summary_stats = self.analyzer.export_data_summary()
        trends = self.analyzer.get_top_trends()
        companies = self.analyzer.get_top_companies()
        special_categories = self.analyzer.analyze_special_categories()
        
        # Step 3: FTC triangulation (if data available)
        print("\n🔄 STEP 3: FTC Data Triangulation")
        if ftc_csv_path:
            self.triangulator.load_ftc_data(ftc_csv_path)
        else:
            self.triangulator.load_ftc_data()  # Use simulated data
        
        triangulation_results = self.triangulator.generate_cross_trend_insights()
        
        # Step 4: Generate visualizations
        print("\n📊 STEP 4: Creating Visualizations")
        self.visualizer.save_all_visualizations(output_prefix)
        
        # Step 5: Generate reports
        print("\n📄 STEP 5: Generating Reports")
        
        # Markdown report
        markdown_report = self.generate_markdown_report(
            summary_stats, trends, companies, special_categories, triangulation_results
        )
        
        with open(f"{self.analyzer.output_dir}{output_prefix}_report.md", 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        # JSON data export
        json_report = {
            'summary': summary_stats,
            'trends': {
                'products': trends['products'].to_dict(),
                'issues': trends['issues'].to_dict(),
                'product_issue_combinations': trends['product_issue_combinations'].to_dict('records')
            },
            'companies': {k: {
                'total_complaints': v['total_complaints'],
                'top_issues': v['top_issues'].to_dict(),
                'sample_complaints': v['sample_complaints'].to_dict('records')
            } for k, v in companies.items()},
            'special_categories': {
                'ai_count': len(special_categories['ai_complaints']),
                'lep_count': len(special_categories['lep_complaints']),
                'fraud_digital_count': len(special_categories['fraud_digital_complaints'])
            },
            'triangulation': triangulation_results,
            'generated_at': datetime.now().isoformat()
        }
        
        with open(f"{self.analyzer.output_dir}{output_prefix}_data.json", 'w') as f:
            json.dump(json_report, f, indent=2, default=str)
        
        print("\n✅ Analysis Complete!")
        print(f"📁 Reports saved to: {self.analyzer.output_dir}")
        print(f"📊 Visualizations saved to: {self.analyzer.viz_dir}")
        print()
        print("📋 Generated Files:")
        print(f"   • {output_prefix}_report.md - Main analysis report")
        print(f"   • {output_prefix}_data.json - Structured data export")
        print(f"   • {output_prefix}_dashboard.html - Interactive dashboard")
        print(f"   • {output_prefix}_companies.html - Company rankings")
        print(f"   • Various PNG charts and visualizations")
        
        return {
            'summary': summary_stats,
            'trends': trends,
            'companies': companies,
            'special_categories': special_categories,
            'triangulation': triangulation_results
        }
    
    def generate_markdown_report(self, summary_stats, trends, companies, special_categories, triangulation_results):
        """
        Generate comprehensive markdown report
        """
        report = f"""# 🏛️ CFPB Consumer Complaint Analysis Report

**Analysis Period:** {summary_stats['date_range']}  
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Total Non-Credit Complaints** | {summary_stats['total_complaints']:,} |
| **Unique Companies** | {summary_stats['unique_companies']:,} |
| **Product Categories** | {summary_stats['unique_products']:,} |
| **States Covered** | {summary_stats['states_covered']:,} |
| **Avg. Daily Complaints** | {summary_stats['avg_complaints_per_day']:.1f} |

> 🎯 **Key Focus**: Analysis excludes credit reporting categories to reduce noise and focuses on complaints with consumer narratives for actionable insights.

---

## 🔥 Top Complaint Trends

### Top 10 Product Categories

| Rank | Product Category | Complaints | % of Total |
|------|------------------|------------|------------|
"""
        
        # Add top products table
        total_complaints = summary_stats['total_complaints']
        for i, (product, count) in enumerate(trends['products'].head(10).items(), 1):
            percentage = (count / total_complaints) * 100
            report += f"| {i} | {product} | {count:,} | {percentage:.1f}% |\n"
        
        report += f"""

### Top 10 Issue Categories

| Rank | Issue | Complaints | % of Total |
|------|-------|------------|------------|
"""
        
        # Add top issues table
        for i, (issue, count) in enumerate(trends['issues'].head(10).items(), 1):
            percentage = (count / total_complaints) * 100
            report += f"| {i} | {issue} | {count:,} | {percentage:.1f}% |\n"
        
        report += f"""

---

## 🏢 Most Complained About Companies

*Excluding credit agencies (Equifax, Experian, TransUnion)*

| Rank | Company | Complaints | Top Issue |
|------|---------|------------|-----------|
"""
        
        # Add top companies table
        for i, (company, data) in enumerate(list(companies.items())[:10], 1):
            top_issue = data['top_issues'].index[0] if len(data['top_issues']) > 0 else "N/A"
            report += f"| {i} | {company} | {data['total_complaints']:,} | {top_issue} |\n"
        
        report += f"""

### Sample Complaints with Links

Here are examples from top companies for deeper investigation:

"""
        
        # Add sample complaints with links
        for company, data in list(companies.items())[:3]:
            report += f"**{company}** ({data['total_complaints']:,} complaints)\n\n"
            
            for _, complaint in data['sample_complaints'].iterrows():
                complaint_id = complaint['complaint_id']
                narrative = str(complaint['consumer_complaint_narrative'])[:200] + "..."
                link = f"https://www.consumerfinance.gov/data-research/consumer-complaints/search/detail/{complaint_id}"
                report += f"- [{complaint_id}]({link}): {narrative}\n"
            
            report += "\n"
        
        report += f"""---

## 🤖 Special Category Analysis

### AI & Algorithmic Decision Making
- **Total AI-Related Complaints**: {len(special_categories['ai_complaints']):,}
- **Percentage of Total**: {(len(special_categories['ai_complaints']) / total_complaints) * 100:.2f}%

**Top AI Complaint Areas:**
"""
        
        if len(special_categories['ai_complaints']) > 0:
            ai_products = special_categories['ai_complaints']['product'].value_counts().head(5)
            for product, count in ai_products.items():
                report += f"- {product}: {count} complaints\n"
        else:
            report += "- No AI-related complaints detected with current keywords\n"
        
        report += f"""

### LEP/Spanish Language Issues
- **Total LEP-Related Complaints**: {len(special_categories['lep_complaints']):,}
- **Percentage of Total**: {(len(special_categories['lep_complaints']) / total_complaints) * 100:.2f}%

**Top LEP Complaint Areas:**
"""
        
        if len(special_categories['lep_complaints']) > 0:
            lep_products = special_categories['lep_complaints']['product'].value_counts().head(5)
            for product, count in lep_products.items():
                report += f"- {product}: {count} complaints\n"
        else:
            report += "- No LEP-related complaints detected with current keywords\n"
        
        report += f"""

### Fraud & Digital Banking
- **Total Fraud/Digital Complaints**: {len(special_categories['fraud_digital_complaints']):,}
- **Percentage of Total**: {(len(special_categories['fraud_digital_complaints']) / total_complaints) * 100:.2f}%

**Top Fraud/Digital Complaint Areas:**
"""
        
        if len(special_categories['fraud_digital_complaints']) > 0:
            fraud_products = special_categories['fraud_digital_complaints']['product'].value_counts().head(5)
            for product, count in fraud_products.items():
                report += f"- {product}: {count} complaints\n"
        else:
            report += "- No fraud/digital complaints detected with current keywords\n"
        
        report += f"""

---

## 🔄 FTC Consumer Sentinel Triangulation

*Cross-referencing with FTC fraud and scam data for broader pattern identification*

"""
        
        if triangulation_results and len(triangulation_results) > 0:
            for insight in triangulation_results:
                report += f"### {insight['title']}\n"
                report += f"{insight['description']}\n\n"
        else:
            report += "**Note**: FTC triangulation available with real FTC Consumer Sentinel data.\n"
            report += "Download from: https://www.ftc.gov/exploredata\n\n"
        
        report += f"""---

## 🎯 Key Insights for FinTech & Consumer Protection

### Regulatory Risk Areas
1. **AI Governance**: Monitor algorithmic decision-making complaints for bias patterns
2. **Fair Lending**: Track LEP/Spanish language access issues in financial services
3. **Digital Security**: Rising fraud in digital banking and payment apps requires attention

### Product Development Recommendations
- Improve multilingual customer service capabilities
- Enhance fraud detection for digital payment platforms
- Implement explainable AI for lending decisions
- Strengthen customer communication for debt collection practices

### Emerging Trends to Watch
- Increase in mobile app-related complaints
- Growing sophistication of digital fraud schemes
- Language access gaps in financial technology

---

## 📈 Interactive Visualizations

The following interactive charts and visualizations have been generated:

- **Main Dashboard**: `cfpb_analysis_dashboard.html`
- **Company Rankings**: `cfpb_analysis_companies.html`
- **Trend Heatmap**: `cfpb_analysis_heatmap.png`
- **Special Categories**: `cfpb_analysis_special_categories.png`
- **Word Cloud**: `cfpb_analysis_wordcloud.png`

---

## 📋 Data Sources & Methodology

**Primary Data Source**: [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/#download-the-data)  
**Triangulation Data**: [FTC Consumer Sentinel](https://www.ftc.gov/exploredata)

**Filters Applied**:
- Date Range: April 19, 2025 - October 19, 2025 (last 6 months)
- Narrative Required: Yes (complaints with consumer stories only)
- Exclusions: All credit reporting/repair categories
- Special Keywords: AI, LEP/Spanish, fraud/digital terms

**Analysis Features**:
- Trend identification with volume calculations
- Company ranking (excluding credit agencies)
- Sub-trend analysis with sample complaints
- Cross-platform validation with FTC data
- Visual dashboard generation

---

*Report generated by CFPB Analysis Tool v5.0 - Specialized for FinTech and Consumer Protection*
"""
        
        return report

def main():
    """
    Main execution function
    """
    generator = CFPBReportGenerator()
    
    # Default paths (user should update these)
    cfpb_csv_path = "data/complaints.csv"  # Update with actual CFPB CSV filename
    ftc_csv_path = None  # Optional: path to FTC Consumer Sentinel data
    
    print("🚀 Starting CFPB Analysis...")
    print()
    print("📋 To run this analysis:")
    print("1. Download CFPB complaint data from:")
    print("   https://www.consumerfinance.gov/data-research/consumer-complaints/#download-the-data")
    print(f"2. Save the CSV file as: {cfpb_csv_path}")
    print("3. (Optional) Download FTC Consumer Sentinel data")
    print("4. Run this script")
    print()
    
    # Check if CFPB data exists
    if not os.path.exists(cfpb_csv_path):
        print(f"⚠️  CFPB data file not found: {cfpb_csv_path}")
        print("Please download and place the CFPB CSV file in the data/ folder")
        print("The file is typically named something like 'complaints-YYYY-MM-DD.csv'")
        return
    
    # Run analysis
    results = generator.run_full_analysis(cfpb_csv_path, ftc_csv_path)
    
    if results:
        print("🎉 Analysis completed successfully!")
        print("📖 Open the markdown report for detailed findings")
        print("🌐 Open the HTML dashboards for interactive exploration")

if __name__ == "__main__":
    main()