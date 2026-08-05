"""
Election results aggregation service providing candidate totals and constituency tallies.
"""

import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.voting_record_repository import VotingRecordRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.constituency_repository import ConstituencyRepository


class ResultsService:
    """Business service for compiling election results and tallies."""

    def __init__(
        self,
        session: Session,
        voting_record_repo: VotingRecordRepository,
        candidate_repo: CandidateRepository,
        constituency_repo: ConstituencyRepository
    ):
        self.session = session
        self.voting_record_repo = voting_record_repo
        self.candidate_repo = candidate_repo
        self.constituency_repo = constituency_repo

    def get_candidate_vote_count(self, candidate_id: uuid.UUID) -> int:
        """Get total vote tally for a given candidate."""
        return self.voting_record_repo.get_vote_count_by_candidate(candidate_id)

    def get_constituency_results(self, constituency_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get total candidate vote tallies for a constituency with details."""
        constituency = self.constituency_repo.get_by_id(constituency_id)
        if not constituency:
            raise ValueError(f"Constituency '{constituency_id}' not found")

        raw_results = self.voting_record_repo.get_voting_results_by_constituency(constituency_id)
        candidates = self.candidate_repo.get_by_constituency(constituency_id)

        results_map = {res['candidate_id']: res['vote_count'] for res in raw_results}

        output = []
        for cand in candidates:
            cand_id_str = str(cand.id)
            output.append({
                'candidate_id': cand_id_str,
                'candidate_name': cand.full_name,
                'party': cand.party,
                'vote_count': results_map.get(cand_id_str, 0)
            })

        output.sort(key=lambda x: x['vote_count'], reverse=True)
        return output

    def get_overall_turnout(self) -> Dict[str, Any]:
        """Calculate overall voting turnout and total vote stats."""
        return self.voting_record_repo.get_voting_stats()
