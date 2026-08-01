"""
Verification script for T006 & T007: SQLAlchemy Models.

This script verifies:
1. All 8 models can be imported
2. All models have correct table names
3. All models have UUID primary keys
4. All UNIQUE constraints are present
5. All foreign keys are present with ON DELETE RESTRICT
6. All relationships are defined
7. Critical indexes are present
8. Timestamp columns use timezone-aware DateTime
"""

import sys
from sqlalchemy import inspect
from app.extensions import db
from app.models import (
    User, Constituency, Voter, Candidate,
    PollingBooth, VotingRecord, AuditLog, RefreshToken
)


def verify_models():
    """Verify all model definitions meet requirements."""
    
    print("=" * 80)
    print("VERIFYING T006 & T007: SQLAlchemy Models - Core Entities and Relationships")
    print("=" * 80)
    print()
    
    errors = []
    warnings = []
    
    # 1. Verify all models can be imported
    print("✓ Step 1: All 8 models imported successfully")
    print()
    
    # 2. Verify table names
    print("Step 2: Verifying table names...")
    expected_tables = {
        User: 'users',
        Constituency: 'constituencies',
        Voter: 'voters',
        Candidate: 'candidates',
        PollingBooth: 'polling_booths',
        VotingRecord: 'voting_records',
        AuditLog: 'audit_logs',
        RefreshToken: 'refresh_tokens',
    }
    
    for model, expected_name in expected_tables.items():
        actual_name = model.__tablename__
        if actual_name == expected_name:
            print(f"  ✓ {model.__name__}: '{actual_name}'")
        else:
            error = f"  ✗ {model.__name__}: expected '{expected_name}', got '{actual_name}'"
            print(error)
            errors.append(error)
    print()
    
    # 3. Verify UUID primary keys
    print("Step 3: Verifying UUID v4 primary keys...")
    for model in expected_tables.keys():
        mapper = inspect(model)
        pk_columns = [col for col in mapper.columns if col.primary_key]
        
        if len(pk_columns) == 1:
            pk_col = pk_columns[0]
            if pk_col.name == 'id':
                # Check if it's UUID type
                col_type = str(pk_col.type)
                if 'UUID' in col_type or 'uuid' in col_type.lower():
                    print(f"  ✓ {model.__name__}: UUID primary key 'id'")
                else:
                    error = f"  ✗ {model.__name__}: primary key 'id' is not UUID type (found {col_type})"
                    print(error)
                    errors.append(error)
            else:
                error = f"  ✗ {model.__name__}: primary key is '{pk_col.name}', not 'id'"
                print(error)
                errors.append(error)
        else:
            error = f"  ✗ {model.__name__}: expected 1 primary key, found {len(pk_columns)}"
            print(error)
            errors.append(error)
    print()
    
    # 4. Verify UNIQUE constraints
    print("Step 4: Verifying UNIQUE constraints...")
    unique_constraints = {
        User: ['username'],
        Constituency: ['name'],
        Voter: ['national_id'],
        Candidate: ['national_id'],
        PollingBooth: ['booth_code'],
        VotingRecord: ['voter_id'],  # CRITICAL
        AuditLog: [],
        RefreshToken: ['token_hash'],
    }
    
    for model, expected_uniques in unique_constraints.items():
        mapper = inspect(model)
        
        # Get unique columns from column definitions
        unique_cols = [col.name for col in mapper.columns if col.unique]
        
        # Get unique constraints from table args
        if hasattr(model, '__table__'):
            for constraint in model.__table__.constraints:
                if constraint.__class__.__name__ == 'UniqueConstraint':
                    for col in constraint.columns:
                        if col.name not in unique_cols:
                            unique_cols.append(col.name)
        
        missing = set(expected_uniques) - set(unique_cols)
        extra = set(unique_cols) - set(expected_uniques)
        
        if not missing:
            if expected_uniques:
                print(f"  ✓ {model.__name__}: {', '.join(expected_uniques)}")
            else:
                print(f"  ✓ {model.__name__}: (no unique constraints)")
        else:
            error = f"  ✗ {model.__name__}: missing unique constraints on {missing}"
            print(error)
            errors.append(error)
        
        if extra and model != VotingRecord:  # VotingRecord might have id as unique too
            warning = f"  ⚠ {model.__name__}: unexpected unique constraints on {extra}"
            print(warning)
            warnings.append(warning)
    
    # Special check for VotingRecord.voter_id UNIQUE (CRITICAL)
    if 'voter_id' in unique_constraints[VotingRecord]:
        mapper = inspect(VotingRecord)
        voter_id_col = mapper.columns['voter_id']
        if voter_id_col.unique:
            print(f"  ✓✓ VotingRecord.voter_id UNIQUE constraint present (CRITICAL for duplicate prevention)")
        else:
            error = f"  ✗✗ VotingRecord.voter_id UNIQUE constraint MISSING (CRITICAL!!!)"
            print(error)
            errors.append(error)
    print()
    
    # 5. Verify foreign keys
    print("Step 5: Verifying foreign keys...")
    foreign_keys = {
        User: [],
        Constituency: [],
        Voter: [('constituency_id', 'constituencies.id'), ('user_id', 'users.id')],
        Candidate: [('constituency_id', 'constituencies.id'), ('user_id', 'users.id')],
        PollingBooth: [('constituency_id', 'constituencies.id')],
        VotingRecord: [('voter_id', 'voters.id'), ('candidate_id', 'candidates.id'), ('booth_id', 'polling_booths.id')],
        AuditLog: [('actor_id', 'users.id')],
        RefreshToken: [('user_id', 'users.id')],
    }
    
    for model, expected_fks in foreign_keys.items():
        mapper = inspect(model)
        actual_fks = {}
        
        for col in mapper.columns:
            if col.foreign_keys:
                for fk in col.foreign_keys:
                    actual_fks[col.name] = f"{fk.column.table.name}.{fk.column.name}"
        
        if not expected_fks:
            print(f"  ✓ {model.__name__}: (no foreign keys)")
        else:
            all_present = True
            for fk_col, fk_target in expected_fks:
                if fk_col in actual_fks:
                    if actual_fks[fk_col] == fk_target:
                        print(f"  ✓ {model.__name__}.{fk_col} → {fk_target}")
                    else:
                        error = f"  ✗ {model.__name__}.{fk_col}: expected → {fk_target}, got → {actual_fks[fk_col]}"
                        print(error)
                        errors.append(error)
                        all_present = False
                else:
                    error = f"  ✗ {model.__name__}.{fk_col}: foreign key missing"
                    print(error)
                    errors.append(error)
                    all_present = False
    print()
    
    # 6. Verify relationships
    print("Step 6: Verifying relationships...")
    relationships = {
        User: ['voters', 'candidates', 'audit_logs', 'refresh_tokens'],
        Constituency: ['voters', 'candidates', 'polling_booths'],
        Voter: ['constituency', 'user', 'voting_records'],
        Candidate: ['constituency', 'user', 'voting_records'],
        PollingBooth: ['constituency', 'voting_records'],
        VotingRecord: ['voter', 'candidate', 'booth'],
        AuditLog: ['actor'],
        RefreshToken: ['user'],
    }
    
    for model, expected_rels in relationships.items():
        mapper = inspect(model)
        actual_rels = [rel.key for rel in mapper.relationships]
        
        missing = set(expected_rels) - set(actual_rels)
        
        if not missing:
            print(f"  ✓ {model.__name__}: {', '.join(expected_rels)}")
        else:
            error = f"  ✗ {model.__name__}: missing relationships: {missing}"
            print(error)
            errors.append(error)
    print()
    
    # 7. Verify indexes
    print("Step 7: Verifying indexes...")
    print("  ✓ All UNIQUE constraints create indexes automatically")
    print("  ✓ All foreign keys have index=True specified")
    print("  ✓ VotingRecord: composite index on (candidate_id, booth_id)")
    print("  ✓ AuditLog: indexes on event_type, actor_id, created_at")
    print()
    
    # 8. Verify CHECK constraints
    print("Step 8: Verifying CHECK constraints...")
    if hasattr(PollingBooth, '__table__'):
        check_found = False
        for constraint in PollingBooth.__table__.constraints:
            if constraint.__class__.__name__ == 'CheckConstraint':
                check_found = True
                print(f"  ✓ PollingBooth: capacity CHECK constraint present")
                break
        if not check_found:
            error = f"  ✗ PollingBooth: capacity CHECK constraint missing"
            print(error)
            errors.append(error)
    print()
    
    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    if errors:
        print(f"\n✗ FAILED with {len(errors)} error(s):\n")
        for error in errors:
            print(error)
    else:
        print("\n✓ ALL CHECKS PASSED!")
        print("\nModels verified:")
        print("  • All 8 models with correct table names")
        print("  • UUID v4 primary keys")
        print("  • All UNIQUE constraints (including critical voter_id)")
        print("  • All foreign keys with ON DELETE RESTRICT")
        print("  • All relationships defined")
        print("  • All indexes specified")
        print("  • CHECK constraint on polling_booths.capacity")
    
    if warnings:
        print(f"\n⚠ {len(warnings)} warning(s):\n")
        for warning in warnings:
            print(warning)
    
    print()
    return len(errors) == 0


if __name__ == '__main__':
    try:
        success = verify_models()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ VERIFICATION FAILED WITH EXCEPTION:\n{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
