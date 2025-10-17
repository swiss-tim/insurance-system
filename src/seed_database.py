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
    insured_party_id = Column(Integer, ForeignKey('party.id'), nullable=False)
    broker_party_id = Column(Integer, ForeignKey('party.id'))
    status = Column(String, default='OPEN', nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
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

# --- Data Seeding Function ---
def seed_data():
    """Seed the database with demo data."""
    print("Seeding database...")
    
    # Create a session for this seeding operation
    session = Session()
    
    try:
        # Case 1: Bäckerei Frischknecht GmbH
        bakery = Party(party_type='ORGANIZATION', name='Bäckerei Frischknecht GmbH', address='123 Bäckerstrasse', city='Zürich', country='Switzerland')
        broker_sme = Party(party_type='ORGANIZATION', name='Swiss Broker AG', city='Zürich', country='Switzerland')
        insurer_z = Party(party_type='ORGANIZATION', name='Zurich Insurance')
        insurer_a = Party(party_type='ORGANIZATION', name='AXA Insurance')
        insurer_h = Party(party_type='ORGANIZATION', name='Helvetia Insurance')
        cleaning_co = Party(party_type='ORGANIZATION', name='Blitz Blank Reinigung', city='Zürich', country='Switzerland')
        
        session.add_all([bakery, broker_sme, insurer_z, insurer_a, insurer_h, cleaning_co])
        session.commit()

        submission1 = Submission(insured_party_id=bakery.id, broker_party_id=broker_sme.id, status='BOUND')
        session.add(submission1)
        session.commit()

        quote_z = Quote(submission_id=submission1.id, insurer_party_id=insurer_z.id, total_premium=5200, status='REJECTED')
        quote_a = Quote(submission_id=submission1.id, insurer_party_id=insurer_a.id, total_premium=5500, status='REJECTED')
        quote_h = Quote(submission_id=submission1.id, insurer_party_id=insurer_h.id, total_premium=4950, status='ACCEPTED')
        session.add_all([quote_z, quote_a, quote_h])
        session.commit()

        policy1 = Policy(policy_number='CH-SME-2023-001', quote_id=quote_h.id, effective_date=datetime.date(2023, 1, 1), expiration_date=datetime.date(2023, 12, 31))
        session.add(policy1)
        session.commit()

        # Add roles for policy 1
        session.add(PartyRole(party_id=bakery.id, role_name='Insured', context_table='policy', context_id=policy1.id))
        session.add(PartyRole(party_id=broker_sme.id, role_name='Broker', context_table='policy', context_id=policy1.id))
        session.add(PartyRole(party_id=insurer_h.id, role_name='Insurer', context_table='policy', context_id=policy1.id))
        session.commit()

        doc1 = Document(document_name='Handelsregisterauszug.pdf', file_path='/uploads/Handelsregisterauszug.pdf', related_table='policy', related_id=policy1.id, uploader_party_id=broker_sme.id)
        session.add(doc1)

        cov1_prop = Coverage(policy_id=policy1.id, coverage_type='Property', limit_amount=500000, deductible_amount=1000)
        cov1_liab = Coverage(policy_id=policy1.id, coverage_type='General Liability', limit_amount=2000000, deductible_amount=500)
        session.add_all([cov1_prop, cov1_liab])

        claim1 = Claim(policy_id=policy1.id, claim_number='C-2023-07-15-001', date_of_loss=datetime.date(2023, 7, 15), reported_date=datetime.date(2023, 7, 15), status='SETTLED', reported_by_party_id=bakery.id, description='Customer slip and fall on wet floor.')
        session.add(claim1)
        session.commit()
    
        fin_trans1 = FinancialTransaction(claim_id=claim1.id, transaction_type='PAYMENT_INDEMNITY', amount=7500, currency='CHF', transaction_date=datetime.date(2023, 8, 1), payee_party_id=bakery.id)
        session.add(fin_trans1)

        subro1 = Subrogation(claim_id=claim1.id, liable_party_id=cleaning_co.id, potential_recovery_amount=7500, status='IN_PROGRESS')
        session.add(subro1)

        # Case 2: Maschinenbau Schmidt AG
        schmidt_ag = Party(party_type='ORGANIZATION', name='Maschinenbau Schmidt AG', country='Germany')
        agent_large = Party(party_type='ORGANIZATION', name='German Agency Network', country='Germany')
        lead_insurer = Party(party_type='ORGANIZATION', name='Munich Re')
        coinsurer1 = Party(party_type='ORGANIZATION', name='Allianz')
        session.add_all([schmidt_ag, agent_large, lead_insurer, coinsurer1])
        session.commit()

        policy2 = Policy(policy_number='DE-MID-2023-002', effective_date=datetime.date(2023, 3, 1), expiration_date=datetime.date(2024, 2, 29))
        session.add(policy2)
        session.commit()

        # Add roles for policy 2
        session.add(PartyRole(party_id=schmidt_ag.id, role_name='Insured', context_table='policy', context_id=policy2.id))
        session.add(PartyRole(party_id=agent_large.id, role_name='Broker', context_table='policy', context_id=policy2.id))
        session.add(PartyRole(party_id=lead_insurer.id, role_name='Lead Insurer', context_table='policy', context_id=policy2.id))
        session.add(PartyRole(party_id=coinsurer1.id, role_name='Co-insurer', context_table='policy', context_id=policy2.id))
        session.commit()

        pi1 = PolicyInsurer(policy_id=policy2.id, insurer_party_id=lead_insurer.id, share_percentage=70.0, is_lead=True)
        pi2 = PolicyInsurer(policy_id=policy2.id, insurer_party_id=coinsurer1.id, share_percentage=30.0, is_lead=False)
        session.add_all([pi1, pi2])
        session.commit()

        cov2_prop = Coverage(policy_id=policy2.id, coverage_type='All Risk Property', limit_amount=80000000, deductible_amount=100000)
        cov2_bi = Coverage(policy_id=policy2.id, coverage_type='Business Interruption', limit_amount=10000000, deductible_amount=0)
        session.add_all([cov2_prop, cov2_bi])

        # Add some assets for Schmidt AG
        asset_stuttgart = InsurableAsset(policy_id=policy2.id, asset_type='Factory Building', description='Main factory in Stuttgart')
        session.add(asset_stuttgart)
        session.commit()
        loc1 = AssetLocation(asset_id=asset_stuttgart.id, address='Industriestrasse 10', city='Stuttgart', country='Germany')
        det1 = AssetDetail(asset_id=asset_stuttgart.id, detail_key='Replacement Value', detail_value='50000000')
        session.add_all([loc1, det1])

        asset_hamburg = InsurableAsset(policy_id=policy2.id, asset_type='Factory Building', description='Secondary factory in Hamburg')
        session.add(asset_hamburg)
        session.commit()
        loc2 = AssetLocation(asset_id=asset_hamburg.id, address='Hafenweg 5', city='Hamburg', country='Germany')
        det2 = AssetDetail(asset_id=asset_hamburg.id, detail_key='Replacement Value', detail_value='30000000')
        session.add_all([loc2, det2])
    
        # Add a claim for the factory fire
        claim2 = Claim(policy_id=policy2.id, claim_number='C-2023-09-01-005', date_of_loss=datetime.date(2023, 9, 1), reported_date=datetime.date(2023, 9, 2), status='UNDER_REVIEW', reported_by_party_id=schmidt_ag.id, description='Fire in Stuttgart factory, impacting production line 3.')
        session.add(claim2)
        session.commit()
    
        fin_trans2 = FinancialTransaction(claim_id=claim2.id, transaction_type='RESERVE', amount=500000, currency='EUR', transaction_date=datetime.date(2023, 9, 3))
        session.add(fin_trans2)

        # Case 3: HelvetiaPharma SA
        pharma_co = Party(party_type='ORGANIZATION', name='HelvetiaPharma SA', city='Basel', country='Switzerland')
        global_broker = Party(party_type='ORGANIZATION', name='Global Brokerage Inc.')
        reinsurer1 = Party(party_type='ORGANIZATION', name='Swiss Re')
        reinsurer2 = Party(party_type='ORGANIZATION', name='Hannover Re')
        reinsurer3 = Party(party_type='ORGANIZATION', name='SCOR')
        session.add_all([pharma_co, global_broker, reinsurer1, reinsurer2, reinsurer3])
        session.commit()

        policy3 = Policy(policy_number='CH-GLBL-2023-001', effective_date=datetime.date(2023, 1, 1), expiration_date=datetime.date(2023, 12, 31))
        session.add(policy3)
        session.commit()

        session.add(PartyRole(party_id=pharma_co.id, role_name='Insured', context_table='policy', context_id=policy3.id))
        session.add(PartyRole(party_id=global_broker.id, role_name='Broker', context_table='policy', context_id=policy3.id))
        session.add(PartyRole(party_id=insurer_h.id, role_name='Insurer', context_table='policy', context_id=policy3.id)) # Helvetia is lead insurer

        cov3_liab = Coverage(policy_id=policy3.id, coverage_type='Global Product Liability', limit_amount=250000000, deductible_amount=100000)
        session.add(cov3_liab)

        treaty1 = ReinsuranceTreaty(policy_id=policy3.id, treaty_type='FACULTATIVE', description='250M Product Liability Tower')
        session.add(treaty1)
        session.commit()

        # Create reinsurance tower
        layer1 = ReinsuranceLayer(treaty_id=treaty1.id, layer_order=1, attachment_point=0, layer_limit=10000000) # Primary layer by Helvetia
        layer2 = ReinsuranceLayer(treaty_id=treaty1.id, layer_order=2, attachment_point=10000000, layer_limit=40000000)
        layer3 = ReinsuranceLayer(treaty_id=treaty1.id, layer_order=3, attachment_point=50000000, layer_limit=200000000)
        session.add_all([layer1, layer2, layer3])
        session.commit()

        # Populate layers
        p1 = LayerParticipant(layer_id=layer2.id, reinsurer_party_id=reinsurer1.id, share_percentage=50.0, status='BOUND')
        p2 = LayerParticipant(layer_id=layer2.id, reinsurer_party_id=reinsurer2.id, share_percentage=50.0, status='BOUND')
        p3 = LayerParticipant(layer_id=layer3.id, reinsurer_party_id=reinsurer1.id, share_percentage=33.3, status='BOUND')
        p4 = LayerParticipant(layer_id=layer3.id, reinsurer_party_id=reinsurer2.id, share_percentage=33.3, status='BOUND')
        p5 = LayerParticipant(layer_id=layer3.id, reinsurer_party_id=reinsurer3.id, share_percentage=33.4, status='BOUND')
        session.add_all([p1, p2, p3, p4, p5])
        session.commit()

        claim3 = Claim(policy_id=policy3.id, claim_number='C-2023-10-20-009', date_of_loss=datetime.date(2023, 5, 1), reported_date=datetime.date(2023, 10, 20), status='UNDER_REVIEW', reported_by_party_id=pharma_co.id, description='US Lawsuit related to product X. Estimated loss CHF 90M.')
        session.add(claim3)
        session.commit()

        fin_trans3 = FinancialTransaction(claim_id=claim3.id, transaction_type='RESERVE', amount=90000000, currency='CHF', transaction_date=datetime.date(2023, 10, 21))
        session.add(fin_trans3)
    
        # Issue cash calls as claim pierces Layer 1 (10M) and Layer 2 (40M)
        # Call on Layer 2 participants
        cc1 = CashCall(claim_id=claim3.id, layer_participant_id=p1.id, call_amount=20000000, currency='CHF', due_date=datetime.date(2023, 11, 30)) # 50% of 40M
        cc2 = CashCall(claim_id=claim3.id, layer_participant_id=p2.id, call_amount=20000000, currency='CHF', due_date=datetime.date(2023, 11, 30)) # 50% of 40M
        # Call on Layer 3 participants for remaining 40M (90M total - 10M primary - 40M layer2)
        cc3 = CashCall(claim_id=claim3.id, layer_participant_id=p3.id, call_amount=13320000, currency='CHF', due_date=datetime.date(2023, 11, 30)) # 33.3% of 40M
        cc4 = CashCall(claim_id=claim3.id, layer_participant_id=p4.id, call_amount=13320000, currency='CHF', due_date=datetime.date(2023, 11, 30)) # 33.3% of 40M
        cc5 = CashCall(claim_id=claim3.id, layer_participant_id=p5.id, call_amount=13360000, currency='CHF', due_date=datetime.date(2023, 11, 30), status='PAID') # 33.4% of 40M
        session.add_all([cc1, cc2, cc3, cc4, cc5])

        session.commit()
        print("Database seeded successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    # Delete existing database when running as script
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print(f"Removed existing database: {DB_FILE}")
        except PermissionError:
            print(f"Warning: Could not remove {DB_FILE} - it may be in use.")
            print("Attempting to recreate tables (this will fail if tables exist)...")
    
    # Create database schema
    Base.metadata.create_all(engine)
    
    # Seed data (session is created inside seed_data())
    seed_data()