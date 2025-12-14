from app import app, db, Candidate

def seed():
    with app.app_context():
        db.create_all()
        # Check if we have candidates
        if Candidate.query.first():
            print("Database already seeded.")
            return

        names = [
            "Alice Johnson",
            "Bob Smith",
            "Charlie Brown",
            "Diana Prince",
            "Evan Wright"
        ]

        for name in names:
            c = Candidate(name=name)
            db.session.add(c)
        
        db.session.commit()
        print(f"Seeded {len(names)} candidates.")

if __name__ == '__main__':
    seed()
