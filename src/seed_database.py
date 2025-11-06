import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, ForeignKey, TIMESTAMP, TEXT, CheckConstraint
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func

# --- Database Setup ---
DB_FILE = "pnc_demo.db"

# Don't delete database on import - only when running as script
engine = create_engine(f'sqlite:///{DB_FILE}')
Session = sessionmaker(bind=engine)
Base = declarative_base()

# --- SQLAlchemy ORM Model Definitions ---

class Party(Base):
    __tablename__ = 'party'
    id = Column(Integer, primary_key=True)
    party_type = Column(String, CheckConstraint("party_type IN ('PERSON', 'ORGANIZATION')"), nullable=False)
    name = Column(String, nullable=False)
    address = Column(String)
    city = Column(String)
    country = Column(String)
    email = Column(String)
    phone = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    roles = relationship("PartyRole", back_populates="party")

class PartyRole(Base):
    __tablename__ = 'party_role'
    id = Column(Integer, primary_key=True)
    party_id = Column(Integer, ForeignKey('party.id', ondelete='CASCADE'), nullable=False)
    role_name = Column(String, nullable=False)
    context_table = Column(String, nullable=False)
    context_id = Column(Integer, nullable=False)
    party = relationship("Party", back_populates="roles")

class Submission(Base):
    __tablename__ = 'submission'
    id = Column(Integer, primary_key=True)
    submission_number = Column(String, unique=True)  # e.g., "SUB-2026-001"
    insured_party_id = Column(Integer, ForeignKey('party.id'), nullable=False)
    broker_party_id = Column(Integer, ForeignKey('party.id'))
    status = Column(String, default='OPEN', nullable=False)  # TRIAGED, IN_REVIEW, QUOTED, BOUND, DECLINED
    created_at = Column(TIMESTAMP, server_default=func.now())
    effective_date = Column(Date)  # Requested effective date
    
    # Underwriting Center fields
    completeness = Column(Integer, default=0)  # 0-100%
    priority_score = Column(Float)  # e.g., 4.8
    risk_appetite = Column(String)  # High, Medium, Low
    broker_tier = Column(String)  # Tier 1, Tier 2, Tier 3
    accepted = Column(Boolean, default=False)  # True when quote sent to broker
    
    quotes = relationship("Quote", back_populates="submission")

class Quote(Base):
    __tablename__ = 'quote'
    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey('submission.id', ondelete='CASCADE'), nullable=False)
    insurer_party_id = Column(Integer, ForeignKey('party.id'), nullable=False)
    total_premium = Column(Float, nullable=False)
    currency = Column(String, default='CHF', nullable=False)
    status = Column(String, default='PENDING', nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    submission = relationship("Submission", back_populates="quotes")
    policy = relationship("Policy", back_populates="quote", uselist=False)

class Policy(Base):
    __tablename__ = 'policy'
    id = Column(Integer, primary_key=True)
    policy_number = Column(String, unique=True, nullable=False)
    quote_id = Column(Integer, ForeignKey('quote.id'))
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    status = Column(String, default='ACTIVE', nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    quote = relationship("Quote", back_populates="policy")
    coverages = relationship("Coverage", back_populates="policy")
    assets = relationship("InsurableAsset", back_populates="policy")
    claims = relationship("Claim", back_populates="policy")
    coinsurers = relationship("PolicyInsurer", back_populates="policy")
    reinsurance_treaties = relationship("ReinsuranceTreaty", back_populates="policy")

class Coverage(Base):
    __tablename__ = 'coverage'
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policy.id', ondelete='CASCADE'), nullable=False)
    coverage_type = Column(String, nullable=False)
    limit_amount = Column(Float, nullable=False)
    deductible_amount = Column(Float, nullable=False)
    policy = relationship("Policy", back_populates="coverages")

class InsurableAsset(Base):
    __tablename__ = 'insurable_asset'
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policy.id', ondelete='CASCADE'), nullable=False)
    asset_type = Column(String, nullable=False)
    description = Column(String)
    policy = relationship("Policy", back_populates="assets")
    locations = relationship("AssetLocation", back_populates="asset")
    details = relationship("AssetDetail", back_populates="asset")

class AssetLocation(Base):
    __tablename__ = 'asset_location'
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('insurable_asset.id', ondelete='CASCADE'), nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    asset = relationship("InsurableAsset", back_populates="locations")

class AssetDetail(Base):
    __tablename__ = 'asset_detail'
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('insurable_asset.id', ondelete='CASCADE'), nullable=False)
    detail_key = Column(String, nullable=False)
    detail_value = Column(String, nullable=False)
    asset = relationship("InsurableAsset", back_populates="details")

class Claim(Base):
    __tablename__ = 'claim'
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policy.id'), nullable=False)
    claim_number = Column(String, unique=True, nullable=False)
    date_of_loss = Column(Date, nullable=False)
    reported_date = Column(Date, nullable=False)
    status = Column(String, default='OPEN', nullable=False)
    reported_by_party_id = Column(Integer, ForeignKey('party.id'), nullable=False)
    description = Column(TEXT)
    policy = relationship("Policy", back_populates="claims")
    details = relationship("ClaimDetail", back_populates="claim")
    financials = relationship("FinancialTransaction", back_populates="claim")
    subrogations = relationship("Subrogation", back_populates="claim")
    cash_calls = relationship("CashCall", back_populates="claim")

class ClaimDetail(Base):
    __tablename__ = 'claim_detail'
    id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey('claim.id', ondelete='CASCADE'), nullable=False)
    log_entry = Column(TEXT, nullable=False)
    entry_timestamp = Column(TIMESTAMP, server_default=func.now())
    author_party_id = Column(Integer, ForeignKey('party.id'))
    claim = relationship("Claim", back_populates="details")

class FinancialTransaction(Base):
    __tablename__ = 'financial_transaction'
    id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey('claim.id', ondelete='CASCADE'), nullable=False)
    transaction_type = Column(String, CheckConstraint("transaction_type IN ('RESERVE', 'PAYMENT_EXPENSE', 'PAYMENT_INDEMNITY')"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    transaction_date = Column(Date, nullable=False)
    payee_party_id = Column(Integer, ForeignKey('party.id'))
    claim = relationship("Claim", back_populates="financials")

class Subrogation(Base):
    __tablename__ = 'subrogation'
    id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey('claim.id', ondelete='CASCADE'), nullable=False)
    liable_party_id = Column(Integer, ForeignKey('party.id'), nullable=False)
    potential_recovery_amount = Column(Float)
    actual_recovery_amount = Column(Float)
    status = Column(String, default='IDENTIFIED', nullable=False)
    claim = relationship("Claim", back_populates="subrogations")

class PolicyInsurer(Base):
    __tablename__ = 'policy_insurer'
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policy.id', ondelete='CASCADE'), nullable=False)
    insurer_party_id = Column(Integer, ForeignKey('party.id'), nullable=False)
    share_percentage = Column(Float, nullable=False)
    is_lead = Column(Boolean, default=False, nullable=False)
    policy = relationship("Policy", back_populates="coinsurers")

class ReinsuranceTreaty(Base):
    __tablename__ = 'reinsurance_treaty'
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policy.id', ondelete='CASCADE'), nullable=False)
    treaty_type = Column(String, default='FACULTATIVE', nullable=False)
    description = Column(String)
    policy = relationship("Policy", back_populates="reinsurance_treaties")
    layers = relationship("ReinsuranceLayer", back_populates="treaty")

class ReinsuranceLayer(Base):
    __tablename__ = 'reinsurance_layer'
    id = Column(Integer, primary_key=True)
    treaty_id = Column(Integer, ForeignKey('reinsurance_treaty.id', ondelete='CASCADE'), nullable=False)
    layer_order = Column(Integer, nullable=False)
    attachment_point = Column(Float, nullable=False)
    layer_limit = Column(Float, nullable=False)
    premium = Column(Float)
    treaty = relationship("ReinsuranceTreaty", back_populates="layers")
    participants = relationship("LayerParticipant", back_populates="layer")

class LayerParticipant(Base):
    __tablename__ = 'layer_participant'
    id = Column(Integer, primary_key=True)
    layer_id = Column(Integer, ForeignKey('reinsurance_layer.id', ondelete='CASCADE'), nullable=False)
    reinsurer_party_id = Column(Integer, ForeignKey('party.id'), nullable=False)
    share_percentage = Column(Float, nullable=False)
    status = Column(String, default='QUOTED', nullable=False)
    layer = relationship("ReinsuranceLayer", back_populates="participants")
    cash_calls = relationship("CashCall", back_populates="participant")

class CashCall(Base):
    __tablename__ = 'cash_call'
    id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey('claim.id', ondelete='CASCADE'), nullable=False)
    layer_participant_id = Column(Integer, ForeignKey('layer_participant.id', ondelete='CASCADE'), nullable=False)
    call_amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, default='ISSUED', nullable=False)
    due_date = Column(Date, nullable=False)
    issued_date = Column(Date, server_default=func.current_date())
    claim = relationship("Claim", back_populates="cash_calls")
    participant = relationship("LayerParticipant", back_populates="cash_calls")

class Document(Base):
    __tablename__ = 'document'
    id = Column(Integer, primary_key=True)
    document_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_timestamp = Column(TIMESTAMP, server_default=func.now())
    related_table = Column(String, nullable=False)
    related_id = Column(Integer, nullable=False)
    uploader_party_id = Column(Integer, ForeignKey('party.id'))

# --- Customer Portal Tables ---

class CustomerUser(Base):
    __tablename__ = 'customer_user'
    id = Column(Integer, primary_key=True)
    party_id = Column(Integer, ForeignKey('party.id'), nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    avatar_url = Column(String)
    avatar_prompt = Column(TEXT)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_login = Column(TIMESTAMP)
    party = relationship("Party")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    generated_ads = relationship("GeneratedAd", back_populates="user", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = 'chat_message'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customer_user.id', ondelete='CASCADE'), nullable=False)
    message = Column(TEXT, nullable=False)
    response = Column(TEXT, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    is_user = Column(Boolean, nullable=False)
    model_used = Column(String)
    user = relationship("CustomerUser", back_populates="chat_messages")

class GeneratedAd(Base):
    __tablename__ = 'generated_ad'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customer_user.id', ondelete='CASCADE'), nullable=False)
    product_type = Column(String, nullable=False)
    image_prompt = Column(TEXT)
    image_url = Column(String)
    ad_copy = Column(TEXT, nullable=False)
    generated_at = Column(TIMESTAMP, server_default=func.now())
    clicked = Column(Boolean, default=False)
    click_timestamp = Column(TIMESTAMP)
    user = relationship("CustomerUser", back_populates="generated_ads")

class PolicySummary(Base):
    __tablename__ = 'policy_summary'
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey('policy.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('customer_user.id'), nullable=False)
    summary_text = Column(TEXT, nullable=False)
    generated_at = Column(TIMESTAMP, server_default=func.now())
    model_used = Column(String)

class EmailTemplate(Base):
    __tablename__ = 'email_template'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customer_user.id', ondelete='CASCADE'), nullable=False)
    policy_id = Column(Integer, ForeignKey('policy.id'))
    claim_id = Column(Integer, ForeignKey('claim.id'))
    template_type = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(TEXT, nullable=False)
    generated_at = Column(TIMESTAMP, server_default=func.now())
    sent = Column(Boolean, default=False)
    sent_at = Column(TIMESTAMP)

# --- Data Seeding Function ---
def clear_all_data():
    """Clear all data from the database while keeping the schema."""
    print("Clearing existing data...")
    session = Session()
    try:
        # Delete in reverse order of dependencies to avoid foreign key constraints
        session.query(ChatMessage).delete()
        session.query(GeneratedAd).delete()
        session.query(PolicySummary).delete()
        session.query(EmailTemplate).delete()
        session.query(CustomerUser).delete()
        
        session.query(CashCall).delete()
        session.query(LayerParticipant).delete()
        session.query(ReinsuranceLayer).delete()
        session.query(ReinsuranceTreaty).delete()
        session.query(PolicyInsurer).delete()
        
        session.query(Subrogation).delete()
        session.query(FinancialTransaction).delete()
        session.query(ClaimDetail).delete()
        session.query(Claim).delete()
        session.query(Document).delete()
        
        session.query(PartyRole).delete()
        session.query(AssetDetail).delete()
        session.query(AssetLocation).delete()
        session.query(InsurableAsset).delete()
        session.query(Coverage).delete()
        session.query(Policy).delete()
        session.query(Quote).delete()
        session.query(Submission).delete()
        session.query(Party).delete()
        
        session.commit()
        print("[OK] All data cleared successfully")
        session.close()
        return True
    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error clearing data: {e}")
        return False


# Old seed_data() function removed - now using market-specific seed files:
# - seed_data_german.py for German SHUK market
# - seed_data_us.py for U.S. Workers Compensation market

if __name__ == '__main__':
    import sys
    from seed_data_german import seed_german_data
    from seed_data_us import seed_us_data
    
    # Get market selection from command line argument (default: german)
    market = 'german'
    if len(sys.argv) > 1:
        market = sys.argv[1].lower()
    
    # When running as script, check if database exists
    db_exists = os.path.exists(DB_FILE)
    
    # Always drop and recreate tables to ensure schema is up to date
    # This is safe because we clear data anyway
    print("Creating/updating database schema...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("[OK] Schema ready")
    
    # Seed data based on market selection
    session = Session()
    try:
        if market == 'us':
            print("Seeding U.S. Workers' Compensation market...")
            seed_us_data(session)
        else:
            print("Seeding German SHUK market (default)...")
            seed_german_data(session)
    except Exception as e:
        print(f"Error during seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()
    
    print("Database seeded successfully.")