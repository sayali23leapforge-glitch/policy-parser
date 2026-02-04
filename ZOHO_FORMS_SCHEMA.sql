-- ===================================
-- ZOHO SIGNER FORMS TABLE
-- ===================================
-- Create the zoho_forms table in Supabase for storing form submission records

CREATE TABLE IF NOT EXISTS zoho_forms (
  id BIGSERIAL PRIMARY KEY,
  form_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
  form_name TEXT NOT NULL,
  signer_email VARCHAR(255) NOT NULL,
  signer_name VARCHAR(255),
  broker_email VARCHAR(255),
  broker_name VARCHAR(255),
  original_file_path TEXT NOT NULL,
  saved_filename TEXT NOT NULL,
  status VARCHAR(50) DEFAULT 'pending_signature',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  zoho_request_id VARCHAR(255),
  completed_at TIMESTAMPTZ,
  notes TEXT
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_zoho_forms_form_id ON zoho_forms(form_id);
CREATE INDEX IF NOT EXISTS idx_zoho_forms_signer_email ON zoho_forms(signer_email);
CREATE INDEX IF NOT EXISTS idx_zoho_forms_status ON zoho_forms(status);
CREATE INDEX IF NOT EXISTS idx_zoho_forms_created_at ON zoho_forms(created_at DESC);

-- Enable Row Level Security
ALTER TABLE zoho_forms ENABLE ROW LEVEL SECURITY;

-- Create a policy allowing all operations (adjust as needed for security)
CREATE POLICY "Allow all operations on zoho_forms" ON zoho_forms
  FOR ALL USING (true);

-- Add trigger to automatically update updated_at
CREATE OR REPLACE FUNCTION update_zoho_forms_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER zoho_forms_updated_at_trigger
BEFORE UPDATE ON zoho_forms
FOR EACH ROW
EXECUTE FUNCTION update_zoho_forms_updated_at();

-- Comments for documentation
COMMENT ON TABLE zoho_forms IS 'Stores Zoho Signer form submission records';
COMMENT ON COLUMN zoho_forms.form_id IS 'Unique identifier for the form submission (UUID)';
COMMENT ON COLUMN zoho_forms.status IS 'Current status: pending_signature, signed, expired, cancelled';
COMMENT ON COLUMN zoho_forms.zoho_request_id IS 'Zoho API request ID when integrated';
