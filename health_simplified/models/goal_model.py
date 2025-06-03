from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from health_simplified.db.database import Base

class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint('daily_calories > 0', name='check_daily_positive'),
        CheckConstraint('weekly_calories > 0', name='check_weekly_positive'),
    )

    id = Column(Integer, primary_key=True, index=True)
    daily_calories = Column(Integer)
    weekly_calories = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="goals")

    @classmethod
    def create_or_update(cls, db, user_id, daily, weekly):
        """Upsert pattern with validation"""
        if daily <= 0 or weekly <= 0:
            raise ValueError("Goals must be positive values")
        if weekly < daily:
            raise ValueError("Weekly goal should be ≥ daily goal")

        goal = db.query(cls).filter(cls.user_id == user_id).first()
        if goal:
            goal.daily_calories = daily
            goal.weekly_calories = weekly
        else:
            goal = cls(
                user_id=user_id,
                daily_calories=daily,
                weekly_calories=weekly
            )
            db.add(goal)

        db.commit()
        db.refresh(goal)
        return goal

    @classmethod
    def get_by_user(cls, db, user_id):
        return db.query(cls).filter(cls.user_id == user_id).first()

    @classmethod
    def delete_by_user(cls, db, user_id):
        db.query(cls).filter_by(user_id=user_id).delete()
        db.commit()
