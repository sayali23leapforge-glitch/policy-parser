"""
Meta/Facebook Lead Form Backend
Integrates with Facebook Lead API and Supabase
"""

import sys
import io

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from dotenv import load_dotenv
from supabase import create_client, Client
import hmac
import hashlib
# Import pdf_parser using relative import
from .pdf_parser import parse_mvr_pdf, parse_dash_pdf, parse_quote_pdf

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env.local'))

# Configure Flask to serve static files from parent directory
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), '..')
app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
CORS(app)
# SocketIO with HTTP Long Polling fallback (no async workers needed)
socketio = SocketIO(app, cors_allowed_origins="*", 
                     async_mode='threading',
                     ping_timeout=60,
                     ping_interval=25,
                     engineio_logger=False)

# ========== CONFIG ==========
META_APP_ID = os.getenv('META_APP_ID')
META_APP_SECRET = os.getenv('META_APP_SECRET')
META_PAGE_ID = os.getenv('META_PAGE_ID')
META_PAGE_ACCESS_TOKEN = os.getenv('META_PAGE_ACCESS_TOKEN')
META_LEAD_FORM_ID = os.getenv('META_LEAD_FORM_ID')
META_WEBHOOK_VERIFY_TOKEN = os.getenv('META_WEBHOOK_VERIFY_TOKEN')
FB_PIXEL_ID = os.getenv('FB_PIXEL_ID')

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_SERVICE_ROLE_KEY')

# Zoho OAuth (for token exchange)
ZOHO_CLIENT_ID = os.getenv('ZOHO_CLIENT_ID')
ZOHO_CLIENT_SECRET = os.getenv('ZOHO_CLIENT_SECRET')
ZOHO_REDIRECT_URI = os.getenv('ZOHO_REDIRECT_URI')

# Debug: Print Supabase URL
print(f"🔗 Supabase URL: {SUPABASE_URL}")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Meta API Base URL
META_API_VERSION = 'v18.0'
META_BASE_URL = f'https://graph.facebook.com/{META_API_VERSION}'

# ========== HELPER FUNCTIONS ==========

def verify_meta_webhook(data, hub_signature):
    """Verify webhook signature from Meta"""
    hash_obj = hmac.new(
        META_APP_SECRET.encode('utf-8'),
        data,
        hashlib.sha256
    )
    expected_signature = f'sha256={hash_obj.hexdigest()}'
    return hmac.compare_digest(expected_signature, hub_signature)


def get_leads_from_meta():
    """Fetch all leads from Meta Lead Form API with pagination (up to 500 leads)"""
    try:
        all_leads = []
        url = f'{META_BASE_URL}/{META_LEAD_FORM_ID}/leads'
        
        # Try to get leads from Jan 12, 2026 onwards
        from datetime import datetime, timezone
        jan_12_timestamp = int(datetime(2026, 1, 12, 0, 0, 0, tzinfo=timezone.utc).timestamp())
        
        params = {
            'fields': 'id,created_time,field_data,adgroup_id',
            'access_token': META_PAGE_ACCESS_TOKEN,
            'limit': 500,  # Request max leads
            'filtering': f'[{{"field":"time_created","operator":"GREATER_THAN","value":{jan_12_timestamp}}}]'
        }
        
        print(f"📞 Fetching leads from Meta API since Jan 12, 2026: {url}")
        print(f"🔑 Using Lead Form ID: {META_LEAD_FORM_ID}")
        print(f"📅 Filtering from timestamp: {jan_12_timestamp}")
        
        # Fetch first page
        response = requests.get(url, params=params)
        print(f"📡 Meta API Response Status: {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        all_leads.extend(data.get('data', []))
        print(f"📄 Page 1: {len(data.get('data', []))} leads")
        
        # Continue fetching all pages (max 500 total to avoid overwhelming)
        page_count = 1
        while 'paging' in data and 'next' in data['paging'] and len(all_leads) < 500:
            page_count += 1
            next_url = data['paging']['next']
            print(f"📄 Fetching page {page_count}... (Total so far: {len(all_leads)})")
            response = requests.get(next_url)
            response.raise_for_status()
            data = response.json()
            page_leads = data.get('data', [])
            all_leads.extend(page_leads)
            print(f"   + {len(page_leads)} leads")
            
            # Safety limit
            if page_count > 10:
                print(f"⚠️ Reached page limit (10 pages)")
                break
        
        print(f"✅ Found {len(all_leads)} total leads from Meta")
        return all_leads
    
    except Exception as e:
        print(f"❌ Error fetching leads from Meta: {str(e)}")
        if hasattr(e, 'response'):
            print(f"❌ Meta API Error Response: {e.response.text if e.response else 'No response'}")
        return []


def parse_meta_lead(meta_lead):
    """Parse Meta lead data into standardized format"""
    field_data = meta_lead.get('field_data', [])
    lead_dict = {}
    
    # Facebook returns field_data with "values" as an array
    for field in field_data:
        field_name = field.get('name', '').lower()
        field_values = field.get('values', [])
        # Take the first value from the array
        lead_dict[field_name] = field_values[0] if field_values else ''
    
    meta_lead_id = meta_lead.get('id')
    
    return {
        # Don't set 'id' - let database auto-generate it
        'meta_lead_id': meta_lead_id,
        'name': lead_dict.get('full_name', lead_dict.get('name', 'Unknown')),
        'phone': lead_dict.get('phone_number', lead_dict.get('phone', '')),
        'email': lead_dict.get('email_address', lead_dict.get('email', '')),
        'message': lead_dict.get('message', ''),
        'created_at': meta_lead.get('created_time', datetime.utcnow().isoformat()),
        'meta_data': meta_lead,
        'is_manual': False,
        'status': 'New Lead',
        'type': 'Auto',
        'potential_status': 'Not Qualified',
        'premium': 0,
        'sync_status': 'Not Synced',
        'sync_signal': False,
        'notes': ''
        # Removed: company, address, city, state, country, zip_code - not in database schema
    }


def save_lead_to_supabase(lead_data):
    """Save lead to Supabase (skip if already exists)"""
    try:
        # Check if lead already exists by meta_lead_id (only for Facebook leads)
        if lead_data.get('meta_lead_id'):
            existing = supabase.table('leads').select('id').eq('meta_lead_id', lead_data.get('meta_lead_id')).execute()
            
            if existing.data:
                print(f"⏭️ Lead {lead_data.get('meta_lead_id')} already exists, skipping")
                return existing.data[0]
        
        # Insert new lead
        print(f"🔄 Attempting to save lead: {lead_data.get('name')}")
        response = supabase.table('leads').insert(lead_data).execute()
        print(f"💾 Saved lead: {lead_data.get('name')} (ID: {response.data[0].get('id') if response.data else 'N/A'})")
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error saving lead to Supabase: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def get_leads_from_db(filters=None):
    """Get leads from Supabase"""
    try:
        print(f"📋 Querying leads table with filters: {filters}")
        query = supabase.table('leads').select('*')
        
        if filters:
            if filters.get('type'):
                query = query.eq('type', filters['type'])
            if filters.get('status'):
                query = query.eq('status', filters['status'])
        
        # No limit - fetch ALL leads
        response = query.order('created_at', desc=True).execute()
        print(f"✅ Query returned {len(response.data)} leads")
        return response.data
    except Exception as e:
        print(f"❌ Error fetching leads from Supabase: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def send_event_to_meta(lead_id, event_type, event_data):
    """Send event to Meta Conversions API (Event Manager)"""
    try:
        url = f'{META_BASE_URL}/{FB_PIXEL_ID}/events'
        
        payload = {
            'data': [
                {
                    'event_name': event_type,  # 'Purchase', 'Lead', 'ViewContent', etc
                    'event_time': int(datetime.utcnow().timestamp()),
                    'user_data': {
                        'em': event_data.get('email', ''),  # hashed email
                        'ph': event_data.get('phone', ''),  # hashed phone
                        'fn': event_data.get('name', ''),   # hashed first name
                    },
                    'custom_data': {
                        'value': event_data.get('premium', 0),
                        'currency': 'USD'
                    },
                    'event_source_url': event_data.get('source_url', ''),
                    'action_source': 'website'
                }
            ],
            'access_token': META_PAGE_ACCESS_TOKEN
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    except Exception as e:
        print(f"Error sending event to Meta: {str(e)}")
        return {'success': False, 'error': str(e)}


# ========== API ENDPOINTS ==========

@app.route('/')
def index():
    """Serve Meta Dashboard as home page"""
    return send_from_directory(app.static_folder, 'meta dashboard.html')

@app.route('/auto')
def auto_dashboard():
    """Serve Auto Dashboard"""
    return send_from_directory(app.static_folder, 'Auto dashboard.html')

@app.route('/property')
def property_dashboard():
    """Serve Property Dashboard"""
    return send_from_directory(app.static_folder, 'property.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'Meta Lead Dashboard Backend'}), 200


@app.route('/api/leads/from-facebook', methods=['GET'])
def get_leads_from_facebook():
    """Get ALL leads from Facebook Leads Center (not from database)"""
    try:
        print("📱 Fetching leads from Facebook Leads Center...")
        
        if not META_LEAD_FORM_ID:
            return jsonify({'success': False, 'error': 'Lead form ID not configured'}), 400
        
        # Fetch leads from Facebook Leads API for this form
        url = f'{META_BASE_URL}/{META_LEAD_FORM_ID}/leads'
        params = {
            'fields': 'id,created_time,field_data,ad_id,form_id',
            'access_token': META_PAGE_ACCESS_TOKEN,
            'limit': 1000
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        facebook_leads = response.json().get('data', [])
        print(f"📋 Fetched {len(facebook_leads)} leads from Facebook Leads Center")
        
        # Parse all leads from Facebook format
        parsed_leads = []
        for fb_lead in facebook_leads:
            parsed = parse_meta_lead(fb_lead)
            parsed_leads.append(parsed)
        
        # Sort by date (newest first)
        parsed_leads.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'data': parsed_leads,
            'count': len(parsed_leads),
            'source': 'facebook_leads_center'
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching from Facebook: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/manual', methods=['GET'])
def get_manual_leads():
    """Get manual leads from database only"""
    try:
        response = supabase.table('leads').select('*').eq('is_manual', True).order('created_at', desc=True).execute()
        return jsonify({'success': True, 'data': response.data or [], 'count': len(response.data or [])}), 200
    except Exception as e:
        print(f"❌ Error loading manual leads: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get leads from Facebook Leads Center (database is write-only)"""
    return get_leads_from_facebook()


@app.route('/api/leads/sync', methods=['POST'])
def sync_leads():
    """Fetch fresh leads from Facebook and save to database"""
    try:
        print("📞 Fetching fresh leads from Facebook API...")
        
        # Fetch from Facebook
        meta_leads = get_leads_from_meta()
        print(f"✅ Fetched {len(meta_leads)} leads from Facebook")
        
        # Parse and save
        new_leads = []
        for meta_lead in meta_leads:
            parsed_lead = parse_meta_lead(meta_lead)
            saved = save_lead_to_supabase(parsed_lead)
            if saved:
                new_leads.append(parsed_lead)
        
        print(f"💾 Saved {len(new_leads)} new leads to database")
        
        return jsonify({
            'success': True,
            'message': f'Synced {len(new_leads)} new leads from Facebook',
            'leads': new_leads,
            'count': len(new_leads)
        }), 200
        
    except Exception as e:
        print(f"❌ Error syncing from Facebook: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/debug-meta', methods=['GET'])
def debug_meta_leads():
    """Debug endpoint to see raw Facebook API response"""
    try:
        meta_leads = get_leads_from_meta()
        # Get first 10 leads with their names
        debug_info = []
        for lead in meta_leads[:10]:
            parsed = parse_meta_lead(lead)
            debug_info.append({
                'id': lead.get('id'),
                'created_time': lead.get('created_time'),
                'name': parsed.get('name'),
                'email': parsed.get('email'),
                'phone': parsed.get('phone')
            })
        
        return jsonify({
            'success': True,
            'total_from_facebook': len(meta_leads),
            'first_10_leads': debug_info
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/test-save-one', methods=['POST'])
def test_save_one_lead():
    """Test saving one lead from Facebook"""
    try:
        meta_leads = get_leads_from_meta()
        if not meta_leads:
            return jsonify({'success': False, 'error': 'No leads from Facebook'}), 400
        
        # Try to save the first lead
        first_lead = meta_leads[0]
        parsed = parse_meta_lead(first_lead)
        
        # Try to save directly with better error handling
        try:
            if parsed.get('meta_lead_id'):
                existing = supabase.table('leads').select('id').eq('meta_lead_id', parsed.get('meta_lead_id')).execute()
                if existing.data:
                    return jsonify({
                        'success': True,
                        'message': f'Lead already exists: {parsed.get("name")}',
                        'existing': True
                    }), 200
            
            # Try insert
            response = supabase.table('leads').insert(parsed).execute()
            
            if response.data:
                return jsonify({
                    'success': True,
                    'message': f'Successfully saved lead: {parsed.get("name")}',
                    'lead': response.data[0]
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'No data returned from insert',
                    'lead_data': parsed
                }), 500
                
        except Exception as save_error:
            import traceback
            return jsonify({
                'success': False,
                'message': f'Failed to save lead: {parsed.get("name")}',
                'error': str(save_error),
                'traceback': traceback.format_exc(),
                'lead_data': parsed
            }), 500
            
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/leads/check-forms', methods=['GET'])
def check_lead_forms():
    """Check all lead forms on the page"""
    try:
        url = f'{META_BASE_URL}/{META_PAGE_ID}/leadgen_forms'
        params = {
            'fields': 'id,name,status,leads_count',
            'access_token': META_PAGE_ACCESS_TOKEN
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return jsonify({
            'success': True,
            'forms': data.get('data', []),
            'current_form_id': META_LEAD_FORM_ID
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/<lead_id>/sync-event', methods=['POST'])
def sync_lead_event(lead_id):
    """Send lead qualification event to Meta Event Manager"""
    try:
        data = request.get_json()
        event_type = data.get('event_type', 'Lead')  # Lead, Purchase, etc
        
        # Get lead from database
        response = supabase.table('leads').select('*').eq('id', lead_id).execute()
        lead = response.data[0] if response.data else None
        
        if not lead:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        # Send to Meta
        event_data = {
            'email': lead.get('email', ''),
            'phone': lead.get('phone', ''),
            'name': lead.get('name', ''),
            'premium': lead.get('premium', 0),
            'source_url': request.host_url
        }
        
        result = send_event_to_meta(lead_id, event_type, event_data)
        
        # Update lead sync timestamp and status
        supabase.table('leads').update({
            'last_sync': datetime.utcnow().isoformat(),
            'sync_status': 'sent' if result else 'failed'
        }).eq('id', lead_id).execute()
        
        # Log sync event
        supabase.table('sync_events').insert({
            'lead_id': lead_id,
            'event_type': event_type,
            'meta_response': result,
            'created_at': datetime.utcnow().isoformat()
        }).execute()
        
        return jsonify({
            'success': True,
            'message': f'Event "{event_type}" sent to Meta Event Manager',
            'meta_response': result
        }), 200
    
    except Exception as e:
        print(f"Error syncing lead event: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/create', methods=['POST'])
def create_lead():
    """Create manual lead"""
    try:
        data = request.get_json()
        
        new_lead = {
            'name': data.get('name', ''),
            'phone': data.get('phone', ''),
            'email': data.get('email', ''),
            'type': data.get('type', 'general'),
            'status': data.get('status', 'New Lead'),
            'potential_status': data.get('potential_status', 'qualified'),
            'notes': data.get('notes', ''),
            'is_manual': True,
            'premium': float(data.get('premium', 0)),
            'renewal_date': data.get('renewal_date'),
            'insurance_type': data.get('insurance_type'),
            'policy_term': data.get('policy_term'),
            'visa_type': data.get('visa_type'),
            'coverage': float(data.get('coverage', 0)) if data.get('coverage') else None,
            'trip_start': data.get('trip_start'),
            'trip_end': data.get('trip_end'),
            'sync_status': 'pending',
            'sync_signal': 'green',
            'created_at': datetime.utcnow().isoformat()
        }
        
        saved = save_lead_to_supabase(new_lead)
        return jsonify({'success': True, 'data': saved}), 201
    
    except Exception as e:
        print(f"Error creating lead: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/<lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Update lead"""
    try:
        data = request.get_json()
        
        response = supabase.table('leads').update(data).eq('id', lead_id).execute()
        
        return jsonify({'success': True, 'data': response.data[0] if response.data else None}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/<lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    """Delete lead"""
    try:
        # Delete from clients_data and properties_data first
        supabase.table('clients_data').delete().eq('lead_id', lead_id).execute()
        supabase.table('properties_data').delete().eq('lead_id', lead_id).execute()
        # Then delete from leads
        supabase.table('leads').delete().eq('id', lead_id).execute()
        return jsonify({'success': True, 'message': 'Lead and all related data deleted'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/clear-all', methods=['POST'])
def clear_all_leads():
    """Delete all leads from database"""
    try:
        # Get all lead IDs first
        all_leads = supabase.table('leads').select('id').execute()
        
        if all_leads.data:
            # Delete each lead
            for lead in all_leads.data:
                supabase.table('leads').delete().eq('id', lead['id']).execute()
            
            return jsonify({
                'success': True, 
                'message': f'Cleared {len(all_leads.data)} leads from database'
            }), 200
        else:
            return jsonify({
                'success': True, 
                'message': 'Database already empty'
            }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/leads/<lead_id>/signal', methods=['POST'])
def update_signal(lead_id):
    """Update lead signal (green/red)"""
    try:
        data = request.get_json()
        signal = data.get('signal', 'green')  # 'green' or 'red'
        
        supabase.table('leads').update({
            'sync_signal': signal,
            'potential_status': 'qualified' if signal == 'green' else 'not-qualified'
        }).eq('id', lead_id).execute()
        
        return jsonify({'success': True, 'message': f'Signal updated to {signal}'}), 200
    
    except Exception as e:
        print(f"Error updating signal: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Meta webhook endpoint for real-time Facebook Lead Ads via leadgen webhook
    
    FLOW:
    1. Receive leadgen event from Facebook webhook
    2. Fetch full lead details from Graph API
    3. PUSH IMMEDIATELY to all connected Meta Dashboard clients via WebSocket
    4. Then save to database (storage only)
    """
    
    if request.method == 'GET':
        # Webhook verification
        hub_challenge = request.args.get('hub.challenge')
        hub_verify_token = request.args.get('hub.verify_token')
        
        if hub_verify_token != META_WEBHOOK_VERIFY_TOKEN:
            print(f"❌ Webhook verification failed: {hub_verify_token} != {META_WEBHOOK_VERIFY_TOKEN}")
            return 'Invalid verify token', 403
        
        print(f"✅ Webhook verification successful")
        return hub_challenge, 200
    
    elif request.method == 'POST':
        # Verify signature
        hub_signature = request.headers.get('X-Hub-Signature-256', '')
        if not verify_meta_webhook(request.data, hub_signature):
            print(f"❌ Webhook signature verification failed")
            return 'Invalid signature', 403
        
        data = request.get_json()
        print(f"📨 Webhook POST received")
        
        # Process leadgen event (new lead created on Facebook)
        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [])
        
        for change in changes:
            field = change.get('field')
            value = change.get('value', {})
            
            # Handle leadgen_id webhook event
            if field == 'leadgen':
                leadgen_id = value.get('leadgen_id')
                print(f"📝 New leadgen event - ID: {leadgen_id}")
                
                if leadgen_id:
                    # Fetch full lead details from Meta Graph API
                    lead_details = fetch_leadgen_details(leadgen_id)
                    
                    if lead_details:
                        # Parse lead data
                        parsed_lead = parse_meta_lead(lead_details)
                        
                        # STEP 1: IMMEDIATELY PUSH TO ALL CONNECTED DASHBOARD CLIENTS
                        print(f"⚡ PUSHING lead to connected dashboard clients: {parsed_lead.get('name')}")
                        socketio.emit('new_lead', {
                            'lead': parsed_lead,
                            'timestamp': datetime.utcnow().isoformat(),
                            'source': 'webhook'
                        }, room='dashboard')
                        
                        # STEP 2: Save to database (storage only, not for display)
                        saved = save_lead_to_supabase(parsed_lead)
                        
                        if saved:
                            print(f"✅ Lead saved to database from webhook: {parsed_lead.get('name')}")
                            return jsonify({'success': True, 'lead_id': saved.get('id')}), 200
                        else:
                            print(f"✅ Lead pushed to dashboard (database save returned None)")
                            return jsonify({'success': True}), 200
                    else:
                        print(f"❌ Failed to fetch lead details for {leadgen_id}")
                        return jsonify({'success': False, 'error': 'Failed to fetch lead details'}), 500
            
            # Handle messaging webhook events (backward compatibility)
            elif field == 'messages':
                messaging = value.get('messaging', [])
                for msg in messaging:
                    if msg.get('message', {}).get('is_echo'):
                        continue
                    
                    sender_id = msg.get('sender', {}).get('id')
                    message = msg.get('message', {}).get('text', '')
                    
                    lead_data = {
                        'meta_user_id': sender_id,
                        'message': message,
                        'created_at': datetime.utcnow().isoformat(),
                        'status': 'New Lead',
                        'is_manual': False
                    }
                    save_lead_to_supabase(lead_data)
        
        return jsonify({'success': True}), 200


# ========== WEBSOCKET ENDPOINTS ==========

@socketio.on('connect')
def handle_connect():
    """Handle client connection to WebSocket"""
    print(f"👤 Client connected: {request.sid}")
    emit('connection_response', {'data': 'Connected to real-time lead server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection from WebSocket"""
    print(f"👤 Client disconnected: {request.sid}")

@socketio.on('join_dashboard')
def on_join_dashboard():
    """Client joins the dashboard room to receive live lead updates"""
    join_room('dashboard')
    print(f"📊 Client joined dashboard room: {request.sid}")
    emit('joined_dashboard', {'data': 'You are now receiving live lead updates'})



def fetch_leadgen_details(leadgen_id):
    """Fetch full lead details from Facebook Graph API using leadgen_id"""
    try:
        url = f'{META_BASE_URL}/{leadgen_id}'
        
        params = {
            'fields': 'id,created_time,field_data,ad_id,form_id',
            'access_token': META_PAGE_ACCESS_TOKEN
        }
        
        print(f"🔍 Fetching leadgen details for {leadgen_id}")
        response = requests.get(url, params=params)
        print(f"📡 Graph API Response Status: {response.status_code}")
        response.raise_for_status()
        
        lead_data = response.json()
        print(f"✅ Lead details fetched: {lead_data}")
        return lead_data
        
    except Exception as e:
        print(f"❌ Error fetching leadgen details: {str(e)}")
        if hasattr(e, 'response'):
            print(f"❌ Meta API Error Response: {e.response.text if e.response else 'No response'}")
        return None


# ========== PDF PARSING ENDPOINT ==========

@app.route('/api/parse-mvr', methods=['POST'])
def parse_mvr():
    """Parse uploaded MVR PDF and extract driver information"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are supported'}), 400
        
        # Read file content
        pdf_content = file.read()
        
        # Parse the PDF
        result = parse_mvr_pdf(pdf_content)
        
        if not result['success']:
            return jsonify(result), 400
        
        # CRITICAL: Verify policy1_vehicles is in the response before sending to client
        print(f"\n[API] /parse-mvr endpoint response verification:")
        print(f"[API] - 'policy1_vehicles' in result['data']: {'policy1_vehicles' in result['data']}")
        if 'policy1_vehicles' in result['data']:
            print(f"[API] - result['data']['policy1_vehicles']: {result['data']['policy1_vehicles']}")
        
        # Return extracted data
        return jsonify({
            'success': True,
            'data': result['data']
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/parse-dash', methods=['POST'])
def parse_dash():
    """Parse uploaded DASH PDF and extract driver information"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are supported'}), 400
        
        # Read file content
        pdf_content = file.read()
        
        # Parse the PDF
        result = parse_dash_pdf(pdf_content)
        
        if not result['success']:
            return jsonify(result), 400
        
        # Return extracted data AND raw text for debugging
        return jsonify({
            'success': True,
            'data': result['data'],
            'raw_text': result['raw_text'][:1000]  # First 1000 chars for debugging
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/parse-quote', methods=['POST'])
def parse_quote():
    """Parse uploaded Auto Quote PDF and extract coverage information"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are supported'}), 400

        pdf_content = file.read()

        result = parse_quote_pdf(pdf_content)

        if not result['success']:
            return jsonify(result), 400

        return jsonify({
            'success': True,
            'data': result['data']
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/save-client', methods=['POST'])
def save_client():
    """Save complete client data to Supabase linked to a lead"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"💾 Saving client data to Supabase...")
        print(f"📊 Data received keys: {list(data.keys())}")
        print(f"📊 Received drivers: {len(data.get('drivers', []))} driver(s)")
        
        # Get email/phone/name to identify the lead
        email = None
        phone = None
        name = None
        
        if data.get('drivers') and len(data['drivers']) > 0:
            driver = data['drivers'][0]
            print(f"🔍 First driver keys: {list(driver.keys())[:5]}...")
            email = driver.get('personalEmail')
            phone = driver.get('personalMobile')
            name = driver.get('personalName') or driver.get('mainName')
            print(f"✓ Extracted - Email: {email}, Phone: {phone}, Name: {name}")
        else:
            print(f"⚠️ No drivers data found in request")
        
        print(f"📋 Lead info - Name: {name}, Email: {email}, Phone: {phone}")
        
        # Find lead by email, phone, or name
        lead_id = None
        
        # Try email first
        if email:
            try:
                result = supabase.table('leads').select('id').eq('email', email).limit(1).execute()
                if result.data and len(result.data) > 0:
                    lead_id = result.data[0]['id']
                    print(f"✅ Found lead by email {email}: {lead_id}")
            except Exception as e:
                print(f"⚠️ Error finding lead by email: {str(e)}")
        
        # Try phone if email didn't work
        if not lead_id and phone:
            try:
                result = supabase.table('leads').select('id').eq('phone', phone).limit(1).execute()
                if result.data and len(result.data) > 0:
                    lead_id = result.data[0]['id']
                    print(f"✅ Found lead by phone {phone}: {lead_id}")
            except Exception as e:
                print(f"⚠️ Error finding lead by phone: {str(e)}")
        
        # Try name if still not found
        if not lead_id and name:
            try:
                result = supabase.table('leads').select('id').eq('name', name).limit(1).execute()
                if result.data and len(result.data) > 0:
                    lead_id = result.data[0]['id']
                    print(f"✅ Found lead by name {name}: {lead_id}")
            except Exception as e:
                print(f"⚠️ Error finding lead by name: {str(e)}")
        
        if not lead_id:
            print(f"⚠️ No lead found with email={email}, phone={phone}, name={name}")
        
        # Prepare data for storage - only include columns that exist in table
        save_data = {
            'email': email,
            'drivers': data.get('drivers', []),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Add lead_id if found
        if lead_id:
            save_data['lead_id'] = lead_id
        
        print(f"💾 INSERT/UPDATE STEP - lead_id: {lead_id}, email: {email}, phone: {phone}")
        print(f"📦 Data to save keys: {list(save_data.keys())}")
        print(f"📦 Drivers count: {len(save_data.get('drivers', []))}")
        
        # Insert or update in clients_data table
        if email:
            print(f"💡 Saving client data by email: {email} (lead_id: {lead_id})")
            try:
                # Prefer to update by lead_id if found, else by email
                if lead_id:
                    result = supabase.table('clients_data').select('id').eq('lead_id', lead_id).limit(1).execute()
                    if result.data and len(result.data) > 0:
                        print(f"🔄 Existing record found for lead {lead_id}, updating...")
                        save_result = supabase.table('clients_data').update(save_data).eq('lead_id', lead_id).execute()
                        print(f"✅ Updated existing client data for lead {lead_id}")
                    else:
                        print(f"📝 No existing record for lead {lead_id}, inserting new...")
                        save_result = supabase.table('clients_data').insert(save_data).execute()
                        print(f"✅ Inserted new client data for lead {lead_id}")
                        if save_result.data:
                            print(f"   Inserted ID: {save_result.data[0].get('id')}")
                else:
                    # Always upsert by email if no lead_id
                    result = supabase.table('clients_data').select('id').eq('email', email).limit(1).execute()
                    if result.data and len(result.data) > 0:
                        print(f"🔄 Existing record found for email {email}, updating...")
                        save_result = supabase.table('clients_data').update(save_data).eq('email', email).execute()
                        print(f"✅ Updated client data by email {email}")
                    else:
                        print(f"📝 No existing record for email {email}, inserting new...")
                        save_result = supabase.table('clients_data').insert(save_data).execute()
                        print(f"✅ Inserted new client data by email {email}")
                        if save_result.data:
                            print(f"   Inserted ID: {save_result.data[0].get('id')}")
            except Exception as e:
                print(f"❌ Error saving client data: {str(e)}")
                import traceback
                traceback.print_exc()
                save_result = None
        else:
            print(f"❌ Cannot save - no email available in drivers")
            return jsonify({
                'success': False,
                'error': 'Cannot save without email'
            }), 400
        
        print(f"✅ Client data save operation completed")
        
        # Verify data was actually saved
        try:
            verify_result = supabase.table('clients_data').select('count', count='exact').execute()
            print(f"📊 Total clients_data rows in DB: {verify_result.count}")
        except Exception as e:
            print(f"⚠️ Could not verify save: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Client data saved successfully',
            'lead_id': lead_id,
            'email': email,
            'phone': phone
        }), 200
        
    except Exception as e:
        print(f"❌ Error saving client: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to save client: {str(e)}'
        }), 500


@app.route('/api/get-client-data/<query>', methods=['GET'])
def get_client_data(query):
    """Retrieve saved client data by email or lead ID"""
    try:
        print(f"📂 Retrieving client data for: {query}")
        
        # Try to find by lead_id first (if valid UUID format)
        try:
            if len(query) == 36 and query.count('-') == 4:  # UUID format check
                result = supabase.table('clients_data').select('*').eq('lead_id', query).limit(1).execute()
                if result.data and len(result.data) > 0:
                    print(f"✅ Found client data by lead_id: {query}")
                    return jsonify({
                        'success': True,
                        'data': result.data[0]
                    }), 200
        except Exception as e:
            print(f"⚠️ Error searching by lead_id: {str(e)}")
        
        # Try to find by email (primary search)
        try:
            result = supabase.table('clients_data').select('*').eq('email', query).limit(1).execute()
            if result.data and len(result.data) > 0:
                print(f"✅ Found client data by email: {query}")
                return jsonify({
                    'success': True,
                    'data': result.data[0]
                }), 200
        except Exception as e:
            print(f"⚠️ Error searching by email: {str(e)}")
        
        print(f"⚠️ No client data found for: {query}")
        return jsonify({
            'success': False,
            'error': 'No data found',
            'data': None
        }), 404
        
    except Exception as e:
        print(f"❌ Error retrieving client data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve client data: {str(e)}'
        }), 500



@app.route('/api/get-property-data/<query>', methods=['GET'])
def get_property_data(query):
    """Retrieve saved property data by email or lead ID"""
    try:
        print(f"📂 Retrieving property data for: {query}")
        
        # Try to find by email (primary search)
        try:
            result = supabase.table('properties_data').select('*').eq('email', query).limit(1).execute()
            if result.data and len(result.data) > 0:
                print(f"✅ Found property data by email: {query}")
                return jsonify({
                    'success': True,
                    'data': result.data[0]
                }), 200
        except Exception as e:
            print(f"⚠️ Error searching by email: {str(e)}")
        
        print(f"⚠️ No property data found for: {query}")
        return jsonify({
            'success': False,
            'error': 'No data found',
            'data': None
        }), 404
        
    except Exception as e:
        print(f"❌ Error retrieving property data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve property data: {str(e)}'
        }), 500


@app.route('/api/get-auto-data/<query>', methods=['GET'])
def get_auto_data(query):
    """Retrieve saved auto dashboard data by email"""
    try:
        print(f"🚗 Retrieving auto data for: {query}")

        # Try to find by lead_id first (if valid UUID format)
        try:
            if len(query) == 36 and query.count('-') == 4:  # UUID format check
                result = supabase.table('auto_data').select('*').eq('lead_id', query).limit(1).execute()
                if result.data and len(result.data) > 0:
                    print(f"✅ Found auto data by lead_id: {query}")
                    return jsonify({
                        'success': True,
                        'data': result.data[0]
                    }), 200
        except Exception as e:
            print(f"⚠️ Error searching auto data by lead_id: {str(e)}")
        
        # Try to find by email
        try:
            result = supabase.table('auto_data').select('*').eq('email', query).limit(1).execute()
            if result.data and len(result.data) > 0:
                print(f"✅ Found auto data by email: {query}")
                return jsonify({
                    'success': True,
                    'data': result.data[0]
                }), 200
        except Exception as e:
            print(f"⚠️ Error searching auto data by email: {str(e)}")
        
        print(f"⚠️ No auto data found for: {query}")
        return jsonify({
            'success': False,
            'error': 'No data found',
            'data': None
        }), 404
        
    except Exception as e:
        print(f"❌ Error retrieving auto data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve auto data: {str(e)}'
        }), 500


@app.route('/api/save-property', methods=['POST'])
def save_property():
    """Save complete property data to Supabase linked to a lead"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"🏠 Saving property data to Supabase...")
        print(f"📊 Data received keys: {list(data.keys())}")
        
        # Get email to identify the lead
        email = None
        lead_id = None
        
        if data.get('customer') and isinstance(data['customer'], dict):
            email = data['customer'].get('email', '').strip().lower() if data['customer'].get('email') else None
            print(f"✓ Extracted email: {email}")
        
        if not email:
            print(f"⚠️ No email provided in customer data")
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Find lead by email
        if email:
            try:
                result = supabase.table('leads').select('id').eq('email', email).limit(1).execute()
                if result.data and len(result.data) > 0:
                    lead_id = result.data[0]['id']
                    print(f"✅ Found lead by email {email}: {lead_id}")
            except Exception as e:
                print(f"⚠️ Error finding lead by email: {str(e)}")
        
        # Prepare data for storage - WORKAROUND for PostgREST schema cache issue
        # Save all dual-mode data in the 'customer' JSONB column to avoid schema cache conflicts
        combined_data = {
            'viewMode': data.get('viewMode', 'Homeowners'),
            'homeowners': data.get('homeowners', {}),
            'tenants': data.get('tenants', {}),
        }
        
        # Use properties column for backwards compatibility, customer column for dual-mode data
        save_data = {
            'email': email,
            'properties': data.get('properties', []),  # For backwards compatibility
            'customer': combined_data,  # Store all dual-mode data here (JSONB works fine)
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Add lead_id if found
        if lead_id:
            save_data['lead_id'] = lead_id
        
        print(f"\n{'='*80}")
        print(f"💾 INSERT/UPDATE STEP - Saving property data for email: {email}")
        print(f"{'='*80}")
        print(f"📦 Data to save keys: {list(save_data.keys())}")
        print(f"\n📋 DETAILED PAYLOAD RECEIVED:")
        print(f"   viewMode: {combined_data.get('viewMode')}")
        print(f"   homeowners exists: {bool(data.get('homeowners'))}")
        if data.get('homeowners'):
            print(f"      - homeowners.customer keys: {list(data['homeowners'].get('customer', {}).keys())}")
            print(f"      - homeowners.properties count: {len(data['homeowners'].get('properties', []))}")
        print(f"   tenants exists: {bool(data.get('tenants'))}")
        if data.get('tenants'):
            print(f"      - tenants.customer keys: {list(data['tenants'].get('customer', {}).keys())}")
            print(f"      - tenants.properties count: {len(data['tenants'].get('properties', []))}")
        
        print(f"\n🏠 Saving Homeowners data: {bool(data.get('homeowners'))}")
        if data.get('homeowners'):
            print(f"   Homeowners customer: {json.dumps(data['homeowners'].get('customer', {}), indent=2)[:200]}...")
        print(f"🏢 Saving Tenants data: {bool(data.get('tenants'))}")
        if data.get('tenants'):
            print(f"   Tenants customer: {json.dumps(data['tenants'].get('customer', {}), indent=2)[:200]}...")
        
        # Insert or update in properties_data table
        if email:
            print(f"💡 Saving property data by email: {email}")
            try:
                # Check if record exists
                result = supabase.table('properties_data').select('id').eq('email', email).limit(1).execute()
                if result.data and len(result.data) > 0:
                    print(f"🔄 Existing record found for email {email}, updating...")
                    save_result = supabase.table('properties_data').update(save_data).eq('email', email).execute()
                    print(f"✅ Updated existing property data for email {email}")
                    
                    # Verify what was saved
                    verify_result = supabase.table('properties_data').select('*').eq('email', email).limit(1).execute()
                    if verify_result.data:
                        saved_record = verify_result.data[0]
                        saved_customer = saved_record.get('customer', {})
                        print(f"\n📋 VERIFICATION - What was actually saved to database:")
                        print(f"   Record ID: {saved_record.get('id')}")
                        print(f"   Stored in customer column:")
                        print(f"      - Has viewMode: {bool(saved_customer.get('viewMode'))}")
                        print(f"      - Has homeowners: {bool(saved_customer.get('homeowners'))}")
                        print(f"      - Has tenants: {bool(saved_customer.get('tenants'))}")
                        if saved_customer.get('tenants'):
                            print(f"      - Saved tenants data: {json.dumps(saved_customer.get('tenants', {}), indent=2)[:300]}...")
                else:
                    print(f"📝 No existing record for email {email}, inserting new...")
                    save_result = supabase.table('properties_data').insert(save_data).execute()
                    print(f"✅ Inserted new property data for email {email}")
                    if save_result.data:
                        print(f"   Inserted ID: {save_result.data[0].get('id')}")
                        # Verify what was saved
                        verify_result = supabase.table('properties_data').select('*').eq('email', email).limit(1).execute()
                        if verify_result.data:
                            saved_record = verify_result.data[0]
                            saved_customer = saved_record.get('customer', {})
                            print(f"\n📋 VERIFICATION - What was actually saved to database:")
                            print(f"   Record ID: {saved_record.get('id')}")
                            print(f"   Stored in customer column:")
                            print(f"      - Has viewMode: {bool(saved_customer.get('viewMode'))}")
                            print(f"      - Has homeowners: {bool(saved_customer.get('homeowners'))}")
                            print(f"      - Has tenants: {bool(saved_customer.get('tenants'))}")
                            if saved_customer.get('tenants'):
                                print(f"      - Saved tenants data: {json.dumps(saved_customer.get('tenants', {}), indent=2)[:300]}...")
            except Exception as e:
                print(f"❌ Error saving property data: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({'success': False, 'error': f'Failed to save: {str(e)}'}), 500
        else:
            print(f"❌ Cannot save - no email available")
            return jsonify({
                'success': False,
                'error': 'Cannot save without email'
            }), 400
        
        print(f"✅ Property data save operation completed")
        
        return jsonify({
            'success': True,
            'message': 'Property data saved successfully',
            'lead_id': lead_id,
            'email': email
        }), 200
        
    except Exception as e:
        print(f"❌ Error saving property: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to save property: {str(e)}'
        }), 500


@app.route('/api/save-auto-data', methods=['POST'])
def save_auto_data():
    """Save auto dashboard data to Supabase linked to a lead"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"🚗 Saving auto dashboard data to Supabase...")
        print(f"📊 Data received keys: {list(data.keys())}")
        
        # Get email from customer data
        email = None
        lead_id = None
        
        if data.get('email'):
            email = data['email'].strip().lower()
            print(f"✓ Extracted email: {email}")
        
        if not email:
            print(f"⚠️ No email provided")
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Find lead by email
        if email:
            try:
                result = supabase.table('leads').select('id').eq('email', email).limit(1).execute()
                if result.data and len(result.data) > 0:
                    lead_id = result.data[0]['id']
                    print(f"✅ Found lead by email {email}: {lead_id}")
            except Exception as e:
                print(f"⚠️ Error finding lead by email: {str(e)}")
        
        # Prepare data for storage
        save_data = {
            'email': email,
            'auto_data': data.get('auto_data', {}),
            'customer': data.get('customer', {}),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Add lead_id if found
        if lead_id:
            save_data['lead_id'] = lead_id
        
        print(f"💾 INSERT/UPDATE STEP - lead_id: {lead_id}, email: {email}")
        print(f"📦 Data to save keys: {list(save_data.keys())}")
        
        # Insert or update in auto_data table
        if email:
            print(f"💡 Saving auto data by email: {email}")
            try:
                # Check if record exists
                result = supabase.table('auto_data').select('id').eq('email', email).limit(1).execute()
                if result.data and len(result.data) > 0:
                    print(f"🔄 Existing record found for email {email}, updating...")
                    save_result = supabase.table('auto_data').update(save_data).eq('email', email).execute()
                    print(f"✅ Updated existing auto data for email {email}")
                else:
                    print(f"📝 No existing record for email {email}, inserting new...")
                    save_result = supabase.table('auto_data').insert(save_data).execute()
                    print(f"✅ Inserted new auto data for email {email}")
                    if save_result.data:
                        print(f"   Inserted ID: {save_result.data[0].get('id')}")
            except Exception as e:
                print(f"❌ Error saving auto data: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({'success': False, 'error': f'Failed to save: {str(e)}'}), 500
        else:
            print(f"❌ Cannot save - no email available")
            return jsonify({
                'success': False,
                'error': 'Cannot save without email'
            }), 400
        
        print(f"✅ Auto data save operation completed")
        
        return jsonify({
            'success': True,
            'message': 'Auto data saved successfully',
            'lead_id': lead_id,
            'email': email
        }), 200
        
    except Exception as e:
        print(f"❌ Error saving auto data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to save auto data: {str(e)}'
        }), 500


# ========== ZOHO SIGNER INTEGRATION ==========

import uuid
from werkzeug.utils import secure_filename

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/process-form', methods=['POST'])
def process_form():
    """
    Process ZohoSigner form submission
    Accepts: PDF file + form fields (multipart/form-data)
    Returns: form_id and status
    """
    try:
        # Check if PDF file is present
        if 'pdf_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No PDF file provided'
            }), 400
        
        pdf_file = request.files['pdf_file']
        
        if pdf_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(pdf_file.filename):
            return jsonify({
                'success': False,
                'error': 'Only PDF files are allowed'
            }), 400
        
        # Extract form data from request
        form_name = request.form.get('form_name', 'Unknown Form')
        signer_email = request.form.get('signer_email', '')
        signer_name = request.form.get('signer_name', '')
        broker_email = request.form.get('broker_email', '')
        broker_name = request.form.get('broker_name', '')
        
        # Generate unique form_id
        form_id = str(uuid.uuid4())
        
        # Create secure filename
        original_filename = secure_filename(pdf_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_filename = f"{form_id}_{timestamp}_{original_filename}"
        file_path = os.path.join(UPLOAD_FOLDER, saved_filename)
        
        # Save PDF file
        pdf_file.save(file_path)
        print(f"✅ PDF saved to: {file_path}")
        
        # Insert record into Supabase zoho_forms table
        zoho_form_data = {
            'form_id': form_id,
            'form_name': form_name,
            'signer_email': signer_email,
            'signer_name': signer_name,
            'broker_email': broker_email,
            'broker_name': broker_name,
            'original_file_path': file_path,
            'saved_filename': saved_filename,
            'status': 'pending_signature',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Save to Supabase
        result = supabase.table('zoho_forms').insert(zoho_form_data).execute()
        print(f"✅ Form record saved to Supabase: {form_id}")
        
        # Return success response
        return jsonify({
            'success': True,
            'form_id': form_id,
            'status': 'pending_signature',
            'message': 'Form processed successfully'
        }), 200
        
    except Exception as e:
        print(f"❌ Error processing form: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to process form: {str(e)}'
        }), 500


@app.route('/zoho-webhook', methods=['POST', 'GET'])
def zoho_webhook():
    """
    Placeholder for Zoho signature webhook
    Will be used to receive signature completion notifications from Zoho
    """
    try:
        if request.method == 'GET':
            return jsonify({'status': 'webhook endpoint ready'}), 200
        
        if request.method == 'POST':
            webhook_data = request.json or request.form
            print(f"📨 Zoho webhook received: {webhook_data}")
            
            # TODO: Process webhook payload when Zoho integration is enabled
            # - Update form status based on signature completion
            # - Trigger notifications
            # - Archive completed documents
            
            return jsonify({'success': True, 'status': 'webhook received'}), 200
    
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/oauth/callback', methods=['GET'])
def oauth_callback():
    """
    Handle OAuth2 authorization code exchange with Zoho
    """
    import sys
    try:
        # Get the code - Zoho may add extra params like location and accounts-server
        auth_code = request.args.get('code')
        error = request.args.get('error')
        
        # Debug logging with immediate flush
        msg = f"\n{'='*60}\n🔐 OAuth Callback Received\nCode: {auth_code}\nError: {error}\nAll params: {request.args}\n{'='*60}\n"
        print(msg, flush=True)
        sys.stdout.flush()

        if error:
            return jsonify({'success': False, 'error': f'Zoho auth error: {error}', 'error_param': error}), 400

        if not auth_code:
            return jsonify({'success': False, 'error': 'Missing authorization code'}), 400

        token_url = 'https://accounts.zoho.in/oauth/v2/token'
        
        # **IMPORTANT**: Use redirect_uri WITHOUT extra parameters (without ?location=in etc)
        payload = {
            'code': auth_code,
            'client_id': ZOHO_CLIENT_ID,
            'client_secret': ZOHO_CLIENT_SECRET,
            'redirect_uri': ZOHO_REDIRECT_URI,  # This must match exactly what was configured
            'grant_type': 'authorization_code'
        }
        
        print(f"📤 Sending token request...\nRedirect URI: {ZOHO_REDIRECT_URI}\n", flush=True)
        sys.stdout.flush()

        response = requests.post(token_url, data=payload, timeout=30)
        
        print(f"📥 Status: {response.status_code}\nResponse: {response.text[:500]}\n", flush=True)
        sys.stdout.flush()

        try:
            data = response.json()
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid JSON response from Zoho', 'raw': response.text[:500]}), 502

        # Check for tokens
        if 'access_token' in data:
            print(f"✅ ACCESS TOKEN: {data.get('access_token')[:30]}...\n", flush=True)
        if 'refresh_token' in data:
            print(f"✅ REFRESH TOKEN: {data.get('refresh_token')[:30]}...\n", flush=True)
        else:
            print(f"⚠️ No refresh_token in response\n", flush=True)
            
        sys.stdout.flush()
        return jsonify(data), response.status_code
        
    except Exception as e:
        import traceback
        print(f"❌ Error: {str(e)}\n{traceback.format_exc()}\n", flush=True)
        sys.stdout.flush()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== INITIALIZATION ==========

if __name__ == '__main__':
    # Create tables if they don't exist
    try:
        # Check if leads table exists, if not this will fail gracefully
        supabase.table('leads').select('*').limit(1).execute()
    except:
        print("Note: Ensure 'leads' table exists in Supabase")
    
    port = int(os.getenv('FLASK_PORT', 5000))
    # Disable use_reloader to avoid issues on Windows
    app.run(debug=True, port=port, host='0.0.0.0', use_reloader=False)
