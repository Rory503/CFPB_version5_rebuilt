"""
CFPB Analysis Demo Script
Shows example output format and structure with simulated data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def generate_demo_report():
    """
    Generate demo analysis report showing expected output format
    """
    
    print("🏛️  CFPB Consumer Complaint Analysis Tool v5.0 - DEMO")
    print("=" * 60)
    print()
    
    # Simulated summary statistics
    demo_summary = {
        'total_complaints': 247856,
        'date_range': '2025-04-19 to 2025-10-19',
        'unique_companies': 3247,
        'unique_products': 18,
        'states_covered': 50,
        'avg_complaints_per_day': 1348.4
    }
    
    # Simulated trend data based on real CFPB patterns
    demo_trends = {
        'Debt collection': 52341,
        'Checking or savings account': 38429,
        'Credit card or prepaid card': 31287,
        'Mortgage': 28934,
        'Auto loan': 19847,
        'Student loan': 15623,
        'Personal loan': 12456,
        'Money transfer or virtual currency': 9834,
        'Payday loan': 7891,
        'Vehicle loan or lease': 6789
    }
    
    # Simulated company data (excluding credit agencies)
    demo_companies = {
        'WELLS FARGO & COMPANY': {'complaints': 8934, 'top_issue': 'Improper use of your report'},
        'BANK OF AMERICA': {'complaints': 7823, 'top_issue': 'Problem with a purchase'},
        'JPMORGAN CHASE & CO.': {'complaints': 6912, 'top_issue': 'Managing an account'},
        'CAPITAL ONE FINANCIAL CORPORATION': {'complaints': 5634, 'top_issue': 'Problem with a purchase'},
        'CITIBANK': {'complaints': 4789, 'top_issue': 'Managing an account'},
        'DISCOVER BANK': {'complaints': 3987, 'top_issue': 'Problem with a purchase'},
        'SYNCHRONY FINANCIAL': {'complaints': 3456, 'top_issue': 'Problem with a purchase'},
        'AMERICAN EXPRESS COMPANY': {'complaints': 2987, 'top_issue': 'Billing disputes'},
        'ALLY FINANCIAL INC.': {'complaints': 2654, 'top_issue': 'Managing an account'},
        'NAVY FEDERAL CREDIT UNION': {'complaints': 2341, 'top_issue': 'Managing an account'}
    }
    
    # Simulated special category counts
    special_categories = {
        'ai_complaints': 1247,
        'lep_complaints': 3891,
        'fraud_digital_complaints': 18234
    }
    
    # Generate demo markdown report
    report = f"""# 🏛️ CFPB Consumer Complaint Analysis Report - DEMO

**Analysis Period:** {demo_summary['date_range']}  
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Total Non-Credit Complaints** | {demo_summary['total_complaints']:,} |
| **Unique Companies** | {demo_summary['unique_companies']:,} |
| **Product Categories** | {demo_summary['unique_products']:,} |
| **States Covered** | {demo_summary['states_covered']:,} |
| **Avg. Daily Complaints** | {demo_summary['avg_complaints_per_day']:.1f} |

> 🎯 **Key Focus**: Analysis excludes credit reporting categories and includes only complaints with consumer narratives.

---

## 🔥 Top Complaint Trends

### Top 10 Product Categories

| Rank | Product Category | Complaints | % of Total | Trend |
|------|------------------|------------|------------|-------|
"""
    
    total = demo_summary['total_complaints']
    for i, (product, count) in enumerate(demo_trends.items(), 1):
        percentage = (count / total) * 100
        trend_arrow = "📈" if i <= 3 else "📊" if i <= 7 else "📉"
        report += f"| {i} | {product} | {count:,} | {percentage:.1f}% | {trend_arrow} |\n"
    
    report += f"""

---

## 🏢 Most Complained About Companies

*Excluding credit agencies (Equifax, Experian, TransUnion)*

| Rank | Company | Complaints | Top Issue | Sample Link |
|------|---------|------------|-----------|-------------|
"""
    
    for i, (company, data) in enumerate(demo_companies.items(), 1):
        sample_id = f"2025{i:06d}"  # Simulated complaint ID
        link = f"https://www.consumerfinance.gov/data-research/consumer-complaints/search/detail/{sample_id}"
        report += f"| {i} | {company} | {data['complaints']:,} | {data['top_issue']} | [View]({link}) |\n"
    
    report += f"""

---

## 🤖 Special Category Analysis

### AI & Algorithmic Decision Making
- **Total AI-Related Complaints**: {special_categories['ai_complaints']:,}
- **Percentage of Total**: {(special_categories['ai_complaints'] / total) * 100:.2f}%
- **🚨 Rising Trend**: 47% increase from previous 6-month period

**Top AI Complaint Areas:**
- Mortgage lending automated decisions: 423 complaints
- Credit card algorithmic approvals: 298 complaints  
- Auto loan underwriting bias: 187 complaints
- Student loan servicing chatbots: 156 complaints

### LEP/Spanish Language Issues  
- **Total LEP-Related Complaints**: {special_categories['lep_complaints']:,}
- **Percentage of Total**: {(special_categories['lep_complaints'] / total) * 100:.2f}%
- **📊 Steady Growth**: 23% increase in language access complaints

**Top LEP Complaint Areas:**
- Mortgage servicing language barriers: 1,234 complaints
- Debt collection Spanish translation: 987 complaints
- Banking customer service access: 876 complaints
- Credit card Spanish materials: 654 complaints

### Fraud & Digital Banking
- **Total Fraud/Digital Complaints**: {special_categories['fraud_digital_complaints']:,}
- **Percentage of Total**: {(special_categories['fraud_digital_complaints'] / total) * 100:.2f}%
- **🚨 Major Increase**: 89% surge in digital fraud complaints

**Top Fraud/Digital Areas:**
- Zelle unauthorized transfers: 4,567 complaints
- Mobile banking app fraud: 3,891 complaints
- Digital wallet scams: 2,987 complaints
- Cryptocurrency fraud: 2,134 complaints

---

## 🎯 Key Regulatory Insights

### Emerging Risk Areas ⚠️

1. **Algorithmic Bias in Lending**
   - AI-driven underwriting showing disparate impact patterns
   - Lack of explainable AI in loan denials
   - Automated decision appeals process gaps

2. **Digital Payment Fraud Surge**
   - 89% increase in P2P payment fraud (Zelle, Venmo, CashApp)
   - Banks struggling with real-time fraud detection
   - Consumer education gaps on digital security

3. **Language Access Compliance**
   - Growing LEP population not served adequately
   - Spanish language materials often inadequate or missing
   - Interpreter services inconsistently available

### Enforcement Priority Indicators 🎯

| Risk Area | Complaint Volume | YoY Change | Enforcement Likelihood |
|-----------|------------------|------------|----------------------|
| AI Bias in Lending | 1,247 | +47% | 🔴 High |
| Digital Fraud Response | 18,234 | +89% | 🔴 High |
| LEP Services | 3,891 | +23% | 🟡 Medium |
| Debt Collection Practices | 52,341 | +12% | 🟡 Medium |

---

## 📈 FTC Consumer Sentinel Triangulation

### Cross-Platform Fraud Analysis

**CFPB Digital Fraud**: 18,234 complaints  
**FTC Digital Fraud**: 45,678 reports  
**Correlation Factor**: 0.67 (Strong positive correlation)

**Key Cross-Trends:**
- Both platforms show 80%+ increase in P2P payment fraud
- Mobile banking fraud complaints align across databases
- Cryptocurrency scams reported 3x more to FTC than CFPB

### Financial Impact Analysis
- **Total Consumer Losses (FTC data)**: $2.1 billion in reported losses
- **Average Loss per CFPB Complaint**: $8,945
- **Most Costly Category**: Digital investment fraud ($47K avg loss)

---

## 🚀 Strategic Recommendations

### For FinTech Companies

1. **AI Governance Implementation**
   - Implement explainable AI for lending decisions
   - Regular algorithmic bias testing and auditing
   - Clear appeals process for automated decisions

2. **Fraud Prevention Enhancement**
   - Real-time fraud monitoring for P2P payments
   - Enhanced customer education on digital security  
   - Multi-factor authentication improvements

3. **Language Access Expansion**
   - Comprehensive Spanish-language customer service
   - Multilingual mobile app interfaces
   - Cultural competency training for staff

### For Regulatory Bodies

1. **Examination Priorities**
   - Focus examinations on AI decision-making processes
   - Evaluate digital fraud response capabilities
   - Assess language access compliance programs

2. **Guidance Development**
   - Issue specific guidance on algorithmic lending practices
   - Clarify expectations for P2P payment fraud liability
   - Update language access requirements for digital services

---

## 📊 Interactive Dashboards Generated

- **📈 Main Dashboard**: `cfpb_analysis_dashboard.html` - Interactive trend exploration
- **🏢 Company Rankings**: `cfpb_analysis_companies.html` - Drill-down company analysis
- **🗺️ Geographic Heatmap**: `cfpb_analysis_geographic.html` - State-by-state complaint patterns
- **🔍 Keyword Analysis**: `cfpb_analysis_keywords.html` - Complaint narrative insights

---

*This demo shows the comprehensive analysis capabilities of the CFPB Consumer Complaint Analysis Tool v5.0. Real analysis would include actual complaint data, clickable links to individual complaints, and deeper statistical analysis.*

**🔧 To run real analysis:**
1. Download CFPB complaint CSV from official source
2. Place in data/ folder as complaints.csv  
3. Run: `python main_analysis.py`
"""
    
    return report

def save_demo_outputs():
    """
    Save demo report and create sample visualization files
    """
    # Ensure output directories exist
    import os
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('visualizations', exist_ok=True)
    
    # Generate and save demo report
    demo_report = generate_demo_report()
    
    with open('outputs/demo_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(demo_report)
    
    # Create sample JSON output
    demo_json = {
        "summary": {
            "total_complaints": 247856,
            "date_range": "2025-04-19 to 2025-10-19",
            "unique_companies": 3247,
            "unique_products": 18,
            "analysis_type": "DEMO - Simulated Data"
        },
        "top_trends": [
            {"product": "Debt collection", "complaints": 52341, "percentage": 21.1},
            {"product": "Checking or savings account", "complaints": 38429, "percentage": 15.5},
            {"product": "Credit card or prepaid card", "complaints": 31287, "percentage": 12.6}
        ],
        "special_categories": {
            "ai_complaints": 1247,
            "lep_complaints": 3891,
            "fraud_digital_complaints": 18234
        },
        "generated_at": datetime.now().isoformat(),
        "note": "This is demonstration data showing expected output format"
    }
    
    with open('outputs/demo_analysis_data.json', 'w') as f:
        json.dump(demo_json, f, indent=2)
    
    # Create sample HTML dashboard content
    html_dashboard = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CFPB Analysis Dashboard - DEMO</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .dashboard { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .metric-card { display: inline-block; margin: 20px; padding: 20px; background: #e3f2fd; border-radius: 8px; min-width: 200px; text-align: center; }
            .metric-value { font-size: 2em; font-weight: bold; color: #1565c0; }
            .metric-label { color: #666; margin-top: 10px; }
            .chart-placeholder { background: #f0f0f0; height: 400px; margin: 20px 0; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; font-size: 18px; }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <h1>🏛️ CFPB Consumer Complaint Analysis - DEMO Dashboard</h1>
            
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-value">247,856</div>
                    <div class="metric-label">Total Complaints</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">3,247</div>
                    <div class="metric-label">Companies</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">18,234</div>
                    <div class="metric-label">Fraud/Digital</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">1,247</div>
                    <div class="metric-label">AI-Related</div>
                </div>
            </div>
            
            <div class="chart-placeholder">
                📊 Interactive Charts Would Appear Here<br>
                <small>Run real analysis to generate Plotly charts</small>
            </div>
            
            <p><strong>Note:</strong> This is a demo showing the dashboard structure. Real analysis generates interactive Plotly charts with drill-down capabilities.</p>
        </div>
    </body>
    </html>
    """
    
    with open('visualizations/demo_dashboard.html', 'w') as f:
        f.write(html_dashboard)
    
    print("📊 Demo outputs generated:")
    print("   • outputs/demo_analysis_report.md")
    print("   • outputs/demo_analysis_data.json") 
    print("   • visualizations/demo_dashboard.html")
    print()
    print("🔍 Review these files to see the expected output format")
    print("📈 Run main_analysis.py with real CFPB data for full analysis")

if __name__ == "__main__":
    print("🎭 CFPB Analysis Tool - Demo Mode")
    print("================================")
    print()
    
    # Generate demo report
    report = generate_demo_report()
    print(report)
    print()
    
    # Save demo files
    save_demo_outputs()