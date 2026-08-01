"""
Database seeding script for Election Operations Platform.

This script populates the database with test data for development and testing:
- Constituencies
- User accounts (admin, election officers, polling officers)
- Polling booths
- Voters
- Candidates

The script is idempotent - it checks if data exists before creating it,
so it can be run multiple times safely.

Default Credentials:
    Admin:
        username: admin
        password: admin123
        role: Admin
    
    Election Officers:
        username: officer1, officer2
        password: officer123
        role: Election_Officer
    
    Polling Officers:
        username: polling1, polling2, polling3
        password: polling123
        role: Polling_Officer

Usage:
    python scripts/seed_data.py
"""

import sys
import uuid
from datetime import date

import bcrypt

# Add parent directory to path
sys.path.insert(0, '.')

from app import create_app
from app.extensions import db
from app.models import (
    User,
    Constituency,
    Voter,
    Candidate,
    PollingBooth,
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with cost factor 12.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Bcrypt hash as string
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def seed_constituencies(session):
    """
    Create 3 constituencies if they don't exist.
    
    Returns:
        Dict mapping constituency name to Constituency object
    """
    print("\nCreating constituencies...")
    
    constituencies_data = [
        {'name': 'Northern Region', 'region': 'North'},
        {'name': 'Central Region', 'region': 'Central'},
        {'name': 'Southern Region', 'region': 'South'},
    ]
    
    constituencies = {}
    for data in constituencies_data:
        # Check if constituency exists
        existing = session.query(Constituency).filter_by(name=data['name']).first()
        if existing:
            constituencies[data['name']] = existing
        else:
            constituency = Constituency(
                id=uuid.uuid4(),
                name=data['name'],
                region=data['region']
            )
            session.add(constituency)
            constituencies[data['name']] = constituency
    
    session.flush()  # Flush to get IDs without committing
    print(f"✓ Created {len(constituencies)} constituencies")
    return constituencies


def seed_users(session):
    """
    Create admin, election officers, and polling officers if they don't exist.
    
    Returns:
        Dict mapping username to User object
    """
    print("\nCreating users...")
    
    users_data = [
        {'username': 'admin', 'password': 'admin123', 'role': 'Admin'},
        {'username': 'officer1', 'password': 'officer123', 'role': 'Election_Officer'},
        {'username': 'officer2', 'password': 'officer123', 'role': 'Election_Officer'},
        {'username': 'polling1', 'password': 'polling123', 'role': 'Polling_Officer'},
        {'username': 'polling2', 'password': 'polling123', 'role': 'Polling_Officer'},
        {'username': 'polling3', 'password': 'polling123', 'role': 'Polling_Officer'},
    ]
    
    users = {}
    for data in users_data:
        # Check if user exists
        existing = session.query(User).filter_by(username=data['username']).first()
        if existing:
            users[data['username']] = existing
        else:
            user = User(
                id=uuid.uuid4(),
                username=data['username'],
                password_hash=hash_password(data['password']),
                role=data['role']
            )
            session.add(user)
            users[data['username']] = user
    
    session.flush()
    print(f"✓ Created {len(users)} users")
    return users


def seed_polling_booths(session, constituencies):
    """
    Create 6 polling booths (2 per constituency) if they don't exist.
    
    Args:
        constituencies: Dict of Constituency objects by name
        
    Returns:
        List of PollingBooth objects
    """
    print("\nCreating polling booths...")
    
    booths_data = [
        {'booth_code': 'NTH-001', 'location': 'Northern Community Center', 'capacity': 500, 'constituency': 'Northern Region'},
        {'booth_code': 'NTH-002', 'location': 'Northern High School', 'capacity': 750, 'constituency': 'Northern Region'},
        {'booth_code': 'CTR-001', 'location': 'Central Town Hall', 'capacity': 600, 'constituency': 'Central Region'},
        {'booth_code': 'CTR-002', 'location': 'Central Library', 'capacity': 400, 'constituency': 'Central Region'},
        {'booth_code': 'STH-001', 'location': 'Southern Sports Complex', 'capacity': 800, 'constituency': 'Southern Region'},
        {'booth_code': 'STH-002', 'location': 'Southern College', 'capacity': 550, 'constituency': 'Southern Region'},
    ]
    
    booths = []
    for data in booths_data:
        # Check if booth exists
        existing = session.query(PollingBooth).filter_by(booth_code=data['booth_code']).first()
        if existing:
            booths.append(existing)
        else:
            booth = PollingBooth(
                id=uuid.uuid4(),
                booth_code=data['booth_code'],
                location=data['location'],
                capacity=data['capacity'],
                constituency_id=constituencies[data['constituency']].id,
                status='CLOSED'
            )
            session.add(booth)
            booths.append(booth)
    
    session.flush()
    print(f"✓ Created {len(booths)} polling booths")
    return booths


def seed_voters(session, constituencies):
    """
    Create 15 voters (5 per constituency) if they don't exist.
    
    Args:
        constituencies: Dict of Constituency objects by name
        
    Returns:
        List of Voter objects
    """
    print("\nCreating voters...")
    
    voters_data = []
    
    # Northern Region voters (NID001-NID005)
    for i in range(1, 6):
        voters_data.append({
            'national_id': f'NID{i:03d}',
            'full_name': f'Northern Voter {i}',
            'dob': date(1990, 1, i),
            'constituency': 'Northern Region',
            'status': 'active'
        })
    
    # Central Region voters (NID006-NID010)
    for i in range(6, 11):
        voters_data.append({
            'national_id': f'NID{i:03d}',
            'full_name': f'Central Voter {i}',
            'dob': date(1985, 6, i - 5),
            'constituency': 'Central Region',
            'status': 'active'
        })
    
    # Southern Region voters (NID011-NID015)
    for i in range(11, 16):
        voters_data.append({
            'national_id': f'NID{i:03d}',
            'full_name': f'Southern Voter {i}',
            'dob': date(1995, 12, i - 10),
            'constituency': 'Southern Region',
            'status': 'active'
        })
    
    voters = []
    for data in voters_data:
        # Check if voter exists
        existing = session.query(Voter).filter_by(national_id=data['national_id']).first()
        if existing:
            voters.append(existing)
        else:
            voter = Voter(
                id=uuid.uuid4(),
                national_id=data['national_id'],
                full_name=data['full_name'],
                dob=data['dob'],
                constituency_id=constituencies[data['constituency']].id,
                status=data['status']
            )
            session.add(voter)
            voters.append(voter)
    
    session.flush()
    print(f"✓ Created {len(voters)} voters")
    return voters


def seed_candidates(session, constituencies):
    """
    Create 9 candidates (3 per constituency) if they don't exist.
    
    Args:
        constituencies: Dict of Constituency objects by name
        
    Returns:
        List of Candidate objects
    """
    print("\nCreating candidates...")
    
    candidates_data = [
        # Northern Region candidates
        {'national_id': 'CND001', 'full_name': 'Alice Johnson', 'party': 'Progressive Party', 'constituency': 'Northern Region'},
        {'national_id': 'CND002', 'full_name': 'Bob Smith', 'party': 'Conservative Alliance', 'constituency': 'Northern Region'},
        {'national_id': 'CND003', 'full_name': 'Carol Davis', 'party': 'Independent', 'constituency': 'Northern Region'},
        
        # Central Region candidates
        {'national_id': 'CND004', 'full_name': 'David Wilson', 'party': 'Progressive Party', 'constituency': 'Central Region'},
        {'national_id': 'CND005', 'full_name': 'Emma Brown', 'party': 'Conservative Alliance', 'constituency': 'Central Region'},
        {'national_id': 'CND006', 'full_name': 'Frank Miller', 'party': 'Green Movement', 'constituency': 'Central Region'},
        
        # Southern Region candidates
        {'national_id': 'CND007', 'full_name': 'Grace Lee', 'party': 'Progressive Party', 'constituency': 'Southern Region'},
        {'national_id': 'CND008', 'full_name': 'Henry Taylor', 'party': 'Conservative Alliance', 'constituency': 'Southern Region'},
        {'national_id': 'CND009', 'full_name': 'Iris Anderson', 'party': 'People\'s Front', 'constituency': 'Southern Region'},
    ]
    
    candidates = []
    for data in candidates_data:
        # Check if candidate exists
        existing = session.query(Candidate).filter_by(national_id=data['national_id']).first()
        if existing:
            candidates.append(existing)
        else:
            candidate = Candidate(
                id=uuid.uuid4(),
                national_id=data['national_id'],
                full_name=data['full_name'],
                party=data['party'],
                constituency_id=constituencies[data['constituency']].id
            )
            session.add(candidate)
            candidates.append(candidate)
    
    session.flush()
    print(f"✓ Created {len(candidates)} candidates")
    return candidates


def verify_phase_1(session):
    """
    Verify that all Phase 1 data was created successfully.
    
    This is the single integrated verification step as per T010 requirements.
    """
    print("\n" + "=" * 70)
    print("PHASE 1 VERIFICATION")
    print("=" * 70)
    
    # Check table counts
    user_count = session.query(User).count()
    constituency_count = session.query(Constituency).count()
    voter_count = session.query(Voter).count()
    candidate_count = session.query(Candidate).count()
    booth_count = session.query(PollingBooth).count()
    
    print(f"✓ Users: {user_count}")
    print(f"✓ Constituencies: {constituency_count}")
    print(f"✓ Voters: {voter_count}")
    print(f"✓ Candidates: {candidate_count}")
    print(f"✓ Polling Booths: {booth_count}")
    print("\n✓ Phase 1 Complete - Database ready for Phase 2")
    print("=" * 70)


def main():
    """Main seeding function."""
    print("=" * 70)
    print("Election Operations Platform - Database Seeding")
    print("=" * 70)
    
    # Create Flask app and get database session
    app = create_app()
    
    with app.app_context():
        try:
            # Seed all data
            constituencies = seed_constituencies(db.session)
            users = seed_users(db.session)
            booths = seed_polling_booths(db.session, constituencies)
            voters = seed_voters(db.session, constituencies)
            candidates = seed_candidates(db.session, constituencies)
            
            # Commit all changes
            print("\nCommitting changes to database...")
            db.session.commit()
            print("✓ All changes committed successfully")
            
            # Verify Phase 1 completion
            verify_phase_1(db.session)
            
        except Exception as e:
            print(f"\n✗ Error during seeding: {e}")
            db.session.rollback()
            print("✗ Changes rolled back")
            raise


if __name__ == '__main__':
    main()
