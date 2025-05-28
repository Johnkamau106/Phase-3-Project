from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from ..database import Base

class FoodEntry(Base):
    __tablename__ = "food_entries"

    id = Column(Integer, primary_key=True, index=True)
    food = Column(String, index=True)
    calories = Column(Integer)
    date = Column(Date, default=date.today())
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="entries")

    @classmethod
    def create(cls, db, user_id, food, calories, date=None):
        entry = cls(
            user_id=user_id,
            food=food,
            calories=calories,
            date=date or date.today()
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @classmethod
    def get_all(cls, db, user_id=None, entry_date=None):
        query = db.query(cls)
        if user_id:
            query = query.filter(cls.user_id == user_id)
        if entry_date:
            query = query.filter(cls.date == entry_date)
        return query.all()

    @classmethod
    def update(cls, db, entry_id, **kwargs):
        entry = db.query(cls).filter(cls.id == entry_id).first()
        if entry:
            for key, value in kwargs.items():
                setattr(entry, key, value)
            db.commit()
            db.refresh(entry)
            return entry
        return None

    @classmethod
    def delete(cls, db, entry_id):
        entry = db.query(cls).filter(cls.id == entry_id).first()
        if entry:
            db.delete(entry)
            db.commit()
            return True
        return False
    