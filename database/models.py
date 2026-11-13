from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from database.connection import Base


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, index=True)
    city = Column(String(120), default="")
    region = Column(String(120), default="")
    industry = Column(String(120), default="")
    website = Column(String(1000), default="")
    source_url = Column(String(1000), default="")
    description = Column(Text, default="")
    size = Column(String(40), default="Unknown")
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    opportunities = relationship("Opportunity", back_populates="company")
    __table_args__ = (UniqueConstraint("name", "city", name="uq_company_name_city"),)


class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    company_name = Column(String(250), default="Unknown")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    location = Column(String(250), default="")
    region = Column(String(120), default="")
    industry = Column(String(120), default="")
    source = Column(String(100), default="")
    url = Column(String(1500), nullable=False, unique=True)
    snippet = Column(Text, default="")
    published_at = Column(String(80), default="")
    deadline = Column(String(80), default="")
    skills = Column(Text, default="")
    is_pfe = Column(Boolean, default=False)
    score = Column(Float, default=0)
    status = Column(String(40), default="Discovered")
    notes = Column(Text, default="")
    is_new = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    company = relationship("Company", back_populates="opportunities")


class SearchHistory(Base):
    __tablename__ = "search_history"
    id = Column(Integer, primary_key=True)
    query = Column(String(500), nullable=False)
    source = Column(String(100), default="")
    result_count = Column(Integer, default=0)
    status = Column(String(80), default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), default="Default profile")
    academic_level = Column(String(120), default="Fifth-year engineering student")
    graduation = Column(String(40), default="July 2027")
    specializations = Column(Text, default="Robotics, IoT, Artificial Intelligence, Data Science")
    skills = Column(Text, default="Python, C/C++, SQL, Pandas, NumPy, TensorFlow, PyTorch, OpenCV, ROS2")
