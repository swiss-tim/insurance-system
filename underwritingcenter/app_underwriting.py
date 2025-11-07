"""
Guidewire Underwriting Center - Interactive Demo
=================================================
A high-fidelity prototype demonstrating the AI-powered underwriting workflow.

This demo showcases:
- Dashboard with KPIs and submission management
- AI-powered document summarization
- Automated proposal generation and analysis
- Interactive quote comparison
- Complete click-through story for Floor & Decor Outlets (SUB-2026-001)
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
import sys
import os
import time
import datetime
import base64
import textwrap
import re
import json

# Add parent directory to path to import database modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database_queries import get_session
from seed_database import Submission, Party, Quote
from market_config import detect_market, get_market_content, format_currency

# === HELPER FUNCTIONS FOR LOADING MODAL ===

@st.cache_data  # Cache the file conversion
def get_gif_as_base64(file_path):
    """Reads a GIF file and returns it as a Base64 encoded string."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"Error reading GIF file: {e}")
        return None

def get_modal_html(gif_base64, text):
    """
    Generates JavaScript that appends/updates the loading modal in the document body.
    Ensures the overlay remains centered in the viewport even when scrolling.
    """
    safe_text = json.dumps(text)
    return f"""
    <script>
    (function() {{
        const overlayId = 'gw-loading-overlay';
        const textId = 'gw-loading-text';
        const doc = window.parent && window.parent.document ? window.parent.document : document;
        let overlay = doc.getElementById(overlayId);

        if (!overlay) {{
            overlay = doc.createElement('div');
            overlay.id = overlayId;
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.right = '0';
            overlay.style.bottom = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
            overlay.style.zIndex = '9998';
            overlay.style.display = 'flex';
            overlay.style.alignItems = 'center';
            overlay.style.justifyContent = 'center';
            overlay.style.padding = '20px';

            const modal = doc.createElement('div');
            modal.id = 'gw-loading-modal';
            modal.style.backgroundColor = '#ffffff';
            modal.style.padding = '30px';
            modal.style.borderRadius = '8px';
            modal.style.width = '320px';
            modal.style.textAlign = 'center';
            modal.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.3)';
            modal.style.zIndex = '9999';

            const img = doc.createElement('img');
            img.src = 'data:image/gif;base64,{gif_base64}';
            img.alt = 'loading...';
            img.style.width = '80px';
            img.style.marginBottom = '20px';

            const textEl = doc.createElement('p');
            textEl.id = textId;
            textEl.style.margin = '0';
            textEl.style.color = '#333';
            textEl.style.fontSize = '1rem';
            textEl.textContent = {safe_text};

            modal.appendChild(img);
            modal.appendChild(textEl);
            overlay.appendChild(modal);
            doc.body.appendChild(overlay);
        }} else {{
            const textEl = (window.parent && window.parent.document ? window.parent.document : document).getElementById(textId);
            if (textEl) {{
                textEl.textContent = {safe_text};
            }}
        }}
    }})();
    </script>
    """

def show_loading_modal(steps, duration_per_step=1.5):
    """
    Display a loading modal with animated GIF and changing text messages.
    
    Args:
        steps: List of text messages to display sequentially
        duration_per_step: Duration (in seconds) to display each step
    
    Returns:
        The placeholder object (for potential cleanup)
    """
    # Get the GIF as base64
    gif_path = os.path.join(os.path.dirname(__file__), 'logo-moving.gif')
    gif_base64 = get_gif_as_base64(gif_path)
    
    if not gif_base64:
        return None
    
    try:
        # Loop through each step and update the overlay text
        for text in steps:
            modal_html = get_modal_html(gif_base64, text)
            components.html(modal_html, height=0, width=0)
            time.sleep(duration_per_step)
    finally:
        # Remove overlay after completion
        components.html(
            """
            <script>
            (function() {
                const doc = window.parent && window.parent.document ? window.parent.document : document;
                const overlay = doc.getElementById('gw-loading-overlay');
                if (overlay) {
                    overlay.remove();
                }
            })();
            </script>
            """,
            height=0,
            width=0
        )

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Guidewire Underwriting Center",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CUSTOM CSS ===
st.markdown("""
<style>
    /* Global default font size - override Streamlit's default 0.875rem */
    * {
        font-size: 1rem !important;
    }
    
    /* Ensure 'My Submissions' header is 1.25rem */
    .my-submissions-header,
    h3.my-submissions-header {
        font-size: 1.25rem !important;
    }
    
    /* Align selectbox and button on the same level */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-end !important;
    }
    
    /* Remove extra spacing from selectbox label area when label is empty */
    [data-testid="stSelectbox"] label {
        display: none !important;
    }
    
    /* Align button with selectbox */
    [data-testid="column"] [data-testid="stButton"],
    [data-testid="column"] [data-testid="stSelectbox"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Ensure tables/dataframes use 1rem font size - comprehensive targeting with high specificity */
    [data-testid="stDataFrame"] table,
    [data-testid="stDataFrame"] td,
    [data-testid="stDataFrame"] th,
    [data-testid="stDataFrame"] tbody,
    [data-testid="stDataFrame"] thead,
    [data-testid="stDataFrame"] tr,
    [data-testid="stDataFrame"] *,
    [data-testid="stDataFrame"] table td,
    [data-testid="stDataFrame"] table th,
    [data-testid="stDataFrame"] table tbody td,
    [data-testid="stDataFrame"] table tbody th,
    [data-testid="stDataFrame"] table thead td,
    [data-testid="stDataFrame"] table thead th,
    .stDataFrame table,
    .stDataFrame td,
    .stDataFrame th,
    .stDataFrame tbody,
    .stDataFrame thead,
    .stDataFrame tr,
    .stDataFrame *,
    .stDataFrame table td,
    .stDataFrame table th,
    .stDataFrame table tbody td,
    .stDataFrame table tbody th,
    table,
    table td,
    table th,
    table tbody,
    table thead,
    table tr,
    table tbody td,
    table tbody th,
    table thead td,
    table thead th,
    /* Target all text content in table cells */
    td *,
    th *,
    table td *,
    table th *,
    /* More specific targeting for Streamlit dataframes */
    .main [data-testid="stDataFrame"] table,
    .main [data-testid="stDataFrame"] td,
    .main [data-testid="stDataFrame"] th,
    .main table,
    .main table td,
    .main table th,
    [data-testid="stAppViewContainer"] [data-testid="stDataFrame"] table,
    [data-testid="stAppViewContainer"] [data-testid="stDataFrame"] td,
    [data-testid="stAppViewContainer"] [data-testid="stDataFrame"] th {
        font-size: 1rem !important;
    }
    
    /* Override any inline styles on table elements */
    table[style],
    td[style],
    th[style],
    [data-testid="stDataFrame"] table[style],
    [data-testid="stDataFrame"] td[style],
    [data-testid="stDataFrame"] th[style] {
        font-size: 1rem !important;
    }
    
    /* Altair/Vega-Lite chart axis labels - set to 0.75rem (12px) */
    /* Target all SVG text elements in chart containers - axis labels */
    [data-testid="stVegaLiteChart"] svg text,
    .stVegaLiteChart svg text,
    .vega-embed svg text,
    svg.vega text {
        font-size: 0.75rem !important;
    }
    
    /* Ensure tabs use 1rem font size */
    [data-testid="stTabs"] button,
    [data-testid="stTabs"] [role="tab"],
    .stTabs button,
    .stTabs [role="tab"] {
        font-size: 1rem !important;
    }
    
    /* Global styles */
    .main {
        background-color: #f8f9fa;
    }
    
    /* KPI cards */
    .kpi-card {
        background: #1a1a1a;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        text-align: center;
    }
    
    .kpi-title {
        color: #d1d5db;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .kpi-value {
        font-size: 2.5rem !important;
        font-weight: bold;
        color: #ffffff;
        margin: 0.5rem 0;
    }
    
    .kpi-delta {
        color: #10b981;
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: 600;
    }
    
    .status-triaged {
        background-color: #dc2626;
        color: white;
    }
    
    .status-in-review {
        background-color: #ea580c;
        color: white;
    }
    
    .status-quoted {
        background-color: #2563eb;
        color: white;
    }
    
    .status-bound {
        background-color: #059669;
        color: white;
    }
    
    .status-cleared {
        background-color: #6b7280;
        color: white;
    }
    
    .status-declined {
        background-color: #991b1b;
        color: white;
    }
    
    /* Appetite badges */
    .appetite-high {
        background-color: #10b981;
        color: white;
        font-weight: 600;
    }
    
    .appetite-medium {
        background-color: #f59e0b;
        color: white;
        font-weight: 600;
    }
    
    .appetite-low {
        background-color: #ef4444;
        color: white;
        font-weight: 600;
    }
    
    /* Section headers - keep larger size for headers like 'proposal details' */
    .section-header {
        font-size: 1.25rem !important;
        font-weight: 600;
        color: #1f2937;
        margin: 1.5rem 0 1rem 0;
    }
    
    /* AI summary box */
    .ai-summary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Quote cards */
    .quote-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #1f2937;
    }
    
    .quote-card h2 {
        color: #1f2937 !important;
        margin: 0;
    }
    
    .quote-card p {
        color: #4b5563 !important;
        margin: 0.5rem 0;
    }
    
    .quote-card hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 1rem 0;
    }
    
    .quote-card-selected {
        border-color: #5a9fb8;
        box-shadow: 0 0 0 3px rgba(90, 159, 184, 0.1);
    }
    
    .quote-card-selected h2 {
        color: #5a9fb8 !important;
    }
    
    /* Loading overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    }
    
    .loading-content {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        text-align: center;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: #1d4ed8;
    }
    
    /* Reduce side border space by 80% - use negative margins only */
    /* Streamlit default padding is ~5rem (80px), reduce to ~1rem (16px) = 80% reduction */
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        max-width: calc(100% + 8rem) !important;
        width: calc(100% + 8rem) !important;
    }
    
    /* Wide layout specific overrides - reduce both sides */
    [data-testid="stAppViewContainer"][data-layout="wide"] .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        max-width: calc(100% + 8rem) !important;
    }
    
    /* Target the wide layout wrapper - reduce both sides */
    .stApp[data-layout="wide"] .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        max-width: calc(100% + 8rem) !important;
    }
    
    [data-testid="stAppViewContainer"] {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        max-width: calc(100% + 8rem) !important;
    }
    
    [data-testid="stAppViewContainer"] > .main {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        max-width: calc(100% + 8rem) !important;
        width: calc(100% + 8rem) !important;
    }
    
    [data-testid="stAppViewBlockContainer"] {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        max-width: calc(100% + 8rem) !important;
        width: calc(100% + 8rem) !important;
    }
    
    /* Target root app container */
    .stApp {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    
    .stApp > div {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
    }
    
    /* Target element containers - remove their padding */
    .element-container {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    
    /* Override Streamlit's wide layout max-width constraints - reduce both sides */
    .stApp[data-layout="wide"] .main .block-container,
    [data-layout="wide"] .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        max-width: calc(100% + 8rem) !important;
    }
    
    /* Target any divs that might have max-width constraints */
    .main > div {
        max-width: 100% !important;
    }
    
    /* Ensure full width for wide layout - reduce both sides */
    [data-layout="wide"] [data-testid="stAppViewContainer"] {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        max-width: calc(100% + 8rem) !important;
    }
    
    /* More aggressive padding removal - target all nested divs */
    .main .block-container > div {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    
    /* Target Streamlit's column system */
    .main .block-container [data-testid="column"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    
    /* Target all direct children of main - reduce both sides */
    .main > div {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
    }
    
    /* Override any margin that creates space */
    .main .block-container {
        margin-left: -4rem !important;
        margin-right: -4rem !important;
    }
    
    /* Target the actual content wrapper - reduce both sides */
    [data-testid="stAppViewContainer"] .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
    }
    
    /* Remove padding from all nested containers */
    .main .block-container [class*="container"],
    .main .block-container [class*="Container"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    
    /* Remove footer - simple approach */
    footer {
        display: none !important;
    }
    
    footer[data-testid="stFooter"] {
        display: none !important;
    }
    
    .stApp footer {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# === DATABASE INITIALIZATION ===
# Initialize database on first run or if missing
@st.cache_resource
def initialize_database():
    """Initialize the database with German SHUK demo data (default)"""
    try:
        # Add src to path if not already there
        src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Import necessary modules
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session
        from seed_database import Base, Party
        from seed_data_german import seed_german_data
        
        # Create database and tables
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pnc_demo.db'))
        engine = create_engine(f'sqlite:///{db_path}')
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        # Check if database is already populated
        session = Session(engine)
        party_count = session.query(Party).count()
        
        if party_count == 0:
            # Database is empty, seed it with German market data (default)
            seed_german_data(session)
        
        session.close()
        return True
    except Exception as e:
        st.error(f"❌ Failed to initialize database: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return False

# Try to initialize database
try:
    initialize_database()
except Exception as e:
    st.error(f"Database initialization error: {e}")

# === SESSION STATE INITIALIZATION ===
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = 'dashboard'

if 'selected_submission' not in st.session_state:
    st.session_state.selected_submission = None

# Dashboard KPIs state
if 'dashboard_kpis' not in st.session_state:
    st.session_state.dashboard_kpis = {
        'turnaround_time': 4.1,
        'hit_ratio': 32,
        'earned_premium': 1.65,
        'loss_ratio': 49
    }

# Dashboard chart data
if 'chart_data' not in st.session_state:
    st.session_state.chart_data = {
        'hit_ratio_q4': 32,
        'premium_q4': 1.65
    }

# Submission detail state (for Floor & Decor demo)
if 'submission_state' not in st.session_state:
    # Default to German market endorsements (will be updated when viewing specific submission)
    default_market_content = get_market_content('german')
    all_default_endorsements = {**default_market_content['endorsements']['base'], 
                                **default_market_content['endorsements']['recommended']}
    
    st.session_state.submission_state = {
        'status': 'Triaged',
        'completeness': 74,
        'priority_score': 4.8,
        'risk_appetite': 'High',
        'is_summary_visible': False,
        'is_proposal_visible': False,
        'is_recs_visible': False,
        'is_comparison_visible': False,
        'quotes': [],  # Will contain 'base' and/or 'generated'
        'endorsements': all_default_endorsements,
        'widget_key_suffix': '',  # Used to force widget refresh
        'bind_available': False,
        'bind_suppressed': False
    }

# Loading modal state
if 'show_loading' not in st.session_state:
    st.session_state.show_loading = False
    st.session_state.loading_message = ""

# Chatbot state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'show_welcome' not in st.session_state:
    st.session_state.show_welcome = True

# === HELPER FUNCTIONS ===

def show_loading(message, duration=2):
    """Display a loading modal for specified duration"""
    st.session_state.show_loading = True
    st.session_state.loading_message = message
    time.sleep(duration)
    st.session_state.show_loading = False
    st.rerun()

def get_status_badge(status):
    """Return formatted status badge with emoji"""
    status_upper = status.upper()
    if status_upper == 'TRIAGED':
        return '🔴 Triaged'
    elif status_upper == 'IN REVIEW':
        return '🟠 In Review'
    elif status_upper == 'QUOTED':
        return '🔵 Quoted'
    elif status_upper == 'BOUND':
        return '🟢 Bound'
    elif status_upper == 'CLEARED':
        return '⚪ Cleared'
    elif status_upper == 'DECLINED':
        return '⚫ Declined'
    else:
        return status

def get_appetite_badge(appetite):
    """Return formatted appetite badge with emoji"""
    appetite_upper = appetite.upper()
    if appetite_upper == 'HIGH':
        return '🟢 High'
    elif appetite_upper == 'MEDIUM':
        return '🟡 Medium'
    elif appetite_upper == 'LOW':
        return '🔴 Low'
    else:
        return appetite

# === DATABASE FUNCTIONS ===

def get_all_submissions():
    """Fetch all submissions from database"""
    session = get_session()
    submissions = session.query(Submission).join(Party, Submission.insured_party_id == Party.id).add_columns(
        Submission.id,
        Submission.submission_number,
        Submission.status,
        Submission.completeness,
        Submission.priority_score,
        Submission.risk_appetite,
        Submission.broker_tier,
        Submission.effective_date,
        Submission.accepted,
        Party.name.label('account_name')
    ).all()
    
    # Also get broker info
    result_data = []
    for sub in submissions:
        broker_name = ""
        if sub.Submission.broker_party_id:
            broker = session.query(Party).get(sub.Submission.broker_party_id)
            if broker:
                broker_name = broker.name
        
        result_data.append({
            'id': sub.id,
            'submission_number': sub.submission_number,
            'account_name': sub.account_name,
            'status': sub.status,
            'broker': broker_name,
            'broker_tier': sub.broker_tier or '',
            'effective_date': sub.effective_date,
            'priority_score': sub.priority_score,
            'completeness': sub.completeness,
            'risk_appetite': sub.risk_appetite or '',
            'accepted': sub.accepted if hasattr(sub, 'accepted') else False
        })
    
    session.close()
    return result_data

def get_submission_details(submission_id):
    """Fetch detailed submission information"""
    session = get_session()
    submission = session.query(Submission).get(submission_id)
    if not submission:
        session.close()
        return None
    
    account = session.query(Party).get(submission.insured_party_id)
    broker = session.query(Party).get(submission.broker_party_id) if submission.broker_party_id else None
    
    result = {
        'submission': submission,
        'account': account,
        'broker': broker
    }
    
    session.close()
    return result

def update_submission_status(submission_id, status, completeness=None):
    """Update submission status and completeness in database"""
    session = get_session()
    try:
        submission = session.query(Submission).get(submission_id)
        if submission:
            submission.status = status
            if completeness is not None:
                submission.completeness = completeness
            session.commit()
            session.close()
            return True
    except Exception as e:
        session.rollback()
        session.close()
        st.error(f"Error updating submission: {e}")
        return False
    return False

def update_submission_accepted(submission_id, accepted=True):
    """Update submission accepted field in database"""
    session = get_session()
    try:
        submission = session.query(Submission).get(submission_id)
        if submission:
            submission.accepted = accepted
            session.commit()
            session.close()
            return True
    except Exception as e:
        session.rollback()
        session.close()
        st.error(f"Error updating submission accepted: {e}")
        return False
    return False

def reset_demo_database(market='german'):
    """Reset the database to demo state by running seed script with market selection"""
    import subprocess
    import sys
    
    # Get paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    seed_script = os.path.join(project_root, "src", "seed_database.py")
    
    # Run seed script with market parameter
    result = subprocess.run(
        [sys.executable, seed_script, market],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    if result.returncode == 0:
        market_name = "German SHUK" if market == 'german' else "U.S. Workers' Compensation"
        return True, f"Database reset successfully with {market_name} data! ✨"
    else:
        return False, result.stderr

# === SCREEN COMPONENTS ===

def render_loading_modal():
    """Render loading modal if active"""
    if st.session_state.show_loading:
        st.markdown(f"""
        <div class="loading-overlay">
            <div class="loading-content">
                <h3>⏳ {st.session_state.loading_message}</h3>
                <p>Please wait...</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def stream_text(text, delay=0.02):
    """Stream text character by character for a more dynamic feel"""
    placeholder = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        placeholder.markdown(displayed_text)
        time.sleep(delay)
    return placeholder

def render_chatbot_sidebar():
    """Render the AI underwriting assistant chatbot in the sidebar with popover-style features"""
    # Add CSS for sidebar chat - Guidewire styling
    st.markdown("""
    <style>
    /* Style sidebar chat - match header colors, minimize all padding */
    section[data-testid="stSidebar"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        background-color: #3c5c6c !important;
        padding: 0 !important;
        padding-left: 40px !important;
        padding-right: 0px !important;
        padding-bottom: 0 !important;
        margin: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Style sidebar content area - remove all padding, especially bottom */
    section[data-testid="stSidebar"] > div {
        background-color: #3c5c6c !important;
        padding: 0 !important;
        padding-bottom: 0 !important;
        margin: 0 !important;
        margin-bottom: 0 !important;
    }
    
    section[data-testid="stSidebar"] > div > div {
        background-color: #3c5c6c !important;
        padding: 0 !important;
        padding-bottom: 0 !important;
        margin: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Remove padding from sidebar content wrapper */
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding: 0 !important;
        padding-bottom: 0 !important;
        margin: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Style scrollable container - remove padding and outline, especially bottom */
    section[data-testid="stSidebar"] [data-testid="element-container"] {
        background-color: #3c5c6c !important;
        padding: 0 !important;
        padding-bottom: 0 !important;
        margin: 0 !important;
        margin-bottom: 0 !important;
        outline: none !important;
        border: none !important;
    }
    
    section[data-testid="stSidebar"] [data-baseweb="block"] {
        background-color: #3c5c6c !important;
        padding: 0 !important;
        padding-bottom: 0 !important;
        margin: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Remove padding from container, especially bottom */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding: 0 !important;
        padding-bottom: 0 !important;
        margin: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Minimize padding in scrollable area - target container with height */
    /* Increase left padding to prevent text cutoff */
    section[data-testid="stSidebar"] [data-testid="element-container"][style*="height"] {
        padding-left: 0px !important;
        padding-right: 0px !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Remove any borders/outlines from containers */
    section[data-testid="stSidebar"] [data-testid="element-container"],
    section[data-testid="stSidebar"] [data-baseweb="block"],
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Target the scrollable container specifically - increase left padding to prevent cutoff */
    section[data-testid="stSidebar"] div[style*="overflow"] {
        padding-left: 0px !important;
        padding-right: 0px !important;
        padding-top: 0px !important;
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
        outline: none !important;
        border: none !important;
    }
    
    /* Remove bottom padding from form elements */
    section[data-testid="stSidebar"] form {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }
    
    section[data-testid="stSidebar"] [data-baseweb="form"] {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Increase padding on all sidebar content to prevent cutoff */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] ul,
    section[data-testid="stSidebar"] li {
        margin-left: 0px !important;
        margin-right: 0px !important;
    }
    
    /* Increase padding on chat input and disclaimer */
    section[data-testid="stSidebar"] [data-testid="stChatInput"] {
        margin-left: 0px !important;
        margin-right: 0px !important;
    }
    
    section[data-testid="stSidebar"] .sidebar-chat-disclaimer {
        margin-left: 20px !important;
        margin-right: 0px !important;
    }
    
    /* Style sidebar header - keep larger size for 'underwriting assistant' */
    section[data-testid="stSidebar"] h3 {
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        color: white !important;
        margin: 8px 8px 6px 8px !important;
        padding: 0 !important;
        line-height: 1.4 !important;
    }
    
    /* Style paragraphs and text - white on dark background, minimal spacing */
    section[data-testid="stSidebar"] p {
        margin: 0px 0 !important;
        color: white !important;
        line-height: 1.4 !important;
    }
    
    /* Style bullet points - minimal spacing */
    section[data-testid="stSidebar"] ul {
        margin: 0px 0 !important;
        padding-left: 0px !important;
        line-height: 1.4 !important;
    }
    
    section[data-testid="stSidebar"] li {
        margin: 2px 0 !important;
        color: white !important;
    }
    
    /* Style suggested questions header */
    section[data-testid="stSidebar"] p strong {
        color: white !important;
        font-weight: 600 !important;
        display: block !important;
        margin-bottom: 4px !important;
    }
    
    /* Improve welcome message styling - better spacing and formatting */
    /* Prevent word breaking in the middle of words - only break at word boundaries */
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] [data-testid="stChatMessageAssistant"] p {
        margin: 0.75rem 0 !important;
        line-height: 1.6 !important;
        color: white !important;
        word-wrap: normal !important;
        overflow-wrap: normal !important;
        white-space: normal !important;
        word-break: normal !important;
    }
    
    /* Ensure HTML divs in chat messages have proper styling - no word breaking, full width */
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] [data-testid="stChatMessageAssistant"] div {
        color: white !important;
        word-wrap: normal !important;
        overflow-wrap: normal !important;
        white-space: normal !important;
        word-break: normal !important;
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] [data-testid="stChatMessageAssistant"] div p {
        color: white !important;
        margin: 0.5rem 0 !important;
        line-height: 1.6 !important;
        word-wrap: normal !important;
        overflow-wrap: normal !important;
        white-space: normal !important;
        word-break: normal !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] [data-testid="stChatMessageAssistant"] div strong {
        color: white !important;
        font-weight: 700 !important;
        word-wrap: normal !important;
        overflow-wrap: normal !important;
        white-space: normal !important;
    }
    
    /* Keep bold text inline - no special breaking rules */
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] [data-testid="stChatMessageAssistant"] strong {
        display: inline !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] [data-testid="stChatMessageUser"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] [data-testid="stChatMessageAssistant"] {
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Style text in chat messages - minimal spacing, ensure full width */
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] p,
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] div {
        color: white !important;
        margin: 2px 0 !important;
        padding: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Style bullet points - indent wrapped text after the bullet */
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] ul {
        list-style-position: outside !important;
        padding-left: 1.5em !important;
        margin: 0.5rem 0 !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] li {
        margin: 0.25rem 0 !important;
        padding-left: 0.5em !important;
    }
    
    /* For bullet points in markdown text (lines starting with •) - hanging indent */
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] .bullet-point-line {
        display: block !important;
        text-indent: -1.2em !important;
        padding-left: 1.2em !important;
        margin: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        line-height: 1.4 !important;
    }
    
    /* Make avatars 80% smaller - target the avatar container */
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] > div:first-child {
        width: 16px !important;
        height: 16px !important;
        min-width: 16px !important;
        min-height: 16px !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] img,
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] svg {
        width: 16px !important;
        height: 16px !important;
        max-width: 16px !important;
        max-height: 16px !important;
    }
    
    /* Style buttons in sidebar chat - Guidewire styling */
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] button {
        font-size: 1rem !important;
        padding: 0.375rem 1rem !important;
        height: auto !important;
        min-height: 1.75rem !important;
        width: auto !important;
        min-width: 4rem !important;
        border-radius: 4px !important;
        border: 1px solid #3c5c6c !important;
        background-color: #3c5c6c !important;
        color: white !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Hover state for buttons */
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] button:hover {
        background-color: #4a6d7d !important;
        border-color: #4a6d7d !important;
        cursor: pointer !important;
    }
    
    /* Active/pressed state */
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] button:active {
        background-color: #2d4a56 !important;
        border-color: #2d4a56 !important;
    }
    
    /* Apply Guidewire button styling to all buttons in main and detail pages */
    /* Target Streamlit buttons specifically with high specificity */
    .main button,
    [data-testid="stAppViewContainer"] > .main button,
    [data-testid="stAppViewBlockContainer"] button,
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-primary"],
    button[data-testid="baseButton-secondary"],
    button[data-testid="baseButton-primary"],
    .stButton > button,
    div[data-testid="stButton"] > button,
    [data-baseweb="button"] {
        font-size: 1rem !important;
        padding: 0.375rem 1rem !important;
        height: auto !important;
        min-height: 1.75rem !important;
        width: auto !important;
        min-width: 4rem !important;
        border-radius: 4px !important;
        border: 1px solid #3c5c6c !important;
        background-color: #3c5c6c !important;
        background: #3c5c6c !important;
        color: white !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Hover state for main/detail page buttons */
    .main button:hover,
    [data-testid="stAppViewContainer"] > .main button:hover,
    [data-testid="stAppViewBlockContainer"] button:hover,
    [data-testid="baseButton-secondary"]:hover,
    [data-testid="baseButton-primary"]:hover,
    button[data-testid="baseButton-secondary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    .stButton > button:hover,
    div[data-testid="stButton"] > button:hover,
    [data-baseweb="button"]:hover {
        background-color: #4a6d7d !important;
        background: #4a6d7d !important;
        border-color: #4a6d7d !important;
        cursor: pointer !important;
    }
    
    /* Active/pressed state for main/detail page buttons */
    .main button:active,
    [data-testid="stAppViewContainer"] > .main button:active,
    [data-testid="stAppViewBlockContainer"] button:active,
    [data-testid="baseButton-secondary"]:active,
    [data-testid="baseButton-primary"]:active,
    button[data-testid="baseButton-secondary"]:active,
    button[data-testid="baseButton-primary"]:active,
    .stButton > button:active,
    div[data-testid="stButton"] > button:active,
    [data-baseweb="button"]:active {
        background-color: #2d4a56 !important;
        background: #2d4a56 !important;
        border-color: #2d4a56 !important;
    }
    
    /* Focus state */
    .main button:focus,
    [data-testid="stAppViewContainer"] > .main button:focus,
    [data-testid="stAppViewBlockContainer"] button:focus,
    [data-baseweb="button"]:focus {
        outline: 2px solid #5a9fb8 !important;
        outline-offset: 2px !important;
    }
    
    /* Override Streamlit button text color and nested elements */
    .main button *,
    [data-testid="stAppViewContainer"] > .main button *,
    [data-testid="stAppViewBlockContainer"] button *,
    [data-baseweb="button"] *,
    .stButton > button *,
    div[data-testid="stButton"] > button * {
        color: white !important;
    }
    
    /* Override any inline styles that Streamlit might add */
    .main button[style],
    [data-testid="stAppViewContainer"] > .main button[style],
    [data-baseweb="button"][style] {
        background-color: #3c5c6c !important;
        background: #3c5c6c !important;
        border-color: #3c5c6c !important;
        color: white !important;
    }
    
    /* Prevent buttons from stretching to full width unless explicitly set */
    .main button:not([style*="width: 100%"]),
    [data-testid="stAppViewContainer"] > .main button:not([style*="width: 100%"]),
    [data-baseweb="button"]:not([style*="width: 100%"]) {
        width: auto !important;
        max-width: fit-content !important;
    }
    
    /* Ensure sidebar buttons keep their specific styling (higher specificity) */
    section[data-testid="stSidebar"] button {
        font-size: 1rem !important;
        padding: 0.375rem 1rem !important;
        height: auto !important;
        min-height: 1.75rem !important;
        width: auto !important;
        min-width: 4rem !important;
        border-radius: 4px !important;
        border: 1px solid #3c5c6c !important;
        background-color: #3c5c6c !important;
        color: white !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    section[data-testid="stSidebar"] button:hover {
        background-color: #4a6d7d !important;
        border-color: #4a6d7d !important;
        cursor: pointer !important;
    }
    
    section[data-testid="stSidebar"] button:active {
        background-color: #2d4a56 !important;
        border-color: #2d4a56 !important;
    }
    
    /* Style user avatar container - light green */
    section[data-testid="stSidebar"] [data-testid="stChatMessageUser"] > div:first-child {
        background-color: #86efac !important;
        border-radius: 50% !important;
    }
    
    /* Style chat input - minimal margins, no bottom padding, auto-grow */
    section[data-testid="stSidebar"] [data-testid="stChatInput"] {
        margin-top: 4px !important;
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Make chat input textarea auto-grow - one line initially, grows with content */
    section[data-testid="stSidebar"] [data-testid="stChatInput"] textarea {
        min-height: 1.5rem !important;
        max-height: 200px !important;
        height: auto !important;
        resize: none !important;
        overflow-y: auto !important;
        line-height: 1.5 !important;
    }
    
    /* Target the input container to allow growth */
    section[data-testid="stSidebar"] [data-testid="stChatInput"] [data-baseweb="base-input"] {
        min-height: auto !important;
        height: auto !important;
    }
    
    /* Style disclaimer - smaller, below input, no bottom padding */
    .sidebar-chat-disclaimer {
        font-size: 0.65rem !important;
        color: rgba(255, 255, 255, 0.7) !important;
        margin-top: 2px !important;
        padding-top: 2px !important;
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
        line-height: 1.3 !important;
    }
    
    /* Remove bottom padding from sidebar bottom containers */
    section[data-testid="stSidebar"] [data-testid="element-container"]:last-child {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"]:last-child {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Remove bottom padding from sidebar wrapper */
    section[data-testid="stSidebar"] > div:last-child {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }
    
    .sidebar-chat-disclaimer a {
        color: #7db3c4 !important;
        text-decoration: none !important;
        font-size: 0.65rem !important;
    }
    
    .sidebar-chat-disclaimer a:hover {
        text-decoration: underline !important;
        font-size: 0.65rem !important;
    }
    
    /* Style container background */
    section[data-testid="stSidebar"] [data-baseweb="base-input"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    section[data-testid="stSidebar"] [data-baseweb="base-input"] input {
        color: white !important;
    }
    </style>
    <script>
    (function() {
        function styleChatAvatars() {
            const sidebar = document.querySelector('section[data-testid="stSidebar"]');
            if (!sidebar) return;
            
            // Find all assistant chat messages
            const assistantMessages = sidebar.querySelectorAll('[data-testid="stChatMessageAssistant"]');
            assistantMessages.forEach(msg => {
                const avatarContainer = msg.querySelector('div:first-child');
                if (avatarContainer && !avatarContainer.querySelector('.gw-sparkle')) {
                    // Clear existing content
                    avatarContainer.innerHTML = '';
                    // Add sparkle
                    const sparkle = document.createElement('span');
                    sparkle.className = 'gw-sparkle';
                    sparkle.textContent = '✨';
                    sparkle.style.fontSize = '12px';
                    sparkle.style.display = 'flex';
                    sparkle.style.alignItems = 'center';
                    sparkle.style.justifyContent = 'center';
                    sparkle.style.width = '16px';
                    sparkle.style.height = '16px';
                    avatarContainer.appendChild(sparkle);
                    avatarContainer.style.width = '16px';
                    avatarContainer.style.height = '16px';
                    avatarContainer.style.minWidth = '16px';
                    avatarContainer.style.minHeight = '16px';
                }
            });
            
            // Find all user chat messages
            const userMessages = sidebar.querySelectorAll('[data-testid="stChatMessageUser"]');
            userMessages.forEach(msg => {
                const avatarContainer = msg.querySelector('div:first-child');
                if (avatarContainer) {
                    avatarContainer.style.width = '16px';
                    avatarContainer.style.height = '16px';
                    avatarContainer.style.minWidth = '16px';
                    avatarContainer.style.minHeight = '16px';
                    avatarContainer.style.backgroundColor = '#86efac';
                    avatarContainer.style.borderRadius = '50%';
                    // Style any img inside
                    const img = avatarContainer.querySelector('img');
                    if (img) {
                        img.style.width = '16px';
                        img.style.height = '16px';
                        img.style.objectFit = 'cover';
                    }
                }
            });
        }
        
        // Run multiple times
        function run() {
            styleChatAvatars();
            setTimeout(styleChatAvatars, 100);
            setTimeout(styleChatAvatars, 500);
            setTimeout(styleChatAvatars, 1000);
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', run);
        } else {
            run();
        }
        
        const observer = new MutationObserver(run);
        observer.observe(document.body, { childList: true, subtree: true });
        
        // Auto-grow chat input textarea
        function setupAutoGrow() {
            const sidebar = document.querySelector('section[data-testid="stSidebar"]');
            if (!sidebar) return;
            
            const chatInput = sidebar.querySelector('[data-testid="stChatInput"]');
            if (!chatInput) return;
            
            const textarea = chatInput.querySelector('textarea');
            if (!textarea) return;
            
            // Set initial height to one line
            textarea.style.height = 'auto';
            textarea.style.minHeight = '1.5rem';
            textarea.style.maxHeight = '200px';
            textarea.style.overflowY = 'auto';
            textarea.style.resize = 'none';
            
            // Auto-grow function
            function autoGrow() {
                textarea.style.height = 'auto';
                const newHeight = Math.min(textarea.scrollHeight, 200);
                textarea.style.height = newHeight + 'px';
            }
            
            // Add event listeners
            textarea.addEventListener('input', autoGrow);
            textarea.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    // Let Streamlit handle Enter key
                    return;
                }
                autoGrow();
            });
            
            // Initial sizing
            autoGrow();
        }
        
        // Run auto-grow setup
        setupAutoGrow();
        setTimeout(setupAutoGrow, 100);
        setTimeout(setupAutoGrow, 500);
        setTimeout(setupAutoGrow, 1000);
        
        // Also observe for new chat inputs
        const inputObserver = new MutationObserver(setupAutoGrow);
        inputObserver.observe(document.body, { childList: true, subtree: true });
    })();
    </script>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        # Chat header - Guidewire style
        st.markdown("### ✨ Underwriting Assistant")
        
        # Scrollable chat history container
        chat_container = st.container(height=600)
        with chat_container:
            # Detect market for welcome message
            all_submissions = get_all_submissions()
            welcome_market = 'german'  # default
            if all_submissions:
                first_sub = all_submissions[0]
                welcome_market = detect_market(first_sub['submission_number'], first_sub.get('account_country', ''))
            st.session_state['sidebar_market'] = welcome_market
            
            # Add welcome message to chat history if not already there (so it renders like other messages)
            # Market-specific welcome messages
            if welcome_market == 'german':
                welcome_text_raw = """Willkommen zurück, Alice!
            
Hier ist, was seit Ihrem letzten Login passiert ist:
• Das Einreichungsvolumen stieg diese Woche um 12%, mit einem Anstieg in der Bau- und Gesundheitsbranche, was den breiteren Markttrends entspricht, dass diese Sparten aus dem regulären Markt herausgeschrieben werden.
• Die Appetit-Ausrichtung ist in diesen Segmenten stark, während Bau und Gastgewerbe steigende Out-of-Appetite-Flaggen zeigen, was Inflation und Schadenvolatilität widerspiegelt.
• Tier-1-Makler trugen 71% der vollständigen, qualifizierten Einreichungen bei, während Makler niedrigerer Stufen mehr belastete Risiken einreichen — wahrscheinlich eine Reaktion auf sich verschärfende Marktbedingungen.
• Mit 8 veralteten Einreichungen, die kurz vor der automatischen Schließung stehen, ist Workflow-Disziplin entscheidend.
Einige Dinge, die Sie häufig fragen könnten:
• Catch me up
• Erstellen Sie eine Aktionsliste
• Fragen Sie nach meinen Metriken"""
            else:  # US market
                welcome_text_raw = """Welcome back, Alice!
            
Here's what happened since your last login:
• Submission volume rose 12% this week, with a surge in Contractors and Healthcare industry, aligning with broader market trends of these lines being written out of the admitted market.
• Appetite alignment is strong in these segments, while construction and hospitality show rising out-of-appetite flags, reflecting inflation and claims volatility.
• Tier 1 brokers contributed 71% of complete, qualified submissions, while lower-tier brokers are submitting more distressed risks — likely a response to tightening market conditions.
• With 8 stale submissions nearing auto-closure, workflow discipline is key.
Some things you could commonly ask for:
• Catch me up
• Create an action list
• Ask about my metrics"""
            
            # Process line breaks:
            # - Double or triple newlines → <br><br><br> (empty line/paragraph)
            # - Single newlines → <br> (just a line break, no extra spacing)
            welcome_text = welcome_text_raw
            # First, normalize triple+ newlines to double (both become empty line)
            welcome_text = re.sub(r'\n{3,}', '\n\n', welcome_text)
            # Replace double newlines with 3 <br> tags (empty line/paragraph)
            welcome_text = welcome_text.replace('\n\n', '<br><br><br>')
            # Replace single newlines with 1 <br> tag (just a line break)
            welcome_text = welcome_text.replace('\n', '<br>')
            
            # Wrap bullet point lines in spans for hanging indent styling
            lines = welcome_text.split('<br>')
            processed_lines = []
            for i, line in enumerate(lines):
                if line.strip().startswith('•'):
                    # Wrap bullet point line in span with class for styling
                    processed_lines.append(f'<span class="bullet-point-line">{line}</span>')
                    # Only add <br> if next line is not a bullet point and not empty
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not next_line.startswith('•'):
                            processed_lines.append('<br>')
                elif line.strip():  # Non-empty, non-bullet line
                    processed_lines.append(line)
                    if i + 1 < len(lines):
                        processed_lines.append('<br>')
                else:  # Empty line (preserve for paragraph spacing)
                    processed_lines.append('<br>')
            welcome_text = ''.join(processed_lines)
            
            if st.session_state.show_welcome:
                # Add welcome message to chat history so it renders the same way as other messages
                # Check if welcome message is already in chat history
                welcome_already_added = any(
                    msg.get('role') == 'assistant' and (
                        msg.get('content', '').startswith('Welcome back, Alice!') or
                        msg.get('content', '').startswith('Willkommen zurück, Alice!')
                    )
                    for msg in st.session_state.chat_messages
                )
                if not welcome_already_added:
                    st.session_state.chat_messages.insert(0, {'role': 'assistant', 'content': welcome_text})
            
            # Chat history using st.chat_message
            for msg_idx, msg in enumerate(st.session_state.chat_messages):
                if msg['role'] == 'user':
                    with st.chat_message("user"):
                        st.markdown(msg['content'])
                else:
                    with st.chat_message("assistant"):
                        # Check if message contains submission cards marker
                        content = msg['content']
                        if '<!--SUBMISSION_CARDS_START-->' in content or '<!--OPEN_DECLINED_TAB_BUTTON-->' in content:
                            # Remove markers from display
                            display_content = content.replace('<!--SUBMISSION_CARDS_START-->', '')
                            display_content = display_content.replace('<!--OPEN_DECLINED_TAB_BUTTON-->', '')
                            st.markdown(display_content, unsafe_allow_html=True)
                            
                            # Render "Open Declined Tab" button if marker is present and not dismissed
                            if '<!--OPEN_DECLINED_TAB_BUTTON-->' in content:
                                dismissed_set = st.session_state.get('dismissed_declined_tab', set())
                                if msg_idx not in dismissed_set:
                                    # Buttons in columns for Open and Dismiss
                                    col_open, col_dismiss = st.columns([1, 1])
                                    with col_open:
                                        if st.button("Open", key=f"open_declined_{msg_idx}", use_container_width=True):
                                            # Navigate to dashboard and set flag to open declined tab
                                            st.session_state.current_screen = 'dashboard'
                                            st.session_state.open_declined_tab = True
                                            st.rerun()
                                    with col_dismiss:
                                        if st.button("Dismiss", key=f"dismiss_declined_{msg_idx}", use_container_width=True):
                                            # Mark declined tab button as dismissed
                                            if 'dismissed_declined_tab' not in st.session_state:
                                                st.session_state.dismissed_declined_tab = set()
                                            st.session_state.dismissed_declined_tab.add(msg_idx)
                                            st.rerun()
                                    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                            
                            # Render submission cards with buttons
                            if 'chat_submission_cards' in st.session_state:
                                for card_idx, card in enumerate(st.session_state.chat_submission_cards):
                                    if not card.get('dismissed', False):
                                        # Determine if we should show bullet points (only if there are details)
                                        has_details = 'details' in card and len(card.get('details', [])) > 0
                                        
                                        # Create a container for the submission card with styling
                                        message_line = f"• {card['message']}" if has_details else card['message']
                                        st.markdown(f"""
                                        <div style="background-color: rgba(255, 255, 255, 0.05); padding: 0.75rem; border-radius: 4px; margin: 0.5rem 0;">
                                        <strong>{card['submission_number']}</strong><br>
                                        {message_line}
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Display details if available
                                        if has_details:
                                            for detail in card['details']:
                                                st.markdown(f"• {detail}")
                                        
                                        # Buttons in columns - smaller size
                                        col1, col2 = st.columns([1, 1])
                                        with col1:
                                            if st.button("Open", key=f"open_card_{msg_idx}_{card_idx}", use_container_width=True):
                                                # Navigate to submission
                                                handle_chat_navigation({
                                                    'type': 'open_submission',
                                                    'submission_number': card['submission_number']
                                                })
                                                st.rerun()
                                        with col2:
                                            if st.button("Dismiss", key=f"dismiss_card_{msg_idx}_{card_idx}", use_container_width=True):
                                                # Mark card as dismissed
                                                card['dismissed'] = True
                                                st.rerun()
                                        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                        else:
                            # Regular message rendering
                            st.markdown(msg['content'], unsafe_allow_html=True)
        
        # Suggested quick actions
        suggestion_clicked = None
        sidebar_market = st.session_state.get('sidebar_market', 'german')
        suggestion_map = {
            'german': [
                {'label': '• Catch me up', 'prompt': 'Catch me up'},
                {'label': '• Erstellen Sie eine Aktionsliste', 'prompt': 'Erstellen Sie eine Aktionsliste'},
                {'label': '• Fragen Sie nach meinen Metriken', 'prompt': 'Fragen Sie nach meinen Metriken'}
            ],
            'us': [
                {'label': '• Catch me up', 'prompt': 'Catch me up'},
                {'label': '• Create an action list', 'prompt': 'Create an action list'},
                {'label': '• Ask about my metrics', 'prompt': 'Ask about my metrics'}
            ]
        }
        suggestions = suggestion_map.get(sidebar_market, suggestion_map['us'])
        suggestion_container = st.container()
        for idx, suggestion in enumerate(suggestions):
            if suggestion_container.button(suggestion['label'], key=f"chat_suggestion_{sidebar_market}_{idx}"):
                suggestion_clicked = suggestion['prompt']
        
        # Chat input (outside scrollable container - always visible at bottom)
        user_input = st.chat_input("Type your message...")
        if suggestion_clicked:
            user_input = suggestion_clicked
        
        # Disclaimer - Guidewire style (below input)
        st.markdown("""
        <div class="sidebar-chat-disclaimer">
        The above response was generated by an AI system and may not provide a complete and accurate answer. Please reference the provided sources for more detailed information related to your question. <a href="#" style="color: #7db3c4;">Learn more</a>.
        </div>
        """, unsafe_allow_html=True)
        
        if user_input:
            # Add user message
            st.session_state.chat_messages.append({'role': 'user', 'content': user_input})
            
            # Generate AI response and check for navigation triggers
            response, navigation_action = generate_ai_response_with_navigation(user_input)
            st.session_state.chat_messages.append({'role': 'assistant', 'content': response})
            st.session_state.show_welcome = False
            
            # Handle navigation if triggered
            if navigation_action:
                handle_chat_navigation(navigation_action)
            
            st.rerun()

def generate_ai_response(user_input):
    """Generate contextual AI responses based on user input"""
    user_input_lower = user_input.lower()
    
    # Detect market from database
    all_submissions = get_all_submissions()
    current_market = 'german'  # default
    if all_submissions:
        first_sub = all_submissions[0]
        current_market = detect_market(first_sub['submission_number'], first_sub.get('account_country', ''))
    
    # Contextual responses
    # Check for "update" variations first (before catch me up)
    if any(word in user_input_lower for word in ['update', 'updates', 'updated', 'updating']):
        # Store submission cards in session state for rendering
        if 'chat_submission_cards' not in st.session_state:
            st.session_state.chat_submission_cards = []
        
        # Market-specific submission cards for "update"
        if current_market == 'german':
            st.session_state.chat_submission_cards = [
                {
                    'submission_number': 'SUB-2026-001-DE',
                    'message': 'Das Angebot wurde angenommen und ist bereit zur Bindung.',
                    'dismissed': False
                }
            ]
        else:  # US market
            st.session_state.chat_submission_cards = [
                {
                    'submission_number': 'SUB-2026-001',
                    'message': 'The quote has been accepted, and it is ready to be bound.',
                    'dismissed': False
                }
            ]
        
        return """<!--SUBMISSION_CARDS_START-->"""
    
    elif 'catch' in user_input_lower or 'summary' in user_input_lower:
        # Store submission cards in session state for rendering
        if 'chat_submission_cards' not in st.session_state:
            st.session_state.chat_submission_cards = []
        
        # Determine if key submission is already quoted/bind-ready
        target_submission_number = 'SUB-2026-001-DE' if current_market == 'german' else 'SUB-2026-001'
        target_submission = next((sub for sub in all_submissions if sub.get('submission_number', '').upper() == target_submission_number.upper()), None)
        target_status = (target_submission.get('status', '') if target_submission else '').upper()
        ready_to_bind_statuses = {'QUOTED', 'READY TO BIND', 'BINDABLE'}

        if target_submission and target_status in ready_to_bind_statuses:
            # Mirror the update response when the quote is already accepted
            if current_market == 'german':
                st.session_state.chat_submission_cards = [
                    {
                        'submission_number': 'SUB-2026-001-DE',
                        'message': 'Das Angebot wurde angenommen und ist bereit zur Bindung.',
                        'dismissed': False
                    }
                ]
            else:
                st.session_state.chat_submission_cards = [
                    {
                        'submission_number': 'SUB-2026-001',
                        'message': 'The quote has been accepted, and it is ready to be bound.',
                        'dismissed': False
                    }
                ]
            return """<!--SUBMISSION_CARDS_START-->"""

        # Market-specific "catch me up" responses (default path)
        if current_market == 'german':
            st.session_state.chat_submission_cards = [
                {
                    'submission_number': 'SUB-2026-003-DE',
                    'message': 'Diese Einreichung ist zur Freigabe bereit.',
                    'dismissed': False
                },
                {
                    'submission_number': 'SUB-2026-001-DE',
                    'message': 'Diese Einreichung hatte bei Eingang am vergangenen Freitag unzureichende Dokumentation.',
                    'details': [
                        'Gestern wurde eine E-Mail an den Makler gesendet, um die fehlenden Details anzufordern.',
                        'Sie haben heute Morgen neue E-Mails und Dokumente erhalten, die Sie für diese Anfrage prüfen müssen.'
                    ],
                    'dismissed': False
                }
            ]
            
            return """Eine Einreichung, die nicht den grundlegenden Anforderungen entsprach, wurde abgelehnt. Sie können sie im Bereich "Abgelehnte Einreichungen" einsehen.

<!--OPEN_DECLINED_TAB_BUTTON-->

<!--SUBMISSION_CARDS_START-->"""
        else:  # US market
            st.session_state.chat_submission_cards = [
                {
                    'submission_number': 'SUB-2026-003',
                    'message': 'This submission is ready to be cleared.',
                    'dismissed': False
                },
                {
                    'submission_number': 'SUB-2026-001',
                    'message': 'This submission had insufficient documentation when received last Friday.',
                    'details': [
                        'Email was sent yesterday to the broker to request for missing details.',
                        'You have received new emails and documents this morning to review for this request.'
                    ],
                    'dismissed': False
                }
            ]
            
            return """One submission that was not under the basic levels required has been declined. You can check it in the Declined Submissions section.

<!--OPEN_DECLINED_TAB_BUTTON-->

<!--SUBMISSION_CARDS_START-->"""
    
    elif ('action' in user_input_lower or 'priority' in user_input_lower or 'todo' in user_input_lower or 'aktionsliste' in user_input_lower):
        if current_market == 'german':
            return """**Ihre Prioritätenliste:**

1. ⚡ **DRINGEND:** Möbel & Wohnen Schmidt GmbH (SUB-2026-001-DE)
   - Prioritätsscore: 4.8 | Vollständigkeit: 74%
   - Aktion: Prüfen und Angebot erstellen

2. 🔔 **HOCH:** Tech Distribution GmbH (SUB-2026-003-DE)
   - Prioritätsscore: 4.7 | Vollständigkeit: 80%
   - Aktion: Dokumentenprüfung erforderlich

3. 📋 **MITTEL:** Bauhaus AG (SUB-2026-007-DE)
   - Bereit zur Bindung
   - Aktion: Angebot an Makler senden

Soll ich Ihnen zuerst mit Möbel & Wohnen Schmidt helfen?"""
        else:  # US market
            return """**Your Priority Action List:**

1. ⚡ **URGENT:** Floor & Decor (SUB-2026-001)
   - Priority Score: 4.8 | Completeness: 74%
   - Action: Review and generate quote

2. 🔔 **HIGH:** Monrovia Metalworking (SUB-2026-003)
   - Priority Score: 4.7 | Completeness: 80%
   - Action: Document review needed

3. 📋 **MEDIUM:** Construction Dynamics (SUB-2026-007)
   - Ready to bind
   - Action: Send quote to broker

Shall I help you with Floor & Decor first?"""
    
    elif ('help' in user_input_lower or 'what can' in user_input_lower or 'metriken' in user_input_lower or 'hilfe' in user_input_lower):
        if current_market == 'german':
            return """Ich kann Ihnen helfen bei:

**Einreichungsverwaltung:**
• Aktualisierungen zu aktiven Einreichungen erhalten
• Priorisierte Aktionslisten erstellen
• Einreichungsstatus prüfen

**Analysen & Erkenntnisse:**
• KPI-Trends überprüfen
• Maklerleistung analysieren
• Appetit-Ausrichtungsprobleme identifizieren

**Schnellaktionen:**
• Bestimmte Einreichungen öffnen
• Angebote erstellen
• Erinnerungen an Makler senden

Fragen Sie mich einfach!"""
        else:  # US market
            return """I can help you with:

**Submission Management:**
• Get updates on active submissions
• Create prioritized action lists
• Check submission status

**Analytics & Insights:**
• Review KPI trends
• Analyze broker performance
• Identify appetite alignment issues

**Quick Actions:**
• Open specific submissions
• Generate quotes
• Send reminders to brokers

Just ask me anything!"""
    
    elif 'floor' in user_input_lower or '2026-001' in user_input_lower:
        return """**Floor & Decor Outlets (SUB-2026-001):**

📊 **Status:** Triaged (74% complete)
🎯 **Priority:** 4.8/5.0 (High)
💰 **Estimated Premium:** $1.8M
📅 **Effective Date:** Oct 29, 2025

**Next Steps:**
1. Review loss runs (already uploaded)
2. Generate APD quote
3. AI analysis for endorsements

This is a Tier 1 broker submission with strong appetite alignment. Would you like me to open this submission for review?"""
    
    else:
        # Generic helpful response - market-specific
        if current_market == 'german':
            return f"""Ich verstehe, dass Sie nach "{user_input}" fragen.

Ich kann Ihnen bei Einreichungsprüfungen, Prioritätsaktionen, KPI-Einblicken und Workflow-Management helfen.

Versuchen Sie zu fragen:
• "Was braucht meine Aufmerksamkeit?"
• "Zeigen Sie mir Einreichungen mit hoher Priorität"
• "Geben Sie mir eine Zusammenfassung der heutigen Aktivitäten"

Wie kann ich Ihnen helfen?"""
        else:  # US market
            return f"""I understand you're asking about "{user_input}". 

I can help you with submission reviews, priority actions, KPI insights, and workflow management. 

Try asking:
• "What needs my attention?"
• "Show me high-priority submissions"
• "Give me a summary of today's activity"

How can I assist you?"""

def generate_ai_response_with_navigation(user_input):
    """Generate AI response and detect navigation triggers"""
    user_input_lower = user_input.lower()
    navigation_action = None
    
    # Check for submission number patterns (e.g., "SUB-2026-001", "2026-001", "open submission 001")
    import re
    submission_match = re.search(r'sub-?(\d{4})-?(\d{3})', user_input_lower) or \
                      re.search(r'(\d{4})-(\d{3})', user_input_lower) or \
                      re.search(r'submission\s+(\d{3})', user_input_lower) or \
                      re.search(r'open\s+(\d{3})', user_input_lower)
    
    if submission_match:
        # Extract submission number
        if len(submission_match.groups()) == 2:
            year, num = submission_match.groups()
            submission_number = f"SUB-{year}-{num}"
        else:
            num = submission_match.groups()[0]
            submission_number = f"SUB-2026-{num.zfill(3)}"
        
        navigation_action = {'type': 'open_submission', 'submission_number': submission_number}
        response = f"Opening submission {submission_number} for you..."
    elif 'open' in user_input_lower and ('floor' in user_input_lower or 'decor' in user_input_lower):
        navigation_action = {'type': 'open_submission', 'submission_number': 'SUB-2026-001'}
        response = "Opening Floor & Decor submission (SUB-2026-001)..."
    elif 'open' in user_input_lower and ('monrovia' in user_input_lower or 'metalworking' in user_input_lower):
        navigation_action = {'type': 'open_submission', 'submission_number': 'SUB-2026-003'}
        response = "Opening Monrovia Metalworking submission (SUB-2026-003)..."
    elif 'open' in user_input_lower and ('construction' in user_input_lower or 'dynamics' in user_input_lower):
        navigation_action = {'type': 'open_submission', 'submission_number': 'SUB-2026-007'}
        response = "Opening Construction Dynamics submission (SUB-2026-007)..."
    else:
        # Use regular response generator
        response = generate_ai_response(user_input)
    
    return response, navigation_action

def handle_chat_navigation(navigation_action):
    """Handle navigation actions triggered from chat"""
    if navigation_action['type'] == 'open_submission':
        submission_number = navigation_action['submission_number']
        
        # Get all submissions to find the matching one
        all_submissions = get_all_submissions()
        
        # Find submission by number
        matching_sub = None
        for sub in all_submissions:
            if sub.get('submission_number', '').upper() == submission_number.upper():
                matching_sub = sub
                break
        
        if matching_sub:
            # Set selected submission and navigate to detail page
            st.session_state.selected_submission = matching_sub['id']
            st.session_state.current_screen = 'submission_detail'
            st.session_state.chat_open = False  # Close chat after navigation
        else:
            st.warning(f"Submission {submission_number} not found.")

def render_dashboard():
    """Render the main dashboard screen"""
    # Render chatbot sidebar with popover-style features
    render_chatbot_sidebar()
    
    # Load and encode logo
    logo_path = os.path.join(os.path.dirname(__file__), 'guidewire.png')
    logo_base64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    
    # Style header and reduce spacing aggressively
    st.markdown(f"""
    <style>
    /* Style header background */
    header[data-testid="stHeader"] {{
        background-color: #3c5c6c !important;
        position: relative !important;
        height: 3.5rem !important;
    }}
    
    /* DON'T hide Streamlit's header content - keep navigation buttons visible */
    /* Just style the header container to show our content on the left */
    header[data-testid="stHeader"] > div {{
        background-color: transparent !important;
    }}
    
    /* Reduce space between header and main content - BOTH margin AND transform for vertical */
    /* Reduce both left and right padding using negative margins */
    [data-testid="stAppViewContainer"] {{
        padding-top: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        max-width: calc(100% + 8rem) !important;
    }}
    
    [data-testid="stAppViewContainer"] > .main {{
        padding-top: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-top: -60px !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        transform: translateY(-60px) !important;
        max-width: calc(100% + 8rem) !important;
        width: calc(100% + 8rem) !important;
    }}
    
    [data-testid="stAppViewBlockContainer"] {{
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        max-width: calc(100% + 8rem) !important;
    }}
    
    .main .block-container {{
        padding-top: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-top: -60px !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        transform: translateY(-60px) !important;
        max-width: calc(100% + 8rem) !important;
        width: calc(100% + 8rem) !important;
    }}
    
    /* Target the first element container with both margin and transform */
    .main .element-container:first-child {{
        margin-top: -10px !important;
        padding-top: 0 !important;
        transform: translateY(-10px) !important;
    }}
    
    /* Also target any markdown elements that might add space */
    .main .element-container:first-child .stMarkdown {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    
    /* Target appviewblock */
    [data-testid="stAppViewBlockContainer"] {{
        margin-top: -60px !important;
        transform: translateY(-60px) !important;
        padding-top: 0 !important;
    }}
    
    /* Try targeting the space directly after header */
    header[data-testid="stHeader"] ~ * {{
        margin-top: -60px !important;
        transform: translateY(-60px) !important;
    }}
    
    /* Inject logo and text using CSS - positioned on the left, buttons stay on right */
    header[data-testid="stHeader"]::before {{
        content: '';
        display: inline-block;
        width: 28px;
        height: 28px;
        background-image: url('data:image/png;base64,{logo_base64}');
        background-size: contain;
        background-repeat: no-repeat;
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 10;
    }}
    
    header[data-testid="stHeader"]::after {{
        content: 'Guidewire Underwriting Center for DräumVersicherung';
        color: white;
        font-size: 1.25rem !important;
        font-weight: 400;
        letter-spacing: 0.3px;
        position: absolute;
        left: 60px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 10;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Inject JavaScript to force table font size to 1rem
    components.html("""
    <script>
    (function() {
        function forceTableFontSize() {
            // Target all table elements
            const tables = document.querySelectorAll('table, [data-testid="stDataFrame"] table, .stDataFrame table');
            tables.forEach(function(table) {
                // Set font size on table and all cells
                table.style.fontSize = '1rem';
                const cells = table.querySelectorAll('td, th');
                cells.forEach(function(cell) {
                    cell.style.fontSize = '1rem';
                    // Also set on any nested elements
                    const nested = cell.querySelectorAll('*');
                    nested.forEach(function(el) {
                        el.style.fontSize = '1rem';
                    });
                });
            });
        }
        
        // Run immediately
        forceTableFontSize();
        
        // Run after a short delay to catch dynamically loaded content
        setTimeout(forceTableFontSize, 100);
        setTimeout(forceTableFontSize, 500);
        
        // Also run when DOM changes (for dynamic content)
        const observer = new MutationObserver(function(mutations) {
            forceTableFontSize();
        });
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    })();
    </script>
    """, height=0)
    
    st.markdown('<h3 class="my-submissions-header" style="margin-top: 0; margin-bottom: 8px; color: white; font-weight: 700; font-size: 1.25rem !important;">My Submissions</h3>', unsafe_allow_html=True)
    
    # Detect market from first submission in database (German or US)
    all_submissions = get_all_submissions()
    dashboard_market = 'german'  # default
    dashboard_currency = '€'
    if all_submissions:
        first_sub = all_submissions[0]
        dashboard_market = detect_market(first_sub['submission_number'], first_sub.get('account_country', ''))
    dashboard_currency = '€' if dashboard_market == 'german' else '$'
    
    # === TOP KPI ROW ===
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        turnaround_delta = "⬇️ -0.2 days" if st.session_state.dashboard_kpis['turnaround_time'] == 3.9 else "⬇️ -0.1 days"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Quote Turnaround Time</div>
            <div class="kpi-value">{st.session_state.dashboard_kpis['turnaround_time']} Days</div>
            <div class="kpi-delta">{turnaround_delta}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        if st.session_state.dashboard_kpis['hit_ratio'] == 37:
            hit_ratio_delta = "⬆️ +2% from Q3"
        elif st.session_state.chart_data['hit_ratio_q4'] == 32:
            hit_ratio_delta = "⬇️ -3% from Q3"
        else:
            hit_ratio_delta = "⬆️ +2% from Q3"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Hit Ratio</div>
            <div class="kpi-value">{st.session_state.dashboard_kpis['hit_ratio']}%</div>
            <div class="kpi-delta">{hit_ratio_delta}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        premium_delta = "⬆️ +15% YTD" if st.session_state.dashboard_kpis['earned_premium'] == 1.85 else "⬆️ +12% YTD"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Cumulative Earned Premium</div>
            <div class="kpi-value">{dashboard_currency}{st.session_state.dashboard_kpis['earned_premium']}M</div>
            <div class="kpi-delta">{premium_delta}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">In Force Loss Ratio</div>
            <div class="kpi-value">{st.session_state.dashboard_kpis['loss_ratio']}%</div>
            <div class="kpi-delta">⬇️ -2% from target</div>
        </div>
        """, unsafe_allow_html=True)
    
    # === CHARTS ROW ===
    chart_col1, chart_col2, chart_col3, chart_col4 = st.columns(4)
    
    with chart_col1:
        # Quote Turnaround Time - simple display with trend indicator
        st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <p style="color: #6b7280; margin: 0;">Target: 4.0 days</p>
        </div>
        """, unsafe_allow_html=True)
    
    with chart_col2:
        # Average Hit Ratio - Bar chart
        hit_ratio_data = pd.DataFrame({
            'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
            'Hit Ratio %': [19, 24, 35, st.session_state.chart_data['hit_ratio_q4']]
        })
        
        # Add formatted labels with % sign
        hit_ratio_data['Label'] = hit_ratio_data['Hit Ratio %'].apply(lambda x: f'{int(x)}%')
        
        # Bar chart
        chart = alt.Chart(hit_ratio_data).mark_bar(color='#14b8a6', size=50).encode(
            x=alt.X('Quarter:N', axis=alt.Axis(title=None, labelAngle=0, labelFontSize=12, labelFont='Arial')),
            y=alt.Y('Hit Ratio %:Q', 
                    axis=alt.Axis(title=None, grid=True, labelFontSize=12, labelFont='Arial'),
                    scale=alt.Scale(domain=[0, 40]))
        ).properties(
            height=200
        )
        
        # Add text labels on top of bars
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-5,
            color='#0f766e',
            fontSize=13,
            fontWeight='bold'
        ).encode(
            text='Label:N'
        )
        
        # Add "good" threshold line
        threshold_line = alt.Chart(pd.DataFrame({'y': [26]})).mark_rule(
            color='white',
            strokeWidth=2,
            strokeDash=[5, 5]
        ).encode(
            y='y:Q'
        )
        
        # Add "good" label
        threshold_label = alt.Chart(pd.DataFrame({
            'x': ['Q4'],
            'y': [26],
            'label': ['good']
        })).mark_text(
            align='left',
            dx=10,
            dy=-5,
            color='white',
            fontSize=11,
            fontWeight='bold'
        ).encode(
            x=alt.X('x:N'),
            y=alt.Y('y:Q'),
            text='label:N'
        )
        
        # Combine charts and configure axis label size
        combined_chart = (chart + text + threshold_line + threshold_label).configure_axis(
            labelFontSize=12
        )
        
        st.altair_chart(combined_chart, use_container_width=True)
    
    with chart_col3:
        # Cumulative Earned Premium - Bar chart
        premium_data = pd.DataFrame({
            'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
            'Premium': [0.58, 1.02, 1.28, st.session_state.chart_data['premium_q4']]
        })
        
        # Dynamic format based on currency
        y_axis_format = ',.2f' if dashboard_market == 'german' else '$,.2f'
        chart = alt.Chart(premium_data).mark_bar(color='#14b8a6', size=50).encode(
            x=alt.X('Quarter:N', axis=alt.Axis(title=None, labelAngle=0, labelFontSize=12)),
            y=alt.Y('Premium:Q', 
                    axis=alt.Axis(title=None, grid=True, format=y_axis_format, labelFontSize=12),
                    scale=alt.Scale(domain=[0, 2]))
        ).properties(
            height=200
        )
        
        # Add text labels on top of bars with currency-appropriate formatting
        if dashboard_market == 'german':
            # For German market, format manually with € symbol
            premium_data['Label'] = premium_data['Premium'].apply(lambda x: f'€{x:.2f}')
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-5,
                color='#0f766e',
                fontSize=12,
                fontWeight='bold'
            ).encode(
                text='Label:N'
            )
        else:
            # For US market, use standard $ formatting
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-5,
                color='#0f766e',
                fontSize=12,
                fontWeight='bold'
            ).encode(
                text=alt.Text('Premium:Q', format='$,.2f')
            )
        
        st.altair_chart(chart + text, use_container_width=True)
    
    with chart_col4:
        # In Force Loss Ratio - Line chart
        loss_ratio_data = pd.DataFrame({
            'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
            'Loss Ratio %': [49, 51, 52, 49]
        })
        
        # Add formatted labels with % sign
        loss_ratio_data['Label'] = loss_ratio_data['Loss Ratio %'].apply(lambda x: f'{int(x)}%')
        
        # Line chart
        line = alt.Chart(loss_ratio_data).mark_line(
            color='#0891b2',
            strokeWidth=3,
            point=alt.OverlayMarkDef(color='#0891b2', size=80)
        ).encode(
            x=alt.X('Quarter:N', axis=alt.Axis(title=None, labelAngle=0, labelFontSize=12)),
            y=alt.Y('Loss Ratio %:Q', 
                    axis=alt.Axis(title=None, grid=True, format='.0f', labelFontSize=12),
                    scale=alt.Scale(domain=[44, 55]))
        ).properties(
            height=200
        )
        
        # Add text labels on points
        text = line.mark_text(
            align='center',
            baseline='bottom',
            dy=-12,
            color='#5a9fb8',
            fontSize=12,
            fontWeight='bold'
        ).encode(
            text='Label:N'
        )
        
        st.altair_chart(line + text, use_container_width=True)
    
    # === SUBMISSIONS TABLE ===
    # Tabs for filtering
    tab1, tab2, tab3 = st.tabs(["Active Submissions", "Bound", "Declined"])
    
    # Auto-switch to Declined tab if flag is set
    if st.session_state.get('open_declined_tab', False):
        # Use JavaScript to click the Declined tab (index 2) with a small delay to ensure tabs are rendered
        components.html("""
        <script>
        (function() {
            function clickDeclinedTab() {
                const tabs = document.querySelectorAll('[data-testid="stTabs"] button');
                if (tabs.length >= 3) {
                    // Click the third tab (index 2) which is "Declined"
                    tabs[2].click();
                    return true;
                }
                return false;
            }
            // Try immediately
            if (!clickDeclinedTab()) {
                // If tabs aren't ready, try again after a short delay
                setTimeout(clickDeclinedTab, 100);
            }
        })();
        </script>
        """, height=0)
        # Clear the flag after switching
        st.session_state.open_declined_tab = False
    
    # Get all submissions
    all_submissions = get_all_submissions()
    
    with tab1:
        active_subs = [s for s in all_submissions if s['status'].upper() not in ['BOUND', 'DECLINED']]
        # Only show quoted submissions that have been accepted (quote sent to broker)
        quoted_subs = [s for s in active_subs if s['status'].upper() == 'QUOTED' and s.get('accepted', False)]
        in_progress_subs = [s for s in active_subs if s['status'].upper() != 'QUOTED' or not s.get('accepted', False)]
        
        if active_subs:
            st.caption(f"Showing {len(active_subs)} active submission(s)")
            
            # Show bind option for accepted quoted submissions first
            if quoted_subs:
                st.markdown("**📋 Ready to Bind:**")
                for sub in quoted_subs:
                    col_view, col_sub, col_btn = st.columns([1, 2, 1])
                    with col_view:
                        if st.button("👁️ View", key=f"view_quoted_{sub['id']}", use_container_width=True):
                            st.session_state.selected_submission = sub['id']
                            st.session_state.current_screen = 'submission_detail'
                            if sub['submission_number'] in ['SUB-2026-001', 'SUB-2026-001-DE']:
                                demo_market = detect_market(sub['submission_number'])
                                demo_market_content = get_market_content(demo_market)
                                all_endorsements = {**demo_market_content['endorsements']['base'],
                                                   **demo_market_content['endorsements']['recommended']}
                                status_value = sub.get('status') or 'Triaged'
                                completeness_value = sub.get('completeness') or 74
                                priority_value = sub.get('priority_score') or 4.8
                                appetite_value = sub.get('risk_appetite') or 'High'
                                bind_available = status_value.upper() == 'QUOTED' and sub.get('accepted', False)
                                st.session_state.submission_state = {
                                    'status': status_value,
                                    'completeness': completeness_value,
                                    'priority_score': priority_value,
                                    'risk_appetite': appetite_value,
                                    'is_summary_visible': False,
                                    'is_proposal_visible': False,
                                    'is_recs_visible': False,
                                    'is_comparison_visible': False,
                                    'quotes': [],
                                    'endorsements': all_endorsements,
                                    'widget_key_suffix': '',
                                    'bind_available': bind_available,
                                    'bind_suppressed': False
                                }
                            st.rerun()
                    with col_sub:
                        st.markdown(f"**{sub['account_name']}**  \n{sub['submission_number']} - *Quoted*")
                    with col_btn:
                        if st.button("✅ Bind", key=f"bind_active_{sub['id']}", use_container_width=True):
                            import random
                            policy_number = random.randint(2800000000, 2899999999)
                            
                            show_loading_modal([
                                "Sending data to PolicyCenter for Binding",
                                f"Policy Bound: {policy_number}"
                            ])
                            
                            update_submission_status(sub['id'], 'BOUND')
                            
                            # Update dashboard KPIs
                            st.session_state.dashboard_kpis['turnaround_time'] = 3.9
                            st.session_state.dashboard_kpis['hit_ratio'] = 37
                            st.session_state.dashboard_kpis['earned_premium'] = 1.85
                            
                            # Update chart data
                            st.session_state.chart_data['hit_ratio_q4'] = 37
                            st.session_state.chart_data['premium_q4'] = 1.85
                            
                            st.success(f"✅ Policy bound for {sub['account_name']}! Metrics updated.")
                            time.sleep(1)
                            st.rerun()
                st.markdown("---")
            
            # Show in-progress submissions
            if in_progress_subs:
                st.markdown("**🔄 In Progress:**")
                
                # Create DataFrame for display
                df_display = []
                for sub in in_progress_subs:
                    # Create status badge with emoji
                    status_upper = sub['status'].upper()
                    if status_upper == 'TRIAGED':
                        status_display = '🔴 Triaged'
                    elif status_upper == 'IN REVIEW':
                        status_display = '🟠 In Review'
                    elif status_upper == 'QUOTED':
                        status_display = '🔵 Quoted'
                    elif status_upper == 'BOUND':
                        status_display = '🟢 Bound'
                    elif status_upper == 'CLEARED':
                        status_display = '⚪ Cleared'
                    elif status_upper == 'DECLINED':
                        status_display = '⚫ Declined'
                    else:
                        status_display = sub['status']
                    
                    # Create appetite badge with emoji
                    appetite_upper = sub['risk_appetite'].upper()
                    if appetite_upper == 'HIGH':
                        appetite_display = '🟢 High'
                    elif appetite_upper == 'MEDIUM':
                        appetite_display = '🟡 Medium'
                    elif appetite_upper == 'LOW':
                        appetite_display = '🔴 Low'
                    else:
                        appetite_display = sub['risk_appetite']
                    
                    df_display.append({
                        'Account': sub['account_name'],
                        'Submission': sub['submission_number'],
                        'Status': status_display,
                        'Broker': sub['broker'],
                        'Broker Tier': sub['broker_tier'],
                        'Effective Date': sub['effective_date'].strftime('%Y-%m-%d') if sub['effective_date'] else 'N/A',
                        'Priority Score': f"{sub['priority_score']:.1f}" if sub['priority_score'] else 'N/A',
                        'Completeness': f"{sub['completeness']}%" if sub['completeness'] else 'N/A',
                        'Appetite': appetite_display
                    })
                
                df = pd.DataFrame(df_display)
                
                # Style the dataframe to set font size to 1rem
                styled_df = df.style.set_table_styles([
                    {
                        'selector': 'td, th',
                        'props': [('font-size', '1rem')]
                    },
                    {
                        'selector': 'table',
                        'props': [('font-size', '1rem')]
                    }
                ])
                
                # Display as a clickable table using st.dataframe with selection
                event = st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row"
                )
                
                # Handle row selection
                if event and event.selection and event.selection.rows:
                    selected_idx = event.selection.rows[0]
                    selected_sub = in_progress_subs[selected_idx]
                    st.session_state.selected_submission = selected_sub['id']
                    st.session_state.current_screen = 'submission_detail'
                    
                    # Reset submission state if switching to demo submission
                    if selected_sub['submission_number'] in ['SUB-2026-001', 'SUB-2026-001-DE']:
                        # Detect market from submission
                        demo_market = detect_market(selected_sub['submission_number'])
                        demo_market_content = get_market_content(demo_market)
                        
                        # Merge base and recommended endorsements
                        all_endorsements = {**demo_market_content['endorsements']['base'], 
                                           **demo_market_content['endorsements']['recommended']}
                        
                        status_value = (selected_sub.get('status') or 'Triaged')
                        completeness_value = selected_sub.get('completeness') or 74
                        priority_value = selected_sub.get('priority_score') or 4.8
                        appetite_value = selected_sub.get('risk_appetite') or 'High'
                        bind_available = status_value.upper() == 'QUOTED' and selected_sub.get('accepted', False)

                        st.session_state.submission_state = {
                            'status': status_value,
                            'completeness': completeness_value,
                            'priority_score': priority_value,
                            'risk_appetite': appetite_value,
                            'is_summary_visible': False,
                            'is_proposal_visible': False,
                            'is_recs_visible': False,
                            'is_comparison_visible': False,
                            'quotes': [],
                            'endorsements': all_endorsements,
                            'widget_key_suffix': '',
                            'bind_available': bind_available,
                            'bind_suppressed': False
                        }
                    
                    st.rerun()
                
        else:
            st.info("No active submissions found.")
    
    with tab2:
        bound_subs = [s for s in all_submissions if s['status'].upper() == 'BOUND']
        
        # Show bound submissions
        if bound_subs:
            st.caption(f"Showing {len(bound_subs)} bound submission(s)")
            df_bound = pd.DataFrame([{
                'Account': s['account_name'],
                'Submission': s['submission_number'],
                'Broker': s['broker'],
                'Effective Date': s['effective_date'].strftime('%Y-%m-%d') if s['effective_date'] else 'N/A',
                'Priority Score': f"{s['priority_score']:.1f}" if s['priority_score'] else 'N/A'
            } for s in bound_subs])
            # Style the dataframe to set font size to 1rem
            styled_df_bound = df_bound.style.set_table_styles([
                {
                    'selector': 'td, th',
                    'props': [('font-size', '1rem')]
                },
                {
                    'selector': 'table',
                    'props': [('font-size', '1rem')]
                }
            ])
            st.dataframe(styled_df_bound, use_container_width=True, hide_index=True)
        else:
            st.info("No bound submissions yet. Complete the quote process to bind a policy.")
    
    with tab3:
        declined_subs = [s for s in all_submissions if s['status'].upper() == 'DECLINED']
        if declined_subs:
            st.caption(f"Showing {len(declined_subs)} declined submission(s)")
            df_declined = pd.DataFrame([{
                'Account': s['account_name'],
                'Submission': s['submission_number'],
                'Broker': s['broker'],
                'Reason': 'Out of appetite'
            } for s in declined_subs])
            # Style the dataframe to set font size to 1rem
            styled_df_declined = df_declined.style.set_table_styles([
                {
                    'selector': 'td, th',
                    'props': [('font-size', '1rem')]
                },
                {
                    'selector': 'table',
                    'props': [('font-size', '1rem')]
                }
            ])
            st.dataframe(styled_df_declined, use_container_width=True, hide_index=True)
        else:
            st.info("No declined submissions.")
    
    # Reset button
    st.markdown("---")
    # Market selection dropdown and reset button in one line
    col_market, col_reset = st.columns([1, 1])
    
    with col_market:
        market_option = st.selectbox(
            "",
            options=["German SHUK", "U.S. Workers' Compensation"],
            index=0,  # German SHUK is default/preselected
            key="market_selection"
        )
    
    # Map display name to internal value
    market_value = 'german' if market_option == "German SHUK" else 'us'
    
    with col_reset:
        if st.button("🔄 Reset Demo Data", type="secondary", use_container_width=True, help="Reset all submissions to selected market demo state"):
            with st.spinner(f"Resetting demo data with {market_option}..."):
                success, message = reset_demo_database(market=market_value)
                
                if success:
                    # Clear session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.success(f"✅ {message}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Error: {message}")
                    if len(message) > 100:
                        with st.expander("See full error"):
                            st.code(message)

def render_submission_detail():
    """Render the detailed submission view"""
    # Render chatbot sidebar with popover-style features
    render_chatbot_sidebar()
    
    # Add sticky header
    logo_path = os.path.join(os.path.dirname(__file__), 'guidewire.png')
    logo_base64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
    
    # Apply same header styling as dashboard page
    st.markdown(f"""
    <style>
    /* Style header background */
    header[data-testid="stHeader"] {{
        background-color: #3c5c6c !important;
        position: relative !important;
        height: 3.5rem !important;
    }}
    
    /* DON'T hide Streamlit's header content - keep navigation buttons visible */
    /* Just style the header container to show our content on the left */
    header[data-testid="stHeader"] > div {{
        background-color: transparent !important;
    }}
    
    /* Reduce space between header and main content - BOTH margin AND transform for vertical */
    /* Reduce both left and right padding using negative margins */
    [data-testid="stAppViewContainer"] {{
        padding-top: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        max-width: calc(100% + 8rem) !important;
    }}
    
    [data-testid="stAppViewContainer"] > .main {{
        padding-top: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-top: -60px !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        transform: translateY(-60px) !important;
        max-width: calc(100% + 8rem) !important;
        width: calc(100% + 8rem) !important;
    }}
    
    [data-testid="stAppViewBlockContainer"] {{
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        max-width: calc(100% + 8rem) !important;
    }}
    
    .main .block-container {{
        padding-top: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-top: -60px !important;
        margin-left: -4rem !important;
        margin-right: -4rem !important;
        transform: translateY(-60px) !important;
        max-width: calc(100% + 8rem) !important;
        width: calc(100% + 8rem) !important;
    }}
    
    /* Target the first element container with both margin and transform */
    .main .element-container:first-child {{
        margin-top: -10px !important;
        padding-top: 0 !important;
        transform: translateY(-10px) !important;
    }}
    
    /* Also target any markdown elements that might add space */
    .main .element-container:first-child .stMarkdown {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    
    /* Target appviewblock */
    [data-testid="stAppViewBlockContainer"] {{
        margin-top: -60px !important;
        transform: translateY(-60px) !important;
        padding-top: 0 !important;
    }}
    
    /* Try targeting the space directly after header */
    header[data-testid="stHeader"] ~ * {{
        margin-top: -60px !important;
        transform: translateY(-60px) !important;
    }}
    
    /* Inject logo and text using CSS - positioned on the left, buttons stay on right */
    header[data-testid="stHeader"]::before {{
        content: '';
        display: inline-block;
        width: 28px;
        height: 28px;
        background-image: url('data:image/png;base64,{logo_base64}');
        background-size: contain;
        background-repeat: no-repeat;
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 10;
    }}
    
    header[data-testid="stHeader"]::after {{
        content: 'Guidewire Underwriting Center for DräumVersicherung';
        color: white;
        font-size: 1.25rem !important;
        font-weight: 400;
        letter-spacing: 0.3px;
        position: absolute;
        left: 60px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 10;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.selected_submission:
        st.error("No submission selected")
        return
    
    # Get submission details
    details = get_submission_details(st.session_state.selected_submission)
    if not details:
        st.error("Submission not found")
        return
    
    submission = details['submission']
    account = details['account']
    broker = details['broker']
    
    # Detect market and get market-specific content
    market = detect_market(submission.submission_number, account.country)
    market_content = get_market_content(market)
    recs = market_content['ai_recommendations']  # Define at function level for use in multiple places
    state = st.session_state.get('submission_state', {})

    # Determine documents and optional AI status message for accepted German quote
    documents_to_display = list(market_content['documents'])
    is_moebel_case = submission.submission_number in ['SUB-2026-001', 'SUB-2026-001-DE']
    submission_status_upper = (submission.status or '').upper()
    if is_moebel_case and submission_status_upper == 'QUOTED' and bool(getattr(submission, 'accepted', False)):
        if market == 'german':
            documents_to_display = [
                "📎 Moebel_Schmidt_Antrag_signed.pdf (4. Nov 2025 09:30)",
                "📎 Appendix.pdf (4. Nov 2025 09:35)",
                "📧 Email: Akzeptiert (4. Nov 2025 12:45)"
            ]
        else:
            documents_to_display = [
                "📎 FloorDecor_Application_Signed.pdf (Nov 4 2025 09:30)",
                "📎 Appendix.pdf (Nov 4 2025 09:35)",
                "📧 Email: Accepted (Nov 4 2025 12:45)"
            ] 
    
    # Breadcrumb navigation
    if st.button("← Return to Submission List"):
        if is_moebel_case and state.get('status', '').upper() == 'QUOTED':
            update_submission_accepted(st.session_state.selected_submission, True)
            st.session_state.submission_state['bind_available'] = True
            st.session_state.submission_state['bind_suppressed'] = False
        st.session_state.current_screen = 'dashboard'
        st.rerun()
    
    st.markdown(f'<h3 style="margin-bottom: 0;">{account.name}</h3>', unsafe_allow_html=True)
    st.caption(f"Submission: {submission.submission_number}")
    
    st.markdown("---")
    
    # === SUBMISSION KPI ROW ===
    submission_status_upper = (submission.status or state.get('status', '')).upper()
    state['status'] = submission.status or state.get('status', 'Triaged')
    if submission.completeness is not None:
        state['completeness'] = submission.completeness
    if submission.priority_score is not None:
        state['priority_score'] = submission.priority_score
    if submission.risk_appetite:
        state['risk_appetite'] = submission.risk_appetite
    if not state.get('bind_suppressed', False):
        state['bind_available'] = submission_status_upper == 'QUOTED' and bool(getattr(submission, 'accepted', False))
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Status</div>
            <div class="kpi-value">{get_status_badge(state['status'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Risk Appetite</div>
            <div class="kpi-value">{get_appetite_badge(state['risk_appetite'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Priority Score</div>
            <div class="kpi-value">{state['priority_score']:.1f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Completeness</div>
            <div class="kpi-value">{state['completeness']}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === RECENT UPDATES SECTION ===
    st.markdown("### 📄 Recent Updates")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        docs_list = "\n".join([f"- {doc}" for doc in documents_to_display])
        st.markdown(f"**Recent Documents:**\n{docs_list}")
    
    with col2:
        if not state['is_summary_visible']:
            if st.button("✨ Summarize with AI", use_container_width=True):
                show_loading_modal([
                    "Understanding Documents",
                    "Creating the Summary"
                ])
                st.session_state.submission_state['is_summary_visible'] = True
                st.rerun()
    
    # === AI SMART SUMMARY (Conditionally rendered) ===
    if state['is_summary_visible']:
        st.markdown("---")
        st.markdown("### 🤖 Smart Summary")
        
        ai_summary = market_content['ai_summary']
        if is_moebel_case and submission_status_upper == 'QUOTED' and bool(getattr(submission, 'accepted', False)):
            summary_text = "<strong>Status Update:</strong> Der Kunde hat das Angebot unterschrieben und akzeptiert. Die Police ist bereit zur Bindung."
        else:
            risk_factors_html = ''.join([f'<li>{factor}</li>' for factor in ai_summary['risk_factors']])
            summary_text = f"""
            <p><strong>Business Overview:</strong> {ai_summary['business_overview']}</p>
            <p><strong>Coverage Requested:</strong> {ai_summary['coverage_requested']}</p>
            <p><strong>Loss History:</strong> {ai_summary['loss_history']}</p>
            <p><strong>Risk Factors:</strong></p>
            <ul style="padding-left: 1.5rem;">
                {risk_factors_html}
            </ul>
            <p><strong>Recommendation:</strong> {ai_summary['recommendation']}</p>
            """
        
        summary_html = f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                <h4 style="color: white; margin-top: 0;">AI-Generated Submission Analysis</h4>
                {summary_text}
            </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)
        
        if not (is_moebel_case and submission_status_upper == 'QUOTED' and bool(getattr(submission, 'accepted', False))):
            st.markdown("**Impact on Completeness:**")
            st.info(market_content['completeness_impact'])
        
        col_accept1, col_accept2, col_accept3 = st.columns([1, 1, 2])
        with col_accept1:
            if st.button("✅ Accept Summary", use_container_width=True):
                show_loading_modal([
                    "Updating Completeness Score by 12 points",
                    "Unlocking Proposal Creation"
                ])
                
                # Update session state
                st.session_state.submission_state['completeness'] = 86
                st.session_state.submission_state['status'] = 'In Review'
                
                # Save to database
                update_submission_status(
                    st.session_state.selected_submission,
                    'In Review',
                    completeness=86
                )
                
                st.success("✅ Summary accepted! Completeness updated.")
                time.sleep(1)
                st.rerun()
        
        with col_accept2:
            if st.button("❌ Dismiss", use_container_width=True, key="dismiss_summary"):
                st.session_state.submission_state['is_summary_visible'] = False
                st.rerun()
    
    # === GENERATE PROPOSAL BUTTON (Conditionally rendered) ===
    if state['completeness'] >= 86 and not state['is_proposal_visible']:
        st.markdown("---")
        col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
        with col_gen2:
            if st.button("+ Generate Proposal", use_container_width=True):
                show_loading_modal([
                    "Retrieving APD Product Details",
                    "Calculating Quote with PricingCenter",
                    "Finalizing Proposal & Quote"
                ])
                st.session_state.submission_state['is_proposal_visible'] = True
                st.session_state.submission_state['quotes'] = ['base']
                st.rerun()
    
    # === PROPOSAL DETAILS (Conditionally rendered) ===
    if state['is_proposal_visible']:
        st.markdown("---")
        st.markdown("### 📊 Proposal Details")
        
        col_proposal1, col_proposal2 = st.columns(2)
        
        with col_proposal1:
            st.markdown("**Coverages:**")
            # Display market-specific coverages
            for i, coverage in enumerate(market_content['coverages']):
                cov_label = f"{coverage['name']} (Limit: {coverage['limit']})"
                st.checkbox(cov_label, value=coverage['selected'], disabled=True, key=f"cov_{i}")
        
        with col_proposal2:
            st.markdown("**Endorsements:**")
            for endo_name, is_checked in state['endorsements'].items():
                # Create checkbox with current state value
                # Use widget_key_suffix to force refresh when programmatically updated
                checkbox_val = st.checkbox(
                    endo_name,
                    value=state['endorsements'][endo_name],  # Always read from session state
                    key=f"endo_{endo_name}_{state.get('widget_key_suffix', '')}"
                )
                # Only update if user manually changed it (different from current state)
                if checkbox_val != state['endorsements'][endo_name]:
                    st.session_state.submission_state['endorsements'][endo_name] = checkbox_val
        
        # === BASE QUOTE CARD ===
        if 'base' in state['quotes']:
            st.markdown("---")
            st.markdown(f"#### 💵 {market_content['quotes']['base_title']}")
            
            base_quote = market_content['quotes']['base']
            st.markdown(f"""
            <div class="quote-card">
                <h2 style="color: #2563eb;">{base_quote['premium']}</h2>
                <p><strong>Annual Premium</strong></p>
                <hr>
                <p><strong>Rating Basis:</strong> {base_quote['rating_basis']}</p>
                <p><strong>{base_quote['exposure_label']}:</strong> {base_quote['exposure_value']}</p>
                <p><strong>Experience Mod:</strong> {base_quote['experience_mod']}</p>
                <p><strong>{base_quote['geography_label']}:</strong> {base_quote['geography_value']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_analyze1, col_analyze2 = st.columns(2)
            
            with col_analyze1:
                if not state['is_recs_visible']:
                    if st.button("🤖 Analyze Proposal", use_container_width=True):
                        st.session_state.show_loading = True
                        st.session_state.loading_message = "Analyzing proposal with AI..."
                        time.sleep(2)
                        st.session_state.submission_state['is_recs_visible'] = True
                        st.session_state.show_loading = False
                        st.rerun()
            
            with col_analyze2:
                if state['status'].upper() != 'QUOTED':
                    if st.button("📧 Send to Broker", type="primary", use_container_width=True, key="send_base_quote"):
                        show_loading_modal([
                            "Creating Broker Quote page",
                            "Sending Email",
                            "Updating Proposal Status"
                        ])
                        
                        # Update status to Quoted and mark as accepted (ready to bind)
                        st.session_state.submission_state['status'] = 'Quoted'
                        st.session_state.submission_state['bind_available'] = False
                        st.session_state.submission_state['bind_suppressed'] = True
                        update_submission_status(
                            st.session_state.selected_submission,
                            'Quoted'
                        )
                        update_submission_accepted(
                            st.session_state.selected_submission,
                            True
                        )
                        
                        st.success("✅ Quote sent to broker!")
                        time.sleep(1)
                        st.rerun()
        
        # === AI RECOMMENDATIONS (Conditionally rendered) ===
        if state['is_recs_visible'] and not (is_moebel_case and submission_status_upper == 'QUOTED' and bool(getattr(submission, 'accepted', False))):
            st.markdown("---")
            st.markdown("### 💡 Recommended Changes")
            
            # Build recommendations text from market content
            recommendations_text = f"**{recs['title']}**\n\n⚠️ **{recs['subtitle']}**\n\n"
            
            for i, rec in enumerate(recs['items'], 1):
                recommendations_text += f"**{i}. {rec['name']}**\n"
                recommendations_text += f"- **{rec['rationale_label']}:** {rec['rationale']}\n"
                recommendations_text += f"- **{rec['premium_label']}:** {rec['premium_impact']}\n"
                recommendations_text += f"- **{rec['benefit_label']}:** {rec['benefit']}\n\n"
            
            st.info(recommendations_text)
            
            col_rec1, col_rec2, col_rec3 = st.columns([1, 1, 2])
            with col_rec1:
                if st.button("✅ Accept Recommendation", use_container_width=True):
                    show_loading_modal([
                        "Adding Endorsements / Coverages"
                    ])
                    
                    # Update endorsements based on recommendations
                    for rec in recs['items']:
                        endorsement_name = rec['name']
                        if endorsement_name in st.session_state.submission_state['endorsements']:
                            st.session_state.submission_state['endorsements'][endorsement_name] = True
                    
                    # Change widget key suffix to force checkbox refresh
                    import random
                    st.session_state.submission_state['widget_key_suffix'] = str(random.randint(1000, 9999))
                    if 'generated' not in st.session_state.submission_state['quotes']:
                        st.session_state.submission_state['quotes'].append('generated')
                        st.session_state.submission_state['is_comparison_visible'] = False
                    
                    st.success("✅ Endorsements added!")
                    time.sleep(1)
                    st.rerun()
            
            with col_rec2:
                if st.button("❌ Dismiss", use_container_width=True, key="dismiss_recommendation"):
                    st.session_state.submission_state['is_recs_visible'] = False
                    st.rerun()
        
        # === GENERATED QUOTE CARD ===
        if 'generated' in state['quotes'] and not state['is_comparison_visible']:
            st.markdown("---")
            st.markdown(f"#### 💵 {market_content['quotes']['generated_title']}")
            
            # Calculate premium based on selected endorsements from market config
            base_quote = market_content['quotes']['base']
            base_premium_value = int(base_quote['premium'].replace('$', '').replace('€', '').replace(',', ''))
            premium = base_premium_value
            endorsement_list = []
            
            # Apply premium changes for recommended endorsements
            for rec in recs['items']:
                endorsement_name = rec['name']
                if state['endorsements'].get(endorsement_name, False):
                    # Parse premium impact (e.g., "+€29.500" or "-€7.800")
                    impact_str = rec['premium_impact'].replace('€', '').replace('$', '').replace('.', '').replace(',', '')
                    if '+' in impact_str:
                        premium += int(impact_str.replace('+', ''))
                    elif '-' in impact_str:
                        premium -= int(impact_str.replace('-', ''))
                    
                    # Add short name to endorsement list
                    short_name = endorsement_name.replace(' Baustein', '').replace(' Endorsement', '')
                    endorsement_list.append(short_name)
            
            # Add base endorsements
            for endo_name, is_selected in market_content['endorsements']['base'].items():
                if is_selected:
                    short_name = endo_name.replace(' Baustein', '').replace(' Endorsement', '')
                    if short_name not in endorsement_list:
                        endorsement_list.append(short_name)
            
            endorsement_text = ", ".join(endorsement_list)
            
            # Format premium with currency symbol
            currency = '€' if market == 'german' else '$'
            st.markdown(f"""
            <div class="quote-card quote-card-selected">
                <h2 style="color: #2563eb;">{currency}{premium:,}</h2>
                <p><strong>Annual Premium</strong></p>
                <hr>
                <p><strong>Rating Basis:</strong> {base_quote['rating_basis']} + Endorsements</p>
                <p><strong>{base_quote['exposure_label']}:</strong> {base_quote['exposure_value']}</p>
                <p><strong>Experience Mod:</strong> {base_quote['experience_mod']}</p>
                <p><strong>{base_quote['geography_label']}:</strong> {base_quote['geography_value']}</p>
                <p><strong>Endorsements:</strong> {endorsement_text}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_compare1, col_compare2, col_bind = st.columns(3)
            
            with col_compare1:
                if st.button("📊 Compare Quotes", use_container_width=True):
                    st.session_state.show_loading = True
                    st.session_state.loading_message = "Retrieving Quotes..."
                    time.sleep(2)
                    st.session_state.submission_state['is_comparison_visible'] = True
                    st.session_state.show_loading = False
                    st.rerun()
            
            with col_compare2:
                if state['status'].upper() != 'QUOTED':
                    if st.button("📧 Quote", type="primary", use_container_width=True, key="send_generated_quote"):
                        show_loading_modal([
                            "Creating Broker Quote page",
                            "Sending Email",
                            "Updating Proposal Status"
                        ])
                        
                        # Update session state
                        st.session_state.submission_state['status'] = 'Quoted'
                        st.session_state.submission_state['bind_available'] = False
                        st.session_state.submission_state['bind_suppressed'] = True
                        
                        # Save to database and mark as accepted (ready to bind)
                        update_submission_status(
                            st.session_state.selected_submission,
                            'Quoted'
                        )
                        update_submission_accepted(
                            st.session_state.selected_submission,
                            True
                        )
                        
                        st.success("✅ Quote sent to broker successfully!")
                        time.sleep(2)
                        st.rerun()

            with col_bind:
                if state.get('bind_available') and submission_status_upper == 'QUOTED' and bool(getattr(submission, 'accepted', False)):
                    if st.button("✅ Bind Policy", type="primary", use_container_width=True, key="bind_generated_quote"):
                        import random
                        policy_number = random.randint(2800000000, 2899999999)
                        show_loading_modal([
                            "Sending data to PolicyCenter for Binding",
                            f"Policy Bound: {policy_number}"
                        ])

                        update_submission_status(st.session_state.selected_submission, 'BOUND')

                        # Update dashboard KPIs to reflect new bound policy
                        st.session_state.dashboard_kpis['turnaround_time'] = 3.9
                        st.session_state.dashboard_kpis['hit_ratio'] = 37
                        st.session_state.dashboard_kpis['earned_premium'] = 1.85
                        st.session_state.chart_data['hit_ratio_q4'] = 37
                        st.session_state.chart_data['premium_q4'] = 1.85

                        st.session_state.submission_state['status'] = 'Bound'
                        st.session_state.submission_state['bind_available'] = False
                        st.session_state.submission_state['bind_suppressed'] = False

                        st.success("✅ Policy bound successfully! Metrics updated.")
                        time.sleep(1)
                        st.rerun()
        
        # === QUOTE COMPARISON VIEW ===
        if state['is_comparison_visible']:
            st.markdown("---")
            st.markdown("### 📊 Quote Comparison")
            
            comp_col1, comp_col2 = st.columns(2)
            
            # Get market-specific data
            base_quote = market_content['quotes']['base']
            base_premium_value = int(base_quote['premium'].replace('$', '').replace('€', '').replace(',', ''))
            currency = '€' if market == 'german' else '$'
            
            with comp_col1:
                st.markdown(f"### {market_content['quotes']['base_title']}")
                st.markdown(f"#### Premium: {base_quote['premium']}")
                
                st.markdown("**Coverages:**")
                coverages_text = "\n".join([f"- {cov['name']} (Limit: {cov['limit']})" for cov in market_content['coverages'] if cov['selected']])
                st.markdown(coverages_text)
                
                st.markdown("**Endorsements:**")
                base_endorsements = [name for name, selected in market_content['endorsements']['base'].items() if selected]
                base_endo_text = "\n".join([f"- {endo.replace(' Baustein', '').replace(' Endorsement', '')}" for endo in base_endorsements])
                st.markdown(base_endo_text)
                
                st.markdown(f"**{base_quote['geography_label']}:** {base_quote['geography_value']}")
            
            with comp_col2:
                st.markdown(f"### {market_content['quotes']['generated_title']}")
                
                # Calculate premium and build endorsement list
                generated_premium = base_premium_value
                premium_changes = []
                
                # Add selected optional endorsements from recommendations
                for rec in recs['items']:
                    endorsement_name = rec['name']
                    if state['endorsements'].get(endorsement_name, False):
                        # Parse premium impact
                        impact_str = rec['premium_impact'].replace('€', '').replace('$', '').replace('.', '').replace(',', '')
                        impact_value = 0
                        if '+' in impact_str:
                            impact_value = int(impact_str.replace('+', ''))
                            generated_premium += impact_value
                            premium_changes.append(f"+{currency}{impact_value:,}")
                        elif '-' in impact_str:
                            impact_value = int(impact_str.replace('-', ''))
                            generated_premium -= impact_value
                            premium_changes.append(f"-{currency}{impact_value:,}")
                
                premium_diff = generated_premium - base_premium_value
                if premium_diff > 0:
                    premium_display = f"#### Premium: {currency}{generated_premium:,} 🔼 (+{currency}{premium_diff:,})"
                elif premium_diff < 0:
                    premium_display = f"#### Premium: {currency}{generated_premium:,} 🔽 (-{currency}{abs(premium_diff):,})"
                else:
                    premium_display = f"#### Premium: {currency}{generated_premium:,}"
                
                st.markdown(premium_display)
                
                st.markdown("**Coverages:**")
                st.markdown(coverages_text)
                
                st.markdown("**Endorsements:**")
                st.markdown(base_endo_text)
                
                # Add selected endorsements with NEW badges
                for rec in recs['items']:
                    endorsement_name = rec['name']
                    if state['endorsements'].get(endorsement_name, False):
                        short_name = endorsement_name.replace(' Baustein', '').replace(' Endorsement', '')
                        st.markdown(f"- {short_name} ✨ **NEW**")
                
                st.markdown("")
                st.markdown(f"**{base_quote['geography_label']}:** {base_quote['geography_value']}")
            
            st.markdown("---")
            
            # Build dynamic recommendation text from selected endorsements
            rec_parts = []
            for rec in recs['items']:
                endorsement_name = rec['name']
                if state['endorsements'].get(endorsement_name, False):
                    # Extract benefit text (simplified)
                    benefit = rec['benefit'].lower()
                    rec_parts.append(benefit)
            
            if rec_parts:
                rec_text = f"**💡 Recommendation:** The Generated Quote provides {' and '.join(rec_parts)}. The premium adjustments reflect the risk-benefit balance."
            else:
                rec_text = "**💡 Recommendation:** Base quote provides standard coverage. Consider adding recommended endorsements for enhanced protection."
            
            st.info(rec_text)
            
            if st.button("← Back to Quotes"):
                st.session_state.submission_state['is_comparison_visible'] = False
                st.rerun()
    
    # === APPLICANT INFO (Always visible) ===
    st.markdown("---")
    st.markdown("### 🏢 Applicant Information")
    
    # Create tabs based on market
    if market == 'us':
        tabs = st.tabs(["Headquarters", "Operations", "Risk Description", "OSHA-Related Review", "SAFER-Related Review", "Exposure Summary", "Claim & Loss History"])
    else:  # German market
        tabs = st.tabs(["Headquarters", "Operations", "Risk Description", "Berufsgenossenschaft Review", "Fuhrpark & Logistik", "Risiko-Exposition", "Schaden-Historie"])
    
    with tabs[0]:  # Headquarters
        st.markdown(f"""
        **Legal Name:** {account.name}
        
        **Address:** {account.address}, {account.city}, {account.country}
        
        **Phone:** {account.phone}
        
        **Email:** {account.email}
        
        **Broker:** {broker.name if broker else 'Direct'}
        
        **Effective Date:** {submission.effective_date.strftime('%B %d, %Y') if submission.effective_date else 'TBD'}
        """)
    
    with tabs[1]:  # Operations
        comp_info = market_content['company_info']
        st.markdown(f"""
        **Industry:** {comp_info['industry']}
        
        **Number of Locations:** {comp_info['locations']}
        
        **Annual Revenue:** {comp_info['revenue']}
        
        **Number of Employees:** {comp_info['employees']}
        
        **Annual Payroll:** {comp_info['payroll']}
        
        **Years in Business:** {comp_info['years_in_business']}
        """)
    
    with tabs[2]:  # Risk Description
        ops = market_content['operations']
        primary_ops = '\n        - '.join(ops['primary'])
        risk_chars = '\n        - '.join(ops['risk_characteristics'])
        safety_progs = '\n        - '.join(ops['safety_programs'])
        
        st.markdown(f"""
        **Primary Operations:**
        - {primary_ops}
        
        **Risk Characteristics:**
        - {risk_chars}
        
        **Safety Programs:**
        - {safety_progs}
        """)
    
    # Additional tabs for U.S. market only
    if market == 'us':
        with tabs[3]:  # OSHA-Related Review
            st.markdown("""
            **OSHA Compliance Status:** ✅ Compliant
            
            **Last OSHA Inspection:** March 15, 2024
            
            **Inspection Results:**
            - No violations cited
            - Safety program review: Satisfactory
            - Employee training records: Complete
            
            **OSHA 300 Log Summary (2024):**
            - Total Recordable Cases: 8
            - Days Away/Restricted/Transfer (DART) Cases: 3
            - Lost Workday Cases: 2
            
            **OSHA Incident Rate:**
            - Total Recordable Incident Rate (TRIR): 2.1 (Industry Average: 3.5)
            - DART Rate: 0.8 (Industry Average: 1.8)
            
            **Safety Citations History:**
            - 2024: None
            - 2023: None
            - 2022: 1 Minor (corrected within 30 days)
            """)
        
        with tabs[4]:  # SAFER-Related Review
            st.markdown("""
            **SAFER System Check:** ✅ Verified
            
            **Fleet Safety Status:**
            - Total Commercial Vehicles: 45 delivery trucks
            - DOT Compliance: Current
            - Drug & Alcohol Testing Program: Active
            
            **Driver Qualifications:**
            - Licensed Drivers: 52
            - MVR Review Frequency: Quarterly
            - Average Driver Experience: 7.3 years
            
            **Vehicle Maintenance:**
            - Preventive Maintenance Program: Documented
            - Vehicle Inspection Program: Monthly
            - Out-of-Service Rate: 0.8% (Excellent)
            
            **Safety Scores (Last 24 months):**
            - Unsafe Driving: 0.2 (Good)
            - Hours of Service Compliance: 0.4 (Good)
            - Vehicle Maintenance: 0.1 (Excellent)
            - Driver Fitness: 0.0 (Excellent)
            """)
        
        with tabs[5]:  # Exposure Summary
            st.markdown("""
            **Payroll Distribution:**
            
            | Classification | Employees | Annual Payroll | Rate |
            |----------------|-----------|----------------|------|
            | Retail Store - Sales | 1,200 | $180M | $0.85 |
            | Warehouse Operations | 650 | $150M | $2.50 |
            | Delivery Drivers | 52 | $45M | $4.20 |
            | Office/Clerical | 320 | $65M | $0.20 |
            | Management | 28 | $10M | $0.15 |
            
            **Total Payroll:** $450,000,000
            
            **Geographic Distribution:**
            - California: $95M (21%)
            - Texas: $72M (16%)
            - Florida: $58M (13%)
            - New York: $45M (10%)
            - Other 38 states: $180M (40%)
            
            **High-Hazard Operations:**
            - Forklift operations: 650 employees
            - Loading dock activities: 400 employees
            - Heavy lifting (>50 lbs): 850 employees
            """)
        
        with tabs[6]:  # Claim & Loss History
            st.markdown("""
            **3-Year Loss Summary (2022-2024):**
            
            **Total Incurred Losses:** $2,450,000
            **Total Payroll (3 years):** $1,350,000,000
            **Loss Rate:** 0.18%
            
            **Claim Count by Year:**
            - 2024: 42 claims ($780,000)
            - 2023: 48 claims ($890,000)
            - 2022: 51 claims ($780,000)
            
            **Top Claim Categories:**
            1. Slips/Falls: 38% of claims, $920,000
            2. Lifting Injuries: 24% of claims, $610,000
            3. Struck By Object: 18% of claims, $440,000
            4. Vehicle Accidents: 12% of claims, $310,000
            5. Other: 8% of claims, $170,000
            
            **Large Loss Activity:**
            - Claims >$100K: 3 total
            - Largest Single Claim: $285,000 (warehouse forklift incident, 2023)
            
            **Experience Modification:**
            - Current Mod: 0.95
            - 3-Year Trend: Improving (2022: 1.02 → 2023: 0.98 → 2024: 0.95)
            
            **Return-to-Work Program:**
            - Modified Duty Program: Active
            - Average Days to Return: 18 days (Industry Avg: 32 days)
            - RTW Success Rate: 87%
            """)
    else:  # German market tabs
        with tabs[3]:  # Berufsgenossenschaft Review
            st.markdown("""
            **BG-Mitgliedschaft:** Berufsgenossenschaft Handel und Warenlogistik (BGHW)
            
            **Compliance-Status:** ✅ Vollständig konform
            
            **Letzte BG-Prüfung:** 12. April 2024
            
            **Prüfungsergebnisse:**
            - Keine Beanstandungen
            - Gefährdungsbeurteilungen: Aktuell und vollständig
            - Unterweisung der Mitarbeiter: Dokumentiert
            - PSA-Ausstattung: Ausreichend
            
            **Arbeitsunfallstatistik 2024:**
            - Meldepflichtige Arbeitsunfälle: 12
            - Arbeitsunfälle mit Ausfalltagen: 5
            - Wegeunfälle: 3
            
            **Unfallquote (1.000-Mann-Quote):**
            - Unternehmensquote: 18,2 (Branchendurchschnitt: 28,5)
            - Trend: Rückläufig (2022: 24,1 → 2023: 20,8 → 2024: 18,2)
            
            **Sicherheitsmaßnahmen:**
            - Sicherheitsbeauftragter: Bestellt und geschult
            - Betriebsarzt: Regelmäßige Begehungen
            - Brandschutzhelfer: 85 geschulte Mitarbeiter
            - Erste-Hilfe-Personal: 120 ausgebildete Ersthelfer
            
            **BG-Beitragssatz 2025:** 0,92% der Lohnsumme (unter Branchendurchschnitt)
            """)
        
        with tabs[4]:  # Fuhrpark & Logistik
            st.markdown("""
            **Fuhrpark-Übersicht:** ✅ Gut gewartet
            
            **Fahrzeugbestand:**
            - Transporter (bis 3,5t): 38 Fahrzeuge
            - LKW (7,5t - 12t): 15 Fahrzeuge
            - Firmen-PKW: 25 Fahrzeuge
            - Durchschnittsalter: 3,2 Jahre
            
            **Fahrerqualifikation:**
            - Berufskraftfahrer: 53
            - Module nach BKrFQG: Alle aktuell
            - Fahrerunterweisung: Quartalsweise
            - Durchschnittliche Berufserfahrung: 8,4 Jahre
            
            **Flottenmanagement:**
            - Telematik-System: Flächendeckend installiert
            - Wartungsintervalle: Herstellervorgaben eingehalten
            - HU/AU-Quote: 100% aktuell
            - Fahrtenschreiber-Auswertung: Regelmäßig
            
            **Schadensstatistik 2024:**
            - Haftpflichtschäden: 8 (Schadenquote: 0,4%)
            - Kaskoschäden: 12 (meist Parkschäden)
            - Durchschnittliche Schadenhöhe: €2.450
            
            **Logistik-KPIs:**
            - Lieferpünktlichkeit: 96,8%
            - Beschädigungsquote Transport: 0,08%
            - Kilometerleistung p.a.: 2,8 Mio. km
            """)
        
        with tabs[5]:  # Risiko-Exposition
            st.markdown("""
            **Umsatzverteilung nach Geschäftsbereichen:**
            
            | Geschäftsbereich | Mitarbeiter | Jahresumsatz | Anteil |
            |------------------|-------------|--------------|---------|
            | Filialen (Verkauf) | 1.850 | €280M | 62% |
            | Lager & Logistik | 680 | €95M | 21% |
            | Online-Handel | 145 | €55M | 12% |
            | Verwaltung | 125 | €20M | 5% |
            
            **Gesamtumsatz:** €450 Millionen
            **Gesamte Lohnsumme:** €85 Millionen
            
            **Standortverteilung:**
            - Nordrhein-Westfalen: 28 Filialen (33%)
            - Bayern: 22 Filialen (26%)
            - Baden-Württemberg: 18 Filialen (21%)
            - Hessen: 10 Filialen (12%)
            - Sonstige Bundesländer: 7 Filialen (8%)
            
            **Hochrisiko-Bereiche:**
            - Staplerfahrer (Flurförderzeuge): 85 Mitarbeiter
            - Wareneingang/-ausgang: 420 Mitarbeiter
            - Schwere Lasten (>25kg): 650 Mitarbeiter
            - Höhenarbeiten (>3m): 125 Mitarbeiter
            
            **Versicherungssummen:**
            - Betriebshaftpflicht: €10 Millionen
            - Sachversicherung Gebäude: €15 Millionen
            - Sachversicherung Inventar: €25 Millionen
            - Betriebsunterbrechung: €5 Millionen (12 Monate)
            """)
        
        with tabs[6]:  # Schaden-Historie
            st.markdown("""
            **3-Jahres-Schadenübersicht (2022-2024):**
            
            **Gesamtschadenaufwand:** €1.680.000
            **Schadenquote:** 62% (Branchendurchschnitt: 75%)
            **Kombinierte Quote:** 98% (Profitabel)
            
            **Schadenzahl nach Jahr:**
            - 2024: 58 Schäden (€540.000)
            - 2023: 64 Schäden (€610.000)
            - 2022: 61 Schäden (€530.000)
            
            **Schadenarten (nach Aufwand):**
            1. Produkthaftpflicht: 28% (€470.000)
            2. Kundenverletzungen in Filialen: 24% (€405.000)
            3. Transport-/Montageschäden: 18% (€302.000)
            4. Sachschäden (Feuer, Einbruch): 16% (€270.000)
            5. Betriebsunterbrechung: 8% (€135.000)
            6. Sonstige: 6% (€98.000)
            
            **Großschäden (>€50.000):**
            - Anzahl: 4 Schäden
            - Größter Einzelschaden: €185.000 (Wasserschaden Zentrallager, 2023)
            
            **Schadenentwicklung:**
            - Trend: Stabil bis leicht rückläufig
            - Präventionsmaßnahmen: Zeigen Wirkung
            - Schadenreservierung: Konservativ, 95% Abwicklungsquote
            
            **Schaden-Management:**
            - Durchschnittliche Bearbeitungsdauer: 32 Tage
            - Regulierungsquote: 89% (außergerichtlich)
            - Kundenzufriedenheit Schadenabwicklung: 4,2/5,0
            
            **Risikoprävention:**
            - Qualitätssicherung: ISO 9001 zertifiziert
            - Lieferantenprüfung: Standardisiert
            - Mitarbeiterschulungen: 2x jährlich verpflichtend
            """)
    
    # === READY TO BIND SECTION ===
    if state.get('bind_available') and submission_status_upper == 'QUOTED' and bool(getattr(submission, 'accepted', False)):
        st.markdown("---")
        st.markdown("### ✅ Ready to Bind")
        bind_col1, bind_col2, bind_col3 = st.columns([1, 2, 1])
        with bind_col2:
            if st.button("✅ Bind Policy", type="primary", use_container_width=True, key="detail_bind_policy"):
                import random
                policy_number = random.randint(2800000000, 2899999999)
                show_loading_modal([
                    "Sending data to PolicyCenter for Binding",
                    f"Policy Bound: {policy_number}"
                ])

                update_submission_status(st.session_state.selected_submission, 'BOUND')

                # Update dashboard KPIs to reflect new bound policy
                st.session_state.dashboard_kpis['turnaround_time'] = 3.9
                st.session_state.dashboard_kpis['hit_ratio'] = 37
                st.session_state.dashboard_kpis['earned_premium'] = 1.85
                st.session_state.chart_data['hit_ratio_q4'] = 37
                st.session_state.chart_data['premium_q4'] = 1.85

                st.session_state.submission_state['status'] = 'Bound'
                st.session_state.submission_state['bind_available'] = False
                st.session_state.submission_state['bind_suppressed'] = False

                st.success("✅ Policy bound successfully! Metrics updated.")
                time.sleep(1)
                st.rerun()


# === MAIN APP ROUTING ===

def main():
    """Main application entry point"""
    
    # Render loading modal if active
    render_loading_modal()
    
    # Route to appropriate screen
    if st.session_state.current_screen == 'dashboard':
        render_dashboard()
    elif st.session_state.current_screen == 'submission_detail':
        render_submission_detail()

if __name__ == "__main__":
    main()

