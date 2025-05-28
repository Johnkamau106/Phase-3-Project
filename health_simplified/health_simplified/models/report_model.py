from datetime import date
from sqlalchemy import func
from ..database import db

class Report:
    @classmethod
    def generate_daily_report(cls, db, user_id, report_date=None):
        report_date = report_date or date.today()
        
        # Get user's daily goal
        goal = db.query(Goal).filter(Goal.user_id == user_id).first()
        daily_goal = goal.daily_calories if goal else None
        
        # Calculate total calories consumed
        total_calories = db.query(func.sum(FoodEntry.calories)).filter(
            FoodEntry.user_id == user_id,
            FoodEntry.date == report_date
        ).scalar() or 0
        
        # Get all food entries for the day
        entries = db.query(FoodEntry).filter(
            FoodEntry.user_id == user_id,
            FoodEntry.date == report_date
        ).all()
        
        return {
            "date": report_date,
            "daily_goal": daily_goal,
            "total_calories": total_calories,
            "entries": entries,
            "on_track": daily_goal is not None and total_calories <= daily_goal
        }
    