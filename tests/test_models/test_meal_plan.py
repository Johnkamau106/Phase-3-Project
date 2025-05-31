import pytest
from health_simplified.models.meal_plan_model import MealPlan
from health_simplified.models.user_model import User


def test_meal_plan_creation(test_db):
    """Test basic meal plan creation"""
    user = User.create(test_db, name="Test User")
    plan = MealPlan.create(
        test_db,
        user_id=user.id,
        week_number=25,
        plan_details="Test plan details"
    )
    
    assert plan.id is not None
    assert plan.week_number == 25
    assert plan.plan_details == "Test plan details"
    assert plan.user_id == user.id

def test_week_number_validation(test_db):
    """Test week number validation"""
    user = User.create(test_db, name="Test User")
    
    # Test valid week numbers
    for week in [1, 52]:
        plan = MealPlan.create(test_db, user.id, week, "Valid")
        assert plan.week_number == week
    
    # Test invalid week numbers
    with pytest.raises(ValueError, match="Week number must be 1-52"):
        MealPlan.create(test_db, user.id, 0, "Invalid")
    
    with pytest.raises(ValueError, match="Week number must be 1-52"):
        MealPlan.create(test_db, user.id, 53, "Invalid")

def test_meal_plan_update(test_db):
    """Test meal plan updates"""
    user = User.create(test_db, name="Test User")
    plan = MealPlan.create(test_db, user.id, 25, "Original plan")
    
    # Update week number
    updated = MealPlan.update(test_db, plan.id, week_number=26)
    assert updated.week_number == 26
    
    # Update details
    updated = MealPlan.update(test_db, plan.id, plan_details="Updated details")
    assert updated.plan_details == "Updated details"
    
    # Test partial updates
    updated = MealPlan.update(test_db, plan.id, week_number=27, plan_details="Final update")
    assert updated.week_number == 27
    assert updated.plan_details == "Final update"

def test_get_by_week(test_db):
    """Test retrieval by week number"""
    user = User.create(test_db, name="Test User")
    MealPlan.create(test_db, user.id, 25, "Week 25 plan")
    
    # Test found
    plan = MealPlan.get_by_week(test_db, user.id, 25)
    assert plan.plan_details == "Week 25 plan"
    
    # Test not found
    assert MealPlan.get_by_week(test_db, user.id, 26) is None
    