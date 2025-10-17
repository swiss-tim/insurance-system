# 🚀 Quick Start: Customer Portal

## What Was Built

✅ **Complete customer portal with 5 AI features**
✅ **Extended database schema** (5 new tables)
✅ **4th use case:** Maria Weber with 2 policies
✅ **Pre-seeded data:** Chat history, ads, summaries, emails

---

## How to Run

### Option 1: Fresh Start (Recommended)

**Step 1:** Close ALL Streamlit apps
```powershell
# In PowerShell, stop all Python processes
Get-Process python* | Stop-Process -Force
```

**Step 2:** Delete old database
```powershell
cd C:\Users\timha\python\insurance-system\src
Remove-Item pnc_demo.db -Force
```

**Step 3:** Reseed database
```powershell
python seed_database.py
```

You should see:
```
Seeding database...
Seeding Case 4: Customer Portal...
✓ Case 4: Customer Portal data seeded successfully
Database seeded successfully.
```

**Step 4:** Run customer portal
```powershell
streamlit run app_customer_portal.py --server.port 8503
```

Access at: **http://localhost:8503**

---

### Option 2: Use Existing Database

If reseeding fails (database locked), you can still run with existing data:

```powershell
cd src
streamlit run app_customer_portal.py --server.port 8503
```

**Note:** The 4th case (Maria Weber) won't be available until database is reseeded.

---

## Three Apps, Three Ports

### 1. Broker/Agent Story Demo (Port 8502)
```powershell
cd src
streamlit run app_v2.py --server.port 8502
```
- **Audience:** Internal/sales demos
- **Shows:** Manual vs automated processes
- **Cases:** 3 B2B insurance scenarios

### 2. Customer Portal (Port 8503)
```powershell
cd src
streamlit run app_customer_portal.py --server.port 8503
```
- **Audience:** End customers
- **Shows:** AI-powered self-service
- **User:** Maria Weber

### 3. Original Data View (Port 8501)
```powershell
# This is the old app.py (if you still have it)
cd src
streamlit run app.py
```

---

## Customer Portal Features

### 1. 🏠 Dashboard
- Active policies overview
- AI-generated upsell ads (Travel + Life Insurance)
- Quick actions

### 2. 💬 Cacti Bot
**Try these prompts:**
- "What are my policies?"
- "When is my renewal?"
- "How do I file a claim?"

### 3. 📋 My Policies
**For each policy, you can:**
- **Summarize Policy** (AI simplifies complex terms)
- **Email Insurer** (AI generates professional email)
- View coverage details

### 4. 🎯 Special Offers
- See AI-generated personalized ads
- Generate new recommendations
- Request quotes

### 5. 👤 My Account
- View profile
- **Generate Avatar** (describe in text, AI creates image)

---

## Demo Flow (5 Minutes)

1. **Dashboard (30 sec)**
   - "Maria has 2 policies: Home + Auto"
   - Point out AI-generated ads below

2. **Cacti Bot (1 min)**
   - Click chat history
   - Send new message: "What are my current policies?"
   - Show AI response

3. **My Policies (2 min)**
   - Open home insurance
   - Click "📝 Summarize Policy"
   - Show AI-generated summary
   - Click "✉️ Email Insurer"
   - Show pre-filled email

4. **Special Offers (1 min)**
   - "Maria doesn't have travel insurance"
   - Show AI-generated ad (image + text)
   - Explain personalization

5. **My Account (30 sec)**
   - Click "Generate New Avatar"
   - Type: "smiling professional woman"
   - Show generation

**Key message:** "Every feature uses AI (simulating Amazon Bedrock) to make insurance accessible and engaging."

---

## Troubleshooting

### "No insured parties found"
**Cause:** Database doesn't have Case 4
**Fix:** Reseed database (see Option 1 above)

### "Database is locked"
**Cause:** Another process is using the DB
**Fix:** 
1. Stop ALL Streamlit apps
2. Wait 5 seconds
3. Try again

### "Module not found: CustomerUser"
**Cause:** Old database schema
**Fix:** Delete `pnc_demo.db` and reseed

---

## File Structure

```
src/
├── app_customer_portal.py     # 🆕 Customer portal (THIS IS THE NEW APP)
├── app_v2.py                   # Broker/agent demo
├── seed_database.py            # 🆕 Extended with Case 4 + new tables
├── database_queries.py         # 🆕 Updated imports
├── init_db.py                  # Database initialization
└── pnc_demo.db                 # SQLite database (auto-created)
```

---

## What's Different from Broker Apps

| Aspect | Broker Apps | Customer Portal |
|--------|-------------|-----------------|
| **User** | Insurance professionals | End customers |
| **Data** | 3 B2B cases (Bakery, Manufacturing, Pharma) | 1 B2C customer (Maria) |
| **Features** | Process comparison (manual vs auto) | 5 AI features (chatbot, ads, etc.) |
| **Goal** | Show ROI of automation | Customer engagement & self-service |
| **AI** | None (just shows data) | Simulates Bedrock (Claude, Titan, SD) |

---

## Next Steps

### For Demo/POC
✅ You're ready! Just run the app and demo the 5 features.

### For Production
1. Replace `simulate_*` functions with real Bedrock API calls
2. Add proper authentication (OAuth2)
3. Implement rate limiting
4. Set up monitoring
5. Add error handling
6. Deploy to cloud (Streamlit Cloud / AWS / Azure)

See `CUSTOMER_PORTAL_README.md` for detailed production guide.

---

## Support Resources

- **Full Documentation:** `CUSTOMER_PORTAL_README.md`
- **Database Schema:** See `seed_database.py` lines 220-280
- **Sample Data:** See `seed_database.py` lines 447-641
- **AI Simulation:** See `app_customer_portal.py` lines 70-140

---

**🎉 You now have a complete AI-powered customer portal!**

**Access it at:** http://localhost:8503 (after running the app)

