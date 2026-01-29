-- Add missing columns to properties_data table for Tenants and Homeowners data

-- Add viewMode column (stores which tab was active: 'Homeowners' or 'Tenants')
ALTER TABLE properties_data 
ADD COLUMN IF NOT EXISTS viewMode VARCHAR(50) DEFAULT 'Homeowners';

-- Add homeowners column (JSONB to store Homeowners mode data)
ALTER TABLE properties_data 
ADD COLUMN IF NOT EXISTS homeowners JSONB;

-- Add tenants column (JSONB to store Tenants mode data)
ALTER TABLE properties_data 
ADD COLUMN IF NOT EXISTS tenants JSONB;

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_properties_viewmode ON properties_data(viewMode);
CREATE INDEX IF NOT EXISTS idx_properties_email ON properties_data(email);

-- Update existing rows to preserve backward compatibility
UPDATE properties_data 
SET homeowners = jsonb_build_object(
    'customer', customer,
    'properties', CASE WHEN properties IS NOT NULL THEN properties ELSE '[]'::jsonb END
)
WHERE homeowners IS NULL AND customer IS NOT NULL;

-- Update existing rows with default Homeowners viewMode
UPDATE properties_data 
SET viewMode = 'Homeowners'
WHERE viewMode IS NULL;

SELECT 'Columns added successfully!' as result;
