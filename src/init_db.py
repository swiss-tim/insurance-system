"""Database initialization module - automatically sets up database if needed."""
import os
from seed_database import DB_FILE, Base, engine, Session, seed_data


def init_database():
    """Initialize database if it doesn't exist or is empty."""
    
    # Check if database file exists
    db_exists = os.path.exists(DB_FILE)
    
    if not db_exists:
        print(f"Database {DB_FILE} not found. Creating and seeding...")
        # Create all tables
        Base.metadata.create_all(engine)
        
        # Seed with demo data
        session = Session()
        try:
            seed_data()
            session.close()
            print(f"✓ Database created and seeded successfully!")
        except Exception as e:
            session.close()
            print(f"Error seeding database: {e}")
            raise
    else:
        # Database exists, check if it has data
        session = Session()
        try:
            from seed_database import Party
            party_count = session.query(Party).count()
            session.close()
            
            if party_count == 0:
                print(f"Database {DB_FILE} exists but is empty. Seeding...")
                session = Session()
                seed_data()
                session.close()
                print(f"✓ Database seeded successfully!")
            else:
                print(f"✓ Database {DB_FILE} ready ({party_count} parties found)")
        except Exception as e:
            session.close()
            print(f"Note: Database exists but may need initialization: {e}")


if __name__ == '__main__':
    init_database()

