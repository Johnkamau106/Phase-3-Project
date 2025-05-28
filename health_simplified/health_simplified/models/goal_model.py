from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    daily_calories = Column(Integer)
    weekly_calories = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="goals")

    @classmethod
    def create_or_update(cls, db, user_id, daily_calories, weekly_calories):
        goal = db.query(cls).filter(cls.user_id == user_id).first()
        if goal:
            goal.daily_calories = daily_calories
            goal.weekly_calories = weekly_calories
        else:
            goal = cls(
                user_id=user_id,
                daily_calories=daily_calories,
                weekly_calories=weekly_calories
            )
            db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @classmethod
    def get_by_user(cls, db, user_id):
        return db.query(cls).filter(cls.user_id == user_id).first()

    @classmethod
    def delete(cls, db, goal_id):
        goal = db.query(cls).filter(cls.id == goal_id).first()
        if goal:
            db.delete(goal)
            db.commit()
            return True
        return False