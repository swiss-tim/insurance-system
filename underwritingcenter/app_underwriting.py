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
import pandas as pd
import sys
import os
import time
import datetime

# Add parent directory to path to import database modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database_queries import get_session
from seed_database import Submission, Party, Quote

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Guidewire Underwriting Center",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .kpi-title {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e40af;
        margin: 0.5rem 0;
    }
    
    .kpi-delta {
        font-size: 0.75rem;
        color: #059669;
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-triaged {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .status-in-review {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    .status-quoted {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .status-bound {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .status-cleared {
        background-color: #e0e7ff;
        color: #3730a3;
    }
    
    .status-declined {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    /* Appetite badges */
    .appetite-high {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .appetite-medium {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .appetite-low {
        background-color: #fee2e2;
        color: #991b1b;
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
    }
    
    .quote-card-selected {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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
</style>
""", unsafe_allow_html=True)

# === SESSION STATE INITIALIZATION ===
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = 'dashboard'

if 'selected_submission' not in st.session_state:
    st.session_state.selected_submission = None

# Dashboard KPIs state
if 'dashboard_kpis' not in st.session_state:
    st.session_state.dashboard_kpis = {
        'turnaround_time': 4.1,
        'hit_ratio': 26,
        'earned_premium': 1.65,
        'loss_ratio': 49
    }

# Submission detail state (for Floor & Decor demo)
if 'submission_state' not in st.session_state:
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
        'endorsements': {
            'Alternate Employer Endorsement': True,
            'Catastrophe (Other Than Certified Acts of Terrorism) Premium Endorsement': True,
            'Insurance Company As Insured Endorsement': True,
            'Rural Utilities Service Endorsement': True,
            'Sole Proprietors, Partners, Officers And Others Coverage Endorsement': False,
            'KOTECKI': False,
            'Voluntary Compensation Coverage Endorsement': False
        },
        'widget_key_suffix': ''  # Used to force widget refresh
    }

# Loading modal state
if 'show_loading' not in st.session_state:
    st.session_state.show_loading = False
    st.session_state.loading_message = ""

# === HELPER FUNCTIONS ===

def show_loading(message, duration=2):
    """Display a loading modal for specified duration"""
    st.session_state.show_loading = True
    st.session_state.loading_message = message
    time.sleep(duration)
    st.session_state.show_loading = False
    st.rerun()

def get_status_badge(status):
    """Return formatted status badge HTML"""
    status_lower = status.lower().replace(' ', '-')
    return f'<span class="status-badge status-{status_lower}">{status}</span>'

def get_appetite_badge(appetite):
    """Return formatted appetite badge HTML"""
    appetite_lower = appetite.lower()
    return f'<span class="status-badge appetite-{appetite_lower}">{appetite}</span>'

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
            'risk_appetite': sub.risk_appetite or ''
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

def reset_demo_database():
    """Reset the database to demo state by running seed script"""
    import subprocess
    import sys
    
    # Get paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    seed_script = os.path.join(project_root, "src", "seed_database.py")
    
    # Run seed script - it will clear existing data and re-seed
    # No need to delete the database file anymore
    result = subprocess.run(
        [sys.executable, seed_script],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    if result.returncode == 0:
        return True, "Database reset successfully! ✨"
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

def render_dashboard():
    """Render the main dashboard screen"""
    st.markdown("## 🏢 Guidewire Underwriting Center")
    st.caption("Enterprise underwriting management platform")
    
    st.markdown("---")
    
    # === TOP KPI ROW ===
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Quote Turnaround Time</div>
            <div class="kpi-value">{st.session_state.dashboard_kpis['turnaround_time']} Days</div>
            <div class="kpi-delta">⬇️ -0.1 days</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Hit Ratio</div>
            <div class="kpi-value">{st.session_state.dashboard_kpis['hit_ratio']}%</div>
            <div class="kpi-delta">⬆️ +2% from Q3</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Cumulative Earned Premium</div>
            <div class="kpi-value">${st.session_state.dashboard_kpis['earned_premium']}M</div>
            <div class="kpi-delta">⬆️ +12% YTD</div>
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
    
    st.markdown("---")
    
    # === SUBMISSIONS TABLE ===
    st.markdown("### 📋 My Submissions")
    
    # Tabs for filtering
    tab1, tab2, tab3 = st.tabs(["Active Submissions", "Bound", "Declined"])
    
    # Get all submissions
    all_submissions = get_all_submissions()
    
    with tab1:
        active_subs = [s for s in all_submissions if s['status'].upper() not in ['BOUND', 'DECLINED']]
        quoted_subs = [s for s in active_subs if s['status'].upper() == 'QUOTED']
        in_progress_subs = [s for s in active_subs if s['status'].upper() != 'QUOTED']
        
        if active_subs:
            st.caption(f"Showing {len(active_subs)} active submission(s)")
            
            # Show bind option for quoted submissions first
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
                            with st.spinner("Binding policy..."):
                                time.sleep(2)
                                update_submission_status(sub['id'], 'BOUND')
                                st.success(f"✅ Policy bound for {sub['account_name']}!")
                                time.sleep(1)
                                st.rerun()
                st.markdown("---")
            
            # Show in-progress submissions
            if in_progress_subs:
                st.markdown("**🔄 In Progress:**")
                # Create DataFrame for display
                df_display = []
                for sub in in_progress_subs:
                    df_display.append({
                        'Account': sub['account_name'],
                        'Submission': sub['submission_number'],
                        'Status': sub['status'],
                        'Broker': sub['broker'],
                        'Broker Tier': sub['broker_tier'],
                        'Effective Date': sub['effective_date'].strftime('%Y-%m-%d') if sub['effective_date'] else 'N/A',
                        'Priority Score': f"{sub['priority_score']:.1f}" if sub['priority_score'] else 'N/A',
                        'Completeness': f"{sub['completeness']}%" if sub['completeness'] else 'N/A',
                        'Appetite': sub['risk_appetite']
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
                    
                    # Reset submission state if switching to Floor & Decor
                    if selected_sub['submission_number'] == 'SUB-2026-001':
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
                            'endorsements': {
                                'Alternate Employer Endorsement': True,
                                'Catastrophe (Other Than Certified Acts of Terrorism) Premium Endorsement': True,
                                'Insurance Company As Insured Endorsement': True,
                                'Rural Utilities Service Endorsement': True,
                                'Sole Proprietors, Partners, Officers And Others Coverage Endorsement': False,
                                'KOTECKI': False,
                                'Voluntary Compensation Coverage Endorsement': False
                            },
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
        if st.button("🔄 Reset Demo Data", type="secondary", use_container_width=True, help="Reset all submissions to original demo state"):
            with st.spinner("Resetting demo data..."):
                success, message = reset_demo_database()
                
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
    
    # Breadcrumb navigation
    if st.button("← Return to Submission List"):
        st.session_state.current_screen = 'dashboard'
        st.rerun()
    
    st.markdown(f"## {account.name}")
    st.caption(f"Submission: {submission.submission_number}")
    
    st.markdown("---")
    
    # === SUBMISSION KPI ROW ===
    state = st.session_state.submission_state
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Status</div>
            <div style="margin: 1rem 0;">{get_status_badge(state['status'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Risk Appetite</div>
            <div style="margin: 1rem 0;">{get_appetite_badge(state['risk_appetite'])}</div>
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
        st.markdown("""
        **Recent Documents:**
        - 📎 Floor_Decor_Submission_Form.pdf (Oct 15, 2025 09:30)
        - 📎 ACORD_Application.pdf (Oct 15, 2025 09:32)
        - 📧 Email: Additional Risk Information (Oct 16, 2025 14:45)
        - 📎 Loss_Runs_2022-2024.xlsx (Oct 16, 2025 15:10)
        """)
    
    with col2:
        if not state['is_summary_visible']:
            if st.button("✨ Summarize with AI", use_container_width=True):
                st.session_state.show_loading = True
                st.session_state.loading_message = "Analyzing Received Documentation..."
                time.sleep(2)
                st.session_state.submission_state['is_summary_visible'] = True
                st.session_state.show_loading = False
                st.rerun()
    
    # === AI SMART SUMMARY (Conditionally rendered) ===
    if state['is_summary_visible']:
        st.markdown("---")
        st.markdown("### 🤖 Smart Summary")
        
        # AI Summary Box
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                <h4 style="color: white; margin-top: 0;">AI-Generated Submission Analysis</h4>
                <p><strong>Business Overview:</strong> Floor & Decor is a specialty retailer of hard surface flooring and related accessories with 150+ locations across the US. Annual revenue: $3.8B.</p>
                <p><strong>Coverage Requested:</strong> Workers' Compensation insurance with Admitted Product Details (APD) rating. Estimated annual premium: $1.8M based on payroll of $450M.</p>
                <p><strong>Loss History:</strong> Moderate loss ratio of 62% over past 3 years. Primary claims: slips/falls in warehouses, forklift incidents, repetitive strain injuries.</p>
                <p><strong>Risk Factors:</strong></p>
                <ul style="padding-left: 1.5rem;">
                    <li>Strong safety program with OSHA compliance</li>
                    <li>Return-to-work program reduces claim duration</li>
                    <li>High employee turnover in warehouse positions</li>
                    <li>Expansion into new states increases exposure</li>
                </ul>
                <p><strong>Recommendation:</strong> Proceed with underwriting. Account meets appetite criteria. Consider voluntary compensation endorsement for enhanced coverage.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Impact on Completeness:**")
        st.info("✓ Extracted key risk factors (+8%)\n\n✓ Verified loss run data (+4%)\n\n✓ Assessed safety program quality (+2%)")
        
        col_accept1, col_accept2 = st.columns([1, 3])
        with col_accept1:
            if st.button("✅ Accept Summary", use_container_width=True):
                st.session_state.show_loading = True
                st.session_state.loading_message = "Updating Completeness Score..."
                time.sleep(2)
                
                # Update session state
                st.session_state.submission_state['completeness'] = 86
                st.session_state.submission_state['status'] = 'In Review'
                
                # Save to database
                update_submission_status(
                    st.session_state.selected_submission,
                    'In Review',
                    completeness=86
                )
                
                st.session_state.show_loading = False
                st.success("✅ Summary accepted! Completeness updated.")
                time.sleep(1)
                st.rerun()
    
    # === GENERATE PROPOSAL BUTTON (Conditionally rendered) ===
    if state['completeness'] >= 86 and not state['is_proposal_visible']:
        st.markdown("---")
        col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
        with col_gen2:
            if st.button("+ Generate Proposal", use_container_width=True):
                st.session_state.show_loading = True
                st.session_state.loading_message = "Retrieving APD Product Details...\n\nCalculating Quote..."
                time.sleep(3)
                st.session_state.submission_state['is_proposal_visible'] = True
                st.session_state.submission_state['quotes'] = ['base']
                st.session_state.show_loading = False
                st.rerun()
    
    # === PROPOSAL DETAILS (Conditionally rendered) ===
    if state['is_proposal_visible']:
        st.markdown("---")
        st.markdown("### 📊 Proposal Details")
        
        col_proposal1, col_proposal2 = st.columns(2)
        
        with col_proposal1:
            st.markdown("**Coverages:**")
            st.checkbox("Workers' Compensation Covered States (Section 3A)", value=True, disabled=True, key="cov_3a")
            st.checkbox("Workers' Compensation And Employers' Liability Insurance Policy (Section 3B)", value=True, disabled=True, key="cov_3b")
            st.checkbox("Terrorism Risk Insurance Program Reauthorization Act Disclosure Endorsement", value=True, disabled=True, key="cov_tria")
            st.checkbox("Benefits Deductible Endorsement", value=False, disabled=True, key="cov_benefits")
        
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
            st.markdown("#### 💵 Base Quote (Manual Premium)")
            
            st.markdown("""
            <div class="quote-card">
                <h2 style="color: #2563eb;">$42,459</h2>
                <p><strong>Annual Premium</strong></p>
                <hr>
                <p><strong>Rating Basis:</strong> Manual rates per state</p>
                <p><strong>Payroll:</strong> $450,000,000</p>
                <p><strong>Experience Mod:</strong> 0.95</p>
                <p><strong>States:</strong> 42 states + DC</p>
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
                if state['status'].upper() == 'QUOTED':
                    if st.button("📧 Send to Broker", type="primary", use_container_width=True, key="send_base_quote"):
                        st.session_state.show_loading = True
                        st.session_state.loading_message = "Creating Broker Quote Page...\n\nSending Email..."
                        time.sleep(3)
                        st.session_state.show_loading = False
                        st.success("✅ Quote sent to broker!")
                        time.sleep(1)
                        # Don't update status here - wait for user to navigate back
                        st.rerun()
        
        # === AI RECOMMENDATIONS (Conditionally rendered) ===
        if state['is_recs_visible']:
            st.markdown("---")
            st.markdown("### 💡 Recommended Changes")
            
            st.info("""
            **AI Analysis suggests:**
            
            ⚠️ **Add Endorsement: Voluntary Compensation Coverage Endorsement**
            
            **Rationale:** Account has high-paid executives who travel internationally. Voluntary compensation provides coverage for executives exempt from standard workers' comp.
            
            **Premium Impact:** +$32,875
            
            **Risk Benefit:** Reduces potential coverage gap litigation by 87%
            """)
            
            if st.button("✅ Accept Recommendation", use_container_width=True):
                st.session_state.show_loading = True
                st.session_state.loading_message = "Adding Endorsements..."
                time.sleep(2)
                
                # Update endorsement
                st.session_state.submission_state['endorsements']['Voluntary Compensation Coverage Endorsement'] = True
                
                # Change widget key suffix to force checkbox refresh
                import random
                st.session_state.submission_state['widget_key_suffix'] = str(random.randint(1000, 9999))
                
                st.session_state.show_loading = False
                st.success("✅ Endorsement added!")
                time.sleep(1)
                st.rerun()
        
        # === GENERATE NEW QUOTE BUTTON ===
        if state['endorsements'].get('Voluntary Compensation Coverage Endorsement', False) and len(state['quotes']) == 1:
            st.markdown("---")
            col_genq1, col_genq2, col_genq3 = st.columns([1, 2, 1])
            with col_genq2:
                if st.button("🔄 Generate Quote", use_container_width=True):
                    st.session_state.show_loading = True
                    st.session_state.loading_message = "Analyzing Changes...\n\nCalculating Quote..."
                    time.sleep(3)
                    st.session_state.submission_state['quotes'].append('generated')
                    st.session_state.show_loading = False
                    st.rerun()
        
        # === GENERATED QUOTE CARD ===
        if 'generated' in state['quotes'] and not state['is_comparison_visible']:
            st.markdown("---")
            st.markdown("#### 💵 Generated Quote")
            
            st.markdown("""
            <div class="quote-card quote-card-selected">
                <h2 style="color: #2563eb;">$75,334</h2>
                <p><strong>Annual Premium</strong></p>
                <hr>
                <p><strong>Rating Basis:</strong> Manual rates + Endorsements</p>
                <p><strong>Payroll:</strong> $450,000,000</p>
                <p><strong>Experience Mod:</strong> 0.95</p>
                <p><strong>States:</strong> 42 states + DC</p>
                <p><strong>Endorsements:</strong> Voluntary Compensation, Additional Insured</p>
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
                        st.session_state.show_loading = True
                        st.session_state.loading_message = "Creating Broker Quote Page...\n\nSending Email..."
                        time.sleep(3)
                        
                        # Update session state
                        st.session_state.submission_state['status'] = 'Quoted'
                        
                        # Save to database
                        update_submission_status(
                            st.session_state.selected_submission,
                            'Quoted'
                        )
                        
                        st.session_state.show_loading = False
                        st.success("✅ Quote sent to broker successfully!")
                        time.sleep(2)
                        st.rerun()
                elif state['status'].upper() == 'QUOTED':
                    # Show Bind Policy button after quote is sent
                    if st.button("✅ Bind Policy", type="primary", use_container_width=True, key="bind_policy_detail"):
                        st.session_state.show_loading = True
                        st.session_state.loading_message = "Binding Policy..."
                        time.sleep(2)
                        
                        # Update session state
                        st.session_state.submission_state['status'] = 'BOUND'
                        
                        # Save to database
                        update_submission_status(
                            st.session_state.selected_submission,
                            'BOUND'
                        )
                        
                        st.session_state.show_loading = False
                        st.success("✅ Policy bound successfully!")
                        time.sleep(2)
                        st.rerun()
                else:
                    # Already bound
                    st.info("✅ This policy has been bound and moved to the Bound tab.")
        
        # === QUOTE COMPARISON VIEW ===
        if state['is_comparison_visible']:
            st.markdown("---")
            st.markdown("### 📊 Quote Comparison")
            
            comp_col1, comp_col2 = st.columns(2)
            
            with comp_col1:
                st.markdown("**Base Quote (Manual Premium)**")
                st.markdown("""
                **Premium:** $42,459
                
                **Coverages:**
                - Workers' Compensation Covered States (Section 3A)
                - Workers' Compensation And Employers' Liability (Section 3B)
                
                **Endorsements:**
                - Alternate Employer Endorsement
                - Catastrophe Premium Endorsement
                - Insurance Company As Insured Endorsement
                - Rural Utilities Service Endorsement
                
                **States:** 42 + DC
                """)
            
            with comp_col2:
                st.markdown("**Generated Quote (Enhanced)**")
                st.markdown("""
                **Premium:** $75,334 **(+$32,875)**
                
                **Coverages:**
                - Workers' Compensation Covered States (Section 3A)
                - Workers' Compensation And Employers' Liability (Section 3B)
                
                **Endorsements:**
                - Alternate Employer Endorsement
                - Catastrophe Premium Endorsement
                - Insurance Company As Insured Endorsement
                - Rural Utilities Service Endorsement
                - **Voluntary Compensation Coverage Endorsement** ✨ NEW
                
                **States:** 42 + DC
                """)
            
            st.markdown("---")
            st.info("""
            **💡 Recommendation:** The Generated Quote provides enhanced coverage for executives traveling internationally,
            reducing potential coverage gap litigation. Premium increase is justified by risk reduction.
            """)
            
            if st.button("← Back to Quotes"):
                st.session_state.submission_state['is_comparison_visible'] = False
                st.rerun()
    
    # === APPLICANT INFO (Always visible) ===
    st.markdown("---")
    st.markdown("### 🏢 Applicant Information")
    
    tab_info1, tab_info2, tab_info3 = st.tabs(["Headquarters", "Operations", "Risk Description"])
    
    with tab_info1:
        st.markdown(f"""
        **Legal Name:** {account.name}
        
        **Address:** {account.address}, {account.city}, {account.country}
        
        **Phone:** {account.phone}
        
        **Email:** {account.email}
        
        **Broker:** {broker.name if broker else 'Direct'}
        
        **Effective Date:** {submission.effective_date.strftime('%B %d, %Y') if submission.effective_date else 'TBD'}
        """)
    
    with tab_info2:
        st.markdown("""
        **Industry:** Retail - Hard Surface Flooring & Accessories
        
        **Number of Locations:** 150+ stores across United States
        
        **Annual Revenue:** $3.8 Billion
        
        **Number of Employees:** 8,500+
        
        **Annual Payroll:** $450 Million
        
        **Years in Business:** 25+ years
        """)
    
    with tab_info3:
        st.markdown("""
        **Primary Operations:**
        - Retail sales of flooring materials (tile, wood, laminate, vinyl)
        - In-store design services
        - Warehouse operations
        - Delivery and installation services
        
        **Risk Characteristics:**
        - Heavy material handling (forklift operations)
        - Customer-facing retail environment
        - Installation crews (higher risk class)
        - Multi-state operations
        
        **Safety Programs:**
        - OSHA-compliant safety training
        - Return-to-work program
        - Quarterly safety audits
        - Incident investigation protocols
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

