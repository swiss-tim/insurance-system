# Customer Portal with AI Features
# Powered by Amazon Bedrock (Simulated)

import streamlit as st
import pandas as pd
from datetime import datetime
import random

# Initialize database
from init_db import init_database
init_database()

from database_queries import get_session
from seed_database import (
    CustomerUser, ChatMessage, GeneratedAd, PolicySummary,
    EmailTemplate, Policy, Coverage, Party, PartyRole
)

st.set_page_config(layout="wide", page_title="My Insurance Portal", page_icon="🌵")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .chat-user {
        background-color: #E3F2FD;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: right;
    }
    .chat-bot {
        background-color: #F1F8E9;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .ad-card {
        border: 2px solid #4ECDC4;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: white;
    }
    .policy-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: #fafafa;
    }
    .chat-widget {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
    }
    .chat-icon {
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: pulse 2s infinite;
        font-size: 32px;
    }
    .chat-icon:hover {
        transform: scale(1.1);
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }
        50% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.8); }
    }
    .chat-panel {
        position: fixed;
        bottom: 0;
        right: 0;
        width: 400px;
        height: 600px;
        background: white;
        border-radius: 10px 0 0 0;
        box-shadow: -2px 0 10px rgba(0,0,0,0.2);
        z-index: 999;
        display: flex;
        flex-direction: column;
    }
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px 0 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .chat-body {
        flex: 1;
        overflow-y: auto;
        padding: 15px;
        background: #f8f9fa;
    }
    .chat-input-area {
        padding: 15px;
        border-top: 1px solid #ddd;
        background: white;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Simulated AI Functions (in production, these would call Amazon Bedrock)
def simulate_chatbot_response(user_message, user_data):
    """Simulate Cacti Bot using Claude"""
    # In production: call Amazon Bedrock with Claude 3
    responses = {
        "policies": f"You have {len(user_data['policies'])} active policies. Would you like details on any specific policy?",
        "claim": "To file a claim, please provide: 1) Date of incident, 2) Description, 3) Photos if available. I can help you through the process!",
        "renewal": "Your policies are set to renew on Dec 31, 2024. We'll send renewal notices 30 days before expiration.",
        "coverage": "Your current coverage includes home and auto insurance. Would you like to add travel or life insurance?",
    }
    
    # Simple keyword matching (real AI would be much smarter)
    for key, response in responses.items():
        if key in user_message.lower():
            return response
    
    return "I'm here to help! You can ask me about your policies, file claims, request changes, or get quotes for new coverage."

def simulate_image_generation(prompt):
    """Simulate Stable Diffusion image generation"""
    # In production: call Amazon Bedrock with Stable Diffusion
    # Return placeholder image URL
    colors = ["FF6B6B", "4ECDC4", "45B7D1", "96CEB4", "FFEAA7"]
    color = random.choice(colors)
    return f"https://via.placeholder.com/400x300/{color}/FFF?text={prompt[:20].replace(' ', '+')}"

def simulate_ad_copy_generation(product_type):
    """Simulate Titan text generation for ads"""
    # In production: call Amazon Bedrock with Titan
    ad_templates = {
        "Travel Insurance": "✈️ **Adventure Awaits!** Don't let unexpected events ruin your trip. Get comprehensive travel insurance starting from CHF 45. Covers medical emergencies, trip cancellations, and lost luggage!",
        "Life Insurance": "🛡️ **Secure Your Family's Future** Protect your loved ones with life insurance from CHF 25/month. Guaranteed payout, tax advantages, and flexible terms. Get a quote in 2 minutes!",
        "Pet Insurance": "🐾 **Your Furry Friend Deserves Protection** Vet bills can be expensive! Pet insurance covers accidents, illnesses, and routine care. Plans start at CHF 30/month.",
    }
    return ad_templates.get(product_type, "Protect what matters most!")

def simulate_policy_summarization(policy_text):
    """Simulate Claude summarizing complex policy"""
    # In production: call Amazon Bedrock with Claude 3
    return """**Policy Summary (AI-Generated):**

🏠 **What's Covered:**
- Building damage from fire, water, storms
- Personal belongings up to CHF 100,000
- Liability for accidents on your property

⚠️ **Important Exclusions:**
- Regular wear and tear
- Intentional damage
- Floods (optional add-on available)

📞 **Emergency Contact:** 24/7 hotline included
💰 **Deductibles:** CHF 500-1,000 depending on claim type

✅ **Simple Terms:** This policy protects your home and belongings from unexpected damage. You pay a small amount (deductible) when making a claim, and we cover the rest up to the limits shown."""

def simulate_email_generation(template_type, policy_data):
    """Simulate Titan generating email"""
    # In production: call Amazon Bedrock with Titan
    if template_type == "renewal":
        return {
            "subject": f"Policy Renewal Request - {policy_data['number']}",
            "body": f"""Dear Insurance Team,

I would like to request renewal information for my {policy_data['type']} policy (#{policy_data['number']}).

Current policy details:
- Expiration: {policy_data['expiry']}
- Current premium: CHF {policy_data['premium']}

Please send me:
1. Renewal terms and pricing
2. Any available discounts
3. Coverage adjustment options

I am available for a call at your convenience.

Best regards,
{policy_data['customer_name']}"""
        }
    elif template_type == "claim":
        return {
            "subject": f"Claim Notification - Policy {policy_data['number']}",
            "body": f"""Dear Claims Department,

I am writing to file a claim under my {policy_data['type']} policy (#{policy_data['number']}).

Incident details:
- Date: [Please specify]
- Location: [Your address]
- Description: [Describe what happened]

I have attached supporting documentation and photos. Please let me know the next steps.

Policy holder: {policy_data['customer_name']}
Contact: [Your phone]"""
        }

# Main App Logic
def main():
    # Get user session (in production, use proper authentication)
    session = get_session()
    
    # Load customer user (demo: always load Maria Weber)
    user = session.query(CustomerUser).filter(CustomerUser.email == 'maria.weber@example.com').first()
    
    if not user:
        st.error("Please log in to access your portal.")
        session.close()
        return
    
    # Load user's policies
    party = user.party
    policy_roles = session.query(PartyRole).filter(
        PartyRole.party_id == party.id,
        PartyRole.role_name == 'Insured'
    ).all()
    
    policies = []
    for role in policy_roles:
        policy = session.query(Policy).get(role.context_id)
        if policy:
            policies.append(policy)
    
    # Sidebar Navigation
    st.sidebar.markdown(f"### Welcome, {party.name}!")
    st.sidebar.markdown(f"📧 {user.email}")
    
    if user.avatar_url:
        st.sidebar.image(user.avatar_url, width=150)
    
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio("Navigation", [
        "🏠 Dashboard",
        "📋 My Policies",
        "🎯 Special Offers",
        "👤 My Account"
    ])
    
    # Initialize chat widget state
    if 'chat_open' not in st.session_state:
        st.session_state.chat_open = False
    
    # ======================
    # PAGE 1: DASHBOARD
    # ======================
    if page == "🏠 Dashboard":
        st.markdown('<div class="main-header"><h1>🌵 My Insurance Dashboard</h1><p>Your personalized insurance portal powered by AI</p></div>', unsafe_allow_html=True)
        
        # Key Metrics
        col1, col2, col3 = st.columns(3)
        
        total_premium = sum([p.quote.total_premium for p in policies if p.quote])
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{len(policies)}</h3>
                <p>Active Policies</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>CHF {total_premium:,.0f}</h3>
                <p>Total Annual Premium</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>0</h3>
                <p>Active Claims</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💬 Chat with Cacti Bot", use_container_width=True):
                st.session_state.chat_open = True
                st.rerun()
        
        with col2:
            if st.button("📄 View Policies", use_container_width=True):
                st.session_state.nav_page = "📋 My Policies"
                st.rerun()
        
        with col3:
            if st.button("📞 File a Claim", use_container_width=True):
                st.info("Claim filing feature - redirecting to Cacti Bot...")
        
        with col4:
            if st.button("💰 Get a Quote", use_container_width=True):
                st.success("Quote request submitted! Check special offers.")
        
        st.markdown("---")
        
        # AI-Generated Upsell Ads
        st.subheader("🎯 Recommended for You (AI-Generated)")
        st.caption("Powered by Amazon Bedrock - Personalized based on your coverage")
        
        ads = session.query(GeneratedAd).filter(GeneratedAd.user_id == user.id).limit(2).all()
        
        if ads:
            col1, col2 = st.columns(2)
            
            for idx, ad in enumerate(ads):
                with (col1 if idx == 0 else col2):
                    st.markdown(f"""
                    <div class="ad-card">
                        <img src="{ad.image_url}" style="width:100%; border-radius:8px; margin-bottom:10px;">
                        <h4>{ad.product_type}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(ad.ad_copy)
                    
                    if st.button(f"Get Quote for {ad.product_type}", key=f"ad_{ad.id}"):
                        st.success(f"✅ Quote request sent for {ad.product_type}! We'll contact you within 24 hours.")
        
        st.markdown("---")
        
        # Recent Activity
        st.subheader("📊 Recent Activity")
        
        recent_chats = session.query(ChatMessage).filter(
            ChatMessage.user_id == user.id
        ).order_by(ChatMessage.timestamp.desc()).limit(3).all()
        
        if recent_chats:
            for chat in recent_chats:
                st.caption(f"🕒 {chat.timestamp.strftime('%Y-%m-%d %H:%M')}")
                st.info(f"**You asked:** {chat.message[:100]}...")
        else:
            st.info("No recent activity. Start a conversation with Cacti Bot!")
    
    # ======================
    # FLOATING CACTI BOT WIDGET
    # ======================
    
    # Floating chat icon (always visible)
    chat_container = st.container()
    with chat_container:
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("🌵", key="chat_toggle", help="Chat with Cacti Bot"):
                st.session_state.chat_open = not st.session_state.chat_open
    
    # Chat panel (conditional)
    if st.session_state.chat_open:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🌵 Cacti Bot")
            st.caption("Your AI Insurance Assistant")
            
            # Chat history in sidebar
            chat_history = session.query(ChatMessage).filter(
                ChatMessage.user_id == user.id
            ).order_by(ChatMessage.timestamp).all()
            
            # Scrollable chat history
            chat_container = st.container()
            with chat_container:
                for chat in chat_history[-5:]:  # Show last 5 messages
                    with st.expander(f"💬 {chat.timestamp.strftime('%H:%M')}", expanded=False):
                        st.markdown(f"**You:** {chat.message}")
                        st.markdown(f"**Bot:** {chat.response[:100]}...")
            
            st.markdown("---")
            
            # Chat input
            user_message = st.text_input("💬 Ask me anything:", placeholder="e.g., What are my policies?", key="chat_input")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                send_button = st.button("Send", type="primary", use_container_width=True)
            with col2:
                if st.button("Close", use_container_width=True):
                    st.session_state.chat_open = False
                    st.rerun()
            
            if send_button and user_message:
                # Simulate AI response
                user_data = {
                    'policies': policies,
                    'name': party.name,
                    'email': user.email
                }
                
                response = simulate_chatbot_response(user_message, user_data)
                
                # Save to database
                new_chat = ChatMessage(
                    user_id=user.id,
                    message=user_message,
                    response=response,
                    timestamp=datetime.now(),
                    is_user=True,
                    model_used='Claude 3 (Simulated)'
                )
                session.add(new_chat)
                session.commit()
                
                st.success("Message sent!")
                st.rerun()
            
            # Example prompts
            st.markdown("**💡 Try:**")
            if st.button("What are my policies?", use_container_width=True):
                st.session_state.example_q = "What are my current policies?"
                st.rerun()
            if st.button("When is my renewal?", use_container_width=True):
                st.session_state.example_q = "When is my home insurance renewal?"
                st.rerun()
    
    # ======================
    # OLD CACTI BOT PAGE (REMOVED)
    # ======================
    elif page == "💬 Cacti Bot" and False:  # Disabled - now using floating widget
        st.markdown('<div class="main-header"><h1>🌵 Cacti Bot</h1><p>Your AI-powered insurance assistant</p></div>', unsafe_allow_html=True)
        
        st.markdown("### Chat with Cacti Bot")
        st.caption("Powered by Amazon Bedrock (Claude 3) - Ask me anything about your insurance!")
        
        # Load chat history
        chat_history = session.query(ChatMessage).filter(
            ChatMessage.user_id == user.id
        ).order_by(ChatMessage.timestamp).all()
        
        # Display chat history
        for chat in chat_history:
            st.markdown(f"""
            <div class="chat-user">
                <strong>You:</strong> {chat.message}
                <br><small>{chat.timestamp.strftime('%Y-%m-%d %H:%M')}</small>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="chat-bot">
                <strong>🌵 Cacti Bot:</strong> {chat.response}
                <br><small>Model: {chat.model_used or 'Claude 3'}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Chat input
        st.markdown("---")
        
        user_message = st.text_input("💬 Type your question:", placeholder="e.g., What are my policy details?")
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            send_button = st.button("Send", type="primary")
        
        if send_button and user_message:
            # Simulate AI response
            user_data = {
                'policies': policies,
                'name': party.name,
                'email': user.email
            }
            
            response = simulate_chatbot_response(user_message, user_data)
            
            # Save to database
            new_chat = ChatMessage(
                user_id=user.id,
                message=user_message,
                response=response,
                timestamp=datetime.now(),
                is_user=True,
                model_used='Claude 3 (Simulated)'
            )
            session.add(new_chat)
            session.commit()
            
            st.success("Message sent! Refreshing...")
            st.rerun()
        
        # Example prompts
        st.markdown("---")
        st.markdown("**💡 Try asking:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("What are my policies?"):
                st.session_state.example_q = "What are my current policies?"
        
        with col2:
            if st.button("When is my renewal?"):
                st.session_state.example_q = "When is my home insurance renewal?"
        
        with col3:
            if st.button("How do I file a claim?"):
                st.session_state.example_q = "How do I file a claim?"
    
    # ======================
    # PAGE 3: MY POLICIES
    # ======================
    elif page == "📋 My Policies":
        st.markdown('<div class="main-header"><h1>📋 My Insurance Policies</h1></div>', unsafe_allow_html=True)
        
        if not policies:
            st.info("No active policies found.")
        else:
            for policy in policies:
                insurer = session.query(Party).join(
                    PartyRole, PartyRole.party_id == Party.id
                ).filter(
                    PartyRole.context_table == 'policy',
                    PartyRole.context_id == policy.id,
                    PartyRole.role_name == 'Insurer'
                ).first()
                
                with st.expander(f"🔹 {policy.policy_number} - {insurer.name if insurer else 'Unknown'}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Status", policy.status)
                    
                    with col2:
                        st.metric("Annual Premium", f"CHF {policy.quote.total_premium:,.0f}" if policy.quote else "N/A")
                    
                    with col3:
                        st.metric("Expires", policy.expiration_date.strftime('%Y-%m-%d'))
                    
                    # Coverages
                    st.markdown("**📊 Coverage Details:**")
                    coverage_data = []
                    for cov in policy.coverages:
                        coverage_data.append({
                            "Type": cov.coverage_type,
                            "Limit": f"CHF {cov.limit_amount:,.0f}",
                            "Deductible": f"CHF {cov.deductible_amount:,.0f}",
                            "Premium": f"CHF {cov.premium:,.0f}"
                        })
                    
                    if coverage_data:
                        st.dataframe(pd.DataFrame(coverage_data), use_container_width=True)
                    
                    # CTI Assistant Actions
                    st.markdown("---")
                    st.markdown("**🤖 CTI Assistant Actions:**")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(f"📝 Summarize Policy", key=f"sum_{policy.id}"):
                            with st.spinner("AI is analyzing your policy..."):
                                # Check if summary exists
                                existing_summary = session.query(PolicySummary).filter(
                                    PolicySummary.policy_id == policy.id,
                                    PolicySummary.user_id == user.id
                                ).first()
                                
                                if existing_summary:
                                    st.info("**AI-Generated Summary:**")
                                    st.markdown(existing_summary.summary_text)
                                else:
                                    summary = simulate_policy_summarization("Policy text...")
                                    
                                    # Save summary
                                    new_summary = PolicySummary(
                                        policy_id=policy.id,
                                        user_id=user.id,
                                        summary_text=summary,
                                        model_used='Claude 3 Sonnet (Simulated)'
                                    )
                                    session.add(new_summary)
                                    session.commit()
                                    
                                    st.info("**AI-Generated Summary:**")
                                    st.markdown(summary)
                    
                    with col2:
                        if st.button(f"✉️ Email Insurer", key=f"email_{policy.id}"):
                            policy_data = {
                                'number': policy.policy_number,
                                'type': 'Home' if 'HOME' in policy.policy_number else 'Auto',
                                'expiry': policy.expiration_date.strftime('%Y-%m-%d'),
                                'premium': policy.quote.total_premium if policy.quote else 0,
                                'customer_name': party.name
                            }
                            
                            email = simulate_email_generation("renewal", policy_data)
                            
                            st.success("**AI-Generated Email (Ready to Send):**")
                            st.text_input("Subject:", value=email['subject'], key=f"subj_{policy.id}")
                            st.text_area("Body:", value=email['body'], height=300, key=f"body_{policy.id}")
                            
                            if st.button("📤 Send Email", key=f"send_{policy.id}"):
                                # Save email template
                                new_email = EmailTemplate(
                                    user_id=user.id,
                                    policy_id=policy.id,
                                    template_type='renewal_inquiry',
                                    subject=email['subject'],
                                    body=email['body'],
                                    sent=True,
                                    sent_at=datetime.now()
                                )
                                session.add(new_email)
                                session.commit()
                                
                                st.success("✅ Email sent to insurer!")
                    
                    with col3:
                        if st.button(f"📞 File Claim", key=f"claim_{policy.id}"):
                            st.info("Claim filing redirected to Cacti Bot for assistance!")
    
    # ======================
    # PAGE 4: SPECIAL OFFERS
    # ======================
    elif page == "🎯 Special Offers":
        st.markdown('<div class="main-header"><h1>🎯 Special Offers</h1><p>AI-personalized recommendations just for you</p></div>', unsafe_allow_html=True)
        
        st.markdown("### 💡 Personalized Insurance Recommendations")
        st.caption("Generated by AI based on your current coverage gaps")
        
        # Load all ads
        all_ads = session.query(GeneratedAd).filter(GeneratedAd.user_id == user.id).all()
        
        if all_ads:
            for ad in all_ads:
                st.markdown(f"""
                <div class="ad-card">
                    <h3>{ad.product_type}</h3>
                    <p><small>Generated: {ad.generated_at.strftime('%Y-%m-%d %H:%M')}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.image(ad.image_url, width=400)
                
                with col2:
                    st.markdown(ad.ad_copy)
                    
                    if st.button(f"💰 Get Quote", key=f"offer_{ad.id}"):
                        # Mark as clicked
                        ad.clicked = True
                        ad.click_timestamp = datetime.now()
                        session.commit()
                        
                        st.success(f"✅ Quote request submitted for {ad.product_type}!")
                        st.balloons()
                
                st.markdown("---")
        
        # Generate new ad option
        st.markdown("### 🎨 Generate Custom Recommendation")
        
        product_types = ["Travel Insurance", "Life Insurance", "Pet Insurance", "Dental Insurance", "Critical Illness"]
        selected_product = st.selectbox("What insurance are you interested in?", product_types)
        
        if st.button("🤖 Generate AI Recommendation"):
            with st.spinner("AI is creating personalized content..."):
                # Simulate image generation
                image_url = simulate_image_generation(f"{selected_product} advertisement")
                
                # Simulate text generation
                ad_copy = simulate_ad_copy_generation(selected_product)
                
                # Save new ad
                new_ad = GeneratedAd(
                    user_id=user.id,
                    product_type=selected_product,
                    image_prompt=f"{selected_product} marketing visual",
                    image_url=image_url,
                    ad_copy=ad_copy,
                    clicked=False
                )
                session.add(new_ad)
                session.commit()
                
                st.success("✅ New recommendation generated!")
                st.rerun()
    
    # ======================
    # PAGE 5: MY ACCOUNT
    # ======================
    elif page == "👤 My Account":
        st.markdown('<div class="main-header"><h1>👤 My Account</h1></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Profile Picture")
            
            if user.avatar_url:
                st.image(user.avatar_url, width=200)
            else:
                st.info("No avatar set")
            
            if st.button("✏️ Generate New Avatar"):
                st.session_state.show_avatar_gen = True
            
            if st.session_state.get('show_avatar_gen', False):
                st.markdown("---")
                st.markdown("### 🎨 AI Avatar Generator")
                st.caption("Powered by Amazon Bedrock (Stable Diffusion)")
                
                avatar_prompt = st.text_input(
                    "Describe your avatar:",
                    placeholder="e.g., professional woman with glasses and friendly smile"
                )
                
                if st.button("🤖 Generate Avatar"):
                    if avatar_prompt:
                        with st.spinner("AI is creating your avatar..."):
                            # Simulate image generation
                            new_avatar_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={avatar_prompt[:20]}"
                            
                            # Update user avatar
                            user.avatar_url = new_avatar_url
                            user.avatar_prompt = avatar_prompt
                            session.commit()
                            
                            st.success("✅ New avatar generated!")
                            st.session_state.show_avatar_gen = False
                            st.rerun()
                    else:
                        st.warning("Please enter a description")
        
        with col2:
            st.subheader("Account Information")
            
            st.text_input("Name:", value=party.name, disabled=True)
            st.text_input("Email:", value=user.email, disabled=True)
            st.text_input("Phone:", value=party.phone or "Not provided", disabled=True)
            st.text_input("Address:", value=f"{party.address}, {party.city} {party.postal_code}", disabled=True)
            
            st.markdown("---")
            
            st.subheader("Account Activity")
            st.metric("Last Login", user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "N/A")
            st.metric("Member Since", user.created_at.strftime('%Y-%m-%d'))
            
            chat_count = session.query(ChatMessage).filter(ChatMessage.user_id == user.id).count()
            st.metric("Cacti Bot Conversations", chat_count)
    
    # Floating Chat Button (Always visible at bottom right)
    st.markdown("""
    <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
        <div style="
            width: 70px; 
            height: 70px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            cursor: pointer;
            animation: pulse 2s infinite;
            font-size: 32px;
        ">
            🌵
        </div>
        <div style="
            position: absolute;
            top: -5px;
            right: -5px;
            background: #FF6B6B;
            color: white;
            border-radius: 50%;
            width: 25px;
            height: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        ">
            💬
        </div>
    </div>
    <style>
    @keyframes pulse {
        0%, 100% { box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }
        50% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.8); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    session.close()

if __name__ == '__main__':
    main()

