from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from models import db, Candidate, Vote
import uuid
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_request
def ensure_identity():
    # We use a cookie to track the user.
    # If not present, we create a new 'user_hash'.
    if 'user_hash' not in request.cookies:
        # We'll just generate it here, but actually we need to set it on response.
        # So we'll access it via a wrapper or helper.
        pass

def get_user_hash():
    return request.cookies.get('user_hash')

@app.route('/')
def index():
    user_hash = get_user_hash()
    candidates = Candidate.query.all()
    
    # Check which candidates this user has already voted for
    user_votes = {}
    if user_hash:
        votes = Vote.query.filter_by(user_hash=user_hash).all()
        user_votes = {v.candidate_id: v.score for v in votes}

    resp = make_response(render_template('index.html', candidates=candidates, user_votes=user_votes))
    
    if not user_hash:
        new_hash = str(uuid.uuid4())
        resp.set_cookie('user_hash', new_hash, max_age=60*60*24*365) # 1 year
    
    return resp

@app.route('/vote', methods=['POST'])
def vote():
    user_hash = get_user_hash()
    
    # If no cookie, the user is technically new, but the browser should have sent one if we set it on index.
    # If they posted directly without visiting index, we might want to handle that, but let's assume normal flow.
    if not user_hash:
        # Generate one now, but they lose previous context.
        # Ideally, the frontend should ensure the cookie exists or flow starts at index.
        # For simplicity, if no hash, we reject or set one. 
        # But we can't set cookie on a JSON response easily if frontend doesn't reload.
        # Let's rely on index setting it.
        return jsonify({'error': 'No user identity found. Please reload pages.'}), 400

    data = request.json
    candidate_id = data.get('candidate_id')
    score = data.get('score')

    if not candidate_id or not score:
        return jsonify({'error': 'Missing data'}), 400
    
    try:
        score = int(score)
        if score < 1 or score > 5:
            return jsonify({'error': 'Invalid score'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid score'}), 400

    # Check if already voted
    existing_vote = Vote.query.filter_by(user_hash=user_hash, candidate_id=candidate_id).first()
    if existing_vote:
        return jsonify({'error': 'You have already voted for this person'}), 400

    new_vote = Vote(user_hash=user_hash, candidate_id=candidate_id, score=score)
    db.session.add(new_vote)
    db.session.commit()

    return jsonify({'success': True})

@app.route('/results')
def results():
    # Aggregate results
    # We want: Candidate Name, Total Score, Count, Average
    candidates = Candidate.query.all()
    results_data = []

    for cand in candidates:
        votes = Vote.query.filter_by(candidate_id=cand.id).all()
        total = sum(v.score for v in votes)
        count = len(votes)
        average = round(total / count, 1) if count > 0 else 0
        results_data.append({
            'name': cand.name,
            'total': total,
            'count': count,
            'average': average
        })

    # Sort by total score descending
    results_data.sort(key=lambda x: x['total'], reverse=True)

    return render_template('results.html', results=results_data)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin/reset', methods=['POST'])
def admin_reset():
    try:
        db.session.query(Vote).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {e}", 500
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
