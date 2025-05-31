import pytest
from datetime import date, timedelta
from health_simplified.models.report_model import ReportService as Report
from health_simplified.models.food_entry_model import FoodEntry
from health_simplified.models.goal_model import Goal
from health_simplified.models.user_model import User


@pytest.fixture
def setup_report_data(test_db):
    """Fixture to set up test data for reports"""
    # Create test user
    user = User.create(test_db, name="Test User")
    
    # Set goals
    goal = Goal.create_or_update(test_db, user.id, 2000, 14000)
    
    # Create food entries
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    entries = [
        FoodEntry.create(test_db, user.id, "Breakfast", 400, today),
        FoodEntry.create(test_db, user.id, "Lunch", 600, today),
        FoodEntry.create(test_db, user.id, "Dinner", 800, today),
        FoodEntry.create(test_db, user.id, "Snack", 200, yesterday)
    ]
    
    return {
        "db": test_db,
        "user": user,
        "goal": goal,
        "entries": entries,
        "today": today,
        "yesterday": yesterday
    }

def test_daily_report_with_goal(setup_report_data):
    """Test daily report with goals set"""
    data = setup_report_data
    report = Report.generate_daily_report(data["db"], data["user"].id, data["today"])
    
    assert report["date"] == data["today"].isoformat()
    assert report["daily_goal"] == 2000
    assert report["total_calories"] == 1800  # 400 + 600 + 800
    assert report["calorie_diff"] == 200
    assert report["on_track"] is True
    assert len(report["entries"]) == 3

def test_daily_report_no_goal(test_db):
    """Test daily report when no goals are set"""
    user = User.create(test_db, name="No Goal User")
    FoodEntry.create(test_db, user.id, "Meal", 500)
    
    report = Report.generate_daily_report(test_db, user.id)
    
    assert report["daily_goal"] is None
    assert report["total_calories"] == 500
    assert report["calorie_diff"] is None
    assert report["on_track"] is False

def test_daily_report_no_entries(setup_report_data):
    """Test daily report with no food entries"""
    data = setup_report_data
    # Test a date with no entries
    future_date = data["today"] + timedelta(days=5)
    report = Report.generate_daily_report(data["db"], data["user"].id, future_date)
    
    assert report["total_calories"] == 0
    assert report["on_track"] is True  # 0 <= goal

def test_daily_report_exceeds_goal(setup_report_data):
    """Test report when calories exceed goal"""
    data = setup_report_data
    # Add extra entry to exceed goal
    FoodEntry.create(data["db"], data["user"].id, "Dessert", 500, data["today"])
    
    report = Report.generate_daily_report(data["db"], data["user"].id, data["today"])
    
    assert report["total_calories"] == 2300  # 1800 + 500
    assert report["calorie_diff"] == -300
    assert report["on_track"] is False

def test_daily_report_invalid_user(test_db):
    """Test report with invalid user ID"""
    with pytest.raises(ValueError, match="User not found"):
        Report.generate_daily_report(test_db, 999)  # Non-existent user ID

def test_daily_report_invalid_date(setup_report_data):
    """Test report with invalid date format"""
    data = setup_report_data
    with pytest.raises(ValueError):
        # Using incorrect date string format
        Report.generate_daily_report(data["db"], data["user"].id, "2023/05/01")

def test_report_class_methods():
    """Test Report class method availability"""
    assert hasattr(Report, 'generate_daily_report')
    assert callable(Report.generate_daily_report)
