"""
CFPB Real Data Analysis - Main Script
Fetches and analyzes real CFPB complaint data with no simulation

This script:
1. Downloads real CFPB complaint data from official source
2. Filters for last 6 months, narratives only, excludes credit reporting  
3. Identifies top trends and most complained about companies
4. Provides clickable links to individual complaints
5. Generates comprehensive analysis report
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'analysis'))

from analysis.cfpb_real_analyzer import CFPBRealAnalyzer
from analysis.ftc_real_triangulator import FTCRealTriangulator
import pandas as pd
from datetime import datetime

def main():
    """
    Main execution function for real CFPB data analysis
    """
    print("🏛️  CFPB Consumer Complaint Analysis Tool v5.0")
    print("📡 REAL DATA ANALYSIS - No Simulated Data")
    print("=" * 50)
    print()
    
    print("🎯 Analysis Specifications:")
    print("   • Time Period: Last 6 months (April 19 - October 19, 2025)")
    print("   • Data Source: Official CFPB Consumer Complaint Database")
    print("   • Filters: Narratives only, exclude credit reporting categories")
    print("   • Focus: Top trends, companies, with clickable complaint links")
    print()
    
    # Initialize real data analyzer
    analyzer = CFPBRealAnalyzer()
    
    print("📥 Step 1: Downloading Real CFPB Data")
    print("=====================================")
    
    # Load real data from CFPB
    success = analyzer.load_real_data()
    
    if not success:
        print("❌ Failed to load real CFPB data.")
        print("🔗 Please check your internet connection or download manually from:")
        print("   https://www.consumerfinance.gov/data-research/consumer-complaints/#download-the-data")
        return
    
    print("\n📊 Step 2: Analyzing Real Data")
    print("==============================")
    
    # Generate comprehensive analysis
    results = analyzer.create_detailed_report()
    
    if not results:
        print("❌ Failed to generate analysis report")
        return
    
    print("\n🔍 Step 3: Key Findings Summary")
    print("===============================")
    
    # Display key findings
    summary = results['summary']
    trends = results['trends']
    companies = results['companies']
    special = results['special_categories']
    
    print(f"📈 Total Complaints Analyzed: {summary['total_complaints']:,}")
    print(f"🏢 Unique Companies: {summary['unique_companies']:,}")
    print(f"📋 Product Categories: {summary['unique_products']:,}")
    print()
    
    print("🔥 Top 5 Complaint Categories (Excluding Credit Reporting):")
    for i, (product, count) in enumerate(list(trends['top_products'].items())[:5], 1):
        pct = (count / summary['total_complaints']) * 100
        print(f"   {i}. {product:<40} {count:>8,} ({pct:>5.1f}%)")
    
    print()
    print("🏢 Top 5 Most Complained About Companies:")
    for i, (company, data) in enumerate(list(companies.items())[:5], 1):
        print(f"   {i}. {company:<40} {data['total_complaints']:>8,}")
    
    print()
    print("🎯 Special Categories Detected:")
    print(f"   🤖 AI/Algorithmic Issues:    {len(special['ai_complaints']):>8,}")
    print(f"   🌐 LEP/Spanish Language:     {len(special['lep_complaints']):>8,}")  
    print(f"   🚨 Fraud/Digital Banking:    {len(special['fraud_digital_complaints']):>8,}")
    
    print("\n📄 Step 4: FTC Triangulation")
    print("=============================")
    
    # Initialize FTC triangulator
    ftc_triangulator = FTCRealTriangulator(analyzer)
    
    # Load FTC data and create triangulation report
    if ftc_triangulator.load_ftc_real_data():
        triangulation_results = ftc_triangulator.create_triangulation_report()
        if triangulation_results:
            print(f"✅ FTC triangulation report: {triangulation_results['report_path']}")
        else:
            print("⚠️  FTC triangulation report generation failed")
    else:
        print("⚠️  Using FTC published statistics for triangulation")
    
    print("\n📄 Step 5: Report Generation Complete")
    print("=====================================")
    print(f"✅ Detailed analysis report: {results['report_path']}")
    print("📊 Excel export: outputs/cfpb_real_analysis.xlsx")
    
    # Export additional Excel data
    analyzer.data_fetcher.export_analysis_data(
        analyzer.filtered_df, 
        "outputs/cfpb_real_analysis.xlsx"
    )
    
    print("\n🔗 Next Steps:")
    print("==============")
    print("1. Review the detailed markdown report for comprehensive findings")
    print("2. Use the Excel export for further data analysis")
    print("3. Click complaint links in the report to view individual cases")
    print("4. Focus on sub-trends under top complaint categories")
    
    print(f"\n📅 Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🏛️  All data sourced directly from CFPB - No simulated data used")
    
    return results

def show_sample_analysis():
    """
    Show what the analysis will look like without running full analysis
    """
    print("📋 Sample Analysis Structure:")
    print("=============================")
    print()
    print("The analysis will provide:")
    print()
    print("1. 📊 HIGH-LEVEL DASHBOARD")
    print("   • Total non-credit complaints (last 6 months)")
    print("   • Key trends and YoY growth patterns")
    print("   • Geographic and temporal distribution")
    print()
    print("2. 🔥 TOP 10 TRENDS (Excluding credit reporting)")
    print("   • Product categories with complaint volumes")
    print("   • Percentage of total complaints")
    print("   • Sub-trends within each category")
    print("   • Sample complaints with clickable links")
    print()
    print("3. 🏢 TOP 10 COMPANIES (Excluding credit agencies)")
    print("   • Most complained about financial institutions")
    print("   • Common complaint topics for each company")
    print("   • Sample complaint links for investigation")
    print()
    print("4. 🎯 SPECIAL ANALYSIS")
    print("   • AI/Algorithmic bias complaints")
    print("   • LEP/Spanish language access issues")
    print("   • Fraud and digital banking problems")
    print()
    print("5. 🔗 CLICKABLE COMPLAINT LINKS")
    print("   • Direct links to CFPB complaint details")
    print("   • Format: https://www.consumerfinance.gov/data-research/consumer-complaints/search/detail/{ID}")
    print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='CFPB Real Data Analysis Tool')
    parser.add_argument('--sample', action='store_true', help='Show sample analysis structure')
    parser.add_argument('--run', action='store_true', help='Run full real data analysis')
    
    args = parser.parse_args()
    
    if args.sample:
        show_sample_analysis()
    elif args.run:
        main()
    else:
        print("🏛️  CFPB Consumer Complaint Analysis Tool v5.0")
        print("=" * 50)
        print()
        print("Options:")
        print("  --sample    Show what the analysis will look like")
        print("  --run       Run full analysis with real CFPB data")
        print()
        print("Example usage:")
        print("  python real_main_analysis.py --sample")
        print("  python real_main_analysis.py --run")
        print()
        print("📡 This tool downloads and analyzes real CFPB complaint data")
        print("🚫 No simulated data is used in this analysis")
        print("🔗 All complaint links are clickable and lead to real CFPB records")