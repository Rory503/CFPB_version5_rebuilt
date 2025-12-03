"""
Simple test script to run trend_analytics.py
This demonstrates how to use the TrendAnalytics and CompanyAnalytics classes
"""

import sys
import os

# Add analysis folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'analysis'))

try:
    from analysis.cfpb_real_analyzer import CFPBRealAnalyzer
    from analysis.trend_analytics import TrendAnalytics, CompanyAnalytics
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the project root directory")
    sys.exit(1)


def main():
    print("=" * 60)
    print("🔍 CFPB Trend Analytics Test Script")
    print("=" * 60)
    print()
    
    # Step 1: Initialize analyzer and load data
    print("📥 Step 1: Loading CFPB data...")
    print("   (This may take a few minutes on first run)")
    print()
    
    analyzer = CFPBRealAnalyzer()
    success = analyzer.load_real_data()
    
    if not success:
        print("❌ Failed to load data. Please check your connection.")
        return
    
    print()
    print("✅ Data loaded successfully!")
    print(f"   Total complaints: {len(analyzer.filtered_df):,}")
    print()
    
    # Step 2: Initialize TrendAnalytics
    print("=" * 60)
    print("📊 Step 2: Running Trend Analytics")
    print("=" * 60)
    print()
    
    trend_analytics = TrendAnalytics(analyzer)
    
    # Run various analytics
    print("1️⃣ Top 5 Categories (Last 30 Days)")
    result = trend_analytics.top_five_categories_last_30_days()
    if result:
        print(f"   📅 Date Range: {result['date_range']}")
        print(f"   📊 Total Complaints: {result['total_complaints']:,}")
        print("   Top Categories:")
        for category, count in list(result['data'].items())[:5]:
            print(f"      • {category}: {count:,}")
    else:
        print("   ⚠️ No data available")
    print()
    
    print("2️⃣ Companies with Most Recent Complaints")
    result = trend_analytics.companies_with_most_recent_complaints(days=30)
    if result:
        print(f"   📅 Date Range: {result['date_range']}")
        print(f"   📊 Total Complaints: {result['total_complaints']:,}")
        print("   Top Companies:")
        for company, count in list(result['data'].items())[:5]:
            print(f"      • {company}: {count:,}")
    else:
        print("   ⚠️ No data available")
    print()
    
    print("3️⃣ Mortgage Complaints: Current vs Previous Quarter")
    result = trend_analytics.mortgage_complaints_vs_last_quarter()
    if result:
        print(f"   Current Quarter: {result['current_quarter']['count']:,} complaints")
        print(f"   Previous Quarter: {result['previous_quarter']['count']:,} complaints")
        change = result['change']
        print(f"   Change: {change['absolute']:+,} ({change['percentage']:+.1f}%) - {change['direction']}")
    else:
        print("   ⚠️ No data available")
    print()
    
    print("4️⃣ Complaints with Consumer Narratives")
    result = trend_analytics.complaints_percentage_with_narratives()
    if result:
        print(f"   Total Complaints: {result['total_complaints']:,}")
        print(f"   With Narratives: {result['with_narratives']:,}")
        print(f"   Percentage: {result['percentage']:.1f}%")
    else:
        print("   ⚠️ No data available")
    print()
    
    # Step 3: Company Analytics
    print("=" * 60)
    print("🏢 Step 3: Running Company Analytics")
    print("=" * 60)
    print()
    
    company_analytics = CompanyAnalytics(analyzer)
    
    # Get top companies and analyze one
    if analyzer.filtered_df is not None and 'Company' in analyzer.filtered_df.columns:
        top_companies = analyzer.filtered_df['Company'].value_counts().head(3)
        if len(top_companies) > 0:
            sample_company = top_companies.index[0]
            print(f"📊 Analyzing: {sample_company}")
            result = company_analytics.company_recent_complaints_summary(sample_company, days=90)
            if result:
                print(f"   Total Complaints (last 90 days): {result['total_complaints']:,}")
                if result['top_issues']:
                    print("   Top Issues:")
                    for issue, count in list(result['top_issues'].items())[:3]:
                        print(f"      • {issue}: {count:,}")
    print()
    
    print("=" * 60)
    print("✅ Analytics Complete!")
    print("=" * 60)
    print()
    print("💡 Tip: You can also run this through the web dashboard:")
    print("   streamlit run web_dashboard.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()









