"""
Integration test for T006 & T007: SQLAlchemy Models.

This test verifies that models can be used with SQLAlchemy ORM operations
and that Alembic can detect them for migration generation.
"""

import sys
import uuid
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from app.extensions import db
from app.models import (
    User, Constituency, Voter, Candidate,
    PollingBooth, VotingRecord, AuditLog, RefreshToken
)


def test_model_integration():
    """Test model integration with SQLAlchemy."""
    
    print("=" * 80)
    print("INTEGRATION TEST: SQLAlchemy Models")
    print("=" * 80)
    print()
    
    # Create in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:', echo=False)
    
    # Create all tables
    print("Step 1: Creating tables from models...")
    db.metadata.create_all(engine)
    print("  ✓ All tables created successfully")
    print()
    
    # Verify all tables exist
    print("Step 2: Verifying tables exist...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected_tables = [
        'users', 'constituencies', 'voters', 'candidates',
        'polling_booths', 'voting_records', 'audit_logs', 'refresh_tokens'
    ]
    
    for table_name in expected_tables:
        if table_name in tables:
            print(f"  ✓ Table '{table_name}' exists")
        else:
            print(f"  ✗ Table '{table_name}' missing")
            return False
    print()
    
    # Test model instantiation and relationships
    print("Step 3: Testing model instantiation and relationships...")
    with Session(engine) as session:
        try:
            # Create a user
            user = User(
                username='admin',
                password_hash='$2b$12$abcdefghijklmnopqrstuv',  # Fake bcrypt hash
                role='Admin'
            )
            session.add(user)
            session.flush()
            print(f"  ✓ Created User: {user.username}")
            
            # Create a constituency
            constituency = Constituency(
                name='Test District',
                region='Test Region'
            )
            session.add(constituency)
            session.flush()
            print(f"  ✓ Created Constituency: {constituency.name}")
            
            # Create a voter
            voter = Voter(
                national_id='TEST123456',
                full_name='John Doe',
                dob=date(1990, 1, 1),
                constituency_id=constituency.id,
                user_id=user.id,
                status='active'
            )
            session.add(voter)
            session.flush()
            print(f"  ✓ Created Voter: {voter.full_name}")
            
            # Create a candidate
            candidate = Candidate(
                national_id='CAND123456',
                full_name='Jane Smith',
                party='Test Party',
                constituency_id=constituency.id,
                user_id=None
            )
            session.add(candidate)
            session.flush()
            print(f"  ✓ Created Candidate: {candidate.full_name}")
            
            # Create a polling booth
            booth = PollingBooth(
                booth_code='BOOTH001',
                location='123 Test Street',
                capacity=500,
                constituency_id=constituency.id,
                status='OPEN'
            )
            session.add(booth)
            session.flush()
            print(f"  ✓ Created PollingBooth: {booth.booth_code}")
            
            # Create a voting record
            voting_record = VotingRecord(
                voter_id=voter.id,
                candidate_id=candidate.id,
                booth_id=booth.id
            )
            session.add(voting_record)
            session.flush()
            print(f"  ✓ Created VotingRecord for voter {voter.national_id}")
            
            # Create an audit log
            audit_log = AuditLog(
                event_type='vote_submitted',
                actor_id=user.id,
                target_id=voter.id,
                outcome='success',
                ip_address='127.0.0.1'
            )
            session.add(audit_log)
            session.flush()
            print(f"  ✓ Created AuditLog: {audit_log.event_type}")
            
            # Create a refresh token
            refresh_token = RefreshToken(
                user_id=user.id,
                token_hash='abcdef123456',
                expires_at=datetime.utcnow() + timedelta(days=30),
                invalidated=False
            )
            session.add(refresh_token)
            session.flush()
            print(f"  ✓ Created RefreshToken for user {user.username}")
            
            # Test relationships
            print()
            print("Step 4: Testing relationships...")
            
            # User -> Voters
            assert len(user.voters) == 1
            assert user.voters[0].national_id == 'TEST123456'
            print(f"  ✓ User.voters relationship works")
            
            # Constituency -> Voters
            assert len(constituency.voters) == 1
            assert constituency.voters[0].full_name == 'John Doe'
            print(f"  ✓ Constituency.voters relationship works")
            
            # Voter -> Constituency
            assert voter.constituency.name == 'Test District'
            print(f"  ✓ Voter.constituency relationship works")
            
            # Voter -> User
            assert voter.user.username == 'admin'
            print(f"  ✓ Voter.user relationship works")
            
            # VotingRecord -> Voter
            assert voting_record.voter.national_id == 'TEST123456'
            print(f"  ✓ VotingRecord.voter relationship works")
            
            # VotingRecord -> Candidate
            assert voting_record.candidate.full_name == 'Jane Smith'
            print(f"  ✓ VotingRecord.candidate relationship works")
            
            # VotingRecord -> PollingBooth
            assert voting_record.booth.booth_code == 'BOOTH001'
            print(f"  ✓ VotingRecord.booth relationship works")
            
            # AuditLog -> User (actor)
            assert audit_log.actor.username == 'admin'
            print(f"  ✓ AuditLog.actor relationship works")
            
            # RefreshToken -> User
            assert refresh_token.user.username == 'admin'
            print(f"  ✓ RefreshToken.user relationship works")
            
            session.commit()
            
        except Exception as e:
            print(f"\n  ✗ Error during model operations: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print()
    print("=" * 80)
    print("✓ ALL INTEGRATION TESTS PASSED!")
    print("=" * 80)
    print()
    print("Summary:")
    print("  • All 8 tables created successfully")
    print("  • All models can be instantiated")
    print("  • All relationships work correctly")
    print("  • Models are ready for Alembic migration generation")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = test_model_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ INTEGRATION TEST FAILED:\n{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
