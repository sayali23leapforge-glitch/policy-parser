# ZohoSigner Backend Integration

This document describes the backend setup for the ZohoSigner HTML page integration.

## Overview

The backend is configured to:
1. Accept PDF uploads + form fields from the ZohoSigner HTML form
2. Save PDFs to `/uploads` folder
3. Generate unique form IDs (UUID)
4. Store submission records in Supabase `zoho_forms` table
5. Return success/failure responses to the frontend

## Backend Routes

### POST `/process-form`
**Purpose**: Process ZohoSigner form submissions

**Request**: `multipart/form-data`
```
- pdf_file: (file) PDF document to process
- form_name: (string) Name of the form
- signer_email: (string) Client email address
- signer_name: (string) Client name
- broker_email: (string) Broker email address
- broker_name: (string) Broker name
```

**Response** (Success - 200):
```json
{
  "success": true,
  "form_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending_signature",
  "message": "Form processed successfully"
}
```

**Response** (Error):
```json
{
  "success": false,
  "error": "Only PDF files are allowed"
}
```

### POST `/zoho-webhook`
**Purpose**: Placeholder for Zoho signature completion webhooks

**Status**: Not yet implemented
- Will receive signature completion notifications from Zoho
- Will update form status in database
- Will trigger notifications

### GET `/oauth/callback`
**Purpose**: Placeholder for OAuth2 callback handling

**Status**: Not yet implemented
- Will handle Zoho authorization code exchange
- Will store OAuth tokens securely

## Database Schema

### Table: `zoho_forms`

Created via [ZOHO_FORMS_SCHEMA.sql](ZOHO_FORMS_SCHEMA.sql)

**Columns**:
| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Auto-incrementing primary key |
| form_id | UUID | Unique identifier for the submission |
| form_name | TEXT | Name of the form (e.g., "PAC Form (Auto)") |
| signer_email | VARCHAR(255) | Client email address |
| signer_name | VARCHAR(255) | Client name |
| broker_email | VARCHAR(255) | Broker email address |
| broker_name | VARCHAR(255) | Broker name |
| original_file_path | TEXT | Full path to saved PDF |
| saved_filename | TEXT | Filename of saved PDF |
| status | VARCHAR(50) | Current status: `pending_signature`, `signed`, `expired`, `cancelled` |
| created_at | TIMESTAMPTZ | Timestamp when submitted |
| updated_at | TIMESTAMPTZ | Auto-updated on any record change |
| zoho_request_id | VARCHAR(255) | Zoho API request ID (future) |
| completed_at | TIMESTAMPTZ | Timestamp when signing completed |
| notes | TEXT | Additional notes |

## File Uploads

**Upload Folder**: `/uploads`
- Created automatically if doesn't exist
- Stored on filesystem in server directory
- Filenames: `{uuid}_{timestamp}_{original_filename}`

**Allowed Extensions**: `.pdf` only

## Environment Setup

Ensure these are in `.env.local`:
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
FLASK_PORT=5000
```

## Setup Instructions

### 1. Create Supabase Table

Run the SQL in [ZOHO_FORMS_SCHEMA.sql](ZOHO_FORMS_SCHEMA.sql) in your Supabase SQL Editor:
- https://app.supabase.com/project/[PROJECT_ID]/sql

### 2. Install Dependencies

Backend dependencies are already in `backend/requirements.txt`:
```bash
pip install -r backend/requirements.txt
```

### 3. Start Backend Server

```bash
python backend/app.py
```

Or use the provided batch file:
```bash
run_backend.bat
```

## Frontend Integration

The ZohoSigner HTML page (`zoho signer auto.html`) sends form data when user clicks "Process" button:

```javascript
// In RUN mode (not SETUP):
// 1. User uploads PDF
// 2. User fills signer info (name, email)
// 3. User clicks "Process" button
// 4. Frontend calls: POST /process-form with FormData
// 5. Backend returns form_id and status
// 6. Frontend shows success notification
```

## Future Enhancements

### Zoho Webhook Integration (TODO)
When implemented, the `/zoho-webhook` route will:
- Validate webhook signature from Zoho
- Parse signature completion events
- Update `zoho_forms.status` to `signed`
- Update `zoho_forms.zoho_request_id`
- Set `completed_at` timestamp
- Trigger notifications to broker

### OAuth2 Integration (TODO)
When implemented, the `/oauth/callback` route will:
- Exchange authorization code for access token
- Store tokens securely in Supabase
- Redirect user to appropriate page
- Enable automatic form submission to Zoho API

## Current Limitations

- ❌ Zoho API integration not enabled
- ❌ OAuth2 not configured
- ❌ Webhook signatures not validated
- ❌ Automatic Zoho submission not implemented
- ✅ Manual file upload and database storage working
- ✅ Form ID generation working
- ✅ Status tracking working

## Monitoring

Check form submissions:
```bash
# View uploaded PDFs
ls -la uploads/

# Query database (via Supabase console)
SELECT form_id, signer_email, status, created_at FROM zoho_forms ORDER BY created_at DESC;
```

## Troubleshooting

**Issue**: `Table 'zoho_forms' does not exist`
- **Solution**: Run the SQL schema from ZOHO_FORMS_SCHEMA.sql in Supabase

**Issue**: PDF not saving
- **Solution**: Check `/uploads` folder has write permissions

**Issue**: Form submission returns 500 error
- **Solution**: Check Flask server logs for detailed error message

## Security Notes

- PDFs are saved with UUIDs to prevent filename collisions
- RLS policies should be configured for production
- Service role key should not be exposed to frontend
- Webhook signatures must be validated when enabled
- OAuth tokens should be stored encrypted in database

## Related Files

- [ZOHO_FORMS_SCHEMA.sql](ZOHO_FORMS_SCHEMA.sql) - Database schema
- [backend/app.py](backend/app.py) - Backend routes (lines ~1350+)
- [zoho signer auto.html](zoho%20signer%20auto.html) - Frontend form
