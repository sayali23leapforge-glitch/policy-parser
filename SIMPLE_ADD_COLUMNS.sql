-- Simpler version to add missing columns to properties_data table

-- Step 1: Add viewMode column
ALTER TABLE properties_data 
ADD COLUMN viewMode text DEFAULT 'Homeowners';

-- Step 2: Add homeowners JSONB column
ALTER TABLE properties_data 
ADD COLUMN homeowners jsonb;

-- Step 3: Add tenants JSONB column
ALTER TABLE properties_data 
ADD COLUMN tenants jsonb;
