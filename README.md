# P&C Insurance Management System

A comprehensive Property & Casualty (P&C) Insurance Management System built with Python and SQLite. This system provides complete management capabilities for insurance operations including party management, policy lifecycle, claims processing, and reinsurance structures.

## Features

### Core Capabilities

- **Party Management**: Manage all entities (individuals and organizations) with flexible role assignments
- **Policy Lifecycle**: Handle submissions, quotes, policy creation, and coverage management
- **Asset Management**: Track insurable assets with locations and flexible key-value attributes
- **Claims Processing**: Complete claims management with financial transactions and subrogation
- **Co-insurance**: Support for multiple insurers sharing policy risk
- **Reinsurance**: Full facultative and quota share reinsurance with layered structures
- **Cash Calls**: Track reinsurance cash calls and payment statuses
- **Document Management**: Attach and manage documents for any entity

### Technical Features

- SQLite database with full referential integrity
- Clean layered architecture (Models → Repositories → Services)
- Type-safe dataclasses for all entities
- Enum-based status management
- Comprehensive CRUD operations
- Interactive CLI interface

## Architecture

```
src/
├── database/          # Database management and schema
│   ├── db_manager.py  # Connection and initialization
│   └── schema.sql     # Complete DDL schema
├── models/            # Data models (dataclasses)
│   ├── party.py       # Party and roles
│   ├── policy.py      # Submissions, quotes, policies, coverage
│   ├── asset.py       # Insurable assets
│   ├── claim.py       # Claims and transactions
│   ├── reinsurance.py # Reinsurance structures
│   └── document.py    # Document management
├── repositories/      # Data access layer
│   ├── party_repository.py
│   ├── policy_repository.py
│   ├── asset_repository.py
│   ├── claim_repository.py
│   ├── reinsurance_repository.py
│   └── document_repository.py
├── services/          # Business logic layer
│   └── insurance_service.py
├── cli/               # Command-line interface
│   └── cli.py
└── main.py            # Application entry point
```

## Installation

### Requirements

- Python 3.8 or higher
- No external dependencies (uses Python standard library only)

### Setup

1. Clone or download this repository

2. Navigate to the project directory:
   ```bash
   cd insurance-system
   ```

3. The system uses only Python's standard library, so no pip installation needed!

## Usage

### Running the Application

From the project root directory:

```bash
cd src
python main.py
```

On first run, the system will automatically:
1. Create a SQLite database file (`insurance.db`)
2. Initialize the complete schema
3. Launch the interactive CLI

### CLI Menu Structure

```
Main Menu
├── 1. Party Management
│   ├── Create Party
│   ├── List Parties
│   └── View Party Details
├── 2. Policy Management
│   ├── Create Submission
│   ├── Add Quote to Submission
│   ├── Create Policy from Quote
│   ├── Add Coverage to Policy
│   ├── Add Asset to Policy
│   ├── View Policy Details
│   └── List All Policies
├── 3. Claim Management
│   ├── Create Claim
│   ├── Add Claim Note
│   ├── Record Transaction
│   ├── View Claim Details
│   └── Create Subrogation
├── 4. Reinsurance Management
│   ├── Add Co-insurer
│   ├── Create Reinsurance Treaty
│   ├── Add Reinsurance Layer
│   ├── Add Reinsurer to Layer
│   └── Issue Cash Call
└── 5. Reports & Queries
    ├── Database Statistics
    ├── Active Policies Count
    └── Open Claims Count
```

## Database Schema

The system implements a comprehensive insurance database with the following table groups:

### Part I: Core Party and Role Management
- `party` - Central repository for all entities (people, organizations)
- `party_role` - Context-specific roles parties play

### Part II: Submission, Quoting, and Policy Lifecycle
- `submission` - Initial insurance requests
- `quote` - Insurer offers
- `policy` - Binding insurance contracts
- `coverage` - Specific protections under policies

### Part III: Insurable Assets and Details
- `insurable_asset` - Items covered by policies
- `asset_location` - Physical locations of assets
- `asset_detail` - Flexible key-value asset attributes

### Part IV: Claim Management
- `claim` - Claim headers
- `claim_detail` - Claim logs and notes
- `financial_transaction` - Reserves and payments
- `subrogation` - Recovery efforts

### Part V: Co-insurance and Reinsurance
- `policy_insurer` - Co-insurance shares
- `reinsurance_treaty` - Reinsurance agreements
- `reinsurance_layer` - Coverage tower layers
- `layer_participant` - Reinsurer participation
- `cash_call` - Payment demands to reinsurers

### Part VI: Document Management
- `document` - File attachments for any entity

## Example Workflows

### Creating a Complete Policy

1. **Create Parties**:
   - Create insured party (ORGANIZATION)
   - Create broker party (ORGANIZATION)
   - Create insurer party (ORGANIZATION)

2. **Submission Process**:
   - Create submission for insured (optionally with broker)
   - Add quote from insurer with premium

3. **Bind Policy**:
   - Create policy from accepted quote
   - Add coverages (Property Damage, Liability, etc.)
   - Add insurable assets with locations

4. **Optional - Add Reinsurance**:
   - Create reinsurance treaty
   - Define layers (attachment points and limits)
   - Add reinsurer participants with share percentages

### Processing a Claim

1. **Create Claim**:
   - Link to policy
   - Specify date of loss and description

2. **Claim Handling**:
   - Add claim notes for documentation
   - Set reserve (RESERVE transaction)
   - Make payments (PAYMENT_EXPENSE or PAYMENT_INDEMNITY)

3. **Optional - Subrogation**:
   - Create subrogation record against liable party
   - Track potential and actual recovery amounts

4. **Optional - Reinsurance Recovery**:
   - Issue cash calls to layer participants
   - Track payment status

## Data Models

All entities are represented as type-safe dataclasses with proper enums for status fields:

- **Party Types**: PERSON, ORGANIZATION
- **Submission Status**: OPEN, QUOTED, BOUND
- **Quote Status**: PENDING, ACCEPTED, REJECTED
- **Policy Status**: ACTIVE, EXPIRED, CANCELLED
- **Claim Status**: OPEN, UNDER_REVIEW, APPROVED, SETTLED, REJECTED
- **Transaction Types**: RESERVE, PAYMENT_EXPENSE, PAYMENT_INDEMNITY
- **Subrogation Status**: IDENTIFIED, IN_PROGRESS, RECOVERED, CLOSED
- **Treaty Types**: FACULTATIVE, QUOTA_SHARE
- **Cash Call Status**: ISSUED, PAID, OVERDUE

## Development

### Project Structure

The system follows a clean layered architecture:

1. **Models Layer** (`models/`): Dataclass definitions with business enums
2. **Repository Layer** (`repositories/`): Database access and CRUD operations
3. **Service Layer** (`services/`): Business logic and orchestration
4. **Presentation Layer** (`cli/`): User interface

### Extending the System

To add new functionality:

1. Update `database/schema.sql` with new tables
2. Create models in `models/` with appropriate dataclasses
3. Implement repository methods in `repositories/`
4. Add service methods in `services/insurance_service.py`
5. Add CLI menu options in `cli/cli.py`

### Database Management

The DatabaseManager class handles:
- Connection pooling with row factory
- Foreign key constraint enforcement
- Schema initialization
- Transaction management
- Context manager support

## API Examples

### Using the Service Layer Directly

```python
from database import DatabaseManager
from services import InsuranceService
from models import PartyType

# Initialize
db = DatabaseManager("insurance.db")
db.initialize_schema()
service = InsuranceService(db)

# Create parties
insured_id = service.create_party(
    PartyType.ORGANIZATION,
    name="ABC Manufacturing Ltd",
    city="Zurich",
    country="Switzerland"
)

broker_id = service.create_party(
    PartyType.ORGANIZATION,
    name="Swiss Insurance Brokers SA",
    email="contact@swissbrokers.ch"
)

# Create submission and quote
submission_id = service.create_submission(insured_id, broker_id)
quote_id = service.add_quote_to_submission(submission_id, insurer_id=1, total_premium=50000)

# Create policy
from datetime import date, timedelta
service.accept_quote(quote_id)
policy_id = service.create_policy_from_quote(
    quote_id,
    policy_number="POL-2025-001",
    effective_date=date.today(),
    expiration_date=date.today() + timedelta(days=365)
)

# Add coverage
service.add_coverage_to_policy(
    policy_id,
    coverage_type="Property Damage",
    limit_amount=1000000,
    deductible_amount=10000
)

# Close connection
db.close()
```

## License

This project is provided as-is for educational and commercial use.

## Support

For questions or issues, please refer to the documentation or examine the code structure.

---

**Built with Python 3 and SQLite**

