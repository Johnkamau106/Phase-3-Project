import datetime
from sqlalchemy import Column, Integer, String, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from health_simplified.db.database import Base

class FoodEntry(Base):
    __tablename__ = "food_entries"
    __table_args__ = (
        CheckConstraint('calories > 0', name='check_calories_positive'),
    )

    id = Column(Integer, primary_key=True, index=True)
    food = Column(String(100), index=True)
    calories = Column(Integer)
    date = Column(Date, default=datetime.date.today)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="entries")

    @classmethod
    def create(cls, db, user_id, food, calories, date=None):
        """Create with validation"""
        if not food or len(food) > 100:
            raise ValueError("Food name must be 1-100 characters")
        if not isinstance(calories, int) or calories <= 0:
            raise ValueError("Calories must be positive integer")
            
        entry = cls(
            user_id=user_id,
            food=food,
            calories=calories,
            date=date or datetime.date.today()
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @classmethod
    def update(cls, db, entry_id, **kwargs):
        entry = db.query(cls).filter(cls.id == entry_id).first()
        if not entry:
            return None
            
        if 'calories' in kwargs and kwargs['calories'] <= 0:
            raise ValueError("Calories must be positive")
            
        for key, value in kwargs.items():
            setattr(entry, key, value)
            
        db.commit()
        db.refresh(entry)
        return entry

    @classmethod
    def get_all(cls, db, user_id, date):
        return db.query(cls).filter(
            cls.user_id == user_id,
            cls.date == date
        ).all()
    @classmethod
    def delete(cls, db, entry_id):
        entry = db.query(cls).filter(cls.id == entry_id).first()
        if entry:
           db.delete(entry)
           db.commit()
        return True
        return False
