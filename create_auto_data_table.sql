-- Create auto_data table for storing Auto Dashboard data
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS auto_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    auto_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    customer JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_auto_data_lead_id ON auto_data(lead_id);
CREATE INDEX IF NOT EXISTS idx_auto_data_email ON auto_data(email);
CREATE INDEX IF NOT EXISTS idx_auto_data_updated_at ON auto_data(updated_at);

-- Add comment
COMMENT ON TABLE auto_data IS 'Stores Auto Dashboard form data linked to leads';

-- Enable Row Level Security (optional, adjust policies as needed)
ALTER TABLE auto_data ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust based on your auth setup)
CREATE POLICY "Enable all operations for auto_data" ON auto_data
    FOR ALL
    USING (true)
    WITH CHECK (true);
