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

from .migrations import run_migrations, DEFAULT_PROJECTS

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
    yield

app = FastAPI(
    title="Tejas CK Portfolio API",
    description="Backend API powering projects, anonymous visit telemetry, and contact inquiries for Tejas CK's developer portfolio.",
    version="1.0.0",
    lifespan=lifespan,
)

cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
origins = [x.strip() for x in cors_origins_env.split(",") if x.strip()]
cors_origin_regex = os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.vercel\.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=cors_origin_regex if cors_origin_regex else None,
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
    admin_secret = os.getenv("ADMIN_SECRET_KEY", "portfolio-admin-secret-2026").strip()
    if not admin_secret or x_admin_key != admin_secret:
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
