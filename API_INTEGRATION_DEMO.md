# 🔌 API Integration Demo - Live Guidewire Simulation

## Overview

This demo shows a **live API integration** between a customer-facing portal and a Guidewire-style policy system. Watch quotes flow through the system in real-time!

---

## 🎯 What You'll See

### Customer Portal (app_customer_portal.py)
- Customer clicks "Get Free Quote"
- AI chatbot asks questions
- Quote generated in 12 seconds
- Delivered directly in chat

### Guidewire Backend (app_v2.py - Case 4)
- API request received
- Rating engine processes risk
- Automated underwriting decision
- Quote generated and delivered
- Full audit trail

---

## 🚀 Quick Start

### Option 1: Automated Setup (Windows)
Simply double-click:
```
run_both_demos.bat
```

### Option 2: Manual Setup

**Terminal 1 - Guidewire Backend:**
```bash
cd src
streamlit run app_v2.py --server.port 8501
```

**Terminal 2 - Customer Portal:**
```bash
cd src
streamlit run app_customer_portal.py --server.port 8502
```

---

## 📋 How to Use

### Step 1: Open Both Apps
- **Browser Tab 1** (http://localhost:8501): Guidewire Backend View
- **Browser Tab 2** (http://localhost:8502): Customer Portal View

### Step 2: Arrange Side-by-Side
Split your screen so you can see both windows simultaneously:
```
┌──────────────────────┬──────────────────────┐
│   Guidewire Backend  │   Customer Portal    │
│      (Port 8501)     │     (Port 8502)      │
│                      │                      │
│  📊 Processing View  │  👤 Customer View    │
└──────────────────────┴──────────────────────┘
```

### Step 3: Select Case 4
In the Guidewire Backend window (port 8501):
- Open the sidebar
- Select **"Case 4: API Integration Demo"**

### Step 4: Generate a Quote
In the Customer Portal window (port 8502):
- Go to **"🎯 Special Offers"** tab
- Click **"💰 Get Free Quote"** on Travel Insurance

### Step 5: Watch the Magic! ✨
- Customer Portal: Chat sidebar opens with AI conversation
- Guidewire Backend: Real-time processing stages appear
- See the complete flow from request to delivery!

---

## 🔄 Live Synchronization

Both apps share the same **SQLite database** (`pnc_demo.db`), enabling real-time synchronization:

```
Customer Action → Database Write → Guidewire Detects → Display Update
     (8502)           (SQLite)         (8501)            (Live!)
```

### Enable Auto-Refresh
In the Guidewire Backend (Case 4), enable **"🔄 Auto-refresh (every 2s)"** in the sidebar to see updates appear automatically.

---

## 📊 What the Demo Shows

### API Request Flow
```
1. ⚡ API Request Received
   └─ POST /api/v1/quote/create
   └─ Authentication validated
   └─ Duration: 0.1s

2. 🧮 Rating Engine Processing
   └─ Risk factors analyzed: 15
   └─ Premium calculated: CHF 89-450
   └─ Duration: 3.2s

3. 🤖 Automated Underwriting
   └─ Rules engine: 47 rules checked
   └─ Decision: ✅ Auto-approved
   └─ Confidence: 98%
   └─ Duration: 5.8s

4. ✅ Quote Generated
   └─ Quote ID: QT-10XXX
   └─ Delivered via Chat API
   └─ Total Duration: 12.1s
```

### Key Metrics Displayed
- **API Response Time**: p50, p95, p99 percentiles
- **Success Rate**: 99.8%
- **Auto-approval Rate**: 94%
- **Throughput**: 500 requests/minute
- **Active Connections**: Real-time count
- **Completed Today**: Live counter

---

## 🎬 Demo Scenarios

### Scenario 1: Travel Insurance Quote
1. Customer: Clicks "Get Free Quote" for Travel Insurance
2. System: Processes in 12 seconds
3. Backend: Shows all 4 processing stages
4. Result: Quote delivered in chat with full details

### Scenario 2: Life Insurance Quote
1. Customer: Clicks "Get Free Quote" for Life Insurance
2. System: Custom questions based on product type
3. Backend: Different risk factors analyzed
4. Result: Personalized premium calculation

### Scenario 3: Multiple Quotes
1. Generate 3-4 quotes in succession
2. Watch backend "Completed Today" counter increase
3. See full history in "Live Activity Feed"
4. Review API call details for each request

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│              Customer Portal (Frontend)             │
│  - Streamlit UI                                     │
│  - Chat Interface (OpenAI GPT-3.5)                  │
│  - Session Management                               │
└─────────────────┬───────────────────────────────────┘
                  │ HTTP/REST API
┌─────────────────▼───────────────────────────────────┐
│                  API Gateway                        │
│  - Authentication & Authorization                   │
│  - Rate Limiting                                    │
│  - Request Validation                               │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│         Guidewire PolicyCenter (Backend)            │
│  ┌───────────────────────────────────────────────┐  │
│  │  Rating Engine                                │  │
│  │  - Risk scoring                               │  │
│  │  - Premium calculation                        │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Underwriting Rules Engine                    │  │
│  │  - 47+ rules                                  │  │
│  │  - Auto-approval logic                        │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Quote Management                             │  │
│  │  - Quote generation                           │  │
│  │  - Policy creation                            │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│              Database Layer (SQLite)                │
│  - Customer data                                    │
│  - Chat messages                                    │
│  - Generated quotes                                 │
│  - Audit logs                                       │
└─────────────────────────────────────────────────────┘
```

---

## 💡 Key Benefits Demonstrated

### ✅ Speed
- **Before**: 2-3 days for manual quote
- **After**: 12 seconds automated quote
- **Improvement**: 99.9% faster

### ✅ Accuracy
- **Before**: Human error in data entry
- **After**: Automated rules engine
- **Improvement**: Zero transcription errors

### ✅ Scale
- **Before**: 10-20 quotes/day manually
- **After**: 500+ quotes/minute
- **Improvement**: 3,600x capacity increase

### ✅ Customer Experience
- **Before**: Call back next business day
- **After**: Instant quote in chat
- **Improvement**: 100% self-service

### ✅ Cost
- **Before**: $50-100 per quote (labor)
- **After**: $0.10 per quote (automated)
- **Improvement**: 99% cost reduction

---

## 🔍 Technical Details

### API Endpoints (Simulated)
```http
POST /api/v1/quote/create
Content-Type: application/json
Authorization: Bearer <token>

{
  "customer_id": "1",
  "product_type": "travel_insurance",
  "context": {
    "existing_policies": 2,
    "customer_segment": "individual",
    "channel": "customer_portal"
  }
}
```

### Response Structure
```json
{
  "quote_id": "QT-10001",
  "status": "approved",
  "premium": 89,
  "currency": "CHF",
  "valid_until": "2025-11-01",
  "processing_time_ms": 12100,
  "underwriting_decision": "auto_approved",
  "coverage_details": {
    "medical": 100000,
    "cancellation": 5000,
    "baggage": 2000
  }
}
```

---

## 🎯 Demo Tips

### For Sales Presentations
1. Start with the customer view to show UX
2. Switch to backend to reveal "under the hood"
3. Emphasize real-time synchronization
4. Show the performance metrics dashboard

### For Technical Audiences
1. Start with Case 4 architecture overview
2. Enable auto-refresh to show live updates
3. Expand API call details to show request/response
4. Discuss scaling and throughput metrics

### For Executive Audiences
1. Show the customer experience first
2. Highlight the 12-second quote time
3. Show the "Key Benefits" summary
4. Focus on cost savings and scale

---

## 🐛 Troubleshooting

### Apps Not Updating?
- Enable "🔄 Auto-refresh" in Guidewire Backend sidebar
- Or click "🔃 Manual Refresh" after each quote request

### Database Locked Error?
Close both apps and restart with the batch file

### Missing Data?
Ensure you've generated at least one quote in the Customer Portal first

---

## 📚 Related Documentation

- [Customer Portal README](./CUSTOMER_PORTAL_README.md)
- [Project Summary](./PROJECT_SUMMARY.md)
- [Quick Start Guide](./QUICK_START_CUSTOMER_PORTAL.md)

---

## 🎉 Enjoy the Demo!

This setup demonstrates how modern insurance platforms integrate multiple systems to deliver seamless customer experiences. Watch the magic of API automation in action!

**Questions?** Review the code in:
- `src/app_v2.py` (lines 1045-1331) - Backend view
- `src/app_customer_portal.py` (lines 364-382, 693-704) - Customer flow
- `src/seed_database.py` - Shared data models

