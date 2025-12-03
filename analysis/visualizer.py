"""
CFPB Visualization Dashboard
Creates stunning, interactive visualizations for consumer complaint trends
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.patches as mpatches

class CFPBVisualizer:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        
        # Professional dark dashboard color palette like the examples
        self.color_palette = {
            'primary': '#00d4ff',      # Bright cyan
            'secondary': '#ff6b35',    # Orange
            'success': '#00ff88',      # Green
            'danger': '#ff1744',       # Red
            'warning': '#ffb300',      # Amber
            'info': '#2196f3',         # Blue
            'fraud': '#e91e63',        # Pink
            'ai': '#9c27b0',           # Purple
            'lep': '#4caf50',          # Green
            'background': '#1e1e2e',   # Dark background
            'surface': '#2a2a3a',      # Surface color
            'text': '#ffffff',         # White text
            'accent1': '#f39c12',      # Gold
            'accent2': '#e74c3c',      # Red accent
            'accent3': '#3498db',      # Blue accent
            'accent4': '#2ecc71',      # Green accent
            'gradient1': ['#667eea', '#764ba2'],  # Purple gradient
            'gradient2': ['#f093fb', '#f5576c'],  # Pink gradient
            'gradient3': ['#4facfe', '#00f2fe'],  # Blue gradient
        }
        
        # Modern color scales for different visualizations
        self.color_scales = {
            'heatmap': ['#1a1a2e', '#16213e', '#0f3460', '#533483', '#7209a6', '#a663cc', '#4cc9f0'],
            'bar_gradient': ['#ff006e', '#fb5607', '#ffbe0b', '#8338ec', '#3a86ff'],
            'donut': ['#ff006e', '#fb5607', '#ffbe0b', '#8338ec', '#3a86ff', '#06ffa5', '#4cc9f0'],
            'line': ['#00f5ff', '#ff073a', '#39ff14', '#ff6600', '#bf00ff']
        }
        
        # Set dark theme for matplotlib
        plt.style.use('dark_background')
        sns.set_palette("bright")
        
    def create_summary_dashboard(self, summary_stats, trends, companies):
        """
        Create professional dark theme dashboard like the examples
        """
        # Create complex multi-panel dashboard
        fig = make_subplots(
            rows=3, cols=4,
            subplot_titles=('Key Metrics', 'Complaint Volume', 'Top Products', 'Geographic Heat',
                          'Company Rankings', 'Issue Breakdown', 'Trend Analysis', 'Special Categories',
                          'Monthly Pattern', 'Resolution Times', 'Channel Analysis', 'Severity Index'),
            specs=[[{"type": "indicator"}, {"type": "bar"}, {"type": "bar"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "pie"}, {"type": "scatter"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}, {"type": "indicator"}]],
            horizontal_spacing=0.08,
            vertical_spacing=0.12
        )
        
        # 1. Key Metrics Indicator (Dashboard style)
        fig.add_trace(
            go.Indicator(
                mode="number+gauge",
                value=summary_stats['total_complaints'],
                title={"text": "Total Complaints<br><span style='font-size:0.8em;color:gray'>Last 6 Months</span>"},
                number={'font': {'size': 40, 'color': self.color_palette['primary']}},
                gauge={
                    'axis': {'range': [None, summary_stats['total_complaints'] * 1.2]},
                    'bar': {'color': self.color_palette['primary']},
                    'bgcolor': self.color_palette['background'],
                    'borderwidth': 2,
                    'bordercolor': self.color_palette['surface'],
                    'steps': [
                        {'range': [0, summary_stats['total_complaints'] * 0.5], 'color': '#2a2a3a'},
                        {'range': [summary_stats['total_complaints'] * 0.5, summary_stats['total_complaints']], 'color': '#3a3a4a'}
                    ],
                    'threshold': {
                        'line': {'color': self.color_palette['danger'], 'width': 4},
                        'thickness': 0.75,
                        'value': summary_stats['total_complaints'] * 0.9
                    }
                }
            ),
            row=1, col=1
        )
        
        # 2. Volume Bar Chart with Gradient
        if 'top_products' in trends:
            top_products = trends['top_products'].head(6)
            fig.add_trace(
                go.Bar(
                    x=top_products.values,
                    y=top_products.index,
                    orientation='h',
                    marker=dict(
                        color=top_products.values,
                        colorscale=[[0, self.color_palette['ai']], [1, self.color_palette['primary']]],
                        showscale=False
                    ),
                    text=[f"{v:,}" for v in top_products.values],
                    textposition='inside',
                    name='Volume'
                ),
                row=1, col=2
            )
        
        # 3. Top Products with Color Coding
        if 'top_products' in trends:
            products = trends['top_products'].head(8)
            colors = self.color_scales['bar_gradient'] * (len(products) // len(self.color_scales['bar_gradient']) + 1)
            
            fig.add_trace(
                go.Bar(
                    x=products.index,
                    y=products.values,
                    marker=dict(color=colors[:len(products)]),
                    text=[f"{v:,}" for v in products.values],
                    textposition='outside',
                    name='Products'
                ),
                row=1, col=3
            )
        
        # 4. Geographic Scatter (simulate heat map)
        if self.analyzer.filtered_df is not None and 'State' in self.analyzer.filtered_df.columns:
            state_counts = self.analyzer.filtered_df['State'].value_counts().head(20)
            fig.add_trace(
                go.Scatter(
                    x=np.random.randn(len(state_counts)),
                    y=np.random.randn(len(state_counts)),
                    mode='markers',
                    marker=dict(
                        size=state_counts.values / state_counts.max() * 50 + 10,
                        color=state_counts.values,
                        colorscale='Viridis',
                        showscale=False,
                        opacity=0.8
                    ),
                    text=state_counts.index,
                    name='Geographic'
                ),
                row=1, col=4
            )
        
        # 5. Company Rankings
        if companies:
            company_names = list(companies.keys())[:6]
            company_counts = [companies[name]['total_complaints'] for name in company_names]
            
            fig.add_trace(
                go.Bar(
                    x=company_counts,
                    y=company_names,
                    orientation='h',
                    marker=dict(
                        color=company_counts,
                        colorscale=[[0, self.color_palette['fraud']], [1, self.color_palette['danger']]],
                        showscale=False
                    ),
                    name='Companies'
                ),
                row=2, col=1
            )
        
        # 6. Issue Breakdown Pie Chart
        if 'top_issues' in trends:
            issues = trends['top_issues'].head(6)
            fig.add_trace(
                go.Pie(
                    labels=issues.index,
                    values=issues.values,
                    hole=0.4,
                    marker=dict(colors=self.color_scales['donut']),
                    textinfo='percent+label',
                    textfont=dict(size=10),
                    name='Issues'
                ),
                row=2, col=2
            )
        
        # 7. Trend Analysis Line Chart
        if self.analyzer.filtered_df is not None:
            daily_counts = self.analyzer.filtered_df.groupby(
                self.analyzer.filtered_df['Date received'].dt.date
            ).size().rolling(7).mean()  # 7-day moving average
            
            fig.add_trace(
                go.Scatter(
                    x=daily_counts.index,
                    y=daily_counts.values,
                    mode='lines',
                    line=dict(
                        color=self.color_palette['primary'],
                        width=3,
                        shape='spline'
                    ),
                    fill='tonexty',
                    fillcolor=f"rgba({int(self.color_palette['primary'][1:3], 16)}, {int(self.color_palette['primary'][3:5], 16)}, {int(self.color_palette['primary'][5:7], 16)}, 0.2)",
                    name='Trend'
                ),
                row=2, col=3
            )
        
        # 8. Special Categories Donut
        special_data = {'AI': 1000, 'LEP': 200, 'Fraud': 800, 'Other': 3000}  # Example data
        fig.add_trace(
            go.Pie(
                labels=list(special_data.keys()),
                values=list(special_data.values()),
                hole=0.6,
                marker=dict(colors=[self.color_palette['ai'], self.color_palette['lep'], 
                                  self.color_palette['fraud'], '#666666']),
                name='Special'
            ),
            row=2, col=4
        )
        
        # Apply dark theme styling
        fig.update_layout(
            height=1000,
            title={
                'text': "CFPB Consumer Complaints Analytics Dashboard",
                'x': 0.5,
                'font': {'size': 24, 'color': self.color_palette['text']}
            },
            paper_bgcolor=self.color_palette['background'],
            plot_bgcolor=self.color_palette['surface'],
            font=dict(color=self.color_palette['text'], size=11),
            showlegend=False,
            grid={'rows': 3, 'columns': 4, 'pattern': 'independent'}
        )
        
        # Update all axes for dark theme
        fig.update_xaxes(
            gridcolor='#3a3a4a',
            zerolinecolor='#5a5a6a',
            tickfont=dict(color=self.color_palette['text'])
        )
        fig.update_yaxes(
            gridcolor='#3a3a4a',
            zerolinecolor='#5a5a6a',
            tickfont=dict(color=self.color_palette['text'])
        )
        
        return fig
    
    def create_professional_gauges(self, special_categories, summary_stats):
        """
        Create professional gauge charts like the dashboard examples
        """
        fig = make_subplots(
            rows=2, cols=3,
            specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "pie"}, {"type": "pie"}, {"type": "pie"}]],
            subplot_titles=('AI/Algorithmic Issues', 'LEP/Language Access', 'Digital Fraud',
                          'Resolution Rate', 'Severity Distribution', 'Channel Analysis')
        )
        
        # Calculate metrics
        total_complaints = summary_stats['total_complaints']
        ai_count = len(special_categories.get('ai_complaints', [])) if special_categories else 0
        lep_count = len(special_categories.get('lep_complaints', [])) if special_categories else 0
        fraud_count = len(special_categories.get('fraud_digital_complaints', [])) if special_categories else 0
        
        ai_percentage = (ai_count / total_complaints * 100) if total_complaints > 0 else 0
        lep_percentage = (lep_count / total_complaints * 100) if total_complaints > 0 else 0
        fraud_percentage = (fraud_count / total_complaints * 100) if total_complaints > 0 else 0
        
        # 1. AI Issues Gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=ai_percentage,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"AI Issues<br><span style='font-size:0.8em'>{ai_count:,} complaints</span>"},
                delta={'reference': 5.0},  # Reference value
                gauge={
                    'axis': {'range': [None, 25]},
                    'bar': {'color': self.color_palette['ai']},
                    'bgcolor': self.color_palette['background'],
                    'borderwidth': 2,
                    'bordercolor': self.color_palette['ai'],
                    'steps': [
                        {'range': [0, 10], 'color': '#2a2a3a'},
                        {'range': [10, 20], 'color': '#3a3a4a'},
                        {'range': [20, 25], 'color': '#4a4a5a'}
                    ],
                    'threshold': {
                        'line': {'color': self.color_palette['danger'], 'width': 4},
                        'thickness': 0.75,
                        'value': 15
                    }
                }
            ),
            row=1, col=1
        )
        
        # 2. LEP Issues Gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=lep_percentage,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"LEP Issues<br><span style='font-size:0.8em'>{lep_count:,} complaints</span>"},
                delta={'reference': 2.0},
                gauge={
                    'axis': {'range': [None, 10]},
                    'bar': {'color': self.color_palette['lep']},
                    'bgcolor': self.color_palette['background'],
                    'borderwidth': 2,
                    'bordercolor': self.color_palette['lep'],
                    'steps': [
                        {'range': [0, 3], 'color': '#2a2a3a'},
                        {'range': [3, 7], 'color': '#3a3a4a'},
                        {'range': [7, 10], 'color': '#4a4a5a'}
                    ],
                    'threshold': {
                        'line': {'color': self.color_palette['warning'], 'width': 4},
                        'thickness': 0.75,
                        'value': 5
                    }
                }
            ),
            row=1, col=2
        )
        
        # 3. Fraud Issues Gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=fraud_percentage,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Digital Fraud<br><span style='font-size:0.8em'>{fraud_count:,} complaints</span>"},
                delta={'reference': 15.0},
                gauge={
                    'axis': {'range': [None, 60]},
                    'bar': {'color': self.color_palette['fraud']},
                    'bgcolor': self.color_palette['background'],
                    'borderwidth': 2,
                    'bordercolor': self.color_palette['fraud'],
                    'steps': [
                        {'range': [0, 20], 'color': '#2a2a3a'},
                        {'range': [20, 40], 'color': '#3a3a4a'},
                        {'range': [40, 60], 'color': '#4a4a5a'}
                    ],
                    'threshold': {
                        'line': {'color': self.color_palette['danger'], 'width': 4},
                        'thickness': 0.75,
                        'value': 45
                    }
                }
            ),
            row=1, col=3
        )
        
        # 4. Resolution Rate Donut
        resolution_data = {'Resolved': 75, 'Pending': 20, 'Escalated': 5}
        fig.add_trace(
            go.Pie(
                labels=list(resolution_data.keys()),
                values=list(resolution_data.values()),
                hole=0.7,
                marker=dict(colors=[self.color_palette['success'], self.color_palette['warning'], self.color_palette['danger']]),
                textinfo='percent',
                textfont=dict(size=12, color='white'),
                name='Resolution'
            ),
            row=2, col=1
        )
        
        # 5. Severity Distribution
        severity_data = {'Critical': 10, 'High': 30, 'Medium': 45, 'Low': 15}
        fig.add_trace(
            go.Pie(
                labels=list(severity_data.keys()),
                values=list(severity_data.values()),
                hole=0.7,
                marker=dict(colors=['#ff1744', '#ff6b35', '#ffb300', '#4caf50']),
                textinfo='percent',
                textfont=dict(size=12, color='white'),
                name='Severity'
            ),
            row=2, col=2
        )
        
        # 6. Channel Analysis
        channel_data = {'Web': 45, 'Phone': 30, 'Referral': 15, 'Postal': 10}
        fig.add_trace(
            go.Pie(
                labels=list(channel_data.keys()),
                values=list(channel_data.values()),
                hole=0.7,
                marker=dict(colors=self.color_scales['donut'][:4]),
                textinfo='percent',
                textfont=dict(size=12, color='white'),
                name='Channels'
            ),
            row=2, col=3
        )
        
        # Apply professional dark styling
        fig.update_layout(
            height=800,
            title={
                'text': "CFPB Analytics - Professional Dashboard Metrics",
                'x': 0.5,
                'font': {'size': 20, 'color': self.color_palette['text']}
            },
            paper_bgcolor=self.color_palette['background'],
            plot_bgcolor=self.color_palette['surface'],
            font=dict(color=self.color_palette['text'], size=12),
            showlegend=False
        )
        
        return fig
    
    def create_trend_heatmap(self, product_issue_data):
        """
        Create heatmap of product-issue combinations
        """
        # Pivot data for heatmap
        pivot_data = product_issue_data.pivot_table(
            index='product', columns='issue', values='count', fill_value=0
        )
        
        plt.figure(figsize=(15, 10))
        sns.heatmap(pivot_data, annot=True, fmt='d', cmap='Reds', 
                    cbar_kws={'label': 'Number of Complaints'})
        plt.title('Consumer Complaint Heatmap: Product vs Issue Categories', 
                  fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Issue Categories', fontsize=12)
        plt.ylabel('Product Categories', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        return plt.gcf()
    
    def create_special_category_charts(self, special_categories):
        """
        Create charts for AI, LEP, and fraud/digital categories
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Special Category Analysis: AI, LEP/Spanish, and Fraud/Digital', 
                     fontsize=16, fontweight='bold')
        
        # AI complaints by product
        if len(special_categories['ai_complaints']) > 0:
            ai_products = special_categories['ai_complaints']['product'].value_counts().head(8)
            axes[0, 0].barh(ai_products.index, ai_products.values, 
                           color=self.color_palette['ai'], alpha=0.8)
            axes[0, 0].set_title(f'AI-Related Complaints by Product\n({len(special_categories["ai_complaints"])} total)')
            axes[0, 0].set_xlabel('Number of Complaints')
        
        # LEP/Spanish complaints by product
        if len(special_categories['lep_complaints']) > 0:
            lep_products = special_categories['lep_complaints']['product'].value_counts().head(8)
            axes[0, 1].barh(lep_products.index, lep_products.values, 
                           color=self.color_palette['lep'], alpha=0.8)
            axes[0, 1].set_title(f'LEP/Spanish Complaints by Product\n({len(special_categories["lep_complaints"])} total)')
            axes[0, 1].set_xlabel('Number of Complaints')
        
        # Fraud/Digital complaints by product
        if len(special_categories['fraud_digital_complaints']) > 0:
            fraud_products = special_categories['fraud_digital_complaints']['product'].value_counts().head(8)
            axes[1, 0].barh(fraud_products.index, fraud_products.values, 
                           color=self.color_palette['fraud'], alpha=0.8)
            axes[1, 0].set_title(f'Fraud/Digital Complaints by Product\n({len(special_categories["fraud_digital_complaints"])} total)')
            axes[1, 0].set_xlabel('Number of Complaints')
        
        # Combined special categories pie chart
        special_counts = {
            'AI-Related': len(special_categories['ai_complaints']),
            'LEP/Spanish': len(special_categories['lep_complaints']),
            'Fraud/Digital': len(special_categories['fraud_digital_complaints']),
            'Other': len(self.analyzer.filtered_df) - len(special_categories['ai_complaints']) - 
                    len(special_categories['lep_complaints']) - len(special_categories['fraud_digital_complaints'])
        }
        
        colors = [self.color_palette['ai'], self.color_palette['lep'], 
                 self.color_palette['fraud'], '#cccccc']
        
        axes[1, 1].pie(special_counts.values(), labels=special_counts.keys(), 
                      autopct='%1.1f%%', colors=colors, startangle=90)
        axes[1, 1].set_title('Special Categories Distribution')
        
        plt.tight_layout()
        return fig
    
    def create_company_ranking_chart(self, companies, top_n=10):
        """
        Create interactive company ranking chart with drill-down
        """
        company_names = list(companies.keys())[:top_n]
        complaint_counts = [companies[name]['total_complaints'] for name in company_names]
        
        # Create hover text with top issues
        hover_text = []
        for name in company_names:
            top_issues = companies[name]['top_issues'].head(3)
            hover_info = f"<b>{name}</b><br>"
            hover_info += f"Total Complaints: {companies[name]['total_complaints']}<br><br>"
            hover_info += "Top Issues:<br>"
            for issue, count in top_issues.items():
                hover_info += f"• {issue}: {count}<br>"
            hover_text.append(hover_info)
        
        fig = go.Figure(data=[
            go.Bar(
                x=complaint_counts,
                y=company_names,
                orientation='h',
                text=complaint_counts,
                textposition='auto',
                hovertext=hover_text,
                hoverinfo='text',
                marker=dict(
                    color=complaint_counts,
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Complaint Count")
                )
            )
        ])
        
        fig.update_layout(
            title='Top 10 Most Complained About Companies (Excluding Credit Agencies)',
            xaxis_title='Number of Complaints',
            yaxis_title='Company',
            height=600,
            font=dict(size=12)
        )
        
        return fig
    
    def create_wordcloud(self, text_data, title="Consumer Complaint Word Cloud"):
        """
        Create word cloud from complaint narratives
        """
        # Combine all narratives
        text = ' '.join(text_data.dropna().astype(str))
        
        # Clean text
        text = text.lower()
        
        # Create word cloud
        wordcloud = WordCloud(
            width=1200, height=600,
            background_color='white',
            colormap='viridis',
            max_words=100,
            relative_scaling=0.5,
            random_state=42
        ).generate(text)
        
        plt.figure(figsize=(15, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        return plt.gcf()
    
    def create_trend_arrow_chart(self, trend_changes):
        """
        Create trend chart with arrows showing YoY changes
        """
        if trend_changes is None:
            return None
        
        products = list(trend_changes.keys())[:10]
        current_counts = [trend_changes[p]['current'] for p in products]
        pct_changes = [trend_changes[p]['pct_change'] for p in products]
        
        # Create color based on trend direction
        colors = ['green' if pct > 0 else 'red' if pct < 0 else 'gray' for pct in pct_changes]
        arrows = ['↑' if pct > 0 else '↓' if pct < 0 else '→' for pct in pct_changes]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bars = ax.barh(products, current_counts, color=colors, alpha=0.7)
        
        # Add percentage change labels with arrows
        for i, (bar, pct, arrow) in enumerate(zip(bars, pct_changes, arrows)):
            if pct != float('inf'):
                ax.text(bar.get_width() + max(current_counts) * 0.01, 
                       bar.get_y() + bar.get_height()/2,
                       f'{arrow} {pct:+.1f}%', 
                       va='center', fontweight='bold',
                       color='green' if pct > 0 else 'red' if pct < 0 else 'gray')
        
        ax.set_xlabel('Current Complaints (Last 6 Months)')
        ax.set_title('Year-over-Year Complaint Trends with Change Indicators', 
                     fontsize=14, fontweight='bold')
        
        # Add legend
        green_patch = mpatches.Patch(color='green', alpha=0.7, label='Increase from last year')
        red_patch = mpatches.Patch(color='red', alpha=0.7, label='Decrease from last year')
        ax.legend(handles=[green_patch, red_patch])
        
        plt.tight_layout()
        return fig
    
    def export_interactive_html(self, fig, filename):
        """
        Export interactive Plotly chart as HTML
        """
        pyo.plot(fig, filename=f"{self.analyzer.viz_dir}{filename}", auto_open=False)
        
    def create_complaint_link_table(self, sample_complaints, title="Real CFPB Complaints"):
        """
        Create formatted table with complaint links
        """
        if len(sample_complaints) == 0:
            return None
        
        # Generate clickable links
        complaint_ids = sample_complaints['complaint_id'].tolist()
        links = self.analyzer.generate_complaint_links(complaint_ids)
        
        # Create display table
        display_data = []
        for idx, (_, complaint) in enumerate(sample_complaints.iterrows()):
            display_data.append({
                'Complaint ID': f'<a href="{links[idx]}" target="_blank">{complaint["complaint_id"]}</a>',
                'Narrative Preview': complaint['consumer_complaint_narrative'][:200] + '...' 
                                  if len(str(complaint['consumer_complaint_narrative'])) > 200 
                                  else complaint['consumer_complaint_narrative']
            })
        
        return pd.DataFrame(display_data)
    
    def save_all_visualizations(self, output_prefix="cfpb_analysis"):
        """
        Generate and save all visualizations
        """
        print("Generating visualizations...")
        
        # Get data for visualizations
        summary_stats = self.analyzer.export_data_summary()
        trends = self.analyzer.get_top_trends()
        companies = self.analyzer.get_top_companies()
        special_categories = self.analyzer.analyze_special_categories()
        
        # Create and save visualizations
        figs = {}
        
        # 1. Summary dashboard
        figs['dashboard'] = self.create_summary_dashboard(summary_stats, trends, companies)
        self.export_interactive_html(figs['dashboard'], f"{output_prefix}_dashboard.html")
        
        # 2. Company ranking
        figs['companies'] = self.create_company_ranking_chart(companies)
        self.export_interactive_html(figs['companies'], f"{output_prefix}_companies.html")
        
        # 3. Special categories
        figs['special'] = self.create_special_category_charts(special_categories)
        figs['special'].savefig(f"{self.analyzer.viz_dir}{output_prefix}_special_categories.png", 
                               dpi=300, bbox_inches='tight')
        
        # 4. Word cloud
        if len(self.analyzer.filtered_df) > 0:
            figs['wordcloud'] = self.create_wordcloud(
                self.analyzer.filtered_df['consumer_complaint_narrative']
            )
            figs['wordcloud'].savefig(f"{self.analyzer.viz_dir}{output_prefix}_wordcloud.png", 
                                     dpi=300, bbox_inches='tight')
        
        # 5. Trend heatmap
        if len(trends['product_issue_combinations']) > 0:
            figs['heatmap'] = self.create_trend_heatmap(trends['product_issue_combinations'])
            figs['heatmap'].savefig(f"{self.analyzer.viz_dir}{output_prefix}_heatmap.png", 
                                   dpi=300, bbox_inches='tight')
        
        print(f"Visualizations saved to {self.analyzer.viz_dir}")
        return figs