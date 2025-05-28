from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Relationships
    entries = relationship("FoodEntry", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    meal_plans = relationship("MealPlan", back_populates="user")

    @classmethod
    def create(cls, db, name):
        user = cls(name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def get_all(cls, db):
        return db.query(cls).all()

    @classmethod
    def get_by_name(cls, db, name):
        return db.query(cls).filter(cls.name == name).first()

    @classmethod
    def delete(cls, db, user_id):
        user = db.query(cls).filter(cls.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
    