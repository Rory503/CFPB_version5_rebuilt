# Supabase Security Fix - Enable Row Level Security

## Issue
The `cfpb_complaints` table has RLS disabled, which means anyone with API access can read/write all data without restrictions.

## Solution
Run this SQL in your Supabase SQL Editor to enable RLS and set proper policies:

```sql
-- 1. Enable Row Level Security on cfpb_complaints table
ALTER TABLE cfpb_complaints ENABLE ROW LEVEL SECURITY;

-- 2. Allow public read access (dashboard needs to read complaint data)
CREATE POLICY "Allow public read access to complaints"
ON cfpb_complaints
FOR SELECT
TO anon, authenticated
USING (true);

-- 3. Allow authenticated users to insert/update (for caching from API)
CREATE POLICY "Allow authenticated users to cache complaints"
ON cfpb_complaints
FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update complaints"
ON cfpb_complaints
FOR UPDATE
TO authenticated
USING (true)
WITH CHECK (true);

-- 4. Prevent delete operations (keep historical data)
-- No delete policy = deletes are blocked by RLS

-- 5. Create index for performance
CREATE INDEX IF NOT EXISTS idx_cfpb_complaints_company ON cfpb_complaints(company);
CREATE INDEX IF NOT EXISTS idx_cfpb_complaints_date ON cfpb_complaints(date_received);
CREATE INDEX IF NOT EXISTS idx_cfpb_complaints_product ON cfpb_complaints(product);
CREATE INDEX IF NOT EXISTS idx_cfpb_complaints_state ON cfpb_complaints(state);

-- Verify RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename = 'cfpb_complaints';
```

## What This Does:

1. **Enables RLS** - Blocks all access by default
2. **Allows reading** - Anyone can read complaint data (it's public CFPB data anyway)
3. **Allows caching** - Authenticated apps can write/update for caching
4. **Blocks deletes** - Preserves historical data
5. **Adds indexes** - Speeds up queries

## Security Model:
- ✅ Public read (CFPB data is public anyway)
- ✅ Authenticated write (only your dashboard app can cache)
- ✅ No deletes (data integrity)
- ✅ Fast queries (indexed)

## Run This Now:
1. Go to Supabase Dashboard
2. Click "SQL Editor"
3. Copy/paste the SQL above
4. Click "Run"
5. Done! ✅

---

## If you have a `users` table issue:

If Supabase is complaining about a `users` table, run this:

```sql
-- Enable RLS on users table (if it exists)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Allow users to read only their own data
CREATE POLICY "Users can view own data"
ON public.users
FOR SELECT
TO authenticated
USING (auth.uid()::text = id::text);

-- Allow users to update only their own data
CREATE POLICY "Users can update own data"
ON public.users
FOR UPDATE
TO authenticated
USING (auth.uid()::text = id::text)
WITH CHECK (auth.uid()::text = id::text);
```

This locks down user data so each user can only see/edit their own record.
