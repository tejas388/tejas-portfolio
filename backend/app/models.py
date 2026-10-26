from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text
from .database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(80), unique=True, nullable=False, index=True)
    title = Column(String(160), nullable=False)
    category = Column(String(120), nullable=False, default="SELECTED PROJECT")
    summary = Column(String(300), nullable=False, default="")
    description = Column(Text, nullable=False)
    role = Column(String(120), nullable=False, default="Developer")
    year = Column(String(30), nullable=False, default="2024")
    stack = Column(String(500), nullable=False, default="")
    outcome = Column(String(180), nullable=True)
    accent = Column(String(30), nullable=True, default="red")
    visual = Column(String(40), nullable=True, default="medisync")
    github_url = Column(String(500), nullable=True)
    demo_url = Column(String(500), nullable=True)
    problem = Column(Text, nullable=True)
    architecture = Column(Text, nullable=True)
    features = Column(Text, nullable=True)
    challenges = Column(Text, nullable=True)
    status_note = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)

class ContactMessage(Base):
    __tablename__ = "contact_messages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(254), nullable=False, index=True)
    company = Column(String(160), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="new")
    notification_status = Column(String(50), nullable=False, default="pending")
    notification_attempts = Column(Integer, nullable=False, default=0)
    notification_error = Column(String(500), nullable=True)
    notification_sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

class Certification(Base):
    __tablename__ = "certifications"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    issuing_organization = Column(String(160), nullable=False)
    issue_date = Column(String(50), nullable=True)
    credential_url = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    organization = Column(String(160), nullable=False)
    date = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    highlight = Column(String(200), nullable=True)
    evidence_url = Column(String(500), nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

class PortfolioVisit(Base):
    __tablename__ = "portfolio_visits"
    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(String(100), nullable=False, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    device_category = Column(String(50), nullable=True)
    page_path = Column(String(300), nullable=False, default="/")
    referrer = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
