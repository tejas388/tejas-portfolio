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

import json

DEFAULT_PROJECTS = [
    {
        "slug": "medisync",
        "title": "MediSync",
        "category": "MOBILE PRODUCT / IOT",
        "summary": "A connected medication adherence platform linking a Flutter mobile app, FastAPI backend services, and a smart ESP32 dispenser prototype.",
        "description": "MediSync helps patients and caregivers manage medication routines through dosage scheduling, time-sensitive reminders, and an IoT dispenser interface that validates physical dispensing events.",
        "role": "Flutter & Backend Developer",
        "year": "2026",
        "stack": "Flutter, Dart, FastAPI, SQLite, ESP32, REST APIs",
        "outcome": "Mobile app + hardware dispenser prototype",
        "accent": "red",
        "visual": "medisync",
        "github_url": "https://github.com/tejas388/MediSync",
        "demo_url": None,
        "problem": "Missing doses and uncertainty around whether medication was taken can lead to severe health consequences. Traditional pillboxes cannot verify consumption or alert caregivers when a critical dose is skipped.",
        "architecture": "Flutter Mobile UI <──REST API (JSON)──> FastAPI Services <──SQLAlchemy ORM──> SQLite Storage; ESP32 microcontroller communicates via HTTP/WiFi to receive dispensing commands and transmit physical completion telemetry.",
        "features": json.dumps([
            "Customizable daily prescription schedules with specific intake timings and meal relations",
            "Visual adherence tracking dashboard showing compliance history",
            "Bi-directional hardware synchronization with ESP32 microcontroller dispenser",
            "Idempotent dose-logging API endpoints preventing duplicate triggers on flaky connections",
            "Offline schedule caching in Flutter when network links fluctuate"
        ]),
        "challenges": json.dumps([
            "Handling intermittent connectivity between the dispenser and backend via status reconciliation loops",
            "Implementing idempotent dispensing endpoints so dropped packets never cause duplicate dosage releases"
        ]),
        "status_note": "Functional prototype: The Flutter mobile app and FastAPI backend workflows are tested locally; dispenser mechanics were validated on an ESP32 breadboard rig. Not released to commercial app stores.",
        "sort_order": 1,
    },
    {
        "slug": "recoverai",
        "title": "RECOVERAI",
        "category": "AI / DATA RECOVERY",
        "summary": "An intelligent file recovery and integrity inspection workflow featuring a React interface and Python FastAPI backend for reconstructing damaged files.",
        "description": "RECOVERAI explores programmatic file recovery techniques. It provides byte-level header analysis, file signature verification, and automated reconstruction pipelines for damaged media and document formats.",
        "role": "Full-Stack Developer",
        "year": "2026",
        "stack": "React, JavaScript, FastAPI, Python, File Signatures, Hex Analysis",
        "outcome": "File recovery pipeline & diagnostic UI",
        "accent": "graphite",
        "visual": "recoverai",
        "github_url": "https://github.com/tejas388/RECOVERAI",
        "demo_url": None,
        "problem": "Accidental file corruption, interrupted writes, and filesystem errors frequently leave documents unopenable. Non-technical users lack accessible tools to understand if a file is repairable or irrecoverable.",
        "architecture": "React Frontend (file upload, chunking, recovery logs, hex preview) <──REST Endpoints──> FastAPI Backend (file buffer inspection, magic byte extraction) <──Python Recovery Engine (header reconstruction, signature validation)──> Restored File Artifacts.",
        "features": json.dumps([
            "File header and magic-byte integrity inspection for common formats (PNG, JPEG, PDF, DOCX)",
            "Automated header rebuilding for truncated or partially overwritten file signatures",
            "Visual recovery feasibility assessment based on container structure",
            "Interactive hexadecimal previewer displaying file byte offset headers",
            "Downloadable restored file artifacts with validation checksums"
        ]),
        "challenges": json.dumps([
            "Accurately identifying the threshold between reconstructible header damage and unrecoverable payload entropy loss",
            "Providing transparent user messaging to avoid overstating recovery chances on encrypted or zero-filled data"
        ]),
        "status_note": "Prototype stage: Demonstrates deterministic header reconstruction for common image and text formats. Machine learning synthesis for payload reconstruction is experimental.",
        "sort_order": 2,
    },
    {
        "slug": "ai-memory-bot",
        "title": "AI Memory Bot",
        "category": "LLM / CONVERSATIONAL AI",
        "summary": "A conversational assistant exploring stateful memory extraction, context retention, and multi-turn retrieval mechanisms using Python and LLM APIs.",
        "description": "AI Memory Bot investigates long-term conversational memory. It extracts user preferences, constraints, and project details across interactions, selectively retrieving context to produce informed multi-turn responses.",
        "role": "AI & Python Developer",
        "year": "2025–2026",
        "stack": "Python, LLM APIs, Context Management, Vector Embeddings, Prompt Engineering",
        "outcome": "Context-aware conversational prototype",
        "accent": "light",
        "visual": "memory",
        "github_url": "https://github.com/tejas388/AI_Memory_Bot",
        "demo_url": None,
        "problem": "Standard conversational models operate in stateless isolation, requiring users to repeat preferences, constraints, and background details in every new session or after context window boundaries.",
        "architecture": "Chat Interface / CLI <──User Message──> Memory Ingestion Pipeline (extracts key facts & preferences) <──Memory Store (ephemeral / file-based memory nodes & vector indices)──> Contextual Prompt Formatter <──Injected Context + Query──> LLM API <──Informed Response──> User Stream.",
        "features": json.dumps([
            "Automatic fact extraction from conversational dialogue turns",
            "Semantic similarity retrieval for memory recall within prompt budgets",
            "Interactive memory inspection tag and memory control panel",
            "Memory editing and deletion controls for privacy and accuracy",
            "Token-efficient prompt synthesis and fallback to stateless mode"
        ]),
        "challenges": json.dumps([
            "Mitigating memory hallucination and context drift across multi-turn interactions",
            "Ensuring retrieved historical facts do not conflict with or override current user instructions"
        ]),
        "status_note": "Exploratory research prototype: Evaluates memory scoring and contextual prompt synthesis using Python scripts and LLM APIs. Persistent distributed vector database integration is identified as a next phase.",
        "sort_order": 3,
    },
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
                dt_type = "TIMESTAMPTZ" if engine.dialect.name == "postgresql" else "DATETIME"
                conn.execute(text(f"ALTER TABLE contact_messages ADD COLUMN notification_sent_at {dt_type}"))
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

    # 5. Seed default projects if empty, or ensure project years match current timeline
    proj_count = db.query(Project).count()
    if proj_count == 0:
        logger.info("Seeding verified projects into database")
        for p in DEFAULT_PROJECTS:
            db.add(Project(**p))
        db.commit()
    else:
        for p in DEFAULT_PROJECTS:
            existing = db.query(Project).filter(Project.slug == p["slug"]).first()
            if existing and existing.year != p["year"]:
                existing.year = p["year"]
        db.commit()
