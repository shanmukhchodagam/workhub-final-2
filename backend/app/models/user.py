from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)  # Nullable for Google OAuth users
    role = Column(String)  # Manager, Employee
    force_reset = Column(Boolean, default=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Google OAuth fields
    google_id = Column(String, nullable=True, unique=True, index=True)
    profile_picture = Column(String, nullable=True)
    auth_provider = Column(String, default="local")  # "local", "google"
    
    # Relationships
    team = relationship("Team", back_populates="members")
    chat_sessions = relationship("ChatSession", back_populates="user")
