from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db.database import Base

# Define the User model in the database
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 
    
    # Travel preferences
    preferred_destinations = Column(String, nullable=True)  # JSON string of preferred destinations
    travel_style = Column(String, nullable=True)  # e.g., "adventure", "relaxation", "cultural"
    budget_range = Column(String, nullable=True)  # e.g., "budget", "moderate", "luxury" 