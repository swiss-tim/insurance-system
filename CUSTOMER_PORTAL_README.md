# 🌵 Customer Portal with AI Features

## Overview

This is a **customer-facing insurance portal** with AI-powered features simulating Amazon Bedrock integration. It's completely separate from the broker/agent demo apps.

## Features

### 1. 🏠 Main Dashboard
- Overview of active policies and premiums
- Quick actions (chat, view policies, file claim, get quote)
- AI-generated personalized upsell ads
- Recent activity feed

### 2. 💬 Cacti Bot - AI Chatbot
**Simulates:** Amazon Bedrock with Claude 3

- Natural language Q&A about policies
- Context-aware responses using customer data
- Chat history saved to database
- Example prompts provided

**How it works:**
- User asks question → System retrieves customer/policy data → AI generates response
- In production, would call Bedrock API

### 3. 📋 My Policies with CTI Assistant
**CTI Assistant Features:**

#### Policy Summarization
**Simulates:** Claude 3 Sonnet
- Simplifies complex policy documents
- Generates easy-to-understand summaries
- Highlights key coverage, exclusions, and terms

#### Email Generation
**Simulates:** Titan Text Generation
- Auto-generates professional emails to insurers
- Pre-filled with policy details and customer info
- Ready to review and send

### 4. 🎯 Special Offers - AI-Generated Ads
**Simulates:** Stable Diffusion (images) + Titan (text)

- Personalized product recommendations based on coverage gaps
- AI-generated imagery for each product
- Compelling ad copy tailored to customer
- Quote request tracking

**How it works:**
- System checks what policies customer has
- Identifies products they're missing
- Generates unique visual + text for that product

### 5. 👤 My Account - Avatar Generator
**Simulates:** Stable Diffusion

- Custom AI-generated profile pictures
- Text-to-image: describe your ideal avatar
- Instant generation and profile update

---

## Running the Customer Portal

### Prerequisites
Ensure you have:
- Python environment with dependencies installed
- Database seeded with Case 4 data (Maria Weber)

### Step 1: Reset Database (if needed)

**Option A: Manual**
```powershell
# Close ALL running Streamlit apps first
# Then delete the database file
cd src
Remove-Item pnc_demo.db -Force
```

**Option B: Using script**
```powershell
cd src
python reset_db.py
python seed_database.py
```

### Step 2: Run Customer Portal

```powershell
cd src
streamlit run app_customer_portal.py --server.port 8503
```

Access at: **http://localhost:8503**

### Step 3: Login (Demo Mode)

The demo automatically logs in as:
- **User:** Maria Weber
- **Email:** maria.weber@example.com
- **Policies:** Home Insurance + Auto Insurance

---

## Demo User Story: Maria Weber

### Profile
- **Name:** Maria Weber
- **Location:** Lucerne, Switzerland
- **Current Policies:**
  1. Home Insurance (Casa Insurance AG) - CHF 1,200/year
  2. Auto Insurance (DriveSecure Insurance) - CHF 850/year

### Pre-seeded Data

#### Chat History
- 3 conversations with Cacti Bot about policies, renewals, claims

#### Generated Ads
- Travel Insurance (she doesn't have this yet)
- Life Insurance (she doesn't have this yet)

#### Policy Summaries
- AI-generated summary of home insurance

#### Email Templates
- Renewal inquiry draft for home insurance

---

## AI Simulation vs Production

### Current Implementation (Demo)
```python
def simulate_chatbot_response(user_message, user_data):
    # Simple keyword matching
    return "Simulated response"
```

### Production Implementation
```python
import boto3

bedrock = boto3.client('bedrock-runtime')

def chatbot_response(user_message, user_data):
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            "messages": [{
                "role": "user",
                "content": f"Context: {user_data}\n\nQuestion: {user_message}"
            }],
            "max_tokens": 1000,
            "anthropic_version": "bedrock-2023-05-31"
        })
    )
    return json.loads(response['body'].read())['content'][0]['text']
```

---

## Architecture

### Database Tables (New)

```sql
-- Customer user accounts
customer_user (
    id, party_id, email, password_hash, 
    avatar_url, avatar_prompt, created_at, last_login
)

-- Chatbot conversations
chat_message (
    id, user_id, message, response, 
    timestamp, is_user, model_used
)

-- AI-generated advertisements
generated_ad (
    id, user_id, product_type, image_prompt,
    image_url, ad_copy, generated_at, clicked
)

-- Policy summaries (CTI Assistant)
policy_summary (
    id, policy_id, user_id, summary_text, 
    generated_at, model_used
)

-- Email templates (CTI Assistant)
email_template (
    id, user_id, policy_id, claim_id,
    template_type, subject, body,
    generated_at, sent, sent_at
)
```

### Data Flow

```
User Action → Streamlit UI → Simulate AI Call → Update Database → Display Result
```

In production:
```
User Action → Streamlit UI → Amazon Bedrock API → Update Database → Display Result
```

---

## Customization

### Add More Demo Users
Edit `seed_database.py` around line 450:

```python
# Add another customer
customer2 = CustomerUser(
    party_id=new_party.id,
    email='john.smith@example.com',
    password_hash='demo_hash',
    ...
)
```

### Change AI Responses
Edit `app_customer_portal.py`:

```python
def simulate_chatbot_response(user_message, user_data):
    # Customize responses here
    if "claim" in user_message.lower():
        return "Your customized claim response..."
```

### Add New Ad Products
```python
ad_templates = {
    "Travel Insurance": "Your ad copy...",
    "Your New Product": "Custom ad copy..."
}
```

---

## Integration with Amazon Bedrock

### Required Changes

1. **Install AWS SDK**
```bash
pip install boto3
```

2. **Configure AWS Credentials**
```bash
aws configure
```

3. **Replace Simulation Functions**

**Chatbot (Claude 3)**
```python
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def call_claude(prompt, context):
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            "messages": [{"role": "user", "content": f"{context}\n\n{prompt}"}],
            "max_tokens": 2000,
            "anthropic_version": "bedrock-2023-05-31"
        })
    )
    return json.loads(response['body'].read())['content'][0]['text']
```

**Image Generation (Stable Diffusion)**
```python
def generate_image(prompt):
    response = bedrock.invoke_model(
        modelId='stability.stable-diffusion-xl-v1',
        body=json.dumps({
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 10,
            "steps": 50
        })
    )
    image_data = json.loads(response['body'].read())
    return base64.b64decode(image_data['artifacts'][0]['base64'])
```

**Text Generation (Titan)**
```python
def generate_text(prompt):
    response = bedrock.invoke_model(
        modelId='amazon.titan-text-express-v1',
        body=json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.7
            }
        })
    )
    return json.loads(response['body'].read())['results'][0]['outputText']
```

---

## Troubleshooting

### Database Locked Error
```
sqlite3.OperationalError: database is locked
```

**Solution:**
1. Close all running Streamlit apps
2. Wait 5 seconds
3. Delete `pnc_demo.db`
4. Re-run `python seed_database.py`

### No Customer Found
```
st.error("Please log in to access your portal.")
```

**Solution:**
Database doesn't have Case 4 data. Re-seed:
```powershell
python seed_database.py
```

### Missing Imports
```
ImportError: cannot import name 'CustomerUser'
```

**Solution:**
The database schema was updated. Delete DB and reseed.

---

## Comparison: Broker Apps vs Customer Portal

| Feature | Broker Apps (app_v2.py) | Customer Portal (app_customer_portal.py) |
|---------|-------------------------|------------------------------------------|
| **Audience** | Insurance professionals | End customers |
| **Focus** | Process efficiency & pain points | Self-service & engagement |
| **AI Features** | None (shows data) | 5 AI features (chatbot, ads, summaries, etc.) |
| **Navigation** | Case studies → Process steps | Dashboard → My account |
| **Data** | 3 B2B cases | 1 B2C customer |
| **Story** | Manual vs automated processes | Customer empowerment |

---

## Demo Script

### For Presentations

1. **Start on Dashboard**
   - "This is Maria's personalized insurance portal"
   - Show active policies and premiums
   - Point out AI-generated ads

2. **Open Cacti Bot**
   - "Maria can ask questions in natural language"
   - Type: "What are my policies?"
   - Show AI response with context

3. **View My Policies**
   - Select home insurance
   - Click "Summarize Policy"
   - Show AI-generated simple summary
   - Click "Email Insurer"
   - Show AI-generated professional email

4. **Check Special Offers**
   - "These ads are personalized based on what Maria doesn't have"
   - Show travel insurance recommendation
   - Explain AI generated both image and text

5. **Visit My Account**
   - Click "Generate New Avatar"
   - Type: "friendly professional woman with glasses"
   - Show AI-generated avatar

**Key Message:**
"Every feature here uses AI to make insurance more accessible and engaging for customers. In production, this runs on Amazon Bedrock with Claude, Titan, and Stable Diffusion."

---

## Production Checklist

- [ ] Replace all `simulate_*` functions with real Bedrock calls
- [ ] Add proper authentication (OAuth, JWT)
- [ ] Implement rate limiting on AI calls
- [ ] Add error handling for API failures
- [ ] Set up monitoring for API usage/costs
- [ ] Add HTTPS/SSL
- [ ] Implement proper password hashing (bcrypt)
- [ ] Add email verification
- [ ] Create admin panel for content moderation
- [ ] Add analytics tracking
- [ ] Implement A/B testing for AI-generated content
- [ ] Set up automated testing for AI responses

---

## Cost Estimation (Production)

### Amazon Bedrock Pricing (Approximate)

- **Claude 3 Sonnet:** $0.003 per 1K input tokens, $0.015 per 1K output tokens
- **Titan Text:** $0.0008 per 1K input tokens, $0.0016 per 1K output tokens
- **Stable Diffusion XL:** $0.040 per image

### Example Monthly Cost (1000 active users)

- **Chatbot:** 1000 users × 10 messages × $0.02 avg = $200
- **Policy Summaries:** 1000 users × 2 policies × $0.05 = $100
- **Email Generation:** 500 emails × $0.02 = $10
- **Upsell Ads:** 1000 users × 2 ads × $0.08 = $160
- **Avatars:** 200 generations × $0.04 = $8

**Total:** ~$478/month for AI features

---

## Support

For questions about:
- **Database:** Check `seed_database.py`
- **AI Simulation:** Check `app_customer_portal.py` simulation functions
- **Bedrock Integration:** See "Integration with Amazon Bedrock" section

---

**Built with ❤️ using Streamlit, SQLAlchemy, and (simulated) Amazon Bedrock**

