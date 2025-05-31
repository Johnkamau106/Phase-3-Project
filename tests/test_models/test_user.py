import pytest
from health_simplified.models.user_model import User


def test_user_creation(test_db):
    """Test basic user creation"""
    user = User.create(test_db, name="Test User")
    assert user.id is not None
    assert user.name == "Test User"
    assert len(user.entries) == 0

def test_user_name_uniqueness(test_db):
    """Test duplicate user names are rejected"""
    User.create(test_db, name="Unique User")
    with pytest.raises(ValueError, match="already exists"):
        User.create(test_db, name="Unique User")

def test_user_name_validation(test_db):
    """Test name length validation"""
    with pytest.raises(ValueError, match="1-50 characters"):
        User.create(test_db, name="")
    with pytest.raises(ValueError, match="1-50 characters"):
        User.create(test_db, name="A" * 51)

def test_user_deletion(test_db):
    """Test user deletion"""
    user = User.create(test_db, name="To Delete")
    assert User.delete(test_db, user.id) is True
    assert User.get_by_id(test_db, user.id) is None

def test_user_get_methods(test_db):
    """Test user retrieval methods"""
    user = User.create(test_db, name="Test User")
    
    # Test get_by_id
    fetched = User.get_by_id(test_db, user.id)
    assert fetched.name == "Test User"
    
    # Test get_by_name
    fetched = User.get_by_name(test_db, "Test User")
    assert fetched.id == user.id
    
    # Test get_all
    users = User.get_all(test_db)
    assert len(users) == 1
    assert users[0].name == "Test User"
    