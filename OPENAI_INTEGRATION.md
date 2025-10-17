# OpenAI Integration Guide

## Overview

The Customer Portal now uses **OpenAI GPT-4** to power:
1. **Cacti Bot** - Intelligent chat assistant that answers questions using real customer data
2. **Quote Generation** - AI-guided conversation flow for generating insurance quotes

## Features

### 1. Intelligent Chat Assistant
- Answers questions about policies, renewals, claims, and coverage
- Uses **real customer data** from the database in responses
- Provides personalized, context-aware answers
- Supports keywords: "renewal", "policies", "claim", "coverage", "premium"

### 2. AI Quote Generation
- Follows a trained 7-step conversation pattern
- Asks relevant questions for each insurance product
- Generates realistic, bindable quotes
- Completes in ~12-15 seconds

## Setup

### 1. Install Dependencies
```bash
pip install openai>=1.0.0
```

### 2. Configure API Key
Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-api-key-here"
```

**Note:** The API key is stored securely and excluded from version control via `.gitignore`

### 3. Run the Application
```bash
cd src
streamlit run app_customer_portal.py
```

## How It Works

### Chat Assistant Flow
1. User sends a message (e.g., "when is my renewal?")
2. System builds context with customer's policy data:
   - Policy numbers and types
   - Premium amounts
   - Expiration dates
   - Customer name and email
3. OpenAI GPT-4 generates personalized response
4. Response displayed in chat UI

### Quote Flow
1. User clicks "Get Free Quote" for a product
2. System generates 7-message conversation using OpenAI:
   - **Message 1 (Bot):** Greeting with customer name
   - **Message 2 (User):** Positive response
   - **Message 3 (Bot):** First question about product
   - **Message 4 (User):** Customer answer
   - **Message 5 (Bot):** Follow-up question
   - **Message 6 (User):** Additional details
   - **Message 7 (Bot):** Complete quote with pricing
3. Conversation auto-plays with 1-second delays
4. Final quote is bindable and ready to purchase

## Example Conversations

### Renewal Question
**User:** "when do my policies renew?"

**Cacti Bot:** "Your policies are set to renew on **December 31, 2024**. Your current annual premium across both policies (Home Insurance and Auto Insurance) is **CHF 2,050**. Would you like me to help you explore any changes or additional coverage options before renewal?"

### Travel Insurance Quote
```
Bot: "Great choice, Maria Weber! I'll help you get a personalized Travel Insurance quote. This will only take 15 seconds. ✈️"
User: "Sounds good!"
Bot: "Perfect! Let me ask you a few quick questions. **Where are you planning to travel?**"
User: "Europe - planning a 2-week trip to Italy and France"
Bot: "Excellent! **How many travelers?** And any pre-existing medical conditions I should know about?"
User: "Just me, and no pre-existing conditions"
Bot: "Perfect! 🎉

**Your Personalized Quote:**
✓ Destination: Europe (Italy & France)
✓ Duration: 14 days
✓ Travelers: 1 adult
✓ Medical Coverage: CHF 100,000
✓ Trip Cancellation: CHF 5,000
✓ Baggage Loss: CHF 2,000
✓ 24/7 Emergency Assistance

**Total Premium: CHF 89**

This quote is bindable and ready to purchase! ⏱️ Generated in 12 seconds."
```

## Cost Considerations

- **Model:** GPT-4
- **Average tokens per chat:** ~500 tokens
- **Average tokens per quote:** ~1,500 tokens
- **Estimated cost:** $0.01-0.05 per interaction

## Error Handling

If the OpenAI API fails:
- Chat responses fall back to a friendly error message
- Quote flows use hardcoded fallback conversations
- User experience remains smooth

## Security

✅ API key stored in `.streamlit/secrets.toml` (gitignored)
✅ No API key exposed in code
✅ Secure server-side API calls only
✅ No client-side API key exposure

## Future Enhancements

- [ ] Add conversation memory across sessions
- [ ] Support multi-turn quote negotiations
- [ ] Generate actual policy documents
- [ ] Voice input/output support
- [ ] Multi-language support

