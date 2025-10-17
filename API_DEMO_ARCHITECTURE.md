# 🏗️ API Integration Demo - Architecture

## System Flow Diagram

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃               CUSTOMER PORTAL (Port 8502)               ┃
┃  ┌────────────────────────────────────────────────┐    ┃
┃  │  Customer clicks "Get Free Quote"              │    ┃
┃  │  • Travel Insurance                            │    ┃
┃  │  • Life Insurance                              │    ┃
┃  │  • Pet Insurance                               │    ┃
┃  └────────────┬───────────────────────────────────┘    ┃
┃               │                                         ┃
┃               ▼                                         ┃
┃  ┌────────────────────────────────────────────────┐    ┃
┃  │  AI Chatbot Opens (OpenAI GPT-3.5)             │    ┃
┃  │  • Asks product-specific questions             │    ┃
┃  │  • Collects customer information               │    ┃
┃  │  • Simulates 12-second conversation            │    ┃
┃  └────────────┬───────────────────────────────────┘    ┃
┗━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                │
                │ 📝 Write to Database
                │ (ChatMessage table)
                │
                ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                SHARED DATABASE (SQLite)                 ┃
┃  ┌────────────────────────────────────────────────┐    ┃
┃  │  Tables:                                       │    ┃
┃  │  • CustomerUser                                │    ┃
┃  │  • ChatMessage  ← NEW QUOTE REQUEST STORED     │    ┃
┃  │  • Policy                                      │    ┃
┃  │  • Quote                                       │    ┃
┃  └────────────────────────────────────────────────┘    ┃
┗━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                │
                │ 🔍 Database Query
                │ (Auto-refresh every 2s)
                │
                ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃           GUIDEWIRE BACKEND (Port 8501)                 ┃
┃  ┌────────────────────────────────────────────────┐    ┃
┃  │  ⚡ Stage 1: API Request Received               │    ┃
┃  │  • POST /api/v1/quote/create                   │    ┃
┃  │  • Status: 200 OK                              │    ┃
┃  │  • Duration: 0.1s                              │    ┃
┃  └────────────┬───────────────────────────────────┘    ┃
┃               ▼                                         ┃
┃  ┌────────────────────────────────────────────────┐    ┃
┃  │  🧮 Stage 2: Rating Engine                     │    ┃
┃  │  • Analyze 15 risk factors                     │    ┃
┃  │  • Calculate premium: CHF 89-450               │    ┃
┃  │  • Duration: 3.2s                              │    ┃
┃  └────────────┬───────────────────────────────────┘    ┃
┃               ▼                                         ┃
┃  ┌────────────────────────────────────────────────┐    ┃
┃  │  🤖 Stage 3: Automated Underwriting            │    ┃
┃  │  • Check 47 rules                              │    ┃
┃  │  • Decision: Auto-approved                     │    ┃
┃  │  • Confidence: 98%                             │    ┃
┃  │  • Duration: 5.8s                              │    ┃
┃  └────────────┬───────────────────────────────────┘    ┃
┃               ▼                                         ┃
┃  ┌────────────────────────────────────────────────┐    ┃
┃  │  ✅ Stage 4: Quote Generated                   │    ┃
┃  │  • Quote ID: QT-10XXX                          │    ┃
┃  │  • Policy terms generated                      │    ┃
┃  │  • Delivered via Chat API                      │    ┃
┃  │  • Total Duration: 12.1s                       │    ┃
┃  └────────────────────────────────────────────────┘    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## Component Breakdown

### 🌐 Customer Portal (app_customer_portal.py)
**Purpose:** Customer-facing interface

**Key Features:**
- Streamlit web UI
- AI chatbot (OpenAI GPT-3.5)
- Quote request interface
- Real-time chat updates

**Technology Stack:**
- Python + Streamlit
- OpenAI API
- SQLAlchemy ORM
- SQLite database

---

### 🎯 Guidewire Backend (app_v2.py - Case 4)
**Purpose:** Policy system backend simulation

**Key Features:**
- Real-time activity monitoring
- Processing pipeline visualization
- Performance metrics dashboard
- API call detail inspection

**Technology Stack:**
- Python + Streamlit
- SQLAlchemy ORM
- SQLite database
- Auto-refresh mechanism

---

### 💾 Shared Database (pnc_demo.db)
**Purpose:** Central data store enabling real-time sync

**Key Tables:**
```sql
CustomerUser
├─ id (PK)
├─ party_id (FK → Party)
├─ email
├─ avatar_url
└─ last_login

ChatMessage
├─ id (PK)
├─ user_id (FK → CustomerUser)
├─ message
├─ response
├─ timestamp  ← KEY FIELD FOR SYNC
└─ model_used

Policy
├─ id (PK)
├─ policy_number
├─ quote_id (FK → Quote)
├─ effective_date
└─ status

Quote
├─ id (PK)
├─ submission_id
├─ total_premium
└─ status
```

---

## Data Flow: Quote Request

### Step-by-Step Process

#### 1️⃣ Customer Action (Port 8502)
```python
# User clicks "Get Free Quote"
st.button("💰 Get Free Quote")
  ↓
# Session state updated
st.session_state.quote_flow_active = True
st.session_state.quote_product = "Travel Insurance"
  ↓
# Sidebar shows chat conversation
```

#### 2️⃣ AI Conversation (Port 8502)
```python
# OpenAI generates 7-message flow
messages = get_quote_flow(product_type, user)
  ↓
# Messages displayed with delays
for msg in messages:
    display_message(msg)
    time.sleep(1.0)  # Simulate typing
  ↓
# Final quote displayed
```

#### 3️⃣ Database Write (Port 8502)
```python
# Save to database
new_chat = ChatMessage(
    user_id=user.id,
    message="Get quote for Travel Insurance",
    response="🎉 Your Personalized Quote: ...",
    timestamp=datetime.now(),
    model_used='OpenAI GPT-4'
)
session.add(new_chat)
session.commit()
```

#### 4️⃣ Backend Detection (Port 8501)
```python
# Auto-refresh triggers (every 2s)
if auto_refresh:
    time.sleep(2)
    st.rerun()
  ↓
# Query database for new messages
recent_messages = session.query(ChatMessage).filter(
    ChatMessage.user_id == user.id
).order_by(ChatMessage.timestamp.desc()).limit(5).all()
  ↓
# Display processing stages
for msg in recent_messages:
    show_processing_pipeline(msg)
```

---

## Timing Diagram

```
Time    Customer Portal              Database              Guidewire Backend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

T+0s    [Click "Get Free Quote"]
        ↓
T+1s    [AI: Greeting message]
        ↓
T+2s    [User: "Sounds good!"]
        ↓
T+3s    [AI: First question]
        ↓
T+4s    [User: Answer]
        ↓
T+5s    [AI: Second question]
        ↓
T+6s    [User: Answer]
        ↓
T+7s    [AI: Final quote]
        ↓
T+8s    [Write to DB] ─────────────> [ChatMessage created]
                                                ↓
T+9s                                            [Query detects new data]
                                                         ↓
T+10s                                                    [Display: Stage 1]
T+11s                                                    [Display: Stage 2]
T+12s                                                    [Display: Stage 3]
T+13s                                                    [Display: Stage 4]
T+14s                                                    [Show API details]
```

---

## Performance Characteristics

### Latency Breakdown
```
Component                   Time (ms)      % of Total
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
User clicks button             10            0.08%
React/render                   50            0.41%
OpenAI API call             5,000           41.32%
Database write                100            0.83%
Database query (backend)       50            0.41%
UI update (backend)           100            0.83%
Simulated delays           6,790           56.12%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total                      12,100          100.00%
```

### Throughput Capacity
- **Current Demo:** 1 request every 12 seconds
- **Real System:** 500 requests/minute (simulated)
- **Theoretical Max:** 1,000+ requests/minute

### Database Performance
- **Read latency:** <10ms (local SQLite)
- **Write latency:** <50ms (local SQLite)
- **Auto-refresh:** Every 2 seconds
- **Concurrent users:** Demo supports 1, production would support 1,000+

---

## Scalability Considerations

### Current Demo Setup (Local)
```
┌─────────────┐
│   SQLite    │  ← Single file database
│  (pnc_demo  │     • Fast for demos
│    .db)     │     • Limited concurrency
└─────────────┘
```

### Production Setup (Scaled)
```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  PostgreSQL  │◄────►│  Redis Cache │◄────►│  Message     │
│   Primary    │      │  Layer       │      │  Queue       │
└──────────────┘      └──────────────┘      │  (RabbitMQ)  │
        ▲                                    └──────────────┘
        │                                            ▲
        │                                            │
┌──────────────┐                            ┌──────────────┐
│  PostgreSQL  │                            │  API Workers │
│  Read        │                            │  (Multiple   │
│  Replicas    │                            │   Instances) │
└──────────────┘                            └──────────────┘
```

---

## Security Architecture (Production)

### Authentication Flow
```
Customer ──► API Gateway ──► Auth Service ──► Backend
              (Kong/AWS)     (OAuth 2.0)      (Guidewire)
                 ↓
            Rate Limiting
            IP Whitelisting
            JWT Validation
```

### Data Protection
- **In Transit:** TLS 1.3 encryption
- **At Rest:** Database encryption (AES-256)
- **API Keys:** Secrets management (AWS Secrets Manager)
- **PII Data:** Tokenization and masking

---

## Monitoring & Observability

### Metrics Collected
```
Application Metrics
├─ API response times (p50, p95, p99)
├─ Success rate
├─ Error rate
├─ Throughput (requests/minute)
└─ Active connections

Business Metrics
├─ Quotes generated
├─ Auto-approval rate
├─ Average quote value
└─ Conversion rate

System Metrics
├─ CPU usage
├─ Memory usage
├─ Database query time
└─ Disk I/O
```

### Alerting Thresholds
- **Response Time:** Alert if p95 > 200ms
- **Error Rate:** Alert if > 1%
- **Database:** Alert if query time > 100ms
- **Capacity:** Alert if throughput > 80% of max

---

## Summary

This demo showcases:

✅ **Real-time synchronization** between frontend and backend
✅ **End-to-end quote generation** workflow
✅ **Processing pipeline visibility** with detailed stages
✅ **Performance monitoring** with live metrics
✅ **API integration patterns** for modern insurance systems

**Perfect for demonstrating:**
- Technical capabilities to developers
- Business value to executives
- Customer experience to sales teams
- System architecture to architects

