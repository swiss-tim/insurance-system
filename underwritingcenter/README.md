# Guidewire Underwriting Center - Interactive Demo

A high-fidelity, interactive prototype demonstrating AI-powered underwriting workflows in a Guidewire-style interface.

## 🎯 Overview

This demo showcases a complete underwriting journey from submission intake to quote generation, featuring:

- **AI-Powered Document Analysis** - Automated extraction and summarization of submission documents
- **Intelligent Proposal Generation** - Automated coverage and endorsement recommendations
- **Smart Quote Comparison** - Side-by-side analysis of different quote scenarios
- **Real-time Completeness Tracking** - Dynamic scoring of submission readiness
- **Interactive Demo Flow** - Complete 15-step click path following Floor & Decor Outlets (SUB-2026-001)

## 🚀 Quick Start

### 1. Reset and Seed Database

First, reset the database to include all underwriting submissions:

```bash
# From project root
cd src
python seed_database.py
```

This will create:
- ✅ Extended `Submission` table with underwriting fields (completeness, priority_score, risk_appetite, broker_tier)
- ✅ Floor & Decor Outlets (SUB-2026-001) - Main demo submission
- ✅ 6 additional demo submissions (Monrovia, Retail Chain Express, etc.)
- ✅ All existing demo data (Cases 1-4) preserved

### 2. Launch the Underwriting Center

```bash
# From project root
streamlit run underwritingcenter/app_underwriting.py --server.port 8504
```

**App will be available at:** `http://localhost:8504`

## 📊 Demo Flow - The Complete Story

Follow this 15-step journey to experience the full underwriting workflow:

### **Start: Dashboard Screen**

1. **View Dashboard KPIs**
   - Quote Turnaround Time: 4.1 days
   - Average Hit Ratio: 26%
   - Cumulative Earned Premium: $1.65M
   - In Force Loss Ratio: 49%

2. **Click on Floor & Decor Outlets** (SUB-2026-001) in the Active Submissions table

---

### **Submission Detail Screen**

3. **Observe Initial State**
   - Status: **"Triaged"**
   - Completeness: **74%**
   - Priority Score: 4.8
   - Risk Appetite: High

4. **Click "✨ Summarize with AI"**
   - ⏱️ Loading modal appears (2 seconds)
   - 📋 AI summary appears with business overview, coverage details, loss history
   - 💡 Impact on completeness shown (+8%, +4%, +2%)

5. **Click "✅ Accept Summary"**
   - ⏱️ Loading modal appears (2 seconds)
   - 📈 Completeness updates: **74% → 86%**
   - 🔄 Status updates: **"Triaged" → "In Review"**
   - ✨ "+ Generate Proposal" button appears

6. **Click "+ Generate Proposal"**
   - ⏱️ Loading modal appears (3 seconds)
   - 📊 Proposal Details section appears
   - 💵 Base Quote card shows: **$42,459**

7. **Click "🤖 Analyze Proposal"**
   - ⏱️ Wait 2 seconds
   - 💡 AI Recommended Changes appear
   - 📝 Suggestion: Add "Voluntary Compensation" endorsement

8. **Click "✅ Accept Recommendation"**
   - ⏱️ Loading modal appears (2 seconds)
   - ☑️ "Voluntary Compensation" checkbox becomes checked

9. **(Optional) Uncheck "KOTECKI"** endorsement

10. **Click "🔄 Generate Quote"**
    - ⏱️ Loading modal appears (3 seconds)
    - 💵 Generated Quote card appears: **$75,334**

11. **Click "📊 Compare Quotes"**
    - ⏱️ Loading modal appears (2 seconds)
    - 📊 Side-by-side comparison view appears
    - 📈 Shows premium difference: **+$32,875**

12. **Click "← Back to Quotes"** (or scroll down)

13. **Click "📧 Send to Broker"** on Generated Quote
    - ⏱️ Loading modal appears (3 seconds)
    - 🔄 Status updates: **"In Review" → "Quoted"**
    - ✅ Success message appears

14. **Click "← Return to Submission List"**
    - 🔙 Navigate back to Dashboard
    - 👁️ Floor & Decor now shows status "Quoted"
    - **(Demo Step)** Click "Bound" tab → Floor & Decor appears there (simulating broker acceptance)

15. **Click "🔄 Refresh Metrics"**
    - ⏱️ Loading modal appears (2 seconds)
    - 📉 Quote Turnaround Time updates: **4.1 → 3.9 days**
    - 📊 Other metrics update
    - 🎉 **Demo Complete!**

---

## 🗂️ Database Schema Extensions

### Extended `Submission` Table

```python
class Submission(Base):
    # Existing fields
    id
    submission_number          # e.g., "SUB-2026-001"
    insured_party_id
    broker_party_id
    status                     # TRIAGED, IN_REVIEW, QUOTED, BOUND, DECLINED
    created_at
    effective_date
    
    # NEW Underwriting Center fields
    completeness              # 0-100% (Integer)
    priority_score            # e.g., 4.8 (Float)
    risk_appetite             # High, Medium, Low (String)
    broker_tier               # Tier 1, Tier 2, Tier 3 (String)
```

## 📋 Demo Submissions Seeded

| Submission | Account | Status | Completeness | Priority | Broker | Tier |
|------------|---------|--------|--------------|----------|--------|------|
| SUB-2026-001 | Floor & Decor Outlets | Triaged | 74% | 4.8 | Marsh & McLennan | Tier 1 |
| SUB-2026-003 | Monrovia Metalworking | In Review | 80% | 4.7 | Willis Towers Watson | Tier 1 |
| SUB-2026-005 | Retail Chain Express | Cleared | 78% | 4.5 | Brown & Brown | Tier 2 |
| SUB-2026-012 | Restaurant Holdings Inc | Cleared | 82% | 4.7 | Risk Strategies | Tier 3 |
| SUB-2026-007 | Construction Dynamics LLC | Quoted | 75% | 4.6 | Alliant Insurance | Tier 3 |
| SUB-2026-016 | Manufacturing Specialists | Cleared | 89% | 4.9 | Gallagher | Tier 1 |

## 🎨 Features & Components

### Dashboard Screen
- ✅ 4 KPI cards (Turnaround Time, Hit Ratio, Earned Premium, Loss Ratio)
- ✅ 3-tab submission table (Active, Bound, Declined)
- ✅ Clickable rows for navigation
- ✅ Refresh metrics functionality

### Submission Detail Screen
- ✅ Breadcrumb navigation
- ✅ 4 KPI cards (Status, Risk Appetite, Priority Score, Completeness)
- ✅ Recent documents section
- ✅ AI-powered summarization
- ✅ Dynamic proposal generation
- ✅ Interactive endorsement checkboxes
- ✅ Multi-quote management
- ✅ Side-by-side quote comparison
- ✅ Send to broker functionality
- ✅ Applicant information tabs

### Simulated AI Interactions
- ✅ Document summarization (2s delay)
- ✅ Completeness scoring
- ✅ Proposal analysis (2s delay)
- ✅ Endorsement recommendations
- ✅ Quote generation (3s delay)
- ✅ Quote comparison (2s delay)

### UX Enhancements
- ✅ Loading modals with context messages
- ✅ Status badges (color-coded)
- ✅ Appetite badges
- ✅ Smooth state transitions
- ✅ Success notifications
- ✅ Professional Guidewire-inspired styling

## 🏗️ Architecture

### Technology Stack
- **Frontend Framework:** Streamlit
- **Database:** SQLite (extended from existing schema)
- **ORM:** SQLAlchemy
- **State Management:** `st.session_state`
- **Styling:** Custom CSS (Tailwind-inspired)

### File Structure
```
underwritingcenter/
├── app_underwriting.py      # Main Streamlit application
├── specs.md                  # Original technical specifications
└── README.md                 # This file

src/
├── seed_database.py          # Extended with underwriting fields
├── database_queries.py       # Reused for data access
└── init_db.py                # Database initialization
```

### State Management

The app uses `st.session_state` to manage:

```python
# Navigation state
current_screen                # 'dashboard' or 'submission_detail'
selected_submission           # Submission ID

# Dashboard state
dashboard_kpis               # Turnaround time, hit ratio, etc.

# Submission state (Floor & Decor specific)
submission_state {
    status                   # Updates: Triaged → In Review → Quoted
    completeness             # Updates: 74% → 86%
    priority_score
    risk_appetite
    is_summary_visible       # Controls AI summary display
    is_proposal_visible      # Controls proposal section
    is_recs_visible          # Controls AI recommendations
    is_comparison_visible    # Controls quote comparison view
    quotes                   # ['base'], ['base', 'generated']
    endorsements {}          # Checkbox states
}

# Loading modal state
show_loading
loading_message
```

## 🎭 Design Principles

Following the specs.md requirements:

1. **Faked Logic:** All AI interactions are simulated with `time.sleep()` delays
2. **Hardcoded Data:** Submission details (coverages, endorsements, quotes) are mocked in the UI
3. **State-Driven Flow:** User actions progressively reveal new sections
4. **Realistic UX:** Loading modals, status transitions, and animations match enterprise software
5. **Guidewire Styling:** Corporate blue palette, professional card layouts, status badges

## 🔧 Customization

### Modify Demo Submissions

Edit `src/seed_database.py` (lines 682-837) to add/modify submissions:

```python
submission_custom = Submission(
    submission_number='SUB-2026-999',
    insured_party_id=custom_party.id,
    broker_party_id=broker.id,
    status='Triaged',
    effective_date=datetime.date(2026, 1, 1),
    completeness=50,
    priority_score=3.5,
    risk_appetite='Medium',
    broker_tier='Tier 2'
)
```

### Adjust AI Timing

Modify delay times in `app_underwriting.py`:

```python
# Summarize button
time.sleep(2)  # Change to adjust summarization delay

# Generate Proposal button
time.sleep(3)  # Change to adjust proposal generation delay
```

### Update KPIs

Modify initial values in state initialization (lines 152-157):

```python
st.session_state.dashboard_kpis = {
    'turnaround_time': 4.1,    # Adjust initial value
    'hit_ratio': 26,           # Adjust initial value
    # ...
}
```

## 🐛 Troubleshooting

### Database Not Found
```bash
# Reset database from scratch
cd src
python seed_database.py
```

### Port Already in Use
```bash
# Use a different port
streamlit run underwritingcenter/app_underwriting.py --server.port 8505
```

### Submissions Not Showing
```bash
# Verify database was seeded correctly
python -c "from src.database_queries import get_session; from src.seed_database import Submission; s = get_session(); print(f'Submissions: {s.query(Submission).count()}'); s.close()"
```

Expected output: `Submissions: 9` (or more)

## 📚 Related Documentation

- **Original Specs:** `underwritingcenter/specs.md` - React-based technical requirements
- **Database Schema:** `src/seed_database.py` - Full SQLAlchemy models
- **Main Demo App:** `src/app_v2.py` - Cases 1-3 (Broker/Agent demos)
- **Customer Portal:** `src/app_customer_portal.py` - Case 4 (Customer-facing)
- **API Integration:** `src/app_v2.py` Case 4 - STP Dashboard

## 💡 Tips for Presenting

1. **Pre-seed the database** before the presentation
2. **Rehearse the click path** - it's designed to tell a story
3. **Highlight state changes** - completeness, status updates
4. **Emphasize AI features** - summarization, recommendations
5. **Show the refresh** at the end - demonstrates ROI

## 🎯 Key Takeaways (For Audience)

This demo illustrates how AI-powered underwriting can:

- ⚡ **Reduce quote turnaround** from 4.1 → 3.9 days
- 🤖 **Automate document analysis** (14% completeness boost)
- 💡 **Intelligent recommendations** (voluntary compensation suggestion)
- 📊 **Compare scenarios** instantly
- 🎯 **Increase efficiency** while maintaining quality

---

**Built with ❤️ using Streamlit + SQLAlchemy**

*For questions or issues, please refer to the main project documentation.*

