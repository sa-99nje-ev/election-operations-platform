"""
Factory Boy definitions for core domain models.
Generates valid ORM objects automatically matching real model fields.
"""

import factory
import uuid
from app.models.polling_booth import PollingBooth
from app.models.voting_record import VotingRecord


class PollingBoothFactory(factory.Factory):
    class Meta:
        model = PollingBooth

    id = factory.LazyFunction(uuid.uuid4)
    booth_code = factory.Sequence(lambda n: f"BOOTH-{n:04d}")
    location = "Zone A - Central Station"
    capacity = 1000  # Added missing required non-null field
    status = "OPEN"
    constituency_id = factory.LazyFunction(uuid.uuid4)


class VotingRecordFactory(factory.Factory):
    class Meta:
        model = VotingRecord

    id = factory.LazyFunction(uuid.uuid4)
    voter_id = factory.LazyFunction(uuid.uuid4)
    candidate_id = factory.LazyFunction(uuid.uuid4)
    booth_id = factory.LazyFunction(uuid.uuid4)