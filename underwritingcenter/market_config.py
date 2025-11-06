"""
Market-Specific Configuration
==============================
Contains all market-specific demo content for German SHUK and U.S. Workers' Compensation
"""

# Market detection helper
def detect_market(submission_number, country=None):
    """Detect market based on submission number or country"""
    if submission_number and '-DE' in submission_number:
        return 'german'
    if country and country.upper() in ['GERMANY', 'DEUTSCHLAND', 'DE']:
        return 'german'
    return 'us'

# Currency formatters
def format_currency(amount, market):
    """Format currency based on market"""
    if market == 'german':
        return f"€{amount:,.0f}".replace(',', '.')
    else:
        return f"${amount:,.0f}"

# Market-specific content
MARKET_CONTENT = {
    'german': {
        'product_name': 'Betriebshaftpflicht + Sachversicherung',
        'currency': 'EUR',
        'currency_symbol': '€',
        
        # Documents
        'documents': [
            '📎 Moebel_Schmidt_Antrag.pdf (1. Nov 2025 09:30)',
            '📎 GDV_Fragebogen.pdf (1. Nov 2025 09:35)',
            '📧 Email: Zusätzliche Risikoinformationen (2. Nov 2025 14:45)',
            '📎 Schadenhistorie_2022-2024.xlsx (2. Nov 2025 15:10)'
        ],
        
        # AI Summary
        'ai_summary': {
            'business_overview': 'Möbel & Wohnen Schmidt ist ein Facheinzelhändler für Möbel und Wohnaccessoires mit 85 Filialen in Deutschland. Jahresumsatz: €450M.',
            'coverage_requested': 'Betriebshaftpflicht + Sachversicherung Erneuerung. Geschätzte Jahresprämie: €120K basierend auf Umsatz €450M und Verkaufsfläche 125.000 m².',
            'loss_history': 'Moderate Schadenquote von 62% über die letzten 3 Jahre. Hauptschäden: Kundenverletzungen in Filialen, Produkthaftpflichtansprüche, kleinere Sachschäden.',
            'risk_factors': [
                'Solides Sicherheitsprogramm mit BG-Konformität',
                'Qualitätsmanagement reduziert Produkthaftungsrisiken',
                'Expansion in neue Standorte erhöht Exposure',
                'Online-Geschäft wächst (Cyber-Risiko relevant)'
            ],
            'recommendation': 'Fortsetzung der Zeichnung empfohlen. Konto erfüllt Risikoappetit-Kriterien. Cyber-Risiko-Baustein zur erweiterten Deckung in Betracht ziehen.'
        },
        
        # Impact on Completeness
        'completeness_impact': '✓ Risikofaktoren extrahiert (+8%)\n\n✓ Schadenhistorie verifiziert (+4%)\n\n✓ Sicherheitsprogramm bewertet (+2%)',
        
        # Company Info
        'company_info': {
            'industry': 'Einzelhandel - Möbel & Wohnaccessoires',
            'locations': '85 Filialen in Deutschland (NRW, Bayern, Baden-Württemberg)',
            'revenue': '€450 Millionen',
            'employees': '2.800+',
            'payroll': '€85 Millionen',
            'years_in_business': '35+ Jahre'
        },
        
        # Operations
        'operations': {
            'primary': [
                'Verkauf von Möbeln und Wohnaccessoires',
                'Einrichtungsberatung im Geschäft',
                'Lager- und Logistikbetrieb',
                'Lieferung und Montageservice'
            ],
            'risk_characteristics': [
                'Schwere Materialtransporte (Gabelstapler)',
                'Kundenfrequenz in Filialen',
                'Montage-Teams (höhere Risikoklasse)',
                'Bundesweite Operationen'
            ],
            'safety_programs': [
                'BG-konforme Sicherheitsschulungen',
                'Quartalsmäßige Sicherheitsaudits',
                'Unfalluntersuchungsprotokolle',
                'Lieferantenqualitätssicherung'
            ]
        },
        
        # Coverages
        'coverages': [
            {'name': 'Betriebshaftpflicht', 'limit': '10.000.000', 'selected': True},
            {'name': 'Sachversicherung - Gebäude', 'limit': '15.000.000', 'selected': True},
            {'name': 'Sachversicherung - Inventar', 'limit': '25.000.000', 'selected': True},
            {'name': 'Betriebsunterbrechung', 'limit': '5.000.000', 'selected': True}
        ],
        
        # Endorsements
        'endorsements': {
            'base': {
                'Umwelthaftpflicht-Erweiterung': True,
                'Produkthaftpflicht-Erweiterung': True,
                'Glasbruchversicherung': True,
                'Transportversicherung': True,
                'Erhöhter Selbstbehalt (€10.000)': True,
                'All-Risk-Deckung Lager': True
            },
            'recommended': {
                'Cyber-Risiko Baustein': False,
                'Selbstbeteiligung Baustein': False
            }
        },
        
        # Base Quote
        'base_quote': {
            'premium': 115000,
            'coverage_details': [
                'Betriebshaftpflicht: €10M Deckungssumme',
                'Sachversicherung Gebäude: €15M',
                'Sachversicherung Inventar: €25M',
                'Betriebsunterbrechung: €5M',
                'Selbstbehalt: €5.000 pro Schaden'
            ]
        },
        
        # AI Recommendations
        'ai_recommendations': {
            'title': 'KI-Analyse empfiehlt:',
            'subtitle': 'Deckungsänderungen:',
            'loading_message': 'Bausteine werden hinzugefügt...',
            'items': [
                {
                    'name': 'Cyber-Risiko Baustein',
                    'rationale_label': 'Begründung',
                    'rationale': 'Wachsendes Online-Geschäft mit Kundendaten und sensiblen Zahlungsinformationen. Cyber-Risiken nehmen zu.',
                    'premium_label': 'Prämienauswirkung',
                    'premium_impact': '+€29500',
                    'benefit_label': 'Risikominderung',
                    'benefit': 'Reduziert potenzielle Haftung bei Datenschutzverletzungen um 78%'
                },
                {
                    'name': 'Selbstbeteiligung Baustein',
                    'rationale_label': 'Begründung',
                    'rationale': 'Großkunde mit solidem Risikomanagement. Selbstbeteiligung (pro Schaden) kann Prämie senken bei vollem Versicherungsschutz.',
                    'premium_label': 'Prämienauswirkung',
                    'premium_impact': '-€7800',
                    'benefit_label': 'Risikominderung',
                    'benefit': 'Fördert proaktives Schadenmanagement'
                }
            ]
        },
        
        # Quotes
        'quotes': {
            'base_title': 'Basisangebot (Manuelle Prämie)',
            'generated_title': 'Generiertes Angebot (Erweitert)',
            'base': {
                'premium': '€115,000',
                'rating_basis': 'Manuelle Tarifierung nach Umsatz',
                'exposure_label': 'Jahresumsatz',
                'exposure_value': '€450.000.000',
                'experience_mod': '0.92',
                'geography_label': 'Standorte',
                'geography_value': '85 Filialen in Deutschland'
            }
        },
        
        # Generated Quote (with recommendations)
        'generated_quote': {
            'premium': 111500,  # 115000 + 8500 - 12000
            'coverage_details': [
                'Betriebshaftpflicht: €10M Deckungssumme',
                'Sachversicherung Gebäude: €15M',
                'Sachversicherung Inventar: €25M',
                'Betriebsunterbrechung: €5M',
                'Cyber-Risiko: €5M (NEU)',
                'Selbstbehalt: €10.000 pro Schaden'
            ],
            'analysis': {
                'value_prop': 'Bessere Deckung (Cyber hinzugefügt) + €3.500 günstiger als Wettbewerb',
                'competitive_position': 'Allianz-Angebot: €115.000 ohne Cyber',
                'win_probability': '92%'
            }
        }
    },
    
    'us': {
        'product_name': 'Workers\' Compensation Insurance',
        'currency': 'USD',
        'currency_symbol': '$',
        
        # Documents
        'documents': [
            '📎 Floor_Decor_Submission_Form.pdf (Oct 15, 2025 09:30)',
            '📎 ACORD_Application.pdf (Oct 15, 2025 09:32)',
            '📧 Email: Additional Risk Information (Oct 16, 2025 14:45)',
            '📎 Loss_Runs_2022-2024.xlsx (Oct 16, 2025 15:10)'
        ],
        
        # AI Summary
        'ai_summary': {
            'business_overview': 'Floor & Decor is a specialty retailer of hard surface flooring and related accessories with 150+ locations across the US. Annual revenue: $3.8B.',
            'coverage_requested': 'Workers\' Compensation insurance with Admitted Product Details (APD) rating. Estimated annual premium: $1.8M based on payroll of $450M.',
            'loss_history': 'Moderate loss ratio of 62% over past 3 years. Primary claims: slips/falls in warehouses, forklift incidents, repetitive strain injuries.',
            'risk_factors': [
                'Strong safety program with OSHA compliance',
                'Return-to-work program reduces claim duration',
                'High employee turnover in warehouse positions',
                'Expansion into new states increases exposure'
            ],
            'recommendation': 'Proceed with underwriting. Account meets appetite criteria. Consider voluntary compensation endorsement for enhanced coverage.'
        },
        
        # Impact on Completeness
        'completeness_impact': '✓ Extracted key risk factors (+8%)\n\n✓ Verified loss run data (+4%)\n\n✓ Assessed safety program quality (+2%)',
        
        # Company Info
        'company_info': {
            'industry': 'Retail - Hard Surface Flooring & Accessories',
            'locations': '150+ stores across United States',
            'revenue': '$3.8 Billion',
            'employees': '8,500+',
            'payroll': '$450 Million',
            'years_in_business': '25+ years'
        },
        
        # Operations
        'operations': {
            'primary': [
                'Retail sales of flooring materials (tile, wood, laminate, vinyl)',
                'In-store design services',
                'Warehouse operations',
                'Delivery and installation services'
            ],
            'risk_characteristics': [
                'Heavy material handling (forklift operations)',
                'Customer-facing retail environment',
                'Installation crews (higher risk class)',
                'Multi-state operations'
            ],
            'safety_programs': [
                'OSHA-compliant safety training',
                'Return-to-work program',
                'Quarterly safety audits',
                'Incident investigation protocols'
            ]
        },
        
        # Coverages
        'coverages': [
            {'name': 'Workers\' Compensation - Standard', 'limit': 'Statutory', 'selected': True},
            {'name': 'Employers\' Liability', 'limit': '1,000,000', 'selected': True},
            {'name': 'USL&H Coverage', 'limit': 'Statutory', 'selected': True},
            {'name': 'Voluntary Compensation', 'limit': '1,000,000', 'selected': False}
        ],
        
        # Endorsements
        'endorsements': {
            'base': {
                'Alternate Employer Endorsement': True,
                'Catastrophe (Other Than Certified Acts of Terrorism) Premium Endorsement': True,
                'Deductible Buy Back Endorsement': True,
                'KOTECKI Endorsement': True,
                'Premium Discount Endorsement': True,
                'Waiver of Subrogation Endorsement': True
            },
            'recommended': {
                'Voluntary Compensation Coverage Endorsement': False,
                'Benefits Deductible Endorsement': False
            }
        },
        
        # Base Quote
        'base_quote': {
            'premium': 1800000,
            'coverage_details': [
                'Workers\' Compensation: Statutory limits',
                'Employers\' Liability: $1M per occurrence',
                'Experience Mod: 0.95',
                'Payroll Basis: $450M',
                'Rate: $4.00 per $100 payroll'
            ]
        },
        
        # AI Recommendations
        'ai_recommendations': {
            'title': 'AI Analysis suggests:',
            'subtitle': 'Add Endorsements:',
            'loading_message': 'Adding Endorsements...',
            'items': [
                {
                    'name': 'Voluntary Compensation Coverage Endorsement',
                    'rationale_label': 'Rationale',
                    'rationale': 'Account has high-paid executives who travel internationally. Voluntary compensation provides coverage for executives exempt from standard workers\' comp.',
                    'premium_label': 'Premium Impact',
                    'premium_impact': '+$32875',
                    'benefit_label': 'Risk Benefit',
                    'benefit': 'Reduces potential coverage gap litigation by 87%'
                },
                {
                    'name': 'Benefits Deductible Endorsement',
                    'rationale_label': 'Rationale',
                    'rationale': 'Large account with strong safety program. A benefits deductible (per-claim retention) can reduce premium while maintaining full coverage.',
                    'premium_label': 'Premium Impact',
                    'premium_impact': '-$8650',
                    'benefit_label': 'Risk Benefit',
                    'benefit': 'Encourages proactive claims management'
                }
            ]
        },
        
        # Quotes
        'quotes': {
            'base_title': 'Base Quote (Manual Premium)',
            'generated_title': 'Generated Quote (Enhanced)',
            'base': {
                'premium': '$1,800,000',
                'rating_basis': 'Manual rates per state',
                'exposure_label': 'Payroll',
                'exposure_value': '$450,000,000',
                'experience_mod': '0.95',
                'geography_label': 'States',
                'geography_value': '42 states + DC'
            }
        },
        
        # Generated Quote (with recommendations)
        'generated_quote': {
            'premium': 1824225,  # 1800000 + 32875 - 8650
            'coverage_details': [
                'Workers\' Compensation: Statutory limits',
                'Employers\' Liability: $1M per occurrence',
                'Voluntary Compensation: $1M (ADDED)',
                'Benefits Deductible: $1,000 per claim',
                'Experience Mod: 0.95',
                'Payroll Basis: $450M'
            ],
            'analysis': {
                'value_prop': 'Enhanced coverage with executive protection + competitive pricing',
                'competitive_position': 'Market average: $1.85M',
                'win_probability': '89%'
            }
        }
    }
}

def get_market_content(market):
    """Get all market-specific content"""
    return MARKET_CONTENT.get(market, MARKET_CONTENT['us'])

