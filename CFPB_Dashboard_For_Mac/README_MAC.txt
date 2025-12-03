╔══════════════════════════════════════════════════════════════╗
║         CFPB Consumer Complaint Analytics Dashboard         ║
║                    Mac Installation Guide                    ║
╚══════════════════════════════════════════════════════════════╝

SYSTEM REQUIREMENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ macOS 10.13 or later
✓ Python 3.8 or later (usually pre-installed on Mac)
✓ Internet connection (for first-time setup only)


FIRST TIME SETUP (2 MINUTES):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. EXTRACT THE ZIP FILE
   - Double-click the downloaded ZIP file
   - Move the extracted folder to your Desktop or Documents

2. OPEN TERMINAL
   - Go to Applications → Utilities → Terminal
   - A black/white window will open (this is normal!)

3. COPY-PASTE THESE TWO COMMANDS:
   
   First command (makes the script runnable):
   cd ~/Desktop/CFPB_Dashboard_For_Mac && chmod +x run_dashboard.sh
   
   Second command (starts the dashboard):
   ./run_dashboard.sh

   ⚠️ IMPORTANT: Adjust path if you put the folder somewhere other than Desktop!
   
4. WHAT YOU'LL SEE:
   ✓ "Python 3 found"
   ✓ "Creating virtual environment..."
   ✓ "Installing required packages..." (this takes 1-2 minutes)
   ✓ "Starting CFPB Dashboard..."
   → Your browser will open automatically!

5. SECURITY WARNINGS (if they appear):
   - "Cannot be opened because it is from an unidentified developer"
     → System Preferences → Security & Privacy → Click "Open Anyway"
   
   - "Do you want to allow this app to accept incoming network connections?"
     → Click "Allow" (this lets your browser connect to the dashboard)


ALTERNATIVE: TERMINAL METHOD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
If double-clicking doesn't work:

1. Open Terminal
2. Type: cd 
3. Drag the dashboard folder into Terminal
4. Press Enter
5. Type: ./run_dashboard.sh
6. Press Enter


HOW TO USE THE DASHBOARD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Once the dashboard opens in your browser:

📊 ANALYZE REAL CFPB DATA:
   1. Click "Start Analysis" button
   2. Enter company name (e.g., "Bank of America")
   3. Select date range
   4. Click "Fetch & Analyze"
   5. View interactive charts and reports

📁 UPLOAD YOUR OWN DATA:
   1. Click "Browse files" under "Upload Your Own CSV"
   2. Select your complaint data file
   3. Dashboard will automatically analyze and visualize


TROUBLESHOOTING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ "Permission denied" error:
   → Run: chmod +x run_dashboard.sh
   (See step 2 above)

❌ "Python not found" error:
   → Install Python from: https://www.python.org/downloads/
   → Download "macOS 64-bit universal2 installer"

❌ "Command not found: streamlit":
   → This is normal on first run
   → The script will install it automatically

❌ Browser doesn't open:
   → Look for the URL in Terminal (usually http://localhost:8501)
   → Copy and paste it into your browser

❌ "Port already in use":
   → Another instance is running
   → Close the other Terminal window
   → Or restart your computer


STOPPING THE DASHBOARD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Press Ctrl+C in the Terminal window
- Or simply close the Terminal window


NOTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• First run takes 1-2 minutes (installing packages)
• Subsequent runs start in seconds
• No data is sent to external servers (except CFPB API)
• All analysis happens locally on your computer
• Exported reports are saved in the dashboard folder


SUPPORT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For technical support, contact your IT department or the
person who provided this dashboard.

Version: 5.0
Last Updated: November 2025
