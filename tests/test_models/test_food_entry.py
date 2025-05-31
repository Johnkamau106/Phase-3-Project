import pytest
from datetime import date
from health_simplified.models.food_entry_model import FoodEntry
from health_simplified.models.user_model import User

def test_create_food_entry(test_db):
    user = User.create(test_db, name="Test User")
    entry = FoodEntry.create(
        test_db,
        user_id=user.id,
        food="Apple",
        calories=95
    )
    
    assert entry.id is not None
    assert entry.food == "Apple"
    assert entry.calories == 95
    assert entry.date == date.today()

def test_calorie_validation(test_db):
    user = User.create(test_db, name="Test User")
    with pytest.raises(ValueError, match="positive integer"):
        FoodEntry.create(test_db, user.id, "Oil", -100)
        