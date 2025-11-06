"""
German SHUK Market - Seed Data
================================
Demo data for German commercial insurance (SHUK - Sach- und Haftpflichtversicherung)
Product: Betriebshaftpflicht + Sachversicherung (Commercial Liability + Property)
"""

import datetime
from seed_database import (
    Party, Submission, Quote
)

def seed_german_data(session):
    """Seed German SHUK market demo data"""
    
    print("Seeding German SHUK Market Demo...")
    
    # === INSURERS ===
    insurer_g = Party(
        party_type='ORGANIZATION',
        name='Dräum Versicherung AG',
        address='Königsallee 45',
        city='Düsseldorf',
        country='Germany',
        email='underwriting@draeum-versicherung.de',
        phone='+49 211 8765 4321'
    )
    session.add(insurer_g)
    session.commit()
    
    # === BROKERS ===
    marsh_de = Party(
        party_type='ORGANIZATION',
        name='Marsh GmbH',
        address='Friedrichstraße 200',
        city='Berlin',
        country='Germany',
        email='commercial@marsh.de',
        phone='+49 30 2060 9000'
    )
    session.add(marsh_de)
    
    willis_de = Party(
        party_type='ORGANIZATION',
        name='Willis Towers Watson GmbH',
        address='Mies-van-der-Rohe-Straße 8',
        city='München',
        country='Germany',
        email='info@willistowerswatson.de',
        phone='+49 89 3860 6000'
    )
    session.add(willis_de)
    
    aon_de = Party(
        party_type='ORGANIZATION',
        name='Aon Deutschland GmbH',
        address='Caffamacherreihe 16',
        city='Hamburg',
        country='Germany',
        email='commercial@aon.de',
        phone='+49 40 3605 5000'
    )
    session.add(aon_de)
    session.commit()
    
    # === UNDERWRITING CENTER: Main Demo Company ===
    moebel_schmidt = Party(
        party_type='ORGANIZATION',
        name='Möbel & Wohnen Schmidt GmbH',
        address='Industriestraße 123',
        city='Düsseldorf',
        country='Germany',
        email='versicherung@moebel-schmidt.de',
        phone='+49 211 5432 1000'
    )
    session.add(moebel_schmidt)
    session.commit()
    
    submission_schmidt = Submission(
        submission_number='SUB-2026-001-DE',
        insured_party_id=moebel_schmidt.id,
        broker_party_id=marsh_de.id,
        status='Triaged',
        effective_date=datetime.date(2025, 11, 15),
        completeness=74,
        priority_score=4.8,
        risk_appetite='High',
        broker_tier='Tier 1',
        accepted=False,
        created_at=datetime.datetime(2025, 11, 1, 9, 30)
    )
    session.add(submission_schmidt)
    session.commit()
    
    # === OTHER ACTIVE SUBMISSIONS ===
    
    # Bauhaus Retail
    bauhaus_retail = Party(
        party_type='ORGANIZATION',
        name='Bauhaus Einzelhandel AG',
        city='Köln',
        country='Germany'
    )
    session.add(bauhaus_retail)
    session.commit()
    
    submission_bauhaus = Submission(
        submission_number='SUB-2026-003-DE',
        insured_party_id=bauhaus_retail.id,
        broker_party_id=willis_de.id,
        status='In Review',
        effective_date=datetime.date(2026, 1, 1),
        completeness=88,
        priority_score=4.7,
        risk_appetite='High',
        broker_tier='Tier 1',
        accepted=False,
        created_at=datetime.datetime(2025, 10, 18, 14, 20)
    )
    session.add(submission_bauhaus)
    session.commit()
    
    # Tech Distribution
    tech_distribution = Party(
        party_type='ORGANIZATION',
        name='TechDistribution Deutschland GmbH',
        city='Frankfurt',
        country='Germany'
    )
    session.add(tech_distribution)
    session.commit()
    
    submission_tech = Submission(
        submission_number='SUB-2026-004-DE',
        insured_party_id=tech_distribution.id,
        broker_party_id=marsh_de.id,
        status='Quoted',
        effective_date=datetime.date(2026, 2, 1),
        completeness=95,
        priority_score=4.5,
        risk_appetite='Medium',
        broker_tier='Tier 2',
        accepted=False,  # Not yet sent to broker
        created_at=datetime.datetime(2025, 10, 25, 11, 15)
    )
    session.add(submission_tech)
    session.commit()
    
    # Add quote for Tech Distribution
    quote_tech = Quote(
        submission_id=submission_tech.id,
        insurer_party_id=insurer_g.id,
        total_premium=85000,
        currency='EUR',
        status='SENT',
        created_at=datetime.datetime(2025, 11, 5, 16, 45)
    )
    session.add(quote_tech)
    session.commit()
    
    # Gastro Group
    gastro_group = Party(
        party_type='ORGANIZATION',
        name='Gastro Express Holding GmbH',
        city='Stuttgart',
        country='Germany'
    )
    session.add(gastro_group)
    session.commit()
    
    submission_gastro = Submission(
        submission_number='SUB-2026-005-DE',
        insured_party_id=gastro_group.id,
        broker_party_id=aon_de.id,
        status='In Review',
        effective_date=datetime.date(2026, 3, 1),
        completeness=82,
        priority_score=4.3,
        risk_appetite='Medium',
        broker_tier='Tier 2',
        accepted=False,
        created_at=datetime.datetime(2025, 10, 28, 9, 45)
    )
    session.add(submission_gastro)
    session.commit()
    
    # Manufacturing Company
    precision_tech = Party(
        party_type='ORGANIZATION',
        name='Präzisionstechnik Süd GmbH',
        city='Augsburg',
        country='Germany'
    )
    session.add(precision_tech)
    session.commit()
    
    submission_precision = Submission(
        submission_number='SUB-2026-006-DE',
        insured_party_id=precision_tech.id,
        broker_party_id=willis_de.id,
        status='In Review',
        effective_date=datetime.date(2026, 4, 1),
        completeness=79,
        priority_score=4.1,
        risk_appetite='Low',
        broker_tier='Tier 3',
        accepted=False,
        created_at=datetime.datetime(2025, 11, 2, 13, 20)
    )
    session.add(submission_precision)
    session.commit()
    
    # === BOUND SUBMISSIONS (Historical) ===
    
    # Previous bound policy 1
    bound_company_1 = Party(
        party_type='ORGANIZATION',
        name='Logistik Partner Nord GmbH',
        city='Hamburg',
        country='Germany'
    )
    session.add(bound_company_1)
    session.commit()
    
    submission_bound_1 = Submission(
        submission_number='SUB-2023-001-DE',
        insured_party_id=bound_company_1.id,
        broker_party_id=marsh_de.id,
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
        name='Handel & Service Bayern AG',
        city='München',
        country='Germany'
    )
    session.add(bound_company_2)
    session.commit()
    
    submission_bound_2 = Submission(
        submission_number='SUB-2024-012-DE',
        insured_party_id=bound_company_2.id,
        broker_party_id=willis_de.id,
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
        name='Handwerk Meister Rheinland eG',
        city='Köln',
        country='Germany'
    )
    session.add(bound_company_3)
    session.commit()
    
    submission_bound_3 = Submission(
        submission_number='SUB-2025-008-DE',
        insured_party_id=bound_company_3.id,
        broker_party_id=aon_de.id,
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
        name='Risiko Industrie GmbH',
        city='Duisburg',
        country='Germany'
    )
    session.add(declined_company)
    session.commit()
    
    submission_declined = Submission(
        submission_number='SUB-2025-015-DE',
        insured_party_id=declined_company.id,
        broker_party_id=aon_de.id,
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
    print("[OK] German SHUK market data seeded successfully")
    return True

