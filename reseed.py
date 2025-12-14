from app import app, db
from seed import seed

def reseed():
    """
    Drops all tables (deleting all data including votes!)
    and re-runs the seed function to update candidates.
    """
    print("WARNING: This will delete all votes and reset the database.")
    confirmation = input("Type 'yes' to confirm: ")
    if confirmation.lower() != 'yes':
        print("Operation cancelled.")
        return

    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Tables dropped.")
        
    print("Reseeding database...")
    seed()
    print("Done! Candidates have been updated.")

if __name__ == '__main__':
    reseed()
