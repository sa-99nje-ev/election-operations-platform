# Database Optimization and Maintenance Guide

## 1. Connection Pool Configuration
SQLAlchemy engine pool settings are tuned in `app/config/settings.py` for high-concurrency production workloads:

- **`pool_size`**: `10` persistent connections per process.
- **`max_overflow`**: `20` additional burst connections during traffic spikes.
- **`pool_recycle`**: `3600` seconds (1 hour) to recycle stale PostgreSQL connections.
- **`pool_pre_ping`**: `True` to detect and drop disconnected socket connections prior to executing queries.

## 2. PostgreSQL Index Strategy
To optimize response times under load, the following composite indexes are enforced:

1. **`idx_candidates_constituency_party`**: Optimizes party-filtered candidate lookups within an electoral district.
2. **`idx_voters_constituency_status`**: Speeds up active voter eligibility verifications.
3. **`idx_polling_booths_constituency_status`**: Accelerates queries checking for open voting booths in a district.
4. **`idx_voting_records_booth_candidate`**: Optimizes vote tally aggregation per polling station.

## 3. Recommended Vacuum and Maintenance Routines
Execute regular PostgreSQL vacuuming and statistical analysis during low-traffic periods to maintain query planner performance:

```sql
-- Analyze table statistics for query planner optimization
ANALYZE candidates;
ANALYZE voters;
ANALYZE polling_booths;
ANALYZE voting_records;

-- Vacuum dead tuples on high-write append-only tables
VACUUM VERBOSE ANALYZE voting_records;
VACUUM VERBOSE ANALYZE audit_logs;