"""
U.S. Workers' Compensation Market - Seed Data
==============================================
Demo data for U.S. Workers' Compensation insurance
"""

import datetime
from seed_database import (
    Party, Submission, Quote
)

def seed_us_data(session):
    """Seed U.S. Workers' Compensation market demo data"""
    
    print("Seeding U.S. Workers' Compensation Market Demo...")
    
    # === INSURERS ===
    insurer_h = Party(
        party_type='ORGANIZATION',
        name='Harmonic Insurance Company',
        address='123 Insurance Plaza',
        city='Hartford',
        country='USA',
        email='underwriting@harmonic-insurance.com',
        phone='+1 860 555 0100'
    )
    session.add(insurer_h)
    session.commit()
    
    # === BROKERS ===
    marsh = Party(
        party_type='ORGANIZATION',
        name='Marsh & McLennan',
        address='1166 Avenue of the Americas',
        city='New York',
        country='USA',
        email='commercial@marsh.com',
        phone='+1 212 345 5000'
    )
    session.add(marsh)
    
    willis = Party(
        party_type='ORGANIZATION',
        name='Willis Towers Watson',
        address='200 Liberty Street',
        city='New York',
        country='USA',
        email='info@willistowerswatson.com',
        phone='+1 212 915 8888'
    )
    session.add(willis)
    
    alliant = Party(
        party_type='ORGANIZATION',
        name='Alliant Insurance Services',
        address='2 Park Plaza',
        city='Irvine',
        country='USA',
        email='commercial@alliant.com',
        phone='+1 949 756 3000'
    )
    session.add(alliant)
    session.commit()
    
    # === UNDERWRITING CENTER: Main Demo Company ===
    floor_decor = Party(
        party_type='ORGANIZATION',
        name='Floor & Decor Outlets of America, Inc',
        address='2500 Windy Ridge Parkway SE',
        city='Atlanta',
        country='USA',
        email='risk@flooranddecor.com',
        phone='+1 404 471 1634'
    )
    session.add(floor_decor)
    session.commit()
    
    submission_floor_decor = Submission(
        submission_number='SUB-2026-001',
        insured_party_id=floor_decor.id,
        broker_party_id=marsh.id,
        status='Triaged',
        effective_date=datetime.date(2025, 10, 29),
        completeness=74,
        priority_score=4.8,
        risk_appetite='High',
        broker_tier='Tier 1',
        accepted=False,
        created_at=datetime.datetime(2025, 10, 15, 9, 30)
    )
    session.add(submission_floor_decor)
    session.commit()
    
    # === OTHER ACTIVE SUBMISSIONS ===
    
    # Monrovia Metalworking
    monrovia = Party(
        party_type='ORGANIZATION',
        name='Monrovia Metalworking',
        city='Monrovia',
        country='USA'
    )
    session.add(monrovia)
    session.commit()
    
    submission_monrovia = Submission(
        submission_number='SUB-2026-003',
        insured_party_id=monrovia.id,
        broker_party_id=willis.id,
        status='In Review',
        effective_date=datetime.date(2026, 1, 15),
        completeness=88,
        priority_score=4.7,
        risk_appetite='High',
        broker_tier='Tier 1',
        accepted=False,
        created_at=datetime.datetime(2025, 10, 18, 14, 20)
    )
    session.add(submission_monrovia)
    session.commit()
    
    # Retail Chain Express
    retail_chain = Party(
        party_type='ORGANIZATION',
        name='Retail Chain Express',
        city='Chicago',
        country='USA'
    )
    session.add(retail_chain)
    session.commit()
    
    submission_retail = Submission(
        submission_number='SUB-2026-005',
        insured_party_id=retail_chain.id,
        broker_party_id=marsh.id,
        status='In Review',
        effective_date=datetime.date(2026, 3, 1),
        completeness=82,
        priority_score=4.5,
        risk_appetite='Medium',
        broker_tier='Tier 2',
        accepted=False,
        created_at=datetime.datetime(2025, 10, 28, 9, 45)
    )
    session.add(submission_retail)
    session.commit()
    
    # Restaurant Holdings
    restaurant_holdings = Party(
        party_type='ORGANIZATION',
        name='Restaurant Holdings Inc',
        city='Miami',
        country='USA'
    )
    session.add(restaurant_holdings)
    session.commit()
    
    submission_restaurant = Submission(
        submission_number='SUB-2026-006',
        insured_party_id=restaurant_holdings.id,
        broker_party_id=willis.id,
        status='In Review',
        effective_date=datetime.date(2026, 4, 1),
        completeness=79,
        priority_score=4.6,
        risk_appetite='High',
        broker_tier='Tier 3',
        accepted=False,
        created_at=datetime.datetime(2025, 11, 2, 13, 20)
    )
    session.add(submission_restaurant)
    session.commit()
    
    # Construction Dynamics (Already Quoted, not yet sent to broker)
    construction_dynamics = Party(
        party_type='ORGANIZATION',
        name='Construction Dynamics LLC',
        city='Denver',
        country='USA'
    )
    session.add(construction_dynamics)
    session.commit()
    
    submission_construction = Submission(
        submission_number='SUB-2026-007',
        insured_party_id=construction_dynamics.id,
        broker_party_id=alliant.id,
        status='Quoted',
        effective_date=datetime.date(2026, 5, 1),
        completeness=75,
        priority_score=4.6,
        risk_appetite='High',
        broker_tier='Tier 3',
        accepted=False,  # Quote not yet sent to broker
        created_at=datetime.datetime(2025, 10, 5, 16, 30)
    )
    session.add(submission_construction)
    session.commit()
    
    # Add a quote for Construction Dynamics
    quote_construction = Quote(
        submission_id=submission_construction.id,
        insurer_party_id=insurer_h.id,
        total_premium=68500,
        currency='USD',
        status='SENT',
        created_at=datetime.datetime(2025, 10, 16, 14, 20)
    )
    session.add(quote_construction)
    session.commit()
    
    # Manufacturing Specialists
    manufacturing_specialists = Party(
        party_type='ORGANIZATION',
        name='Manufacturing Specialists Corp',
        city='Detroit',
        country='USA'
    )
    session.add(manufacturing_specialists)
    session.commit()
    
    submission_manufacturing = Submission(
        submission_number='SUB-2026-008',
        insured_party_id=manufacturing_specialists.id,
        broker_party_id=alliant.id,
        status='In Review',
        effective_date=datetime.date(2026, 6, 1),
        completeness=71,
        priority_score=4.1,
        risk_appetite='Medium',
        broker_tier='Tier 2',
        accepted=False,
        created_at=datetime.datetime(2025, 11, 3, 10, 15)
    )
    session.add(submission_manufacturing)
    session.commit()
    
    # === BOUND SUBMISSIONS (Historical) ===
    
    # Previous bound policy 1
    bound_company_1 = Party(
        party_type='ORGANIZATION',
        name='Regional Logistics Partners',
        city='Dallas',
        country='USA'
    )
    session.add(bound_company_1)
    session.commit()
    
    submission_bound_1 = Submission(
        submission_number='SUB-2023-001',
        insured_party_id=bound_company_1.id,
        broker_party_id=marsh.id,
        status='BOUND',
        effective_date=datetime.date(2023, 1, 1),
        completeness=100,
        priority_score=3.2,
        risk_appetite='Low',
        broker_tier='Tier 2',
        accepted=True,
        created_at=datetime.datetime(2022, 12, 10, 10, 30)
    )
    session.add(submission_bound_1)
    session.commit()
    
    # Previous bound policy 2
    bound_company_2 = Party(
        party_type='ORGANIZATION',
        name='Pacific Trade Services',
        city='San Francisco',
        country='USA'
    )
    session.add(bound_company_2)
    session.commit()
    
    submission_bound_2 = Submission(
        submission_number='SUB-2024-012',
        insured_party_id=bound_company_2.id,
        broker_party_id=willis.id,
        status='BOUND',
        effective_date=datetime.date(2024, 6, 1),
        completeness=100,
        priority_score=4.5,
        risk_appetite='High',
        broker_tier='Tier 1',
        accepted=True,
        created_at=datetime.datetime(2024, 5, 15, 14, 20)
    )
    session.add(submission_bound_2)
    session.commit()
    
    # Previous bound policy 3
    bound_company_3 = Party(
        party_type='ORGANIZATION',
        name='Eastern Manufacturing Group',
        city='Philadelphia',
        country='USA'
    )
    session.add(bound_company_3)
    session.commit()
    
    submission_bound_3 = Submission(
        submission_number='SUB-2025-008',
        insured_party_id=bound_company_3.id,
        broker_party_id=alliant.id,
        status='BOUND',
        effective_date=datetime.date(2025, 9, 1),
        completeness=100,
        priority_score=3.8,
        risk_appetite='Medium',
        broker_tier='Tier 2',
        accepted=True,
        created_at=datetime.datetime(2025, 8, 10, 11, 45)
    )
    session.add(submission_bound_3)
    session.commit()
    
    # === DECLINED SUBMISSION ===
    declined_company = Party(
        party_type='ORGANIZATION',
        name='High Risk Industries LLC',
        city='Houston',
        country='USA'
    )
    session.add(declined_company)
    session.commit()
    
    submission_declined = Submission(
        submission_number='SUB-2025-015',
        insured_party_id=declined_company.id,
        broker_party_id=alliant.id,
        status='DECLINED',
        effective_date=datetime.date(2025, 12, 1),
        completeness=65,
        priority_score=2.1,
        risk_appetite='Low',
        broker_tier='Tier 3',
        accepted=False,
        created_at=datetime.datetime(2025, 10, 5, 15, 30)
    )
    session.add(submission_declined)
    session.commit()
    
    session.commit()
    print("[OK] U.S. Workers' Compensation market data seeded successfully")
    return True

