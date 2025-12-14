from app import app, db, Vote

def reset_votes():
    with app.app_context():
        try:
            num_deleted = db.session.query(Vote).delete()
            db.session.commit()
            print(f"Successfully deleted {num_deleted} votes.")
            print("The candidates remain in the database.")
        except Exception as e:
            print(f"Error resetting votes: {e}")
            db.session.rollback()

if __name__ == "__main__":
    reset_votes()
