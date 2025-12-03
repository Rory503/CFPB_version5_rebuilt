# Supabase Setup Guide for CFPB Dashboard

## Why Supabase?
- ⚡ **10x faster loading** - Instant access to cached data
- 💾 **Smart caching** - Automatically stores complaints in the cloud
- 📊 **Historical tracking** - Keep complaint data over time
- 🔍 **Advanced filtering** - Query by company, date, product instantly

---

## Step 1: Create Supabase Account

1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub (easiest) or email
4. Create a new project:
   - Name: `cfpb-dashboard` (or whatever you want)
   - Database Password: (save this somewhere safe)
   - Region: Choose closest to you
   - Click "Create new project"
5. Wait 2-3 minutes for project to initialize

---

## Step 2: Create the Database Table

1. In your Supabase project, click **"SQL Editor"** (left sidebar)
2. Click **"New query"**
3. Copy and paste this SQL:

```sql
-- Create complaints table
CREATE TABLE cfpb_complaints (
    complaint_id TEXT PRIMARY KEY,
    date_received DATE,
    product TEXT,
    sub_product TEXT,
    issue TEXT,
    sub_issue TEXT,
    company TEXT,
    state TEXT,
    zip_code TEXT,
    submitted_via TEXT,
    company_response TEXT,
    timely_response TEXT,
    consumer_disputed TEXT,
    complaint_text TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for fast querying
CREATE INDEX idx_company ON cfpb_complaints(company);
CREATE INDEX idx_date_received ON cfpb_complaints(date_received);
CREATE INDEX idx_product ON cfpb_complaints(product);
CREATE INDEX idx_state ON cfpb_complaints(state);

-- Enable Row Level Security (RLS)
ALTER TABLE cfpb_complaints ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust for production)
CREATE POLICY "Enable all operations for authenticated users"
ON cfpb_complaints
FOR ALL
USING (true)
WITH CHECK (true);
```

4. Click **"Run"** (or press F5)
5. You should see "Success. No rows returned"

---

## Step 3: Get Your Credentials

1. Click **"Settings"** (gear icon, left sidebar)
2. Click **"API"**
3. Copy these two values:

   - **Project URL** (looks like: https://xxxxx.supabase.co)
   - **anon public** key (long string starting with eyJ...)

---

## Step 4: Configure Your Dashboard

### Option A: Using .env file (Recommended)

1. In your `cfpb_version5` folder, create a file named `.env` (no extension)
2. Add these lines (replace with your actual values):

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

3. Save the file

### Option B: Using environment variables

**Windows:**
```cmd
setx SUPABASE_URL "https://your-project.supabase.co"
setx SUPABASE_KEY "your-anon-key-here"
```

**Mac/Linux:**
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key-here"
```

---

## Step 5: Install Supabase Package

In your terminal (with virtual environment activated):

```bash
pip install supabase
```

Or just run the dashboard - it will prompt you to install if missing.

---

## Step 6: Test It Out!

1. Start your dashboard:
   ```bash
   python -m streamlit run web_dashboard.py --server.port 8507
   ```

2. First load will fetch from CFPB API and cache to Supabase (30 seconds)
3. **Next loads are INSTANT** (loads from Supabase cache)
4. Look for these messages in console:
   - `✅ Supabase caching enabled`
   - `💾 Cached X complaints to Supabase`
   - `✅ Loaded X complaints from cache (instant!)`

---

## How It Works

### First Run:
1. Dashboard fetches ~5,000 complaints from CFPB API (30 seconds)
2. Automatically caches them to Supabase
3. Shows the data

### Subsequent Runs:
1. Dashboard checks Supabase cache first
2. Finds cached data → Returns instantly (< 1 second!)
3. No need to call CFPB API again

### When to Refresh:
- Data auto-refreshes when you select new date ranges
- Or click "Refresh Data" button to fetch latest from CFPB

---

## Troubleshooting

### "Missing Supabase credentials"
- Make sure `.env` file exists in cfpb_version5 folder
- Check that SUPABASE_URL and SUPABASE_KEY are set correctly
- No quotes needed in .env file

### "Supabase unavailable, using direct API mode"
- This is fine! App works without Supabase
- Just means caching is disabled, data loads from API each time

### "Failed to cache to Supabase"
- Check your internet connection
- Verify Supabase project is running (green status in dashboard)
- Check RLS policies in Supabase (Step 2)

### Still slow loading?
- First load is always slow (fetching from CFPB)
- Subsequent loads should be instant
- Check console for "Loaded X complaints from cache"

---

## Free Tier Limits

Supabase free tier includes:
- ✅ 500 MB database storage (plenty for ~100K complaints)
- ✅ Unlimited API requests
- ✅ No credit card required
- ✅ Projects don't expire

**You're good to go!** 🎉
