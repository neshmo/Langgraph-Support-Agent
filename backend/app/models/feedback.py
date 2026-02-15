from sqlalchemy import Column, String, Text
from app.db.base import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True)
    ticket_id = Column(String, index=True)
    content = Column(Text)
