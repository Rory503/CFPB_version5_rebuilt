# Changelog

## [Latest Update] - 2025-01-28

### Added
- **Consumer Complaints Section** - A new comprehensive tab has been added to display individual consumer complaint details
- Complete complaint details including:
  - Complaint ID with clickable CFPB.gov links
  - Company name and response information
  - Timely response indicator
  - Date received
  - Consumer's state
  - Product and sub-product categories
  - Issue and sub-issue details
  - Full consumer complaint narrative
- Interactive filtering system:
  - Filter by company (top 50 companies available)
  - Filter by product category
  - Adjustable number of complaints to display (10, 25, 50, 100, 200, 500, 1000, All)
  - **NEW:** "All" option to view all complaints in the system (e.g., all 51,466+ complaints)
- **Month Selector** - Choose how many months of data to load (1-6 months) in the analysis options

### Fixed
- **CRITICAL:** Fixed hardcoded future dates (April-October 2025) that prevented all data loading
- **Added cache validation** to prevent loading stale cached data from old hardcoded dates
- **Consumer complaint narratives now display properly** with improved column detection
- **Can now view all complaints** without the 200 complaint limit
- **Fixed "Failed to load pre-filtered real CFPB data" error** in Quick Analysis
- **Date range now uses relative dates** (today minus N months) instead of fixed future dates
- Enhanced narrative column detection with multiple fallback strategies
- Better handling of missing narrative data with clear indicators
- Added `__init__.py` to analysis package for proper imports
- MONTHS_WINDOW environment variable now properly passed to all data fetchers
- Improved error handling to show exact error messages when data loading fails

### Removed
- **FTC Cross-Validation** feature removed from the interface

### Technical Improvements
- Added new `show_consumer_complaints()` function to web_dashboard.py
- Robust column name mapping to handle different case conventions
- Multiple narrative column name variations supported
- Smart handling of missing or empty fields
- Efficient display with pandas data handling
- Improved narrative detection with fallback logic

### Deployment
- Changes pushed to both `restore-website` and `main` branches
- Ready for automatic deployment on Render.com
- No additional configuration needed

---

## [Previous Version]
- Professional analytics dashboard
- AI chat assistant integration
- Comprehensive data visualization
- Special categories analysis (AI bias, LEP issues, fraud)
- Excel export functionality

