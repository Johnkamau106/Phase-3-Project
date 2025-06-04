from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from health_simplified.db.database import Base

class MealPlan(Base):
    __tablename__ = "meal_plans"
    __table_args__ = (
        CheckConstraint('week_number BETWEEN 1 AND 52', name='check_week_number_range'),
        CheckConstraint('day_of_week BETWEEN 1 AND 7', name='check_day_of_week_range')
    )

    id = Column(Integer, primary_key=True, index=True)
    week_number = Column(Integer)
    day_of_week = Column(Integer)  # 1 = Monday, ..., 7 = Sunday
    plan_details = Column(String(2000))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="meal_plans")

    @classmethod
    def create(cls, db, user_id, week_number, day_of_week, plan_details):
        if not (1 <= week_number <= 52):
            raise ValueError("Week number must be 1-52")
        if not (1 <= day_of_week <= 7):
            raise ValueError("Day of week must be 1-7")

        plan = cls(
            user_id=user_id,
            week_number=week_number,
            day_of_week=day_of_week,
            plan_details=plan_details[:2000]
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

    @classmethod
    def get_by_day(cls, db, user_id, week_number, day_of_week):
        return db.query(cls).filter_by(
            user_id=user_id,
            week_number=week_number,
            day_of_week=day_of_week
        ).first()

    @classmethod
    def update(cls, db, plan_id, plan_details=None):
        plan = db.query(cls).filter_by(id=plan_id).first()
        if plan and plan_details:
            plan.plan_details = plan_details[:2000]
            db.commit()
            db.refresh(plan)
            return plan
        return None

    @classmethod
    def delete(cls, db, plan_id):
        plan = db.query(cls).filter_by(id=plan_id).first()
        if plan:
            db.delete(plan)
            db.commit()
            return True
        return False

    @classmethod
    def delete_all_by_user(cls, db, user_id):  
        db.query(cls).filter_by(user_id=user_id).delete()
        db.commit()
