# Underwriting Center - Quick Start Guide

## 🚀 Get Started in 2 Minutes

### 1. Reset Database (One-Time Setup)

```bash
cd src
python seed_database.py
```

**✅ This will seed:**
- All existing demos (Cases 1-4)
- NEW: 7 underwriting submissions including Floor & Decor

### 2. Launch the Underwriting Center

**Option A: Use the Launcher (Recommended)**
```bash
# Double-click or run:
.\run_underwriting_center.bat
```

**Option B: Manual Launch**
```bash
streamlit run underwritingcenter\app_underwriting.py --server.port 8504
```

### 3. Open in Browser

Navigate to: **`http://localhost:8504`**

---

## 🎬 Follow the Demo Story

### The Journey: Floor & Decor Outlets (SUB-2026-001)

1. **Dashboard** → Click on "Floor & Decor Outlets" row
2. **Status: Triaged, Completeness: 74%** → Click "✨ Summarize with AI"
3. **AI Summary appears** → Click "✅ Accept Summary"
4. **Completeness → 86%, Status → In Review** → Click "+ Generate Proposal"
5. **Base Quote: $42,459** → Click "🤖 Analyze Proposal"
6. **AI Recommends: Add Voluntary Compensation** → Click "✅ Accept Recommendation"
7. **Endorsement added** → Click "🔄 Generate Quote"
8. **Generated Quote: $75,334** → Click "📊 Compare Quotes"
9. **Side-by-side comparison** → Click "← Back to Quotes"
10. **Click "📧 Send to Broker"** on Generated Quote
11. **Status → Quoted** → Click "← Return to Submission List"
12. **Dashboard** → Click "🔄 Refresh Metrics"
13. **Turnaround Time: 4.1 → 3.9 days** → Demo complete! 🎉

---

## 📊 What You'll See

### Dashboard Screen
- 4 KPIs: Turnaround Time, Hit Ratio, Earned Premium, Loss Ratio
- Submissions table with tabs: Active | Bound | Declined
- 7 demo submissions ready to explore

### Submission Detail Screen (Floor & Decor)
- Real-time completeness tracking (74% → 86%)
- Status progression (Triaged → In Review → Quoted)
- AI-powered document summarization
- Automated proposal generation
- Smart endorsement recommendations
- Multi-quote comparison
- Broker communication

---

## 🏢 All Available Submissions

| Submission | Account | Status | Use Case |
|------------|---------|--------|----------|
| **SUB-2026-001** | **Floor & Decor** | **Triaged** | **Main Demo - Full Story** |
| SUB-2026-003 | Monrovia Metalworking | In Review | - |
| SUB-2026-005 | Retail Chain Express | Cleared | - |
| SUB-2026-012 | Restaurant Holdings | Cleared | - |
| SUB-2026-007 | Construction Dynamics | Quoted | - |
| SUB-2026-016 | Manufacturing Specialists | Cleared | - |

> **Note:** Full interactive demo flow is configured for SUB-2026-001 (Floor & Decor) only.

---

## 🎯 Key Features Demonstrated

✅ **AI Document Summarization** - Analyzes submission docs in 2 seconds
✅ **Dynamic Completeness Scoring** - Real-time assessment updates
✅ **Automated Proposal Generation** - Creates quotes from product rules
✅ **Smart Recommendations** - AI suggests endorsement additions
✅ **Interactive Quote Comparison** - Side-by-side analysis
✅ **Status Workflow Management** - Triaged → In Review → Quoted → Bound
✅ **Loading States & Animations** - Professional UX with 2-3s delays
✅ **Guidewire-Style UI** - Corporate design matching enterprise software

---

## 🔧 Ports & Apps Overview

| App | Port | Purpose |
|-----|------|---------|
| app_v2.py | 8501 | Cases 1-3 + STP Dashboard |
| app_customer_portal.py | 8502 | Customer Portal + AI Chat |
| **app_underwriting.py** | **8504** | **Underwriting Center** |

---

## 💡 Pro Tips

1. **Always start with Floor & Decor** - It's the fully interactive demo
2. **Let the animations complete** - They tell the story
3. **Refresh metrics at the end** - Shows measurable ROI
4. **The state persists** - Refresh browser to restart demo
5. **Explore other submissions** - See different statuses/scores

---

## 🐛 Troubleshooting

### "No submissions found"
```bash
cd src
python seed_database.py
```

### "Port 8504 already in use"
```bash
# Use different port
streamlit run underwritingcenter\app_underwriting.py --server.port 8505
```

### "Database locked"
```bash
# Stop all Streamlit processes
Get-Process python* | Stop-Process -Force
# Then restart
```

---

## 📚 Full Documentation

**Detailed guide:** `underwritingcenter/README.md`

**Technical specs:** `underwritingcenter/specs.md`

**Database schema:** `src/seed_database.py`

---

## ✨ What's New

### Extended Database Schema
```python
class Submission:
    # NEW fields for Underwriting Center
    submission_number      # "SUB-2026-001"
    completeness          # 0-100%
    priority_score        # Float (e.g., 4.8)
    risk_appetite         # High/Medium/Low
    broker_tier           # Tier 1/2/3
    effective_date        # Requested policy start
```

### 7 New Demo Submissions
- Floor & Decor Outlets (Triaged, 74%, 4.8 score)
- Monrovia Metalworking (In Review, 80%, 4.7 score)
- 5 more realistic submissions with varied states

### Interactive Demo Flow
- 15-step guided journey
- Real-time state updates
- AI-powered interactions
- Professional loading modals

---

**Ready to demo? Run `.\run_underwriting_center.bat` and let's go! 🚀**

