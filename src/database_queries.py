# database_queries.py

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, joinedload
from seed_database import (
    Base, Party, Policy, Quote, Submission, Claim, Coverage, 
    InsurableAsset, AssetLocation, AssetDetail, ClaimDetail, 
    FinancialTransaction, Subrogation, PolicyInsurer, ReinsuranceTreaty, 
    ReinsuranceLayer, LayerParticipant, CashCall, Document, PartyRole,
    CustomerUser, ChatMessage, GeneratedAd, PolicySummary, EmailTemplate
)
import pandas as pd

# --- Database Connection ---
DB_FILE = "pnc_demo.db"
engine = create_engine(f'sqlite:///{DB_FILE}')
Session = sessionmaker(bind=engine)

# --- Query Functions ---

def get_session():
    """Provides a new database session."""
    return Session()

def get_all_insureds():
    """Fetches all parties that have the role of 'Insured'."""
    session = get_session()
    insureds = session.query(Party).join(PartyRole).filter(PartyRole.role_name == 'Insured').distinct().all()
    session.close()
    return insureds

def get_policy_details(policy_id):
    """Fetches comprehensive details for a single policy."""
    session = get_session()
    policy = session.query(Policy).options(
        joinedload(Policy.coverages),
        joinedload(Policy.assets).joinedload(InsurableAsset.details),
        joinedload(Policy.assets).joinedload(InsurableAsset.locations),
        joinedload(Policy.claims),
        joinedload(Policy.coinsurers),
        joinedload(Policy.reinsurance_treaties)
    ).get(policy_id)
    session.close()
    return policy

def get_party_by_id(party_id):
    """Fetches a party by their ID."""
    session = get_session()
    party = session.query(Party).get(party_id)
    session.close()
    return party

def get_quotes_for_submission(submission_id):
    """Fetches all quotes associated with a submission."""
    session = get_session()
    quotes = session.query(Quote).options(
        joinedload(Quote.submission)
    ).filter(Quote.submission_id == submission_id).all()
    
    data = []
    for q in quotes:
        insurer = get_party_by_id(q.insurer_party_id)
        data.append({
            'Insurer': insurer.name,
            'Premium': q.total_premium,
            'Currency': q.currency,
            'Status': q.status
        })
    session.close()
    return pd.DataFrame(data)

def get_submission_for_policy(policy_id):
    """Finds the submission related to a policy via its quote."""
    session = get_session()
    policy = session.query(Policy).get(policy_id)
    if policy and policy.quote:
        submission = session.query(Submission).get(policy.quote.submission_id)
        session.close()
        return submission
    session.close()
    return None

def get_claim_details(claim_id):
    """Fetches comprehensive details for a single claim."""
    session = get_session()
    claim = session.query(Claim).options(
        joinedload(Claim.details),
        joinedload(Claim.financials),
        joinedload(Claim.subrogations),
        joinedload(Claim.cash_calls).joinedload(CashCall.participant).joinedload(LayerParticipant.layer)
    ).get(claim_id)
    session.close()
    return claim

def get_reinsurance_tower(policy_id):
    """Constructs the full reinsurance tower for a policy."""
    session = get_session()
    treaty = session.query(ReinsuranceTreaty).filter(ReinsuranceTreaty.policy_id == policy_id).first()
    if not treaty:
        session.close()
        return None, pd.DataFrame()

    layers = session.query(ReinsuranceLayer).filter(ReinsuranceLayer.treaty_id == treaty.id).order_by(ReinsuranceLayer.layer_order).all()
    
    tower_data = []
    for layer in layers:
        participants = session.query(LayerParticipant).filter(LayerParticipant.layer_id == layer.id).all()
        participant_names = []
        for p in participants:
            reinsurer = get_party_by_id(p.reinsurer_party_id)
            participant_names.append(f"{reinsurer.name} ({p.share_percentage}%)")

        tower_data.append({
            'Layer': layer.layer_order,
            'Attachment': f"{layer.attachment_point:,.0f}",
            'Limit': f"{layer.layer_limit:,.0f}",
            'Coverage': f"{layer.layer_limit:,.0f} xs {layer.attachment_point:,.0f}",
            'Participants': ", ".join(participant_names)
        })
    session.close()
    return treaty, pd.DataFrame(tower_data)

def get_coinsurance_details(policy_id):
    """Fetches co-insurance participation for a policy."""
    session = get_session()
    coinsurers = session.query(PolicyInsurer).filter(PolicyInsurer.policy_id == policy_id).all()
    data = []
    for ci in coinsurers:
        insurer = get_party_by_id(ci.insurer_party_id)
        data.append({
            'Insurer': insurer.name,
            'Role': 'Lead' if ci.is_lead else 'Co-insurer',
            'Share': f"{ci.share_percentage}%"
        })
    session.close()
    return pd.DataFrame(data)

def get_documents_for_record(table_name, record_id):
    """Fetches all documents linked to a specific record."""
    session = get_session()
    docs = session.query(Document).filter(Document.related_table == table_name, Document.related_id == record_id).all()
    session.close()
    return docs

def get_claim_subrogation(claim_id):
    """Fetches subrogation details for a claim."""
    session = get_session()
    subro = session.query(Subrogation).filter(Subrogation.claim_id == claim_id).first()
    if subro:
        liable_party = get_party_by_id(subro.liable_party_id)
        session.close()
        return subro, liable_party
    session.close()
    return None, None