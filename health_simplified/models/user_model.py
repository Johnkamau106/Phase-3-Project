from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from health_simplified.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)

    # Relationships
    entries = relationship("FoodEntry", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")

    @classmethod
    def create(cls, db, name):
        if not name or len(name) > 50:
            raise ValueError("Name must be 1-50 characters")
        
        user = cls(name=name)
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("User with this name already exists")
        db.refresh(user)
        return user


    @classmethod
    def get_all(cls, db):
        return db.query(cls).all()

    @classmethod
    def get_by_name(cls, db, name):
        return db.query(cls).filter(cls.name == name).first()
    
    @classmethod
    def get_by_id(cls, db, user_id):
        return db.query(cls).filter(cls.id == user_id).first()

    @classmethod
    def delete(cls, db, user_id):
        user = db.query(cls).filter(cls.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
    