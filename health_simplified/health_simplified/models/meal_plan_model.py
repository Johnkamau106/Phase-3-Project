from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    week_number = Column(Integer)
    plan_details = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="meal_plans")

    @classmethod
    def create(cls, db, user_id, week_number, plan_details):
        plan = cls(
            user_id=user_id,
            week_number=week_number,
            plan_details=plan_details
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

    @classmethod
    def get_by_week(cls, db, user_id, week_number):
        return db.query(cls).filter(
            cls.user_id == user_id,
            cls.week_number == week_number
        ).first()

    @classmethod
    def update(cls, db, plan_id, **kwargs):
        plan = db.query(cls).filter(cls.id == plan_id).first()
        if plan:
            for key, value in kwargs.items():
                setattr(plan, key, value)
            db.commit()
            db.refresh(plan)
            return plan
        return None

    @classmethod
    def delete(cls, db, plan_id):
        plan = db.query(cls).filter(cls.id == plan_id).first()
        if plan:
            db.delete(plan)
            db.commit()
            return True
        return False