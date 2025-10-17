# Quick Start Guide

## Running the Application

### Option 1: Interactive CLI

```bash
cd src
python main.py
```

This will:
1. Create `insurance.db` database (if it doesn't exist)
2. Initialize the complete schema
3. Launch the interactive menu system

### Option 2: Run the Demo Script

```bash
cd src
python demo.py
```

This will:
1. Create `demo_insurance.db` with sample data
2. Demonstrate all major features:
   - Create parties (insured, broker, insurers, reinsurers)
   - Process submission → quote → policy workflow
   - Add coverages and assets
   - Set up co-insurance
   - Create reinsurance structure with layers
   - Process a claim with transactions
   - Issue cash calls to reinsurers

### Option 3: Use Programmatically

```python
from database import DatabaseManager
from services import InsuranceService
from models import PartyType

# Initialize
db = DatabaseManager("my_insurance.db")
db.initialize_schema()
service = InsuranceService(db)

# Create a party
party_id = service.create_party(
    PartyType.ORGANIZATION,
    name="ABC Company",
    city="Zurich",
    country="Switzerland"
)

# Create a submission
submission_id = service.create_submission(party_id)

# ... continue with your workflow

db.close()
```

## Common Workflows

### 1. Create a Simple Policy

```
Main Menu → 1. Party Management
  → 1. Create Party (create insured)
  → 1. Create Party (create insurer)

Main Menu → 2. Policy Management
  → 1. Create Submission
  → 2. Add Quote to Submission
  → 3. Create Policy from Quote
  → 4. Add Coverage to Policy
```

### 2. Process a Claim

```
Main Menu → 3. Claim Management
  → 1. Create Claim
  → 2. Add Claim Note
  → 3. Record Transaction (set reserve)
  → 3. Record Transaction (make payment)
  → 4. View Claim Details
```

### 3. Set Up Reinsurance

```
Main Menu → 4. Reinsurance Management
  → 2. Create Reinsurance Treaty
  → 3. Add Reinsurance Layer
  → 4. Add Reinsurer to Layer
  → 5. Issue Cash Call (when claim occurs)
```

## Sample Data

After running `demo.py`, you can explore the sample database that includes:
- 6 parties (insured, broker, insurers, reinsurer, adjuster)
- 1 complete policy with 2 coverages
- 1 building asset with location and details
- Co-insurance structure (60% lead, 40% follow)
- Facultative reinsurance with 2 layers
- 1 claim with reserve, expense payment, and indemnity payment
- 1 cash call to reinsurer

## Database Location

All databases are created in the `src/` directory:
- `insurance.db` - Created by main.py
- `demo_insurance.db` - Created by demo.py
- Custom databases - Created via DatabaseManager("your_name.db")

## Exploring the Database

You can use any SQLite tool to explore the database:

```bash
# Using sqlite3 CLI
sqlite3 demo_insurance.db

# View tables
.tables

# View policy data
SELECT * FROM policy;

# View claim financial summary
SELECT 
  claim_number,
  transaction_type,
  SUM(amount) as total
FROM claim c
JOIN financial_transaction ft ON c.id = ft.claim_id
GROUP BY claim_number, transaction_type;
```

## Troubleshooting

**Issue: "No module named 'database'"**
- Make sure you're running from the `src/` directory
- Run: `cd src` before `python main.py`

**Issue: Database already exists**
- Delete the `.db` file to start fresh
- Or use a different database name in DatabaseManager()

**Issue: Foreign key constraint failed**
- Ensure parent records exist before creating child records
- Example: Create party before creating submission

## Next Steps

1. Review the complete database schema in `src/database/schema.sql`
2. Explore data models in `src/models/`
3. Check available service methods in `src/services/insurance_service.py`
4. Customize the CLI in `src/cli/cli.py`
5. Build your own workflows using the service layer

Enjoy managing your P&C insurance operations!

