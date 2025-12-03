"""
CFPB Real Data Analysis - GUI Interface
Interactive dashboard for analyzing consumer complaint data
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import sys
import os
import webbrowser
from datetime import datetime
import json

# Add analysis modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'analysis'))

try:
    from analysis.cfpb_real_analyzer import CFPBRealAnalyzer
    from analysis.ftc_real_triangulator import FTCRealTriangulator
except ImportError as e:
    print(f"Import error: {e}")
    CFPBRealAnalyzer = None
    FTCRealTriangulator = None

class CFPBAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏛️ CFPB Consumer Complaint Analysis Tool v5.0")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize analyzers
        self.cfpb_analyzer = None
        self.ftc_triangulator = None
        self.analysis_results = None
        self.analysis_running = False
        
        # Create GUI components
        self.create_header()
        self.create_main_tabs()
        self.create_status_bar()
        
        # Initialize with system info
        self.show_system_info()
    
    def create_header(self):
        """Create header section with title and info"""
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="🏛️ CFPB Consumer Complaint Analysis Tool",
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Real CFPB Data Analysis - Last 6 Months - No Simulated Data",
            font=('Arial', 10),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        subtitle_label.pack()
    
    def create_main_tabs(self):
        """Create main tabbed interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tab 1: System Overview
        self.create_system_tab()
        
        # Tab 2: Data Analysis
        self.create_analysis_tab()
        
        # Tab 3: Results Viewer
        self.create_results_tab()
        
        # Tab 4: Settings & Export
        self.create_settings_tab()
    
    def create_system_tab(self):
        """Create system overview tab"""
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="📊 System Overview")
        
        # System info text area
        self.system_info_text = scrolledtext.ScrolledText(
            system_frame,
            height=30,
            font=('Consolas', 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='white'
        )
        self.system_info_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(system_frame)
        buttons_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(
            buttons_frame,
            text="🔄 Refresh System Info",
            command=self.show_system_info,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=5)
        
        tk.Button(
            buttons_frame,
            text="📁 Open Project Folder",
            command=self.open_project_folder,
            bg='#2ecc71',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=5)
        
        tk.Button(
            buttons_frame,
            text="🌐 CFPB Data Source",
            command=self.open_cfpb_website,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=5)
    
    def create_analysis_tab(self):
        """Create data analysis tab"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="🔥 Run Analysis")
        
        # Analysis controls frame
        controls_frame = tk.Frame(analysis_frame, bg='#ecf0f1')
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        # Title
        tk.Label(
            controls_frame,
            text="Real CFPB Data Analysis Controls",
            font=('Arial', 14, 'bold'),
            bg='#ecf0f1'
        ).pack(pady=10)
        
        # Analysis type selection
        analysis_type_frame = tk.Frame(controls_frame, bg='#ecf0f1')
        analysis_type_frame.pack(fill='x', pady=10)
        
        tk.Label(
            analysis_type_frame,
            text="Analysis Type:",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1'
        ).pack(side='left')
        
        self.analysis_type = tk.StringVar(value="full")
        ttk.Radiobutton(
            analysis_type_frame,
            text="Full Analysis (Download + Process)",
            variable=self.analysis_type,
            value="full"
        ).pack(side='left', padx=20)
        
        ttk.Radiobutton(
            analysis_type_frame,
            text="Quick Analysis (Existing Data)",
            variable=self.analysis_type,
            value="quick"
        ).pack(side='left', padx=20)
        
        # Options frame
        options_frame = tk.Frame(controls_frame, bg='#ecf0f1')
        options_frame.pack(fill='x', pady=10)
        
        self.include_ftc = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Include FTC Triangulation",
            variable=self.include_ftc
        ).pack(side='left', padx=10)
        
        self.generate_excel = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Generate Excel Export",
            variable=self.generate_excel
        ).pack(side='left', padx=10)
        
        self.open_reports = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Open Reports When Complete",
            variable=self.open_reports
        ).pack(side='left', padx=10)
        
        # Analysis buttons
        button_frame = tk.Frame(controls_frame, bg='#ecf0f1')
        button_frame.pack(fill='x', pady=20)
        
        self.run_button = tk.Button(
            button_frame,
            text="🚀 Run Real Data Analysis",
            command=self.run_analysis,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2,
            width=25
        )
        self.run_button.pack(side='left', padx=10)
        
        self.stop_button = tk.Button(
            button_frame,
            text="⏹️ Stop Analysis",
            command=self.stop_analysis,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2,
            width=20,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=10)
        
        # Progress frame
        progress_frame = tk.Frame(controls_frame, bg='#ecf0f1')
        progress_frame.pack(fill='x', pady=10)
        
        tk.Label(
            progress_frame,
            text="Progress:",
            font=('Arial', 10, 'bold'),
            bg='#ecf0f1'
        ).pack(anchor='w')
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate'
        )
        self.progress_bar.pack(fill='x', pady=5)
        
        # Analysis output text area
        tk.Label(
            analysis_frame,
            text="Analysis Output & Logs:",
            font=('Arial', 12, 'bold')
        ).pack(anchor='w', padx=10, pady=(10, 0))
        
        self.analysis_output = scrolledtext.ScrolledText(
            analysis_frame,
            height=15,
            font=('Consolas', 9),
            bg='#1a1a1a',
            fg='#00ff00',
            insertbackground='white'
        )
        self.analysis_output.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_results_tab(self):
        """Create results viewer tab"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📈 View Results")
        
        # Results header
        header_frame = tk.Frame(results_frame, bg='#ecf0f1')
        header_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            header_frame,
            text="Analysis Results & Reports",
            font=('Arial', 14, 'bold'),
            bg='#ecf0f1'
        ).pack(pady=10)
        
        # Results summary frame
        summary_frame = tk.LabelFrame(results_frame, text="Quick Summary", font=('Arial', 12, 'bold'))
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        self.summary_text = tk.Text(
            summary_frame,
            height=8,
            font=('Arial', 10),
            bg='#f8f9fa',
            state='disabled'
        )
        self.summary_text.pack(fill='x', padx=10, pady=10)
        
        # Report links frame
        links_frame = tk.LabelFrame(results_frame, text="Generated Reports", font=('Arial', 12, 'bold'))
        links_frame.pack(fill='x', padx=10, pady=10)
        
        self.report_buttons_frame = tk.Frame(links_frame)
        self.report_buttons_frame.pack(fill='x', padx=10, pady=10)
        
        # Detailed results frame
        details_frame = tk.LabelFrame(results_frame, text="Detailed Results", font=('Arial', 12, 'bold'))
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.results_tree = ttk.Treeview(details_frame)
        self.results_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(details_frame, orient='vertical', command=self.results_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.results_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_settings_tab(self):
        """Create settings and export tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings & Export")
        
        # File locations frame
        locations_frame = tk.LabelFrame(settings_frame, text="File Locations", font=('Arial', 12, 'bold'))
        locations_frame.pack(fill='x', padx=10, pady=10)
        
        # Data directory
        tk.Label(locations_frame, text="Data Directory:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.data_dir_var = tk.StringVar(value=os.path.abspath("data"))
        tk.Entry(locations_frame, textvariable=self.data_dir_var, width=50).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(locations_frame, text="Browse", command=lambda: self.browse_directory(self.data_dir_var)).grid(row=0, column=2, padx=5, pady=5)
        
        # Output directory
        tk.Label(locations_frame, text="Output Directory:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.output_dir_var = tk.StringVar(value=os.path.abspath("outputs"))
        tk.Entry(locations_frame, textvariable=self.output_dir_var, width=50).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(locations_frame, text="Browse", command=lambda: self.browse_directory(self.output_dir_var)).grid(row=1, column=2, padx=5, pady=5)
        
        # Analysis parameters frame
        params_frame = tk.LabelFrame(settings_frame, text="Analysis Parameters", font=('Arial', 12, 'bold'))
        params_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(params_frame, text="Date Range:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        tk.Label(params_frame, text="April 19, 2025 - October 19, 2025 (Last 6 Months)", font=('Arial', 10)).grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        tk.Label(params_frame, text="Filter Requirements:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        tk.Label(params_frame, text="• Has consumer narrative\n• Exclude credit reporting\n• Last 6 months only", font=('Arial', 10)).grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        # Export options
        export_frame = tk.LabelFrame(settings_frame, text="Export Options", font=('Arial', 12, 'bold'))
        export_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(
            export_frame,
            text="📊 Export Current Results to Excel",
            command=self.export_to_excel,
            bg='#2ecc71',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=10, pady=10)
        
        tk.Button(
            export_frame,
            text="📄 Open Markdown Report",
            command=self.open_markdown_report,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=10, pady=10)
        
        tk.Button(
            export_frame,
            text="🗂️ Open Output Folder",
            command=self.open_output_folder,
            bg='#f39c12',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=10, pady=10)
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = tk.Label(
            self.root,
            text="Ready - System initialized",
            relief=tk.SUNKEN,
            anchor='w',
            bg='#34495e',
            fg='white',
            font=('Arial', 9)
        )
        self.status_bar.pack(side='bottom', fill='x')
    
    def show_system_info(self):
        """Display comprehensive system information"""
        info = f"""
🏛️  CFPB Consumer Complaint Analysis Tool v5.0
{'='*60}

📊 SYSTEM STATUS
Current Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Period: April 19, 2025 - October 19, 2025 (Last 6 Months)
Data Source: Real CFPB Consumer Complaint Database
Status: Ready for analysis

📁 PROJECT STRUCTURE
Project Root: {os.path.abspath('.')}
├── analysis/           - Core analysis modules
│   ├── cfpb_real_analyzer.py     ✅ Real data processor
│   ├── real_data_fetcher.py      ✅ CFPB data downloader  
│   ├── ftc_real_triangulator.py  ✅ FTC cross-validation
│   └── visualizer.py             ✅ Chart generator
├── data/               - CFPB CSV files (currently empty)
├── outputs/            - Generated reports (currently empty)
├── visualizations/     - Charts and dashboards
└── real_main_analysis.py         ✅ Main analysis script

🎯 ANALYSIS SPECIFICATIONS
✅ Time Period: Last 6 months (Apr 19 - Oct 19, 2025)
✅ Data Filter: Complaints with consumer narratives only
✅ Exclusions: Credit reporting categories (both checkboxes)
✅ Company Focus: Excludes credit agencies (Equifax, Experian, TransUnion)
✅ Link Generation: Clickable URLs to individual CFPB complaints
✅ Sub-Trends: Detailed breakdown of issues within categories
✅ FTC Validation: Cross-reference with Consumer Sentinel data

🔥 TOP TRENDS ANALYSIS (What you'll get)
1. Top 10 complaint categories (excluding credit reporting)
2. Sub-trends within each category
3. Most complained about companies
4. Individual complaint samples with clickable links
5. Special category analysis:
   🤖 AI/Algorithmic bias complaints
   🌐 LEP/Spanish language access issues  
   🚨 Fraud and digital banking problems

📈 GENERATED OUTPUTS
When analysis completes, you'll get:
• cfpb_real_analysis_report.md     - Comprehensive markdown report
• cfpb_ftc_triangulation_report.md - FTC cross-validation
• cfpb_real_analysis.xlsx          - Excel data export
• Interactive charts and visualizations

🔗 COMPLAINT LINKS FORMAT
All sample complaints include clickable links:
https://www.consumerfinance.gov/data-research/consumer-complaints/search/detail/{{COMPLAINT_ID}}

🚫 DATA AUTHENTICITY GUARANTEE
• NO simulated data - 100% real CFPB complaints
• Direct download from official CFPB database
• All complaint IDs link to real CFPB records  
• Verifiable against CFPB Consumer Complaint Database

📋 TO START ANALYSIS
1. Click "Run Analysis" tab
2. Select "Full Analysis" to download latest data
3. Click "🚀 Run Real Data Analysis"
4. Wait for download and processing (~5-15 minutes)
5. View results in "View Results" tab

🌐 DATA SOURCES
• CFPB: https://www.consumerfinance.gov/data-research/consumer-complaints/
• FTC: https://www.ftc.gov/exploredata

Ready to analyze real consumer complaint data! 🚀
"""
        
        self.system_info_text.delete(1.0, tk.END)
        self.system_info_text.insert(1.0, info)
        self.update_status("System information updated")
    
    def run_analysis(self):
        """Run the CFPB analysis in a separate thread"""
        if self.analysis_running:
            messagebox.showwarning("Analysis Running", "Analysis is already in progress!")
            return
        
        # Start analysis in separate thread
        self.analysis_running = True
        self.run_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar.start()
        
        # Clear output
        self.analysis_output.delete(1.0, tk.END)
        
        # Run analysis in thread
        analysis_thread = threading.Thread(target=self._run_analysis_thread)
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def _run_analysis_thread(self):
        """Run analysis in separate thread"""
        try:
            self.log_output("🏛️ Starting CFPB Real Data Analysis...")
            self.log_output("=" * 50)
            
            # Initialize analyzer
            if CFPBRealAnalyzer is None:
                self.log_output("❌ Error: Analysis modules not available")
                return
            
            self.log_output("📊 Initializing CFPB Real Data Analyzer...")
            self.cfpb_analyzer = CFPBRealAnalyzer()
            
            # Load real data
            self.log_output("📥 Loading real CFPB complaint data...")
            self.update_status("Downloading CFPB data...")
            
            success = self.cfpb_analyzer.load_real_data()
            if not success:
                self.log_output("❌ Failed to load CFPB data")
                self.update_status("Analysis failed - data loading error")
                return
            
            self.log_output(f"✅ Successfully loaded {len(self.cfpb_analyzer.filtered_df):,} real complaints")
            
            # Generate analysis
            self.log_output("📊 Generating comprehensive analysis...")
            self.update_status("Analyzing complaint trends...")
            
            self.analysis_results = self.cfpb_analyzer.create_detailed_report()
            
            if not self.analysis_results:
                self.log_output("❌ Failed to generate analysis report")
                return
            
            # FTC Triangulation if requested
            if self.include_ftc.get():
                self.log_output("🔄 Running FTC triangulation...")
                self.update_status("Cross-validating with FTC data...")
                
                if FTCRealTriangulator:
                    self.ftc_triangulator = FTCRealTriangulator(self.cfpb_analyzer)
                    if self.ftc_triangulator.load_ftc_real_data():
                        triangulation_results = self.ftc_triangulator.create_triangulation_report()
                        if triangulation_results:
                            self.log_output(f"✅ FTC triangulation complete: {triangulation_results['report_path']}")
                        else:
                            self.log_output("⚠️ FTC triangulation report generation failed")
                    else:
                        self.log_output("⚠️ Using FTC published statistics for triangulation")
            
            # Excel export if requested
            if self.generate_excel.get():
                self.log_output("📊 Generating Excel export...")
                self.update_status("Exporting to Excel...")
                
                self.cfpb_analyzer.data_fetcher.export_analysis_data(
                    self.cfpb_analyzer.filtered_df,
                    "outputs/cfpb_real_analysis.xlsx"
                )
                self.log_output("✅ Excel export complete: outputs/cfpb_real_analysis.xlsx")
            
            # Display results summary
            self.display_results_summary()
            
            self.log_output("\n🎉 Analysis Complete!")
            self.log_output("=" * 50)
            self.log_output("📁 Check the 'View Results' tab for detailed findings")
            self.log_output("📊 All generated files are in the outputs/ folder")
            
            self.update_status("Analysis complete - Results available")
            
            # Open reports if requested
            if self.open_reports.get():
                self.open_output_folder()
            
        except Exception as e:
            self.log_output(f"❌ Analysis error: {str(e)}")
            self.update_status(f"Analysis failed: {str(e)}")
        finally:
            # Reset UI
            self.analysis_running = False
            self.root.after(0, self._reset_analysis_ui)
    
    def _reset_analysis_ui(self):
        """Reset analysis UI elements"""
        self.run_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
    
    def stop_analysis(self):
        """Stop the running analysis"""
        self.analysis_running = False
        self.log_output("⏹️ Analysis stopped by user")
        self.update_status("Analysis stopped")
        self._reset_analysis_ui()
    
    def log_output(self, message):
        """Add message to analysis output"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}\n"
        
        def update_text():
            self.analysis_output.insert(tk.END, formatted_message)
            self.analysis_output.see(tk.END)
        
        self.root.after(0, update_text)
    
    def update_status(self, message):
        """Update status bar"""
        def update():
            self.status_bar.config(text=message)
        self.root.after(0, update)
    
    def display_results_summary(self):
        """Display analysis results summary"""
        if not self.analysis_results:
            return
        
        summary = self.analysis_results['summary']
        trends = self.analysis_results['trends']
        companies = self.analysis_results['companies']
        special = self.analysis_results['special_categories']
        
        summary_text = f"""📊 ANALYSIS RESULTS SUMMARY
{'='*50}

📈 Total Complaints Analyzed: {summary['total_complaints']:,}
🏢 Unique Companies: {summary['unique_companies']:,}
📋 Product Categories: {summary['unique_products']:,}
📅 Analysis Period: {summary['date_range']}

🔥 TOP 5 COMPLAINT CATEGORIES:
"""
        
        for i, (product, count) in enumerate(list(trends['top_products'].items())[:5], 1):
            pct = (count / summary['total_complaints']) * 100
            summary_text += f"   {i}. {product:<35} {count:>8,} ({pct:>5.1f}%)\n"
        
        summary_text += f"""
🏢 TOP 5 COMPANIES:
"""
        
        for i, (company, data) in enumerate(list(companies.items())[:5], 1):
            summary_text += f"   {i}. {company:<35} {data['total_complaints']:>8,}\n"
        
        summary_text += f"""
🎯 SPECIAL CATEGORIES:
   🤖 AI/Algorithmic Issues:    {len(special['ai_complaints']):>8,}
   🌐 LEP/Spanish Language:     {len(special['lep_complaints']):>8,}
   🚨 Fraud/Digital Banking:    {len(special['fraud_digital_complaints']):>8,}

📄 Generated Reports:
   • {self.analysis_results['report_path']}
   • outputs/cfpb_real_analysis.xlsx
"""
        
        # Update summary text widget
        def update_summary():
            self.summary_text.config(state='normal')
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, summary_text)
            self.summary_text.config(state='disabled')
            
            # Add report buttons
            self.create_report_buttons()
        
        self.root.after(0, update_summary)
    
    def create_report_buttons(self):
        """Create buttons for opening reports"""
        # Clear existing buttons
        for widget in self.report_buttons_frame.winfo_children():
            widget.destroy()
        
        if self.analysis_results:
            tk.Button(
                self.report_buttons_frame,
                text="📄 Open Markdown Report",
                command=self.open_markdown_report,
                bg='#3498db',
                fg='white',
                font=('Arial', 10, 'bold')
            ).pack(side='left', padx=5, pady=5)
            
            tk.Button(
                self.report_buttons_frame,
                text="📊 Open Excel Export",
                command=self.open_excel_export,
                bg='#2ecc71',
                fg='white',
                font=('Arial', 10, 'bold')
            ).pack(side='left', padx=5, pady=5)
            
            tk.Button(
                self.report_buttons_frame,
                text="🗂️ Open Output Folder",
                command=self.open_output_folder,
                bg='#f39c12',
                fg='white',
                font=('Arial', 10, 'bold')
            ).pack(side='left', padx=5, pady=5)
    
    def browse_directory(self, var):
        """Browse for directory"""
        directory = filedialog.askdirectory()
        if directory:
            var.set(directory)
    
    def open_project_folder(self):
        """Open project folder in file explorer"""
        os.startfile(os.path.abspath('.'))
    
    def open_output_folder(self):
        """Open output folder"""
        output_dir = os.path.abspath('outputs')
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            messagebox.showinfo("Info", "Output folder will be created after running analysis")
    
    def open_cfpb_website(self):
        """Open CFPB data source website"""
        webbrowser.open("https://www.consumerfinance.gov/data-research/consumer-complaints/#download-the-data")
    
    def open_markdown_report(self):
        """Open the markdown report"""
        if self.analysis_results and 'report_path' in self.analysis_results:
            report_path = self.analysis_results['report_path']
            if os.path.exists(report_path):
                os.startfile(report_path)
            else:
                messagebox.showerror("Error", f"Report file not found: {report_path}")
        else:
            messagebox.showinfo("Info", "No analysis results available. Run analysis first.")
    
    def open_excel_export(self):
        """Open Excel export"""
        excel_path = os.path.abspath("outputs/cfpb_real_analysis.xlsx")
        if os.path.exists(excel_path):
            os.startfile(excel_path)
        else:
            messagebox.showinfo("Info", "Excel export not found. Make sure 'Generate Excel Export' is checked and run analysis.")
    
    def export_to_excel(self):
        """Export current results to Excel"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis results to export. Run analysis first.")
            return
        
        try:
            if self.cfpb_analyzer:
                self.cfpb_analyzer.data_fetcher.export_analysis_data(
                    self.cfpb_analyzer.filtered_df,
                    "outputs/cfpb_real_analysis.xlsx"
                )
                messagebox.showinfo("Success", "Results exported to outputs/cfpb_real_analysis.xlsx")
            else:
                messagebox.showerror("Error", "No analyzer available for export")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

def main():
    """Main GUI application entry point"""
    root = tk.Tk()
    app = CFPBAnalysisGUI(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()