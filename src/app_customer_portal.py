# Customer Portal with AI Features
# Powered by OpenAI GPT-4

import streamlit as st
import pandas as pd
from datetime import datetime
import random
import time
from openai import OpenAI

# Initialize database
from init_db import init_database
init_database()

from database_queries import get_session
from seed_database import (
    CustomerUser, ChatMessage, GeneratedAd, PolicySummary,
    EmailTemplate, Policy, Coverage, Party, PartyRole
)

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

# OpenAI AI Functions
def simulate_chatbot_response(user_message, user_data):
    """Use OpenAI GPT-4 to answer customer questions with real data"""
    
    # Build context from user's database data
    policies_info = []
    for policy in user_data['policies']:
        # Get policy type from coverages or assets
        policy_type = "Insurance"
        if policy.coverages and len(policy.coverages) > 0:
            policy_type = policy.coverages[0].coverage_type
        elif policy.assets and len(policy.assets) > 0:
            policy_type = policy.assets[0].asset_type
        
        policy_text = f"- {policy_type} (Policy #{policy.policy_number})"
        if policy.quote:
            policy_text += f", Premium: CHF {policy.quote.total_premium:,.0f}/year"
        if policy.effective_date and policy.expiration_date:
            policy_text += f", Valid: {policy.effective_date.strftime('%Y-%m-%d')} to {policy.expiration_date.strftime('%Y-%m-%d')}"
        policies_info.append(policy_text)
    
    # Calculate total premium
    total_premium = sum([p.quote.total_premium for p in user_data['policies'] if p.quote])
    
    # Build system prompt with customer data
    system_prompt = f"""You are Cacti Bot, a friendly insurance assistant for {user_data['name']}.

Customer Information:
- Name: {user_data['name']}
- Email: {user_data['email']}
- Active Policies: {len(user_data['policies'])}
{chr(10).join(policies_info)}
- Total Annual Premium: CHF {total_premium:,.0f}
- Next Renewal Date: December 31, 2025

Guidelines:
- Be helpful, friendly, and concise
- Use the customer's actual policy data in your responses
- For renewal questions, mention the date and current premium
- For policy questions, reference their specific policies
- For claims, provide step-by-step guidance
- Suggest relevant products they don't have (Travel, Life, Pet insurance)
- Use markdown formatting for emphasis
- Keep responses under 150 words unless detailed explanation needed"""

    try:
        # Try OpenAI GPT-3.5-turbo first (more widely available)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        # Fallback to keyword-based responses if OpenAI fails
        message_lower = user_message.lower().strip()
        
        # Smart fallback responses using actual user data
        if "renewal" in message_lower or "renew" in message_lower:
            return f"Your policies are set to renew on **December 31, 2025**.\n\nCurrent policies:\n{chr(10).join(['• ' + info for info in policies_info])}\n\n**Total Annual Premium: CHF {total_premium:,.0f}**\n\nWe'll send renewal notices 30 days before expiration. Would you like to discuss renewal options or make any changes?"
        
        if "policies" in message_lower or "policy" in message_lower:
            return f"You have **{len(user_data['policies'])} active policies**:\n\n{chr(10).join(policies_info)}\n\n**Total Annual Premium: CHF {total_premium:,.0f}**\n\nWould you like details on any specific policy?"
        
        if "claim" in message_lower:
            return "To file a claim, please provide:\n\n1. **Date of incident**\n2. **Description** of what happened\n3. **Photos** if available\n4. **Police report** (if applicable)\n\nI can help guide you through the process step-by-step!"
        
        if "coverage" in message_lower:
            policy_types = [info.split('(')[0].strip() for info in policies_info]
            return f"Your current coverage includes:\n\n{chr(10).join(['• ' + pt for pt in policy_types])}\n\nWould you like to add **Travel Insurance**, **Life Insurance**, or **Pet Insurance**? I can get you a quote in seconds!"
        
        if "premium" in message_lower or "cost" in message_lower or "price" in message_lower:
            return f"**Total Annual Premium: CHF {total_premium:,.0f}**\n\nBreakdown:\n{chr(10).join(policies_info)}\n\nWould you like information about payment options or discounts?"
        
        # Default helpful response
        return f"I'm here to help you with your insurance needs!\n\nYou can ask me about:\n• **Renewal** dates and options\n• Your **policies** and coverage details\n• Filing **claims**\n• Adding new **coverage**\n• **Premium** information\n\nWhat would you like to know?"

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

# AI Quote Flow Function (using OpenAI)
def get_quote_flow(product_type, user):
    """Generate quote conversation flow using OpenAI GPT-4"""
    
    # Training data for the AI to learn the pattern
    quote_training = f"""You are generating an insurance quote conversation for {product_type}.

CONVERSATION STRUCTURE (exactly 7 messages):
1. Bot: Greeting - welcome customer by name ({user.party.name}), mention product and say "15 seconds"
2. User: "Sounds good!" or similar positive response
3. Bot: Ask first question relevant to {product_type}
4. User: Answer with reasonable example details
5. Bot: Ask follow-up question about coverage preferences/specifics
6. User: Provide additional details
7. Bot: Present complete quote with:
   - 🎉 celebration emoji
   - "Your Personalized Quote:" header
   - Bulleted list (✓) of coverage details
   - **Total Premium:** in CHF
   - "This quote is bindable and ready to purchase!"
   - "⏱️ Generated in 12 seconds"

EXAMPLE FOR TRAVEL INSURANCE:
Message 1 (Bot): "Great choice, {user.party.name}! I'll help you get a personalized Travel Insurance quote. This will only take 15 seconds. ✈️"
Message 2 (User): "Sounds good!"
Message 3 (Bot): "Perfect! Let me ask you a few quick questions. **Where are you planning to travel?**"
Message 4 (User): "Europe - planning a 2-week trip to Italy and France"
Message 5 (Bot): "Excellent! **How many travelers?** And any pre-existing medical conditions I should know about?"
Message 6 (User): "Just me, and no pre-existing conditions"
Message 7 (Bot): "Perfect! 🎉\n\n**Your Personalized Quote:**\n\n✓ Destination: Europe (Italy & France)\n✓ Duration: 14 days\n✓ Travelers: 1 adult\n✓ Medical Coverage: CHF 100,000\n✓ Trip Cancellation: CHF 5,000\n✓ Baggage Loss: CHF 2,000\n✓ 24/7 Emergency Assistance\n\n**Total Premium: CHF 89**\n\nThis quote is bindable and ready to purchase! Click below to proceed. ⏱️ Generated in 12 seconds."

Generate EXACTLY 7 messages following this pattern for {product_type}. Return as JSON array."""

    try:
        # Use OpenAI to generate the conversation
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an insurance quote conversation generator. Generate realistic, friendly insurance quote conversations."},
                {"role": "user", "content": quote_training}
            ],
            temperature=0.8,
            max_tokens=1500
        )
        
        # Parse the response (expecting JSON array)
        import json
        try:
            flow = json.loads(response.choices[0].message.content)
            if len(flow) == 7:
                return flow
        except:
            pass
            
    except Exception as e:
        pass
    
    # Fallback to hardcoded for Travel Insurance (the example provided)
    if product_type == 'Travel Insurance':
        return [
            {'type': 'bot', 'text': f"Great choice, {user.party.name}! I'll help you get a personalized Travel Insurance quote. This will only take 15 seconds. ✈️"},
            {'type': 'user', 'text': "Sounds good!"},
            {'type': 'bot', 'text': "Perfect! Let me ask you a few quick questions. **Where are you planning to travel?**"},
            {'type': 'user', 'text': "Europe - planning a 2-week trip to Italy and France"},
            {'type': 'bot', 'text': "Excellent! **How many travelers?** And any pre-existing medical conditions I should know about?"},
            {'type': 'user', 'text': "Just me, and no pre-existing conditions"},
            {'type': 'bot', 'text': "Perfect! 🎉\n\n**Your Personalized Quote:**\n\n✓ Destination: Europe (Italy & France)\n✓ Duration: 14 days\n✓ Travelers: 1 adult\n✓ Medical Coverage: CHF 100,000\n✓ Trip Cancellation: CHF 5,000\n✓ Baggage Loss: CHF 2,000\n✓ 24/7 Emergency Assistance\n\n**Total Premium: CHF 89**\n\nThis quote is bindable and ready to purchase! Click below to proceed. ⏱️ Generated in 12 seconds."},
        ]
    
    # Generic fallback for other products
    return [
        {'type': 'bot', 'text': f"Hi {user.party.name}! Let me help you get a quote for {product_type}. Just a few quick questions!"},
        {'type': 'user', 'text': "Sure, go ahead"},
        {'type': 'bot', 'text': f"**What coverage level do you need for {product_type}?**"},
        {'type': 'user', 'text': "Standard coverage would be great"},
        {'type': 'bot', 'text': "Perfect! **Any specific requirements or preferences?**"},
        {'type': 'user', 'text': "No special requirements"},
        {'type': 'bot', 'text': f"🎉 **Your Quote is Ready!**\n\n**Your Personalized Quote:**\n\n✓ Product: {product_type}\n✓ Coverage: Standard\n✓ Deductible: CHF 500\n✓ Coverage Limit: CHF 50,000\n\n**Total Premium: CHF 95/month**\n\nThis bindable quote was generated in 12 seconds! ⏱️"},
    ]

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
    
    # Initialize chat state variables
    if 'quote_flow_active' not in st.session_state:
        st.session_state.quote_flow_active = False
    if 'quote_messages' not in st.session_state:
        st.session_state.quote_messages = []
    if 'quote_step' not in st.session_state:
        st.session_state.quote_step = 0
    if 'quote_product' not in st.session_state:
        st.session_state.quote_product = None
    if 'last_message_time' not in st.session_state:
        st.session_state.last_message_time = None
    
    # Sidebar - Dynamic Content (User Info OR Chat)
    with st.sidebar:
        if st.session_state.quote_flow_active:
            # CHAT MODE - AI Quote Generation
            st.markdown("### 🤖 AI Quote Generation")
            st.caption(f"For: **{st.session_state.quote_product}**")
            st.caption("*Powered by Amazon Bedrock (Claude 3)*")
            
            if st.button("❌ Close Chat", use_container_width=True):
                st.session_state.quote_flow_active = False
                st.session_state.quote_messages = []
                st.session_state.quote_step = 0
                st.session_state.last_message_time = None
                st.rerun()
            
            st.markdown("---")
            
            # Display quote conversation
            for msg in st.session_state.quote_messages:
                if msg['type'] == 'bot':
                    st.markdown(f"""
                    <div style='background: #E8F5E9; padding: 10px; border-radius: 6px; margin: 6px 0; border-left: 3px solid #4CAF50;'>
                        <strong>🤖 AI Agent:</strong> {msg['text']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background: #E3F2FD; padding: 10px; border-radius: 6px; margin: 6px 0; text-align: right; border-right: 3px solid #2196F3;'>
                        <strong>You:</strong> {msg['text']}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Progress quote flow
            quote_flows = get_quote_flow(st.session_state.quote_product, user)
            total_steps = len(quote_flows)
            
            if st.session_state.quote_step < total_steps:
                # Check if enough time has passed since last message
                current_time = time.time()
                time_since_last = current_time - st.session_state.last_message_time if st.session_state.last_message_time else 999
                
                if time_since_last < 1.0:
                    # Still waiting - show typing indicator
                    st.markdown("**🤖 typing...**")
                    time.sleep(0.5)  # Wait a bit
                    st.rerun()  # Force rerun to check again
                else:
                    # Time to show next message
                    st.session_state.quote_messages.append(quote_flows[st.session_state.quote_step])
                    st.session_state.quote_step += 1
                    st.session_state.last_message_time = current_time
                    st.rerun()
            else:
                # Flow complete
                st.markdown("---")
                st.success("✅ **Quote Complete!**")
                st.caption(f"Generated in ~{len(quote_flows)} seconds")
                
                if st.button("🔄 Get Another Quote", use_container_width=True):
                    st.session_state.quote_flow_active = False
                    st.session_state.quote_messages = []
                    st.session_state.quote_step = 0
                    st.session_state.last_message_time = None
                    st.rerun()
        else:
            # NORMAL MODE - User Info & Chat Access
            st.markdown(f"### 👤 {party.name}")
            st.caption(f"📧 {user.email}")
            
            st.markdown("---")
            
            # Manual chat access
            col_title, col_clear = st.columns([3, 1])
            with col_title:
                st.markdown("### 💬 Cacti Bot")
            with col_clear:
                if st.button("🗑️", help="Clear chat history", key="clear_chat"):
                    # Clear session state
                    st.session_state.chat_messages = []
                    st.session_state.chat_loaded = False
                    # Delete from database
                    session.query(ChatMessage).filter(ChatMessage.user_id == user.id).delete()
                    session.commit()
                    st.success("Chat cleared!")
                    st.rerun()
            
            # Initialize session state for chat
            if 'chat_messages' not in st.session_state:
                st.session_state.chat_messages = []
            
            # Load chat history from database only once
            if 'chat_loaded' not in st.session_state:
                chat_history = session.query(ChatMessage).filter(
                    ChatMessage.user_id == user.id
                ).order_by(ChatMessage.timestamp.asc()).limit(10).all()
                
                for chat in chat_history:
                    st.session_state.chat_messages.append({
                        "role": "user",
                        "content": chat.message,
                        "timestamp": chat.timestamp
                    })
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": chat.response,
                        "timestamp": chat.timestamp
                    })
                st.session_state.chat_loaded = True
            
            # Chat container with messages
            chat_container = st.container()
            
            with chat_container:
                # Display all messages
                if len(st.session_state.chat_messages) == 0:
                    st.info("👋 Start a conversation! Ask me about policies, renewals, claims, or coverage.")
                else:
                    for message in st.session_state.chat_messages:
                        if message["role"] == "user":
                            st.markdown(f"""
                            <div style='background: #E3F2FD; padding: 10px; border-radius: 8px; margin: 6px 0; text-align: right; border-right: 3px solid #2196F3;'>
                                <small style='color: #666;'>{message['timestamp'].strftime('%H:%M')}</small><br>
                                <strong>You:</strong> {message['content']}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style='background: #E8F5E9; padding: 10px; border-radius: 8px; margin: 6px 0; border-left: 3px solid #4CAF50;'>
                                <strong>🌵 Cacti:</strong> {message['content']}
                            </div>
                            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Chat input at BOTTOM (using chat_input for Enter-to-send)
            user_input = st.chat_input(
                placeholder="Type your message and press Enter...",
                key="chat_input_box"
            )
            
            # Process message when Enter is pressed or send button clicked
            if user_input:
                # Add user message immediately
                current_time = datetime.now()
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": current_time
                })
                
                # Show thinking message
                with chat_container:
                    st.markdown("""
                    <div style='background: #FFF3CD; padding: 10px; border-radius: 8px; margin: 6px 0; border-left: 3px solid #FFC107;'>
                        <strong>🤖 Cacti is thinking...</strong>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Get AI response
                try:
                    user_data = {
                        'policies': policies,
                        'name': party.name,
                        'email': user.email
                    }
                    
                    response = simulate_chatbot_response(user_input, user_data)
                    
                    # Add assistant response
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": current_time
                    })
                    
                    # Save to database
                    new_chat = ChatMessage(
                        user_id=user.id,
                        message=user_input,
                        response=response,
                        timestamp=current_time,
                        is_user=True,
                        model_used='OpenAI GPT-4'
                    )
                    session.add(new_chat)
                    session.commit()
                    
                    # Clear input and rerun
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    # Remove the user message if failed
                    st.session_state.chat_messages.pop()
    
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
                    
                    if st.button(f"💰 Get Free Quote", key=f"ad_{ad.id}", type="primary"):
                        # Start AI quote flow
                        st.session_state.quote_flow_active = True
                        st.session_state.quote_messages = []
                        st.session_state.quote_step = 0
                        st.session_state.quote_product = ad.product_type
                        st.session_state.last_message_time = None
                        st.rerun()
        
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
                    
                    if st.button(f"💰 Get Free Quote", key=f"offer_{ad.id}", type="primary"):
                        # Mark as clicked
                        ad.clicked = True
                        ad.click_timestamp = datetime.now()
                        session.commit()
                        
                        # Start AI quote flow
                        st.session_state.quote_flow_active = True
                        st.session_state.quote_messages = []
                        st.session_state.quote_step = 0
                        st.session_state.quote_product = ad.product_type
                        st.session_state.last_message_time = None
                        st.rerun()
                
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

