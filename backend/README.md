# Tejas CK Portfolio — Backend API & Architecture

Production-ready FastAPI + SQLAlchemy + SQLite backend supporting verified project case studies, certifications, collaborative events, contact inquiries with anti-spam protections, real-time Gmail notifications, and privacy-conscious anonymous telemetry.

---

## 1. Quick Start

### Backend

```bash
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env

# 5. Run automated test suite (14 checks)
python test_api.py

# 6. Start development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```bash
# 1. From project root, install dependencies (if needed)
npm install

# 2. Configure environment (optional, defaults to http://localhost:8000)
cp .env.example .env

# 3. Build production bundle
npm run build

# 4. Start Vite development server
npm run dev
```

---

## 2. API Endpoints Reference

### `GET /api/health`
Checks API service status and validates active SQLite database connectivity via `SELECT 1`.

**Response (200 OK):**
```json
{
  "ok": true,
  "service": "portfolio-api",
  "database": "connected"
}
```

---

### `GET /api/projects`
Retrieves all portfolio projects with full case-study metadata, ordered by `sort_order`.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "slug": "medisync",
    "title": "MediSync",
    "category": "MOBILE PRODUCT / IOT",
    "summary": "A connected medication adherence platform linking a Flutter mobile app, FastAPI backend services, and a smart ESP32 dispenser prototype.",
    "description": "MediSync helps patients and caregivers manage medication routines through dosage scheduling...",
    "role": "Flutter & Backend Developer",
    "year": "2026",
    "stack": ["Flutter", "Dart", "FastAPI", "SQLite", "ESP32", "REST APIs"],
    "outcome": "Mobile app + hardware dispenser prototype",
    "accent": "red",
    "visual": "medisync",
    "github_url": "https://github.com/tejas388/MediSync",
    "demo_url": null,
    "problem": "Missing doses and uncertainty around whether medication was taken...",
    "architecture": "Flutter Mobile UI <──REST API──> FastAPI Services <──SQLAlchemy──> SQLite Storage...",
    "features": [
      "Customizable daily prescription schedules...",
      "Visual adherence tracking dashboard...",
      "Bi-directional hardware synchronization..."
    ],
    "challenges": [
      "Handling intermittent connectivity...",
      "Implementing idempotent dispensing endpoints..."
    ],
    "status_note": "Functional prototype...",
    "sort_order": 1
  }
]
```

---

### `GET /api/certifications`
Retrieves structured coursework and verified professional certifications, ordered by `display_order`.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Full Stack Web Development Bootcamp",
    "issuing_organization": "Udemy",
    "issue_date": null,
    "credential_url": "https://drive.google.com/file/d/18X_tBdDX8mUPl-qH5lhlpmUJ0YNSzi4u/view?usp=drivesdk",
    "category": "WEB DEVELOPMENT",
    "description": "Comprehensive coursework covering modern frontend frameworks, responsive UI layout patterns, RESTful API architecture, backend services, and database persistence.",
    "display_order": 1
  }
]
```

---

### `GET /api/achievements`
Retrieves collaborative hackathons and engineering ideathons, ordered by `display_order`.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "ClamStack — 24-Hour Hackathon",
    "organization": "Department of CSE, Malnad College of Engineering",
    "date": null,
    "category": "HACKATHON PARTICIPATION",
    "description": "Participated in an intensive 24-hour collegiate hackathon focused on rapid problem breakdown, collaborative software prototyping, and sprint execution under tight deadlines.",
    "highlight": "24-Hour Rapid Prototyping & System Design",
    "evidence_url": "https://drive.google.com/file/d/1ehgKaX6Yc_Gd2VDvpDT0l5QIUlgStkXu/view?usp=drivesdk",
    "display_order": 1
  }
]
```

---

### `POST /api/contact`
Accepts recruiter and collaborator inquiries with client rate limiting, honeypot protection, and automatic background email dispatch via Gmail SMTP.

**Request:**
```json
{
  "name": "Sarah Connor",
  "email": "sarah@example.com",
  "company": "Tech Ventures",
  "message": "We would love to discuss software engineering internship roles.",
  "website": null
}
```

**Response (201 Created):**
```json
{
  "ok": true,
  "message": "Thank you for reaching out! Your message has been received."
}
```

**Anti-Spam & Security Rules:**
- **Rate limiting:** Max 5 submissions per 60 seconds per client IP. Returns `429 Too Many Requests`.
- **Honeypot:** If the hidden `website` field is populated, the server silently responds `201 Created` without storing the spam message in the database.
- **Validation:** Pydantic email validation, name requirement, and minimum 5 character message constraint. Returns `422 Unprocessable Entity`.
- **Email Dispatch:** Runs asynchronously via `BackgroundTasks`. Updates `notification_status` to `"sent"` or `"failed"` without delaying the client's HTTP response.
- **Privacy:** Stored with `status="new"`. No public GET endpoint exists to view contact submissions.

---

### `POST /api/visits`
Records anonymous telemetry (random `visitor_id`, `session_id`, `device_category`, `page_path`, optional `referrer`).

**Request:**
```json
{
  "visitor_id": "v-abc123-1730000000",
  "session_id": "sess-xyz789-1730000000",
  "device_category": "desktop",
  "page_path": "/",
  "referrer": "https://github.com"
}
```

**Response (201 Created):**
```json
{
  "ok": true
}
```

**Privacy Guarantee:**
- No personal data, email addresses, phone numbers, or raw IP addresses are stored.
- Device category is resolved to `"desktop"`, `"mobile"`, or `"tablet"` without invasive hardware fingerprinting.

---

### `POST /api/internal/send-visitor-summary`
Generates and emails the visitor activity summary report to the configured admin email (`tejas2005patel@gmail.com`).

**Headers:**
```http
X-Admin-Key: portfolio-admin-secret-2026
```

**Query Parameters:**
- `hours` (int, default: 24): Reporting window duration.

**Response (200 OK):**
```json
{
  "ok": true,
  "detail": "Email sent successfully.",
  "summary": {
    "period_hours": 24,
    "total_visits": 12,
    "unique_visitors": 8,
    "unique_sessions": 6,
    "device_breakdown": { "desktop": 7, "mobile": 5, "tablet": 0, "unknown": 0 },
    "top_pages": [{ "path": "/", "views": 12 }],
    "prev_total_visits": 5
  }
}
```

---

### `POST /api/internal/retry-notifications`
Retries any failed contact notification emails (up to 3 attempts) while ensuring zero duplicate sends for successfully delivered messages.

**Headers:**
```http
X-Admin-Key: portfolio-admin-secret-2026
```

---

## 3. Email Notification & Daily Summary Setup

### Gmail App Password Configuration

1. Visit **Google Account Security** > **2-Step Verification**.
2. Scroll to the bottom and select **App passwords**.
3. Create a new App Password named `Portfolio Website`.
4. Copy the generated 16-character code (e.g. `xhwhszihqhmgiztt`).
5. Set the following environment variables in `backend/.env`:

```ini
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tejas2005patel@gmail.com
SMTP_APP_PASSWORD=your_16_character_app_password
NOTIFICATION_FROM_EMAIL=tejas2005patel@gmail.com
NOTIFICATION_TO_EMAIL=tejas2005patel@gmail.com
ADMIN_SECRET_KEY=portfolio-admin-secret-2026
```

### CLI Visitor Summary Runner

To trigger or inspect the daily activity report manually:

```bash
# Test report aggregation without sending an email (dry run):
python backend/send_summary.py --dry-run

# Send live report to your email inbox:
python backend/send_summary.py

# Send report for the last 48 hours:
python backend/send_summary.py --hours 48
```

### Automated Daily Cron Job

To receive an automated summary every evening at 8:00 PM:

```bash
crontab -e
```
Add the following line (substitute your workspace path):
```bash
0 20 * * * cd /Users/tejasck/Downloads/tejas-portfolio-v3 && backend/.venv/bin/python backend/send_summary.py >> backend/data/summary_cron.log 2>&1
```

---

## 4. Database Architecture & Migrations

- **Database Engine:** SQLite accessed via SQLAlchemy 2.0 ORM.
- **Location:** `backend/data/portfolio.db`
- **Optimization:** SQLite WAL (Write-Ahead Logging) mode and PRAGMA foreign keys enabled on connection.
- **Migrations:** Implemented in `backend/app/migrations.py`. Automatically verifies and updates schema (e.g. dynamically adds `status`, `notification_status`, `session_id`, `device_category` without dropping tables) and idempotently seeds default records.
- **Data Protection:** Database files (`*.db`, `*.db-wal`, `*.db-shm`) and environment files are strictly excluded in `.gitignore`.

---

## 5. Automated Verification Suite

Run all 14 backend and database checks:

```bash
python backend/test_api.py
```

Checks executed:
1. `GET /api/health` with database ping (`SELECT 1`).
2. `GET /api/projects` structured metadata and timeline validation (`2026`, `2026`, `2025–2026`).
3. `GET /api/certifications` sorted with valid credential URLs.
4. `GET /api/achievements` sorted with valid evidence URLs.
5. `POST /api/contact` storage and persistence.
6. Email notification dispatch and status tracking.
7. Notification retry idempotency (zero duplicates on delivered messages).
8. Pydantic input validation (rejects invalid payloads with 422).
9. Honeypot anti-spam defense.
10. Sliding window rate limiting (blocks 6th rapid request with 429).
11. Privacy guarantee (contact messages not publicly exposed).
12. Anonymous visit telemetry (`session_id`, `device_category`).
13. Visitor Activity Summary analytics and period-over-period comparison.
14. Secured internal admin endpoints (HTTP 401 unauthorized vs HTTP 200 with `X-Admin-Key`).
