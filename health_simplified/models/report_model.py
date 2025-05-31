from datetime import date as dt_date
from sqlalchemy import func
from sqlalchemy.orm import Session
from health_simplified.models.food_entry_model import FoodEntry
from health_simplified.models.goal_model import Goal
from health_simplified.models.user_model import User



class ReportService:
    @staticmethod
    def generate_daily_report(db: Session, user_id: int, report_date: dt_date = None):
        if report_date is None:
            report_date = dt_date.today()
        elif not isinstance(report_date, dt_date):
            raise ValueError("report_date must be a datetime.date instance")

        # Verify user exists
        if not db.query(User).filter(User.id == user_id).first():
            raise ValueError("User not found")

        # Get goals
        goal = db.query(Goal).filter(Goal.user_id == user_id).first()
        daily_goal = goal.daily_calories if goal else None

        # Calculate totals
        total_calories = db.query(func.sum(FoodEntry.calories)).filter(
            FoodEntry.user_id == user_id,
            FoodEntry.date == report_date
        ).scalar() or 0

        # Get entries
        entries = db.query(FoodEntry).filter(
            FoodEntry.user_id == user_id,
            FoodEntry.date == report_date
        ).all()

        return {
            "date": report_date.isoformat(),
            "daily_goal": daily_goal,
            "total_calories": total_calories,
            "calorie_diff": (daily_goal - total_calories) if daily_goal else None,
            "entries": entries,
            "on_track": daily_goal is not None and total_calories <= daily_goal
        }
