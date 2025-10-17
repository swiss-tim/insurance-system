# Interactive P&C Insurance Process Demo
# Story-driven walkthrough of 3 real-world use cases

import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize database on app startup
from init_db import init_database
init_database()

from database_queries import (
    get_all_insureds, get_policy_details, get_party_by_id,
    get_quotes_for_submission, get_submission_for_policy,
    get_claim_details, get_reinsurance_tower, get_coinsurance_details,
    get_documents_for_record, get_claim_subrogation, get_session, Policy, PartyRole
)

st.set_page_config(layout="wide", page_title="P&C Insurance Process Demo", page_icon="🏢")

# Custom CSS for story mode
st.markdown("""
<style>
    .pain-point {
        background-color: #ffebee;
        padding: 15px;
        border-left: 4px solid #f44336;
        margin: 10px 0;
    }
    .solution {
        background-color: #e8f5e9;
        padding: 15px;
        border-left: 4px solid #4caf50;
        margin: 10px 0;
    }
    .story-section {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .step-header {
        background: linear-gradient(90deg, #1976d2 0%, #42a5f5 100%);
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("🏢 Interactive P&C Insurance Process Demo")
st.markdown("### Experience the journey from manual chaos to automated efficiency")

# --- Case Selection ---
st.sidebar.title("📚 Select a Use Case")

cases = {
    "Case 1: Swiss SME (Bakery)": {
        "company": "Bäckerei Frischknecht GmbH",
        "icon": "🥖",
        "tagline": "Local broker serving a small business",
        "color": "#ff9800"
    },
    "Case 2: German Mid-Market (Manufacturing)": {
        "company": "Maschinenbau Schmidt AG",
        "icon": "🏭",
        "tagline": "Multi-location risk with co-insurance",
        "color": "#2196f3"
    },
    "Case 3: Swiss Multinational (Pharma)": {
        "company": "HelvetiaPharma SA",
        "icon": "💊",
        "tagline": "Global program with reinsurance tower",
        "color": "#4caf50"
    },
    "Case 4: API Integration Demo": {
        "company": "Live Guidewire Integration",
        "icon": "🔌",
        "tagline": "Real-time quote generation via API",
        "color": "#9c27b0"
    }
}

selected_case = st.sidebar.radio("Choose a story:", list(cases.keys()))
case_info = cases[selected_case]

# Display case header
st.markdown(f"""
<div style='background: {case_info['color']}; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
    <h2>{case_info['icon']} {selected_case}</h2>
    <h4>{case_info['company']}</h4>
    <p>{case_info['tagline']}</p>
</div>
""", unsafe_allow_html=True)

# Get the insured party and policy (skip for Case 4)
if "Case 4" not in selected_case:
    insured = None
    for i in [get_party_by_id(1), get_party_by_id(7), get_party_by_id(11)]:
        if i and i.name == case_info['company']:
            insured = i
            break

    if not insured:
        st.error(f"Company '{case_info['company']}' not found in database.")
        st.stop()

    session = get_session()
    policy_role = session.query(PartyRole).filter(
        PartyRole.party_id == insured.id,
        PartyRole.role_name == 'Insured'
    ).first()
    session.close()

    if not policy_role:
        st.error("No policy found for this insured.")
        st.stop()

    policy = get_policy_details(policy_role.context_id)

# --- CASE 1: SWISS SME BAKERY ---
if "Case 1" in selected_case:
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Process Steps")
    process_step = st.sidebar.radio(
        "Navigate the journey:",
        ["Overview", "1️⃣ Submission & Quoting", "2️⃣ Document Collection", 
         "3️⃣ Claim Notification", "4️⃣ Status Updates", "5️⃣ Subrogation"]
    )
    
    if process_step == "Overview":
        st.markdown("""
        ## The Journey of Bäckerei Frischknecht GmbH
        
        **The Insured:** A medium-sized bakery in Zürich  
        **The Challenge:** Manual, repetitive tasks at every step  
        **The Opportunity:** End-to-end automation from quote to claim
        
        ### Click through each step to see the transformation:
        - **Submission & Quoting**: From manual portal re-entry to automated comparison
        - **Document Collection**: From email chase to digital repository
        - **Claim Notification**: From phone calls to instant FNOL
        - **Status Updates**: From broker intermediary to self-service portal
        - **Subrogation**: From manual coordination to structured workflow
        """)
        
        st.info("👈 Select a process step from the sidebar to begin the interactive demo")
    
    elif "1️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 1: Submission & Quote Comparison</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Broker gathers info via phone calls</li>
                    <li>Manually re-enters data into 3 different insurer portals</li>
                    <li>Receives 3 PDFs with different layouts</li>
                    <li>Spends 1 hour creating comparison spreadsheet</li>
                    <li>Manually transcribes premiums, deductibles, sub-limits</li>
                </ul>
                <p><strong>Time:</strong> 4-5 hours | <strong>Errors:</strong> High risk</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Single data entry into unified platform</li>
                    <li>Automatic submission to multiple insurers via API</li>
                    <li>Quotes returned in standardized format</li>
                    <li>Instant side-by-side comparison table</li>
                    <li>Zero manual transcription</li>
                </ul>
                <p><strong>Time:</strong> 15 minutes | <strong>Errors:</strong> Eliminated</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📊 Live Demo: Automated Quote Comparison")
        
        submission = get_submission_for_policy(policy.id)
        if submission:
            st.write(f"**Submission ID:** {submission.id} | **Status:** {submission.status}")
            quotes_df = get_quotes_for_submission(submission.id)
            st.dataframe(quotes_df, width=800)
            
            st.success("💡 **Benefit**: Broker saves 3-4 hours per submission. Client sees clear comparison instantly.")
            
            with st.expander("🔍 See what happened behind the scenes"):
                st.code("""
                # Single API call instead of 3 manual portal logins
                submission_data = {
                    "insured": "Bäckerei Frischknecht GmbH",
                    "coverage_types": ["Property", "Liability"],
                    "limits": {"property": 500000, "liability": 2000000}
                }
                
                # Platform sends to multiple insurers simultaneously
                quotes = platform.submit_to_insurers([
                    "Zurich Insurance",
                    "AXA Insurance", 
                    "Helvetia Insurance"
                ])
                
                # Results auto-populate comparison table
                """)
    
    elif "2️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 2: Document Collection</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Insurer's portal flags missing document</li>
                    <li>Broker emails client requesting document</li>
                    <li>Client emails PDF attachment back</li>
                    <li>Broker downloads, saves, re-uploads to portal</li>
                    <li>3-5 day delay typical</li>
                </ul>
                <p><strong>Time:</strong> Multiple days | <strong>Touch points:</strong> 4-6 emails</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Platform sends document request notification</li>
                    <li>Client uploads directly to secure portal</li>
                    <li>Document instantly available to insurer</li>
                    <li>All parties see real-time status</li>
                    <li>Same-day turnaround possible</li>
                </ul>
                <p><strong>Time:</strong> Same day | <strong>Touch points:</strong> 1 notification</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📄 Live Demo: Document Repository")
        
        docs = get_documents_for_record('policy', policy.id)
        if docs:
            doc_data = [{
                "Document Name": d.document_name,
                "Type": "Commercial Register",
                "Uploaded": str(d.upload_timestamp),
                "Status": "✅ Verified"
            } for d in docs]
            st.table(pd.DataFrame(doc_data))
            
            st.success("💡 **Benefit**: Document requests resolved in hours, not days. Audit trail automatically maintained.")
        else:
            st.info("No documents attached to this policy.")
    
    elif "3️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 3: Claim Notification (FNOL)</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Bakery owner calls broker in panic</li>
                    <li>Broker calms client, takes notes</li>
                    <li>Broker manually fills PDF claim form</li>
                    <li>Broker emails form to claims department</li>
                    <li>Claim sits in email queue</li>
                </ul>
                <p><strong>Time to assignment:</strong> 24-48 hours</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Client clicks "Report Claim" in portal</li>
                    <li>Guided form with smart validation</li>
                    <li>Photos/documents uploaded directly</li>
                    <li>Instant routing to correct adjuster</li>
                    <li>Automated acknowledgment sent</li>
                </ul>
                <p><strong>Time to assignment:</strong> 1-2 hours</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🚨 Live Demo: Claim Details")
        
        if policy.claims:
            claim = policy.claims[0]
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Claim Number", claim.claim_number)
            col2.metric("Status", claim.status)
            col3.metric("Date of Loss", str(claim.date_of_loss))
            col4.metric("Reported", "2 hours after incident")
            
            st.write("**Incident Description:**")
            st.info(claim.description)
            
            st.success("💡 **Benefit**: 90% faster assignment. Client has immediate confirmation and claim number.")
    
    elif "4️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 4: Claim Status Updates</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Client calls broker 3 times in 2 weeks</li>
                    <li>Each time: broker calls/emails adjuster</li>
                    <li>Broker waits for adjuster response</li>
                    <li>Broker relays status back to client</li>
                    <li>Broker becomes bottleneck</li>
                </ul>
                <p><strong>Broker time:</strong> 30-45 min per status check</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Client logs into portal 24/7</li>
                    <li>Real-time status dashboard visible</li>
                    <li>Communication log shows all updates</li>
                    <li>Automatic notifications on key milestones</li>
                    <li>Broker freed from intermediary role</li>
                </ul>
                <p><strong>Broker time:</strong> 0 minutes</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📊 Live Demo: Real-Time Communication Log")
        
        if policy.claims:
            claim = get_claim_details(policy.claims[0].id)
            
            log_data = [{
                "Timestamp": str(d.entry_timestamp),
                "Update": d.log_entry,
                "Visible to Client": "✅ Yes"
            } for d in claim.details]
            
            st.dataframe(pd.DataFrame(log_data), width=1000)
            
            st.success("💡 **Benefit**: Client empowerment. Broker can focus on complex cases instead of status updates.")
    
    elif "5️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 5: Subrogation (Recovery from Third Party)</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Adjuster emails broker for liable party details</li>
                    <li>Broker calls bakery owner</li>
                    <li>Owner searches accounting records</li>
                    <li>Owner emails contractor name/address</li>
                    <li>Broker forwards to adjuster</li>
                    <li>Multiple days of back-and-forth</li>
                </ul>
                <p><strong>Time to initiate:</strong> 5-7 days</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Platform links claim to parties automatically</li>
                    <li>Liable party information pre-populated</li>
                    <li>Subrogation workflow triggered instantly</li>
                    <li>All documentation centralized</li>
                    <li>Recovery tracking dashboard</li>
                </ul>
                <p><strong>Time to initiate:</strong> Same day</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🎯 Live Demo: Structured Subrogation")
        
        if policy.claims:
            subro, liable_party = get_claim_subrogation(policy.claims[0].id)
            if subro:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Status", subro.status)
                col2.metric("Liable Party", liable_party.name)
                col3.metric("Potential Recovery", f"CHF {subro.potential_recovery_amount:,.0f}")
                col4.metric("Contact", f"{liable_party.city}, {liable_party.country}")
                
                st.success("💡 **Benefit**: Faster recovery initiation. Better collection rates. Reduced broker workload.")

# --- CASE 2: GERMAN MANUFACTURING ---
elif "Case 2" in selected_case:
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Process Steps")
    process_step = st.sidebar.radio(
        "Navigate the journey:",
        ["Overview", "1️⃣ Data Consolidation", "2️⃣ Co-Insurance Placement",
         "3️⃣ IoT Verification", "4️⃣ Factory Fire Claim", "5️⃣ BI Document Chase"]
    )
    
    if process_step == "Overview":
        st.markdown("""
        ## The Journey of Maschinenbau Schmidt AG
        
        **The Insured:** German engineering firm with factories in Stuttgart and Hamburg  
        **The Challenge:** Multi-location complexity and co-insurance coordination  
        **The Opportunity:** Unified data model and automated placement
        
        ### Click through each step to see the transformation:
        - **Data Consolidation**: From Excel hell to unified asset registry
        - **Co-Insurance Placement**: From manual email chase to automated marketplace
        - **IoT Verification**: From document requests to integrated data sources
        - **Factory Fire Claim**: From coordination nightmare to orchestrated workflow
        - **BI Document Chase**: From email chains to checklist automation
        """)
        
        st.info("👈 Select a process step from the sidebar to begin the interactive demo")
    
    elif "1️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 1: Multi-Location Data Consolidation</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Agent receives 2 separate Excel files (Stuttgart, Hamburg)</li>
                    <li>Hundreds of machines with different formats</li>
                    <li>Spends half a day copy-pasting into master SoV</li>
                    <li>Manual reconciliation of totals</li>
                    <li>High risk of errors and duplicates</li>
                </ul>
                <p><strong>Time:</strong> 4-6 hours | <strong>Error rate:</strong> 5-10%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Import templates with smart mapping</li>
                    <li>Automatic location tagging</li>
                    <li>Instant validation and deduplication</li>
                    <li>Real-time aggregation by location/type</li>
                    <li>Single source of truth</li>
                </ul>
                <p><strong>Time:</strong> 30 minutes | <strong>Error rate:</strong> <1%</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🏭 Live Demo: Unified Statement of Values")
        
        asset_data = []
        for asset in policy.assets:
            location = asset.locations[0] if asset.locations else None
            value = next((d.detail_value for d in asset.details if d.detail_key == 'Replacement Value'), 'N/A')
            asset_data.append({
                "Description": asset.description,
                "Type": asset.asset_type,
                "Location": f"{location.city}, {location.country}" if location else "N/A",
                "Replacement Value (EUR)": value
            })
        
        st.dataframe(pd.DataFrame(asset_data), width=1000)
        
        total_value = sum([float(a["Replacement Value (EUR)"]) for a in asset_data if a["Replacement Value (EUR)"] != 'N/A'])
        st.metric("Total Insured Value", f"EUR {total_value:,.0f}")
        
        st.success("💡 **Benefit**: 90% time savings. Perfect accuracy. Real-time visibility across all locations.")
    
    elif "2️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 2: Co-Insurance Placement</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Lead insurer covers 70% of EUR 80M</li>
                    <li>Agent drafts email summary for 30% placement</li>
                    <li>Sends to 4 insurers with attachments</li>
                    <li>Spends week chasing responses by phone/email</li>
                    <li>Tracks quotes in separate spreadsheet</li>
                </ul>
                <p><strong>Time:</strong> 1-2 weeks | <strong>Touchpoints:</strong> 20-30 emails</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Platform calculates remaining placement need</li>
                    <li>One-click invitation to co-insurer marketplace</li>
                    <li>Automated distribution of risk data</li>
                    <li>Real-time quote submission dashboard</li>
                    <li>Instant comparison and allocation</li>
                </ul>
                <p><strong>Time:</strong> 2-3 days | <strong>Touchpoints:</strong> Automated</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🤝 Live Demo: Co-Insurance Structure")
        
        coinsurance_df = get_coinsurance_details(policy.id)
        st.dataframe(coinsurance_df, width=800)
        
        st.success("💡 **Benefit**: 60% faster placement. Better price discovery. Transparent allocation.")
    
    elif "3️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 3: IoT Verification for Risk Improvement</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Underwriter offers discount for IoT sensors</li>
                    <li>Requires proof of installation/maintenance</li>
                    <li>Agent requests certificates from facility manager</li>
                    <li>Waits for PDFs to arrive</li>
                    <li>Manually forwards to underwriter for review</li>
                </ul>
                <p><strong>Time:</strong> 5-7 days</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Platform integrated with IoT provider API</li>
                    <li>Real-time sensor status visible to underwriter</li>
                    <li>Maintenance records auto-synced</li>
                    <li>Risk score dynamically adjusted</li>
                    <li>Instant discount application</li>
                </ul>
                <p><strong>Time:</strong> Instant</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📡 Live Demo: IoT Integration Dashboard")
        
        st.info("**IoT Sensors Installed:** Temperature monitors, smoke detectors, water leak sensors")
        
        iot_data = [
            {"Location": "Stuttgart - Main Production", "Sensor Type": "Temperature", "Status": "✅ Active", "Last Maintenance": "2023-08-15"},
            {"Location": "Stuttgart - Main Production", "Sensor Type": "Smoke Detection", "Status": "✅ Active", "Last Maintenance": "2023-08-15"},
            {"Location": "Hamburg - Assembly", "Sensor Type": "Water Leak", "Status": "✅ Active", "Last Maintenance": "2023-09-01"},
        ]
        st.table(pd.DataFrame(iot_data))
        
        st.success("💡 **Benefit**: Instant verification. Lower premiums. Better risk management.")
    
    elif "4️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 4: Factory Fire - Multi-Party Coordination</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Agent becomes central coordination hub</li>
                    <li>Days on phone coordinating site visits:</li>
                    <li>&nbsp;&nbsp;- Factory manager</li>
                    <li>&nbsp;&nbsp;- Lead insurer adjuster</li>
                    <li>&nbsp;&nbsp;- Co-insurer representative</li>
                    <li>&nbsp;&nbsp;- Independent expert</li>
                    <li>Finding mutually available time slot</li>
                </ul>
                <p><strong>Time:</strong> 3-5 days of scheduling</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Platform sends calendar invite to all parties</li>
                    <li>Integrated scheduling shows availability</li>
                    <li>AI suggests optimal time slots</li>
                    <li>One-click site visit confirmation</li>
                    <li>Automatic reminders and updates</li>
                    <li>Shared notes and photo repository</li>
                </ul>
                <p><strong>Time:</strong> Same day coordination</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🔥 Live Demo: Multi-Party Claim Workflow")
        
        if policy.claims:
            claim = get_claim_details(policy.claims[0].id)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Claim Number", claim.claim_number)
            col2.metric("Status", claim.status)
            col3.metric("Parties Involved", "4")
            
            st.write("**Coordinated Activities:**")
            activities = [
                {"Activity": "Site Visit Scheduled", "Date": "2023-03-22", "Participants": "Lead Adjuster, Co-Insurer, Expert", "Status": "✅ Completed"},
                {"Activity": "Damage Assessment", "Date": "2023-03-23", "Participants": "Independent Expert", "Status": "✅ Completed"},
                {"Activity": "Settlement Discussion", "Date": "2023-03-27", "Participants": "All parties", "Status": "✅ Completed"}
            ]
            st.table(pd.DataFrame(activities))
            
            st.success("💡 **Benefit**: 70% faster coordination. All parties have visibility. Agent focuses on advocacy.")
    
    elif "5️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 5: Business Interruption Document Collection</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Adjuster provides long list of required docs</li>
                    <li>Agent emails list to finance department</li>
                    <li>Month-long email chain ensues</li>
                    <li>Agent manually tracks what's sent/outstanding</li>
                    <li>Follow-up emails every few days</li>
                    <li>No visibility into completion status</li>
                </ul>
                <p><strong>Time:</strong> 4-6 weeks</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Platform generates standardized checklist</li>
                    <li>Finance dept gets upload portal access</li>
                    <li>Real-time progress tracking dashboard</li>
                    <li>Automatic reminders for outstanding items</li>
                    <li>All parties see completion percentage</li>
                    <li>No manual follow-up needed</li>
                </ul>
                <p><strong>Time:</strong> 1-2 weeks</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📋 Live Demo: Document Checklist Automation")
        
        checklist_data = [
            {"Document": "Profit & Loss Statement (2022)", "Required": "✅", "Received": "✅", "Date": "2023-03-25"},
            {"Document": "Profit & Loss Statement (2023 YTD)", "Required": "✅", "Received": "✅", "Date": "2023-03-26"},
            {"Document": "Production Records (6 months)", "Required": "✅", "Received": "✅", "Date": "2023-03-28"},
            {"Document": "Customer Order Backlog", "Required": "✅", "Received": "✅", "Date": "2023-03-29"},
            {"Document": "Payroll Records", "Required": "✅", "Received": "✅", "Date": "2023-04-02"}
        ]
        
        df = pd.DataFrame(checklist_data)
        st.dataframe(df, width=1000)
        
        completion = (df["Received"] == "✅").sum() / len(df) * 100
        st.metric("Completion Rate", f"{completion:.0f}%")
        
        st.success("💡 **Benefit**: 60% faster document collection. Real-time visibility. Automated reminders.")

# --- CASE 3: SWISS MULTINATIONAL PHARMA ---
elif "Case 3" in selected_case:
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Process Steps")
    process_step = st.sidebar.radio(
        "Navigate the journey:",
        ["Overview", "1️⃣ Compliance Screening", "2️⃣ Reinsurance Tower Placement",
         "3️⃣ Global Policy Instructions", "4️⃣ CHF 90M Claim Coordination", "5️⃣ Cash Call Management"]
    )
    
    if process_step == "Overview":
        st.markdown("""
        ## The Journey of HelvetiaPharma SA
        
        **The Insured:** Pharmaceutical giant based in Basel with global operations  
        **The Challenge:** International compliance and massive reinsurance coordination  
        **The Opportunity:** Automated compliance checks and real-time cash call tracking
        
        ### Click through each step to see the transformation:
        - **Compliance Screening**: From manual sanctions checks to automated KYC
        - **Reinsurance Tower**: From spreadsheet chaos to visual tower builder
        - **Global Coordination**: From manual emails to centralized instructions
        - **Claim Coordination**: From manual reports to auto-generated summaries
        - **Cash Calls**: From individual notices to automated tracking
        """)
        
        st.info("👈 Select a process step from the sidebar to begin the interactive demo")
    
    elif "1️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 1: Compliance Screening</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Compliance team manually checks subsidiary names</li>
                    <li>Manual checks of directors against sanctions lists</li>
                    <li>Multiple international lists to review:</li>
                    <li>&nbsp;&nbsp;- OFAC (USA)</li>
                    <li>&nbsp;&nbsp;- EU Sanctions</li>
                    <li>&nbsp;&nbsp;- Singapore MAS</li>
                    <li>Time-consuming, error-prone process</li>
                </ul>
                <p><strong>Time:</strong> 2-3 days | <strong>Risk:</strong> High</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Platform integrates with compliance APIs</li>
                    <li>Real-time screening against global watchlists</li>
                    <li>Automated checks on:</li>
                    <li>&nbsp;&nbsp;- Company entities</li>
                    <li>&nbsp;&nbsp;- Directors and officers</li>
                    <li>&nbsp;&nbsp;- Ultimate beneficial owners</li>
                    <li>Instant alerts on any matches</li>
                </ul>
                <p><strong>Time:</strong> Minutes | <strong>Risk:</strong> Minimized</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🛡️ Live Demo: Automated Compliance Dashboard")
        
        compliance_data = [
            {"Entity": "HelvetiaPharma SA (Basel)", "Jurisdiction": "Switzerland", "Status": "✅ Clear", "Last Checked": datetime.now().strftime("%Y-%m-%d %H:%M")},
            {"Entity": "HelvetiaPharma USA Inc.", "Jurisdiction": "United States", "Status": "✅ Clear", "Last Checked": datetime.now().strftime("%Y-%m-%d %H:%M")},
            {"Entity": "HelvetiaPharma Singapore Pte Ltd", "Jurisdiction": "Singapore", "Status": "✅ Clear", "Last Checked": datetime.now().strftime("%Y-%m-%d %H:%M")},
        ]
        
        st.table(pd.DataFrame(compliance_data))
        
        st.success("💡 **Benefit**: 95% time savings. Continuous monitoring. Audit trail for regulators.")
    
    elif "2️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 2: CHF 250M Reinsurance Tower Placement</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Broker emails presentation to 30+ reinsurers</li>
                    <li>Massive spreadsheet to track:</li>
                    <li>&nbsp;&nbsp;- Who quoted?</li>
                    <li>&nbsp;&nbsp;- At what price?</li>
                    <li>&nbsp;&nbsp;- On which layer?</li>
                    <li>&nbsp;&nbsp;- Who declined?</li>
                    <li>Weeks of negotiation and follow-up</li>
                </ul>
                <p><strong>Time:</strong> 3-4 weeks | <strong>Errors:</strong> Version control chaos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Visual tower builder interface</li>
                    <li>One-click distribution to reinsurer network</li>
                    <li>Real-time bid submission portal</li>
                    <li>Automatic layer optimization</li>
                    <li>Live participation tracking</li>
                    <li>Instant contract generation</li>
                </ul>
                <p><strong>Time:</strong> 1-2 weeks | <strong>Errors:</strong> Eliminated</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🏗️ Live Demo: Interactive Reinsurance Tower")
        
        treaty, tower_df = get_reinsurance_tower(policy.id)
        
        if treaty:
            st.write(f"**Treaty:** {treaty.description}")
            st.write(f"**Type:** {treaty.treaty_type}")
            
            # Visualize the tower
            st.dataframe(tower_df, width=1000)
            
            # Calculate totals
            num_layers = len(tower_df)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Tower Limit", "CHF 250M")
            col2.metric("Number of Layers", num_layers)
            col3.metric("Reinsurers Involved", "8")
            
            st.success("💡 **Benefit**: 50% faster placement. Better price discovery. Visual clarity for all stakeholders.")
    
    elif "3️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 3: Global Policy Instructions</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Basel broker drafts instruction emails</li>
                    <li>Sends to USA and Singapore offices</li>
                    <li>Specifies exact limits and wordings</li>
                    <li>Must align with Swiss Master policy</li>
                    <li>Manual follow-up for issuance confirmation</li>
                    <li>Risk of misalignment</li>
                </ul>
                <p><strong>Time:</strong> 1-2 weeks | <strong>Risk:</strong> Coverage gaps</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Master policy terms cascade automatically</li>
                    <li>Local office portals show requirements</li>
                    <li>Embedded compliance checks for local regs</li>
                    <li>Automatic wording library access</li>
                    <li>Real-time issuance status dashboard</li>
                    <li>Guaranteed alignment</li>
                </ul>
                <p><strong>Time:</strong> 2-3 days | <strong>Risk:</strong> Eliminated</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🌍 Live Demo: Global Program Coordination")
        
        program_data = [
            {"Location": "Switzerland (Master)", "Policy Number": policy.policy_number, "Status": "✅ Issued", "Limit": "CHF 250M", "Effective": str(policy.effective_date)},
            {"Location": "USA (Local)", "Policy Number": "US-2023-HP-001", "Status": "✅ Issued", "Limit": "USD 100M", "Effective": str(policy.effective_date)},
            {"Location": "Singapore (Local)", "Policy Number": "SG-2023-HP-001", "Status": "✅ Issued", "Limit": "SGD 50M", "Effective": str(policy.effective_date)},
        ]
        
        st.table(pd.DataFrame(program_data))
        
        st.success("💡 **Benefit**: 70% faster global coordination. Consistent coverage. Real-time visibility across regions.")
    
    elif "4️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 4: CHF 90M US Lawsuit Claim Coordination</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>US office alerts Basel broker</li>
                    <li>Broker manually creates summary report for:</li>
                    <li>&nbsp;&nbsp;- Swiss lead insurer</li>
                    <li>&nbsp;&nbsp;- All reinsurers in tower</li>
                    <li>Manual USD to CHF conversion</li>
                    <li>Summarizing US legal proceedings for EU audience</li>
                    <li>Answering dozens of repetitive questions</li>
                </ul>
                <p><strong>Time:</strong> 2-3 weeks | <strong>Volume:</strong> 40+ emails</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>US office enters claim in global portal</li>
                    <li>Auto-generated report to all parties</li>
                    <li>Real-time currency conversion</li>
                    <li>AI-assisted legal summary</li>
                    <li>Centralized Q&A repository</li>
                    <li>Automatic notification to affected layers</li>
                </ul>
                <p><strong>Time:</strong> 2-3 days | <strong>Volume:</strong> Automated</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("⚖️ Live Demo: Large Loss Coordination Dashboard")
        
        if policy.claims:
            claim = get_claim_details(policy.claims[0].id)
            
            st.write(f"**Claim Number:** {claim.claim_number}")
            st.write(f"**Description:** {claim.description}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Loss Amount", "CHF 90M")
            col2.metric("Origin", "USA")
            col3.metric("Status", claim.status)
            col4.metric("Layers Affected", "3 of 3")
            
            st.write("#### Automatic Notifications Sent To:")
            notifications = [
                {"Party": "Swiss Lead Insurer", "Notification": "Large loss alert", "Date": "2023-09-15", "Status": "✅ Acknowledged"},
                {"Party": "Layer 1 Reinsurers (2)", "Notification": "Cash call imminent", "Date": "2023-09-15", "Status": "✅ Acknowledged"},
                {"Party": "Layer 2 Reinsurers (3)", "Notification": "Cash call issued", "Date": "2023-09-16", "Status": "✅ Acknowledged"},
                {"Party": "Layer 3 Reinsurers (3)", "Notification": "Claim monitoring", "Date": "2023-09-16", "Status": "✅ Acknowledged"},
            ]
            st.table(pd.DataFrame(notifications))
            
            st.success("💡 **Benefit**: Instant notification. Consistent messaging. Full audit trail. 80% time savings.")
    
    elif "5️⃣" in process_step:
        st.markdown('<div class="step-header"><h3>Step 5: Reinsurance Cash Call Management</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="pain-point">
                <h4>😰 The Manual Way</h4>
                <ul>
                    <li>Claim exceeds primary CHF 10M layer</li>
                    <li>Broker drafts individual cash call notices</li>
                    <li>Attaches correct documentation to each</li>
                    <li>Emails each reinsurer separately</li>
                    <li>Manually tracks:</li>
                    <li>&nbsp;&nbsp;- Who has paid?</li>
                    <li>&nbsp;&nbsp;- Who needs chasing?</li>
                    <li>Follow-up emails and calls</li>
                </ul>
                <p><strong>Time:</strong> 2-3 weeks | <strong>Collection rate:</strong> 80% on time</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="solution">
                <h4>✅ The Automated Way</h4>
                <ul>
                    <li>Platform calculates layer penetration</li>
                    <li>Auto-generates cash calls with correct shares</li>
                    <li>One-click issuance to all affected reinsurers</li>
                    <li>Real-time payment tracking dashboard</li>
                    <li>Automatic reminders for outstanding payments</li>
                    <li>Integrated payment reconciliation</li>
                </ul>
                <p><strong>Time:</strong> Same day issuance | <strong>Collection rate:</strong> 95% on time</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("💰 Live Demo: Cash Call Tracking Dashboard")
        
        if policy.claims:
            claim = get_claim_details(policy.claims[0].id)
            
            if claim.cash_calls:
                cash_call_data = []
                for cc in claim.cash_calls:
                    participant = cc.participant
                    reinsurer = get_party_by_id(participant.reinsurer_party_id)
                    
                    cash_call_data.append({
                        "Reinsurer": reinsurer.name,
                        "Layer": f"Layer {participant.layer.layer_order}",
                        "Share": f"{participant.share_percentage}%",
                        "Call Amount": f"{cc.call_amount:,.0f} {cc.currency}",
                        "Due Date": str(cc.due_date),
                        "Status": cc.status
                    })
                
                df = pd.DataFrame(cash_call_data)
                st.dataframe(df, width=1200)
                
                # Summary metrics
                total_called = sum([cc.call_amount for cc in claim.cash_calls])
                paid_count = sum([1 for cc in claim.cash_calls if cc.status == 'PAID'])
                pending_count = sum([1 for cc in claim.cash_calls if cc.status == 'PENDING'])
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Called", f"CHF {total_called:,.0f}")
                col2.metric("Calls Issued", len(claim.cash_calls))
                col3.metric("Paid", f"{paid_count} ({paid_count/len(claim.cash_calls)*100:.0f}%)")
                col4.metric("Pending", f"{pending_count}")
                
                st.success("💡 **Benefit**: Instant issuance. Real-time tracking. Better collection rates. Full transparency.")

# --- CASE 4: API INTEGRATION DEMO ---
elif "Case 4" in selected_case:
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Live Demo Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (every 2s)", value=False)
    
    if auto_refresh:
        import time
        time.sleep(2)
        st.rerun()
    
    if st.sidebar.button("🔃 Manual Refresh", use_container_width=True):
        st.rerun()
    
    st.markdown("""
    ## 🔌 Live Guidewire API Integration Demo
    
    **What You're Seeing:** This simulates a Guidewire PolicyCenter backend receiving and processing quotes in real-time.
    
    ### 🎯 How to Use This Demo:
    
    1. **Open Customer Portal** in another browser tab/window:
       ```bash
       streamlit run src/app_customer_portal.py --server.port 8502
       ```
    
    2. **Arrange Windows Side-by-Side:**
       - This window (port 8501) = Guidewire Backend View
       - Other window (port 8502) = Customer Portal View
    
    3. **Trigger a Quote Request:**
       - In the Customer Portal, click "Get Free Quote" on any product
       - Watch this window show the API processing in real-time!
    
    ---
    """)
    
    # Query the database for quote activity
    from seed_database import CustomerUser, ChatMessage
    session = get_session()
    
    # Get Maria's user
    user = session.query(CustomerUser).filter(CustomerUser.email == 'maria.weber@example.com').first()
    
    if not user:
        st.error("Demo user not found in database")
        session.close()
        st.stop()
    
    # Check for active quote flows (recent chat messages about quotes)
    recent_messages = session.query(ChatMessage).filter(
        ChatMessage.user_id == user.id
    ).order_by(ChatMessage.timestamp.desc()).limit(5).all()
    
    st.markdown("---")
    
    # Main dashboard - Guidewire style
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 8px; text-align: center;'>
            <h3 style='margin: 0;'>⏱️ Active</h3>
            <h2 style='margin: 0.5rem 0;'>2</h2>
            <p style='margin: 0; font-size: 0.9rem;'>API Connections</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1rem; border-radius: 8px; text-align: center;'>
            <h3 style='margin: 0;'>📋 Pending</h3>
            <h2 style='margin: 0.5rem 0;'>0</h2>
            <p style='margin: 0; font-size: 0.9rem;'>Quote Requests</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 1rem; border-radius: 8px; text-align: center;'>
            <h3 style='margin: 0;'>✅ Completed</h3>
            <h2 style='margin: 0.5rem 0;'>{}</h2>
            <p style='margin: 0; font-size: 0.9rem;'>Today</p>
        </div>
        """.format(len(recent_messages)), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 1rem; border-radius: 8px; text-align: center;'>
            <h3 style='margin: 0;'>⚡ Avg Time</h3>
            <h2 style='margin: 0.5rem 0;'>12s</h2>
            <p style='margin: 0; font-size: 0.9rem;'>Quote Generation</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Live Activity Feed
    st.subheader("🔴 Live Activity Feed")
    st.caption("Shows real-time API requests from Customer Portal")
    
    if len(recent_messages) == 0:
        st.info("""
        👆 **Waiting for customer activity...**
        
        Open the Customer Portal and click "Get Free Quote" to see this system process the request in real-time!
        
        The system will show:
        1. ⚡ API Request Received
        2. 🧮 Rating Engine Processing
        3. 🤖 Automated Underwriting
        4. ✅ Quote Generated & Delivered
        """)
    else:
        st.success("✅ **System Active** - Displaying recent quote requests")
        
        # Show recent activity as a timeline
        for idx, msg in enumerate(recent_messages):
            with st.expander(f"🔹 Request #{len(recent_messages) - idx} - {msg.timestamp.strftime('%H:%M:%S')}", expanded=(idx == 0)):
                st.markdown(f"**Customer:** {user.party.name}")
                st.markdown(f"**Timestamp:** {msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Request:** {msg.message}")
                
                # Simulate the processing stages
                st.markdown("---")
                st.markdown("### 📊 Processing Pipeline")
                
                # Stage 1: API Request
                st.markdown("""
                <div style='background: #E3F2FD; padding: 10px; border-radius: 6px; margin: 8px 0; border-left: 4px solid #2196F3;'>
                    <strong>⚡ Stage 1: API Request Received</strong><br>
                    <small>Endpoint: POST /api/v1/quote/create</small><br>
                    <small>Status: ✅ 200 OK</small><br>
                    <small>Duration: 0.1s</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Stage 2: Rating Engine
                st.markdown("""
                <div style='background: #FFF3E0; padding: 10px; border-radius: 6px; margin: 8px 0; border-left: 4px solid #FF9800;'>
                    <strong>🧮 Stage 2: Rating Engine</strong><br>
                    <small>Risk factors analyzed: 15</small><br>
                    <small>Premium calculated: CHF 89-450</small><br>
                    <small>Duration: 3.2s</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Stage 3: Automated Underwriting
                st.markdown("""
                <div style='background: #F3E5F5; padding: 10px; border-radius: 6px; margin: 8px 0; border-left: 4px solid #9C27B0;'>
                    <strong>🤖 Stage 3: Automated Underwriting</strong><br>
                    <small>Rules engine: 47 rules checked</small><br>
                    <small>Decision: ✅ Auto-approved</small><br>
                    <small>Confidence: 98%</small><br>
                    <small>Duration: 5.8s</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Stage 4: Quote Generated
                st.markdown("""
                <div style='background: #E8F5E9; padding: 10px; border-radius: 6px; margin: 8px 0; border-left: 4px solid #4CAF50;'>
                    <strong>✅ Stage 4: Quote Generated</strong><br>
                    <small>Quote ID: QT-{}</small><br>
                    <small>Policy Terms: Generated</small><br>
                    <small>Delivered via: Chat API</small><br>
                    <small>Total Duration: 12.1s</small>
                </div>
                """.format(msg.id + 10000), unsafe_allow_html=True)
                
                # Show the response
                st.markdown("---")
                st.markdown("### 💬 Response Delivered to Customer:")
                st.info(msg.response)
                
                # API Call Details
                with st.expander("🔍 View API Call Details"):
                    st.code(f"""
# Incoming Request
POST /api/v1/quote/create HTTP/1.1
Host: guidewire-api.insurancecloud.com
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{{
  "customer_id": "{user.id}",
  "customer_name": "{user.party.name}",
  "product_type": "travel_insurance",
  "request_timestamp": "{msg.timestamp.isoformat()}",
  "context": {{
    "existing_policies": 2,
    "customer_segment": "individual",
    "channel": "customer_portal"
  }}
}}

# Response
HTTP/1.1 200 OK
Content-Type: application/json

{{
  "quote_id": "QT-{msg.id + 10000}",
  "status": "approved",
  "premium": 89,
  "currency": "CHF",
  "valid_until": "2025-11-01",
  "processing_time_ms": 12100,
  "underwriting_decision": "auto_approved"
}}
                    """, language="http")
    
    st.markdown("---")
    
    # System Architecture
    st.subheader("🏗️ System Architecture")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🌐 Customer Portal (Frontend)**
        - Streamlit UI
        - Real-time chat interface
        - Direct API integration
        - Session management
        """)
        
        st.markdown("""
        **📡 API Layer**
        - RESTful endpoints
        - Authentication & authorization
        - Rate limiting
        - Request validation
        """)
    
    with col2:
        st.markdown("""
        **🎯 Guidewire PolicyCenter (Backend)**
        - Rating engine
        - Underwriting rules engine
        - Product configuration
        - Quote management
        """)
        
        st.markdown("""
        **💾 Database Layer**
        - Shared SQLite (demo)
        - Real-time sync
        - Transaction management
        - Audit logging
        """)
    
    st.markdown("---")
    
    # Performance Metrics
    st.subheader("📊 Performance Metrics")
    
    metrics_data = {
        "Metric": ["API Response Time (p50)", "API Response Time (p95)", "API Response Time (p99)", 
                   "Success Rate", "Auto-approval Rate", "Throughput"],
        "Current": ["12ms", "45ms", "120ms", "99.8%", "94%", "500 req/min"],
        "Target": ["<50ms", "<100ms", "<200ms", ">99.5%", ">90%", ">1000 req/min"],
        "Status": ["✅ Good", "✅ Good", "✅ Good", "✅ Good", "✅ Good", "⚠️ Scaling"]
    }
    
    st.dataframe(pd.DataFrame(metrics_data), use_container_width=True)
    
    st.markdown("---")
    
    # Benefits Summary
    st.info("""
    **💡 Key Benefits of API Integration:**
    
    ✅ **Speed:** Quote generation in 12 seconds vs. 2-3 days manual
    
    ✅ **Accuracy:** Automated rules engine eliminates human error
    
    ✅ **Scale:** Handle 500+ quotes/minute vs. 10-20/day manual
    
    ✅ **Customer Experience:** Instant quotes in chat vs. callback next day
    
    ✅ **Cost:** 90% reduction in operational costs per quote
    """)
    
    session.close()

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>💡 <strong>Key Takeaway:</strong> Every manual process you just saw can be automated with a unified platform.</p>
    <p>The result: <strong>60-90% time savings, better customer experience, and scalable growth.</strong></p>
</div>
""", unsafe_allow_html=True)

