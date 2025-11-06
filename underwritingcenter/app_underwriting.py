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
    Generates the full HTML/CSS for the modal,
    injecting the GIF and the current text.
    """
    return f"""
    <style>
        /* The Overlay (dimmed background) */
        .overlay {{
            position: fixed; /* Sit on top of the page content */
            width: 100%; /* Full width */
            height: 100%; /* Full height */
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.7); /* Black background with opacity */
            z-index: 9998; /* Specify a stack order */
        }}

        /* The Modal Box */
        .modal-content {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            width: 320px; /* Set a fixed width */
            text-align: center;
            z-index: 9999; /* Even higher stack order */
            color: #333; /* Text color for the modal */
        }}

        .modal-content img {{
            width: 80px; /* Adjust GIF size as needed */
            margin-bottom: 20px;
        }}
    </style>

    <div class="overlay">
        <div class="modal-content">
            <img src="data:image/gif;base64,{gif_base64}" alt="loading...">
            <p>{text}</p>
        </div>
    </div>
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
    
    # Create a placeholder for the modal
    loading_placeholder = st.empty()
    
    try:
        # Loop through each step
        for text in steps:
            # Generate the HTML with the current text
            modal_html = get_modal_html(gif_base64, text)
            
            # Update the placeholder's content
            loading_placeholder.markdown(modal_html, unsafe_allow_html=True)
            
            # Wait before next step
            time.sleep(duration_per_step)
    
    finally:
        # Clear the placeholder (removes the modal)
        loading_placeholder.empty()
    
    return loading_placeholder

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
        font-size: 1rem;
        color: #d1d5db;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ffffff;
        margin: 0.5rem 0;
    }
    
    .kpi-delta {
        font-size: 0.75rem;
        color: #10b981;
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
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
        font-size: 0.75rem;
    }
    
    .appetite-medium {
        background-color: #f59e0b;
        color: white;
        font-weight: 600;
        font-size: 0.75rem;
    }
    
    .appetite-low {
        background-color: #ef4444;
        color: white;
        font-weight: 600;
        font-size: 0.75rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.25rem;
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
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .quote-card-selected h2 {
        color: #2563eb !important;
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
        'widget_key_suffix': ''  # Used to force widget refresh
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
        padding-left: 30px !important;
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
    
    /* Style sidebar header - increase left padding to prevent cutoff */
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
        font-size: 0.875rem !important;
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
        font-size: 0.875rem !important;
    }
    
    /* Style suggested questions header */
    section[data-testid="stSidebar"] p strong {
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        display: block !important;
        margin-bottom: 4px !important;
    }
    

    
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] [data-testid="stChatMessageUser"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] [data-testid="stChatMessageAssistant"] {
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
    }
    
    /* Style text in chat messages - minimal spacing */
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] p,
    section[data-testid="stSidebar"] [data-testid="stChatMessage"] div {
        color: white !important;
        margin: 2px 0 !important;
        padding: 0 !important;
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
    
    /* Style user avatar container - light green */
    section[data-testid="stSidebar"] [data-testid="stChatMessageUser"] > div:first-child {
        background-color: #86efac !important;
        border-radius: 50% !important;
    }
    
    /* Style chat input - minimal margins, no bottom padding */
    section[data-testid="stSidebar"] [data-testid="stChatInput"] {
        margin-top: 4px !important;
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
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
        color: #93c5fd !important;
        text-decoration: none !important;
    }
    
    .sidebar-chat-disclaimer a:hover {
        text-decoration: underline !important;
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
    })();
    </script>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        # Chat header - Guidewire style
        st.markdown("### ✨ Underwriting Assistant")
        
        # Scrollable chat history container
        chat_container = st.container(height=600)
        with chat_container:
            # Welcome message (show once) - Guidewire style with avatar
            if st.session_state.show_welcome:
                with st.chat_message("assistant"):
                    st.markdown("""
                    • Submission volume **rose 12%** this week, with a surge in **Contractors and Healthcare industry**, aligning with broader market trends of these lines being written out of the admitted market.
                    
                    • Appetite alignment is strong in these segments, while **construction and hospitality show rising out-of-appetite flags**, reflecting inflation and claims volatility.
                    
                    • **Tier 1 brokers** contributed **71%** of complete, qualified submissions, while lower-tier brokers are submitting more distressed risks — likely a response to tightening market conditions.
                    
                    • With **8 stale submissions nearing auto-closure**, workflow discipline is key.
                    """)
                    
                    st.markdown("**Some things you could commonly ask for:**")
                    st.markdown("""
                    • Catch me up
                    • Create an action list
                    • Ask about my metrics
                    """)
            
            # Chat history using st.chat_message
            for msg in st.session_state.chat_messages:
                if msg['role'] == 'user':
                    with st.chat_message("user"):
                        st.markdown(msg['content'])
                else:
                    with st.chat_message("assistant"):
                        st.markdown(msg['content'])
        
        # Chat input (outside scrollable container - always visible at bottom)
        user_input = st.chat_input("Type your message...")
        
        # Disclaimer - Guidewire style (below input)
        st.markdown("""
        <div class="sidebar-chat-disclaimer">
        The above response was generated by an AI system and may not provide a complete and accurate answer. Please reference the provided sources for more detailed information related to your question. <a href="#" style="color: #93c5fd;">Learn more</a>.
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
    
    # Contextual responses
    if 'catch' in user_input_lower or 'update' in user_input_lower or 'summary' in user_input_lower:
        return """Here's your quick update:

**Today's Activity:**
• 3 new submissions received (2 High appetite, 1 Medium)
• Floor & Decor ready for underwriter review
• Monrovia Metalworking awaiting additional documents

**Action Items:**
• Review Floor & Decor submission (Priority Score: 4.8)
• Follow up with broker on Restaurant Holdings documents
• 2 quotes pending your approval

Would you like me to open any of these submissions?"""
    
    elif 'action' in user_input_lower or 'priority' in user_input_lower or 'todo' in user_input_lower:
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
    
    elif 'help' in user_input_lower or 'what can' in user_input_lower:
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
        # Generic helpful response
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
        from database_queries import get_all_submissions
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
            st.session_state.current_screen = 'detail'
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
        font-size: 1em;
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
    
    st.markdown('<h3 style="margin-top: 0; margin-bottom: 8px; color: #4b5563; font-weight: 700;">My Submissions</h3>', unsafe_allow_html=True)
    
    # Detect market from first submission in database (German or US)
    all_submissions = get_all_submissions()
    dashboard_market = 'us'  # default
    dashboard_currency = '$'
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
            <p style="font-size: 0.8em; color: #6b7280; margin: 0;">Target: 4.0 days</p>
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
            x=alt.X('Quarter:N', axis=alt.Axis(title=None, labelAngle=0)),
            y=alt.Y('Hit Ratio %:Q', 
                    axis=alt.Axis(title=None, grid=True),
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
        
        st.altair_chart(chart + text + threshold_line + threshold_label, use_container_width=True)
    
    with chart_col3:
        # Cumulative Earned Premium - Bar chart
        premium_data = pd.DataFrame({
            'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
            'Premium': [0.58, 1.02, 1.28, st.session_state.chart_data['premium_q4']]
        })
        
        # Dynamic format based on currency
        y_axis_format = ',.2f' if dashboard_market == 'german' else '$,.2f'
        chart = alt.Chart(premium_data).mark_bar(color='#14b8a6', size=50).encode(
            x=alt.X('Quarter:N', axis=alt.Axis(title=None, labelAngle=0)),
            y=alt.Y('Premium:Q', 
                    axis=alt.Axis(title=None, grid=True, format=y_axis_format),
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
            x=alt.X('Quarter:N', axis=alt.Axis(title=None, labelAngle=0)),
            y=alt.Y('Loss Ratio %:Q', 
                    axis=alt.Axis(title=None, grid=True, format='.0f'),
                    scale=alt.Scale(domain=[44, 55]))
        ).properties(
            height=200
        )
        
        # Add text labels on points
        text = line.mark_text(
            align='center',
            baseline='bottom',
            dy=-12,
            color='#0e7490',
            fontSize=12,
            fontWeight='bold'
        ).encode(
            text='Label:N'
        )
        
        st.altair_chart(line + text, use_container_width=True)
    
    # === SUBMISSIONS TABLE ===
    # Tabs for filtering
    tab1, tab2, tab3 = st.tabs(["Active Submissions", "Bound", "Declined"])
    
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
                
                # Display as a clickable table using st.dataframe with selection
                event = st.dataframe(
                    df,
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
                        
                        st.session_state.submission_state = {
                            'status': 'Triaged',
                            'completeness': 74,
                            'priority_score': 4.8,
                            'risk_appetite': 'High',
                            'is_summary_visible': False,
                            'is_proposal_visible': False,
                            'is_recs_visible': False,
                            'is_comparison_visible': False,
                            'quotes': [],
                            'endorsements': all_endorsements,
                            'widget_key_suffix': ''
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
            st.dataframe(df_bound, use_container_width=True, hide_index=True)
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
            st.dataframe(df_declined, use_container_width=True, hide_index=True)
        else:
            st.info("No declined submissions.")
    
    # Refresh and Reset buttons
    st.markdown("---")
    col_refresh1, col_refresh2, col_refresh3 = st.columns(3)
    
    with col_refresh1:
        if st.button("🔄 Refresh Metrics", use_container_width=True):
            # Simulate metric update
            st.session_state.show_loading = True
            st.session_state.loading_message = "Updating metrics..."
            time.sleep(2)
            st.session_state.dashboard_kpis['turnaround_time'] = 3.9
            st.session_state.show_loading = False
            st.success("✅ Metrics updated!")
            time.sleep(1)
            st.rerun()
    
    with col_refresh3:
        # Market selection dropdown
        market_option = st.selectbox(
            "Market",
            options=["German SHUK", "U.S. Workers' Compensation"],
            index=0,  # German SHUK is default/preselected
            key="market_selection",
            help="Select the market for demo data"
        )
        
        # Map display name to internal value
        market_value = 'german' if market_option == "German SHUK" else 'us'
        
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
        font-size: 1em;
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
    
    # Breadcrumb navigation
    if st.button("← Return to Submission List"):
        st.session_state.current_screen = 'dashboard'
        st.rerun()
    
    st.markdown(f'<h3 style="margin-bottom: 0;">{account.name}</h3>', unsafe_allow_html=True)
    st.caption(f"Submission: {submission.submission_number}")
    
    st.markdown("---")
    
    # === SUBMISSION KPI ROW ===
    state = st.session_state.submission_state
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Status</div>
            <div style="margin: 1rem 0; font-size: 1.5rem; font-weight: 600;">{get_status_badge(state['status'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Risk Appetite</div>
            <div style="margin: 1rem 0; font-size: 1.5rem; font-weight: 600;">{get_appetite_badge(state['risk_appetite'])}</div>
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
        docs_list = "\n".join([f"- {doc}" for doc in market_content['documents']])
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
        
        # AI Summary Box
        ai_summary = market_content['ai_summary']
        risk_factors_html = ''.join([f'<li>{factor}</li>' for factor in ai_summary['risk_factors']])
        
        summary_html = f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                <h4 style="color: white; margin-top: 0;">AI-Generated Submission Analysis</h4>
                <p><strong>Business Overview:</strong> {ai_summary['business_overview']}</p>
                <p><strong>Coverage Requested:</strong> {ai_summary['coverage_requested']}</p>
                <p><strong>Loss History:</strong> {ai_summary['loss_history']}</p>
                <p><strong>Risk Factors:</strong></p>
                <ul style="padding-left: 1.5rem;">
                    {risk_factors_html}
                </ul>
                <p><strong>Recommendation:</strong> {ai_summary['recommendation']}</p>
            </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)
        
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
        if state['is_recs_visible']:
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
                    
                    st.success("✅ Endorsements added!")
                    time.sleep(1)
                    st.rerun()
            
            with col_rec2:
                if st.button("❌ Dismiss", use_container_width=True, key="dismiss_recommendation"):
                    st.session_state.submission_state['is_recs_visible'] = False
                    st.rerun()
        
        # === GENERATE NEW QUOTE BUTTON ===
        # Check if any recommended endorsements have been selected
        has_recommended = False
        for rec in recs['items']:
            if state['endorsements'].get(rec['name'], False):
                has_recommended = True
                break
        
        if has_recommended and len(state['quotes']) == 1:
            st.markdown("---")
            col_genq1, col_genq2, col_genq3 = st.columns([1, 2, 1])
            with col_genq2:
                if st.button("🔄 Generate Quote", use_container_width=True):
                    show_loading_modal([
                        "Analyzing Changes",
                        "Calculating Quote with PricingCenter",
                        "Finalizing Quote"
                    ])
                    st.session_state.submission_state['quotes'].append('generated')
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
            
            col_compare1, col_compare2 = st.columns(2)
            
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
                    if st.button("📧 Send to Broker", type="primary", use_container_width=True, key="send_generated_quote"):
                        show_loading_modal([
                            "Creating Broker Quote page",
                            "Sending Email",
                            "Updating Proposal Status"
                        ])
                        
                        # Update session state
                        st.session_state.submission_state['status'] = 'Quoted'
                        
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

