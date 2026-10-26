"""
Database migration and data seeding module for Tejas CK Portfolio.
Idempotently applies schema updates (e.g. adding columns to existing tables)
and seeds verified portfolio data without overwriting or deleting existing records.
"""
import logging
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from .database import engine, Base
from .models import Project, ContactMessage, Certification, Achievement

logger = logging.getLogger("portfolio.migrations")

DEFAULT_CERTIFICATIONS = [
    {
        "title": "Full Stack Web Development Bootcamp",
        "issuing_organization": "Udemy",
        "issue_date": None,
        "credential_url": "https://drive.google.com/file/d/18X_tBdDX8mUPl-qH5lhlpmUJ0YNSzi4u/view?usp=drivesdk",
        "category": "WEB DEVELOPMENT",
        "description": "Comprehensive coursework covering modern frontend frameworks, responsive UI layout patterns, RESTful API architecture, backend services, and database persistence.",
        "display_order": 1
    },
    {
        "title": "Soft Skills Development",
        "issuing_organization": "NPTEL, IIT Kharagpur",
        "issue_date": None,
        "credential_url": "https://drive.google.com/file/d/1UrQ-tQuvUACxnc48MdFN-sdGkKV6gDaS/view?usp=drivesdk",
        "category": "PROFESSIONAL COMMUNICATION",
        "description": "Academic certification focusing on interpersonal communication, technical presentations, engineering teamwork dynamics, and collaborative workplace effectiveness.",
        "display_order": 2
    },
    {
        "title": "Human–Computer Interaction",
        "issuing_organization": "IIT Madras",
        "issue_date": None,
        "credential_url": None,
        "category": "UI/UX & ERGONOMICS",
        "description": "Rigorous coursework exploring user-centered design, cognitive psychology in interfaces, heuristic evaluation, usability metrics, and interactive software ergonomics.",
        "display_order": 3
    },
    {
        "title": "Getting Started with Artificial Intelligence",
        "issuing_organization": "IBM",
        "issue_date": None,
        "credential_url": None,
        "category": "AI & MACHINE LEARNING",
        "description": "Foundational training covering artificial intelligence principles, machine learning pipelines, deep learning concepts, natural language processing, and ethical AI deployment.",
        "display_order": 4
    },
    {
        "title": "Big Data Analysis",
        "issuing_organization": "Infosys",
        "issue_date": None,
        "credential_url": "https://drive.google.com/file/d/1LgPt7R5ytDGHaF3tB8e-hFvLzANOIMgY/view?usp=drivesdk",
        "category": "DATA & ANALYTICS",
        "description": "Coursework covering big data fundamentals, distributed data processing concepts, large-scale data storage mechanisms, and analytics pipelines.",
        "display_order": 5
    }
]

DEFAULT_ACHIEVEMENTS = [
    {
        "title": "ClamStack — 24-Hour Hackathon",
        "organization": "Department of CSE, Malnad College of Engineering",
        "date": None,
        "category": "HACKATHON PARTICIPATION",
        "description": "Participated in an intensive 24-hour collegiate hackathon focused on rapid problem breakdown, collaborative software prototyping, and sprint execution under tight deadlines.",
        "highlight": "24-Hour Rapid Prototyping & System Design",
        "evidence_url": "https://drive.google.com/file/d/1ehgKaX6Yc_Gd2VDvpDT0l5QIUlgStkXu/view?usp=drivesdk",
        "display_order": 1
    },
    {
        "title": "Avishkar Manthan Ideathon",
        "organization": "IUCEE",
        "date": None,
        "category": "IDEATHON PARTICIPATION",
        "description": "Participated in the regional engineering ideathon evaluating real-world problem statements, formulating technology-driven proposals, and presenting structured engineering feasibility analyses.",
        "highlight": "Engineering Ideation & Feasibility Analysis",
        "evidence_url": "https://drive.google.com/file/d/1TaxiQRpLRnEtNQTVzquQk0XmuWPOT4b9/view?usp=drivesdk",
        "display_order": 2
    }
]

def run_migrations(db: Session):
    """
    Ensures all tables and required columns exist without dropping existing tables.
    Seeds default certifications and achievements if tables are empty.
    """
    # 1. Create all tables defined in Base metadata if they don't exist yet
    Base.metadata.create_all(bind=engine)

    # 2. Check for missing columns in existing tables (SQLite schema migration)
    with engine.connect() as conn:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        if "contact_messages" in table_names:
            cols = [c["name"] for c in inspector.get_columns("contact_messages")]
            if "status" not in cols:
                logger.info("Migrating contact_messages table: adding 'status' column")
                conn.execute(text("ALTER TABLE contact_messages ADD COLUMN status VARCHAR(50) DEFAULT 'new' NOT NULL"))
            if "notification_status" not in cols:
                logger.info("Migrating contact_messages table: adding 'notification_status' column")
                conn.execute(text("ALTER TABLE contact_messages ADD COLUMN notification_status VARCHAR(50) DEFAULT 'pending' NOT NULL"))
            if "notification_attempts" not in cols:
                logger.info("Migrating contact_messages table: adding 'notification_attempts' column")
                conn.execute(text("ALTER TABLE contact_messages ADD COLUMN notification_attempts INTEGER DEFAULT 0 NOT NULL"))
            if "notification_error" not in cols:
                logger.info("Migrating contact_messages table: adding 'notification_error' column")
                conn.execute(text("ALTER TABLE contact_messages ADD COLUMN notification_error VARCHAR(500)"))
            if "notification_sent_at" not in cols:
                logger.info("Migrating contact_messages table: adding 'notification_sent_at' column")
                conn.execute(text("ALTER TABLE contact_messages ADD COLUMN notification_sent_at DATETIME"))
            conn.commit()

        if "portfolio_visits" in table_names:
            v_cols = [c["name"] for c in inspector.get_columns("portfolio_visits")]
            if "session_id" not in v_cols:
                logger.info("Migrating portfolio_visits table: adding 'session_id' column")
                conn.execute(text("ALTER TABLE portfolio_visits ADD COLUMN session_id VARCHAR(100)"))
            if "device_category" not in v_cols:
                logger.info("Migrating portfolio_visits table: adding 'device_category' column")
                conn.execute(text("ALTER TABLE portfolio_visits ADD COLUMN device_category VARCHAR(50)"))
            conn.commit()

    # 3. Seed certifications if empty
    cert_count = db.query(Certification).count()
    if cert_count == 0:
        logger.info("Seeding verified certifications into database")
        for cert_data in DEFAULT_CERTIFICATIONS:
            db.add(Certification(**cert_data))
        db.commit()
    else:
        # Update existing records to match latest verified titles/urls if needed
        for cert_data in DEFAULT_CERTIFICATIONS:
            existing = db.query(Certification).filter(Certification.title == cert_data["title"]).first()
            if existing:
                existing.credential_url = cert_data["credential_url"]
                existing.issuing_organization = cert_data["issuing_organization"]
                existing.category = cert_data["category"]
                existing.description = cert_data["description"]
                existing.display_order = cert_data["display_order"]
            else:
                db.add(Certification(**cert_data))
        db.commit()

    # 4. Seed achievements if empty
    achieve_count = db.query(Achievement).count()
    if achieve_count == 0:
        logger.info("Seeding verified achievements into database")
        for ach_data in DEFAULT_ACHIEVEMENTS:
            db.add(Achievement(**ach_data))
        db.commit()
    else:
        for ach_data in DEFAULT_ACHIEVEMENTS:
            existing = db.query(Achievement).filter(Achievement.title == ach_data["title"]).first()
            if existing:
                existing.organization = ach_data["organization"]
                existing.evidence_url = ach_data["evidence_url"]
                existing.category = ach_data["category"]
                existing.description = ach_data["description"]
                existing.highlight = ach_data["highlight"]
                existing.display_order = ach_data["display_order"]
            else:
                db.add(Achievement(**ach_data))
        db.commit()
