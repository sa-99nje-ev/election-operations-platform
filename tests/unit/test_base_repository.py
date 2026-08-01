"""
Unit tests for BaseRepository.

These tests verify that the BaseRepository provides correct CRUD operations
using a mock SQLAlchemy session to avoid requiring an actual database connection.
"""

import pytest
from unittest.mock import MagicMock, Mock
from datetime import datetime
from app.repositories.base import BaseRepository


# Mock model class for testing
class MockModel:
    """Mock SQLAlchemy model for testing."""
    
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class MockModelWithSoftDelete:
    """Mock SQLAlchemy model with soft delete support."""
    
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
        self.deleted_at = None


@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session."""
    return MagicMock()


@pytest.fixture
def repository(mock_session):
    """Create a BaseRepository instance with MockModel."""
    return BaseRepository(MockModel, mock_session)


@pytest.fixture
def repository_with_soft_delete(mock_session):
    """Create a BaseRepository instance with soft delete support."""
    return BaseRepository(MockModelWithSoftDelete, mock_session)


class TestBaseRepositoryCreate:
    """Test suite for create() method."""
    
    def test_create_adds_entity_to_session(self, repository, mock_session):
        """Test that create adds entity to session."""
        entity = MockModel(id=1, name="Test Entity")
        
        result = repository.create(entity)
        
        mock_session.add.assert_called_once_with(entity)
        mock_session.flush.assert_called_once()
        assert result is entity
    
    def test_create_returns_entity_with_db_values(self, repository, mock_session):
        """Test that create returns entity after flush (allows DB-generated values)."""
        entity = MockModel(name="Test Entity")
        # Simulate database generating an ID after flush
        def set_id():
            entity.id = 42
        mock_session.flush.side_effect = set_id
        
        result = repository.create(entity)
        
        assert result.id == 42
        assert result.name == "Test Entity"


class TestBaseRepositoryGetById:
    """Test suite for get_by_id() method."""
    
    def test_get_by_id_returns_entity_when_found(self, repository, mock_session):
        """Test that get_by_id returns entity when it exists."""
        expected_entity = MockModel(id=1, name="Found Entity")
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = expected_entity
        
        result = repository.get_by_id(1)
        
        mock_session.query.assert_called_once_with(MockModel)
        assert result is expected_entity
    
    def test_get_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test that get_by_id returns None when entity doesn't exist."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None
        
        result = repository.get_by_id(999)
        
        assert result is None


class TestBaseRepositoryGetAll:
    """Test suite for get_all() method."""
    
    def test_get_all_returns_list_of_entities(self, repository, mock_session):
        """Test that get_all returns all entities."""
        expected_entities = [
            MockModel(id=1, name="Entity 1"),
            MockModel(id=2, name="Entity 2"),
            MockModel(id=3, name="Entity 3")
        ]
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = expected_entities
        
        result = repository.get_all()
        
        mock_session.query.assert_called_once_with(MockModel)
        assert result == expected_entities
        assert len(result) == 3
    
    def test_get_all_returns_empty_list_when_no_entities(self, repository, mock_session):
        """Test that get_all returns empty list when no entities exist."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = []
        
        result = repository.get_all()
        
        assert result == []
        assert len(result) == 0


class TestBaseRepositoryUpdate:
    """Test suite for update() method."""
    
    def test_update_merges_entity_and_flushes(self, repository, mock_session):
        """Test that update merges entity and flushes changes."""
        entity = MockModel(id=1, name="Updated Entity")
        merged_entity = MockModel(id=1, name="Updated Entity")
        mock_session.merge.return_value = merged_entity
        
        result = repository.update(entity)
        
        mock_session.merge.assert_called_once_with(entity)
        mock_session.flush.assert_called_once()
        assert result is merged_entity
    
    def test_update_handles_detached_entity(self, repository, mock_session):
        """Test that update correctly handles detached entities via merge."""
        detached_entity = MockModel(id=1, name="Detached Entity")
        merged_entity = MockModel(id=1, name="Detached Entity")
        mock_session.merge.return_value = merged_entity
        
        result = repository.update(detached_entity)
        
        # Merge should be called to handle detached state
        mock_session.merge.assert_called_once_with(detached_entity)
        assert result is merged_entity


class TestBaseRepositoryDelete:
    """Test suite for delete() method."""
    
    def test_delete_performs_hard_delete_when_no_soft_delete_support(self, repository, mock_session):
        """Test that delete performs hard delete when model has no deleted_at column."""
        entity = MockModel(id=1, name="To Delete")
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = entity
        
        result = repository.delete(1)
        
        mock_session.delete.assert_called_once_with(entity)
        mock_session.flush.assert_called_once()
        assert result is True
    
    def test_delete_performs_soft_delete_when_deleted_at_exists(self, repository_with_soft_delete, mock_session):
        """Test that delete performs soft delete when model has deleted_at column."""
        entity = MockModelWithSoftDelete(id=1, name="To Soft Delete")
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = entity
        
        result = repository_with_soft_delete.delete(1)
        
        # Should NOT call session.delete for soft delete
        mock_session.delete.assert_not_called()
        # Should set deleted_at timestamp
        assert entity.deleted_at is not None
        assert isinstance(entity.deleted_at, datetime)
        mock_session.flush.assert_called_once()
        assert result is True
    
    def test_delete_returns_false_when_entity_not_found(self, repository, mock_session):
        """Test that delete returns False when entity doesn't exist."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None
        
        result = repository.delete(999)
        
        mock_session.delete.assert_not_called()
        assert result is False


class TestBaseRepositoryDependencyInjection:
    """Test suite for dependency injection pattern."""
    
    def test_repository_accepts_session_in_constructor(self, mock_session):
        """Test that repository can be instantiated with injected session."""
        repository = BaseRepository(MockModel, mock_session)
        
        assert repository.session is mock_session
        assert repository.model_class is MockModel
    
    def test_repository_can_use_different_model_classes(self, mock_session):
        """Test that repository pattern works with different model classes."""
        class AnotherModel:
            pass
        
        repository1 = BaseRepository(MockModel, mock_session)
        repository2 = BaseRepository(AnotherModel, mock_session)
        
        assert repository1.model_class is MockModel
        assert repository2.model_class is AnotherModel
        assert repository1.session is repository2.session


class TestBaseRepositoryTypeHints:
    """Test suite verifying type hints work correctly."""
    
    def test_repository_generic_type_parameter(self, mock_session):
        """Test that repository uses Generic type parameter correctly."""
        repository = BaseRepository(MockModel, mock_session)
        entity = MockModel(id=1, name="Test")
        
        # This should work with type checkers due to Generic[T]
        created = repository.create(entity)
        assert isinstance(created, MockModel)
