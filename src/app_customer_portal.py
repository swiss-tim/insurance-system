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
    /* Consistent text sizing */
    .stMarkdown p, .stText, div[data-testid="stMarkdownContainer"] p {
        font-size: 0.95rem !important;
        line-height: 1.5;
    }
    
    /* Reduce padding in info boxes */
    div[data-testid="stAlert"] {
        padding: 0.5rem 0.75rem !important;
    }
    
    /* Smaller metric cards */
    div[data-testid="stMetric"] {
        padding: 0.5rem !important;
    }
    
    /* Compact expanders */
    div[data-testid="stExpander"] {
        border: 1px solid #ddd;
        border-radius: 6px;
        padding: 0.5rem !important;
        margin: 0.5rem 0;
    }
    
    /* Main header styling */
    .main-header {
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        font-size: 1.75rem;
        margin: 0;
    }
    .main-header p {
        font-size: 0.95rem !important;
        margin: 0.25rem 0 0 0;
    }
    
    /* Chat message styling */
    .chat-user {
        background-color: #E3F2FD;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        text-align: right;
        font-size: 0.9rem;
    }
    .chat-bot {
        background-color: #F1F8E9;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    
    /* Ad card styling */
    .ad-card {
        border: 2px solid #4ECDC4;
        border-radius: 6px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        background: white;
    }
    .ad-card h4 {
        font-size: 1.1rem;
        margin: 0.25rem 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .metric-card h3 {
        font-size: 1.5rem;
        margin: 0.25rem 0;
    }
    .metric-card p {
        font-size: 0.9rem !important;
        margin: 0.25rem 0;
    }
    
    /* Compact dataframes */
    div[data-testid="stDataFrame"] {
        font-size: 0.9rem;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        padding-top: 1rem;
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
    # Map product types to relevant Unsplash images
    image_map = {
        'Travel Insurance': 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=400&h=300&fit=crop&q=80',  # Airplane wing
        'Life Insurance': 'https://images.unsplash.com/photo-1511895426328-dc8714191300?w=400&h=300&fit=crop&q=80',  # Family silhouette
        'Pet Insurance': 'https://images.unsplash.com/photo-1450778869180-41d0601e046e?w=400&h=300&fit=crop&q=80',  # Dog
        'Dental Insurance': 'https://images.unsplash.com/photo-1606811971618-4486d14f3f99?w=400&h=300&fit=crop&q=80',  # Dentist
        'Critical Illness': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400&h=300&fit=crop&q=80',  # Medical
    }
    
    # Find matching product type in prompt
    for product_type, url in image_map.items():
        if product_type.lower() in prompt.lower():
            return url
    
    # Default to travel image if no match
    return image_map['Travel Insurance']

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
    
    # Sidebar - Minimal User Info
    with st.sidebar:
        st.markdown(f"### 👤 {party.name}")
        st.caption(f"📧 {user.email}")
        
        if user.avatar_url:
            st.image(user.avatar_url, width=120)
        
        st.markdown("---")
        
        # Quick Stats
        st.metric("Active Policies", len(policies))
        total_premium = sum([p.quote.total_premium for p in policies if p.quote])
        st.metric("Annual Premium", f"CHF {total_premium:,.0f}")
        
        chat_count = session.query(ChatMessage).filter(ChatMessage.user_id == user.id).count()
        st.metric("Chat Messages", chat_count)
    
    # Cacti Bot in top-right corner (before tabs)
    col_main, col_chat = st.columns([10, 1])
    
    with col_chat:
        with st.popover("🌵", help="Chat with Cacti Bot", use_container_width=True):
            st.markdown("### 🌵 Cacti Bot")
            st.caption("Your AI Insurance Assistant")
            st.caption("*Powered by Amazon Bedrock (Claude 3)*")
            
            st.markdown("---")
            
            # Chat input form (moved to top)
            st.markdown("**✍️ Send a Message:**")
            user_message = st.text_area(
                "Your question:", 
                placeholder="Ask about policies, claims, renewals...",
                height=80,
                key="chat_input_popover",
                label_visibility="collapsed"
            )
            
            if st.button("📤 Send", type="primary", use_container_width=True):
                if user_message:
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
                    
                    st.success("✅ Sent!")
                    st.rerun()
                else:
                    st.warning("Please type a message first")
            
            st.markdown("---")
            
            # Chat history (moved to bottom, collapsed by default)
            chat_history = session.query(ChatMessage).filter(
                ChatMessage.user_id == user.id
            ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
            
            if chat_history:
                with st.expander("💬 Recent Conversations", expanded=False):
                    # Display in reverse (oldest first)
                    for chat in reversed(chat_history[-5:]):
                        st.markdown(f"""
                        <div style='background: #E3F2FD; padding: 8px; border-radius: 6px; margin: 4px 0; text-align: right;'>
                            <small style='color: #666;'>{chat.timestamp.strftime('%H:%M')}</small><br>
                            <strong>You:</strong> {chat.message[:80]}{"..." if len(chat.message) > 80 else ""}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style='background: #F1F8E9; padding: 8px; border-radius: 6px; margin: 4px 0;'>
                            <strong>🌵 Cacti:</strong> {chat.response[:100]}{"..." if len(chat.response) > 100 else ""}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.caption("💬 No chat history yet. Ask me anything!")
    
    # Top Navigation using Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Dashboard",
        "📋 My Policies",
        "🎯 Special Offers",
        "👤 My Account"
    ])
    
    # ======================
    # TAB 1: DASHBOARD
    # ======================
    with tab1:
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
        
        # Quick Tips
        st.subheader("⚡ Quick Tips")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("💬 **Need Help?**\n\nClick the 🌵 button at the top-right to chat with Cacti Bot!")
        
        with col2:
            st.info("📋 **Manage Policies**\n\nUse the tabs above to view your policies, special offers, and account")
        
        with col3:
            st.info("🤖 **AI Features**\n\nGet policy summaries, generate emails, and personalized recommendations!")
        
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
    # TAB 2: MY POLICIES
    # ======================
    with tab2:
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
                            "Deductible": f"CHF {cov.deductible_amount:,.0f}"
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
    # TAB 3: SPECIAL OFFERS
    # ======================
    with tab3:
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
    # TAB 4: MY ACCOUNT
    # ======================
    with tab4:
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
            
            # Build address string
            address_parts = []
            if party.address:
                address_parts.append(party.address)
            if party.city:
                address_parts.append(party.city)
            if party.country:
                address_parts.append(party.country)
            address_str = ", ".join(address_parts) if address_parts else "Not provided"
            
            st.text_input("Address:", value=address_str, disabled=True)
            
            st.markdown("---")
            
            st.subheader("Account Activity")
            st.metric("Last Login", user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "N/A")
            st.metric("Member Since", user.created_at.strftime('%Y-%m-%d'))
            
            # Additional stats
            policy_count = len(policies)
            st.metric("Total Policies", policy_count)
    
    session.close()

if __name__ == '__main__':
    main()

