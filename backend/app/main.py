import logging
import os
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Request, status, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from .database import Base, engine, get_db, SessionLocal
from .models import Project, ContactMessage, PortfolioVisit, Certification, Achievement
from .schemas import (
    ProjectOut,
    ContactCreate,
    VisitCreate,
    CertificationOut,
    AchievementOut,
    HealthOut
)
from .migrations import run_migrations
from .email_service import send_contact_notification, retry_failed_notifications, send_visitor_alert_notification
from .visitor_summary import send_daily_summary, generate_visitor_summary_data

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("portfolio.api")

# In-memory sliding window rate limiter
# Maps client identifier -> list of timestamps
_rate_limits = defaultdict(list)

def enforce_rate_limit(key: str, max_requests: int, window_seconds: int):
    """
    Enforces in-memory sliding-window rate limiting.
    Raises HTTPException(429) if the threshold is exceeded.
    """
    now = time.time()
    # Prune timestamps older than window_seconds
    valid_timestamps = [t for t in _rate_limits[key] if now - t < window_seconds]
    if len(valid_timestamps) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Please wait a moment before trying again."
        )
    valid_timestamps.append(now)
    _rate_limits[key] = valid_timestamps

_visitor_alert_ip_limits = defaultdict(list)
_visitor_alert_global_limits = []

def can_send_visitor_alert(client_ip: str) -> bool:
    """Limits visitor alert emails to max 1 per 10 minutes per IP and max 15 per hour globally."""
    now = time.time()
    _visitor_alert_ip_limits[client_ip] = [t for t in _visitor_alert_ip_limits[client_ip] if now - t < 600]
    _visitor_alert_global_limits[:] = [t for t in _visitor_alert_global_limits if now - t < 3600]

    if len(_visitor_alert_ip_limits[client_ip]) >= 1:
        return False
    if len(_visitor_alert_global_limits) >= 15:
        return False

    _visitor_alert_ip_limits[client_ip].append(now)
    _visitor_alert_global_limits.append(now)
    return True

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist and schema migrations are applied
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        try:
            run_migrations(db)
        except Exception as mig_err:
            logger.error("Migration error during startup: %s", mig_err)
            db.rollback()

        try:
            count = db.query(Project).count()
        except Exception:
            db.rollback()
            count = 0

        # Seed default projects if empty, or ensure project years match current timeline
        if count == 0:
            db.add_all([Project(**p) for p in DEFAULT_PROJECTS])
            db.commit()
        else:
            for p in DEFAULT_PROJECTS:
                existing = db.query(Project).filter(Project.slug == p["slug"]).first()
                if existing and existing.year != p["year"]:
                    existing.year = p["year"]
            db.commit()
    yield

app = FastAPI(
    title="Tejas CK Portfolio API",
    description="Backend API powering projects, anonymous visit telemetry, and contact inquiries for Tejas CK's developer portfolio.",
    version="1.0.0",
    lifespan=lifespan,
)

cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
origins = [x.strip() for x in cors_origins_env.split(",") if x.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthOut)
def health(db: Session = Depends(get_db)):
    """Health check endpoint that verifies API uptime and database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        logger.error("Health check failed on database ping: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"ok": False, "service": "portfolio-api", "database": f"unhealthy: {type(exc).__name__}"}
        )
    return {"ok": True, "service": "portfolio-api", "database": db_status}

@app.get("/api/projects", response_model=list[ProjectOut])
def get_projects(db: Session = Depends(get_db)):
    """Retrieve portfolio projects with full case-study details, ordered by sort_order."""
    return db.query(Project).order_by(Project.sort_order.asc(), Project.id.asc()).all()

@app.get("/api/certifications", response_model=list[CertificationOut])
def get_certifications(db: Session = Depends(get_db)):
    """Retrieve verified certifications and coursework, ordered by display_order."""
    return db.query(Certification).order_by(Certification.display_order.asc(), Certification.id.asc()).all()

@app.get("/api/achievements", response_model=list[AchievementOut])
def get_achievements(db: Session = Depends(get_db)):
    """Retrieve verified collaborative events and hackathon participation, ordered by display_order."""
    return db.query(Achievement).order_by(Achievement.display_order.asc(), Achievement.id.asc()).all()

@app.post("/api/contact", status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: ContactCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Accepts contact inquiries. Stored only upon explicit user submission.
    Includes rate limiting and honeypot spam protection.
    Dispatches email notification via background task.
    No contact submissions are ever exposed publicly.
    """
    # Rate limiting: max 5 submissions per 60 seconds per client
    client_ip = request.client.host if request.client else "unknown"
    enforce_rate_limit(f"contact:{client_ip}", max_requests=5, window_seconds=60)

    # Honeypot check: If the hidden 'website' field is populated, silently return success without saving
    if payload.website and payload.website.strip():
        logger.info("Honeypot triggered from client %s; dropping spam submission safely", client_ip)
        return {"ok": True, "message": "Your message has been received."}

    name = payload.name.strip()
    message = payload.message.strip()

    if not name or len(message) < 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please provide a valid name and a message of at least 5 characters."
        )

    try:
        row = ContactMessage(
            name=name,
            email=str(payload.email).strip().lower(),
            company=(payload.company or "").strip() or None,
            message=message,
            status="new",
            notification_status="pending",
            notification_attempts=0
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        logger.info("New contact inquiry received from %s (stored with status 'new', id=%s)", client_ip, row.id)
    except Exception as exc:
        db.rollback()
        logger.error("Failed to save contact inquiry: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving your message. Please try again."
        )

    # Dispatch email notification in background using a separate DB session
    def _dispatch_email(msg_id: int):
        with SessionLocal() as bg_db:
            send_contact_notification(bg_db, msg_id)

    background_tasks.add_task(_dispatch_email, row.id)

    return {"ok": True, "message": "Thank you for reaching out! Your message has been received."}

@app.post("/api/visits", status_code=status.HTTP_201_CREATED)
def create_visit(
    payload: VisitCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Accepts minimal anonymous visitor telemetry (random client ID, session ID, page path, optional referrer).
    No contact information, email, phone numbers, or raw IP addresses are stored.
    Dispatches an asynchronous email alert for genuinely new anonymous visitor sessions (at most 1 per session).
    """
    # Rate limiting: max 30 visits per 60 seconds per client
    client_ip = request.client.host if request.client else "unknown"
    enforce_rate_limit(f"visit:{client_ip}", max_requests=30, window_seconds=60)

    device_cat = payload.device_category
    ua = (request.headers.get("user-agent") or "").lower()
    if not device_cat:
        if any(m in ua for m in ("iphone", "android", "mobile", "ipod")):
            device_cat = "mobile"
        elif any(t in ua for t in ("ipad", "tablet")):
            device_cat = "tablet"
        else:
            device_cat = "desktop"

    session_id = payload.session_id.strip() if payload.session_id else None
    visitor_id = payload.visitor_id.strip()

    # Determine if this is a genuinely new visitor session
    is_new_session = False
    if session_id:
        prior_sessions = db.query(PortfolioVisit.id).filter(PortfolioVisit.session_id == session_id).count()
        if prior_sessions == 0:
            is_new_session = True
    else:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
        prior_visits = db.query(PortfolioVisit.id).filter(
            PortfolioVisit.visitor_id == visitor_id,
            PortfolioVisit.created_at >= cutoff
        ).count()
        if prior_visits == 0:
            is_new_session = True

    # Identify automated crawlers / bots to avoid alert spam
    bot_signatures = ("bot", "spider", "crawl", "slurp", "headless", "curl", "python-requests", "aiohttp", "wget", "httpclient", "scrapy", "postman")
    is_bot = any(b in ua for b in bot_signatures)

    try:
        visit = PortfolioVisit(
            visitor_id=visitor_id,
            session_id=session_id,
            device_category=device_cat,
            page_path=payload.page_path.strip(),
            referrer=payload.referrer.strip() if payload.referrer else None
        )
        db.add(visit)
        db.commit()
        db.refresh(visit)
    except Exception:
        db.rollback()
        # Non-blocking for analytics
        return {"ok": False, "detail": "Telemetry record failed"}

    # Dispatch visitor alert asynchronously if genuinely new session, not a bot, and rate limit allows
    if is_new_session and not is_bot and can_send_visitor_alert(client_ip):
        def _dispatch_visitor_alert(v_id: int):
            with SessionLocal() as bg_db:
                send_visitor_alert_notification(bg_db, v_id)

        background_tasks.add_task(_dispatch_visitor_alert, visit.id)

    return {"ok": True}

def verify_admin_key(x_admin_key: Optional[str] = Header(default=None)):
    """Secures administrative endpoints against unauthorized access."""
    admin_secret = os.getenv("ADMIN_SECRET_KEY", "").strip()
    if not admin_secret:
        return True
    if x_admin_key != admin_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing administrative key."
        )
    return True

@app.post("/api/internal/send-visitor-summary")
def trigger_visitor_summary(
    hours: int = 24,
    authorized: bool = Depends(verify_admin_key),
    db: Session = Depends(get_db)
):
    """Generates the visitor analytics summary and emails it to the configured admin inbox."""
    ok, msg, data = send_daily_summary(db, hours=hours)
    return {"ok": ok, "detail": msg, "summary": data}

@app.post("/api/internal/retry-notifications")
def trigger_retry_notifications(
    authorized: bool = Depends(verify_admin_key),
    db: Session = Depends(get_db)
):
    """Retries any pending/failed email notifications without duplicate sends."""
    results = retry_failed_notifications(db)
    return {"ok": True, "results": results}
