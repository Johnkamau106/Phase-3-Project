from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from health_simplified.db.database import Base

class MealPlan(Base):
    __tablename__ = "meal_plans"
    __table_args__ = (
        CheckConstraint('week_number BETWEEN 1 AND 52', name='check_week_number_range'),
    )

    id = Column(Integer, primary_key=True, index=True)
    week_number = Column(Integer)
    plan_details = Column(String(2000))  # Increased from original
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="meal_plans")

    @classmethod
    def create(cls, db, user_id, week_number, plan_details):
        # Validate week_number before DB insert
        if not (1 <= week_number <= 52):
            raise ValueError("Week number must be 1-52")

        plan = cls(
            user_id=user_id,
            week_number=week_number,
            plan_details=plan_details[:2000]  # Truncate if too long
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
            if 'week_number' in kwargs and not (1 <= kwargs['week_number'] <= 52):
                raise ValueError("Week number must be 1-52")

            for key, value in kwargs.items():
                if key == 'plan_details':
                    value = value[:2000]  # Enforce length limit
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
