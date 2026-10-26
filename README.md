# Tejas CK — Developer Portfolio (Full-Stack & Mobile)

A production-minded, cinematic developer portfolio built for software engineering internships, full-stack development, Flutter/mobile development, and AI/ML opportunities. Features an interactive 3D hero with floating mobile device mockups, in-depth architectural case studies for **MediSync**, **RECOVERAI**, and **AI Memory Bot**, an engineering journey timeline, verified skills matrix, and a privacy-conscious FastAPI + SQLite backend.

---

## Architecture & System Overview

- **Frontend**: React 18, Vite 6, Lucide React, modern CSS with responsive design, keyboard navigation, and `prefers-reduced-motion` support.
- **Backend**: Python 3.13, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn.
- **Database**: SQLite default for zero-friction local development, stored predictably at `backend/data/portfolio.db` (auto-created, excluded from Git).
- **Security & Privacy**:
  - CORS origin allowlists.
  - In-memory sliding-window rate limiting on `/api/contact` (max 5 requests per 60s per client) and `/api/visits` (max 30 requests per 60s).
  - Honeypot bot spam prevention on contact form (`website` field silently drops spam payloads).
  - Form field length and email validation.
  - Privacy-first anonymous visits (records only random client ID, page path, optional referrer, and timestamp; zero IP addresses or personal details).
  - Explicit contact submissions only; no public contact-listing endpoints.

---

## Quick Start on macOS

Follow these exact commands in your macOS terminal to run both the backend and frontend locally.

### 1. Prerequisites
Ensure you have Python 3.11+ and Node.js 18+ installed on your Mac:
```bash
python3 --version
node -v
npm -v
```

---

### 2. Backend Setup & Startup (Terminal 1)

From the project root (`tejas-portfolio-v3`):

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment (if not already created)
python3 -m venv .venv

# 3. Activate the virtual environment
source .venv/bin/activate

# 4. Install backend dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Create local environment configuration
cp .env.example .env

# 6. Run automated verification suite (verifies DB, seed data, and endpoints)
python test_api.py

# 7. Start the FastAPI development server
uvicorn app.main:app --reload --port 8000
```

The backend server will run at:
- API Root: `http://localhost:8000`
- Interactive API Docs (Swagger UI): `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

---

### 3. Frontend Setup & Startup (Terminal 2)

Open a new terminal tab or window in the project root (`tejas-portfolio-v3`):

```bash
# 1. Ensure you are in the project root
pwd

# 2. Copy the frontend environment file
cp .env.example .env

# 3. Install npm dependencies
npm install

# 4. Verify production build
npm run build

# 5. Start the Vite development server
npm run dev
```

Open the displayed Vite URL in your browser:
- **`http://localhost:5173`**

---

## API Endpoints Reference

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Verifies server uptime and tests SQLite connectivity via `SELECT 1` | `200 OK` |
| `GET` | `/api/projects` | Returns all 3 portfolio case studies with verified metadata, role, stack, and architecture | `200 OK` |
| `POST` | `/api/contact` | Submits contact inquiry with Pydantic validation, honeypot protection, and rate limiting | `201 Created` |
| `POST` | `/api/visits` | Anonymous telemetry (random `visitor_id`, `page_path`, optional `referrer`). Zero personal data | `201 Created` |
| `GET` | `/docs` | Interactive OpenAPI / Swagger documentation | `200 OK` |

---

## SQLite Database Management & Backup

### Database Location
The SQLite database is stored at:
```
backend/data/portfolio.db
```
The directory `backend/data/` is automatically created on startup and is strictly ignored in `.gitignore` so your local submissions and logs are never committed to version control.

### How to Back Up the SQLite Database
To create a safe hot backup of your SQLite database:

```bash
cd backend
# Using sqlite3 online backup command
sqlite3 data/portfolio.db ".backup data/portfolio_backup_$(date +%Y%m%d_%H%M%S).db"
```
Or simply copy the file when the server is idle:
```bash
cp backend/data/portfolio.db backend/data/portfolio_backup.db
```

### Inspecting Database Records
To view stored messages or visits in your terminal:
```bash
cd backend
source .venv/bin/activate
python -c "
from app.database import SessionLocal
from app.models import ContactMessage, PortfolioVisit

db = SessionLocal()
print('--- Contact Messages ---')
for msg in db.query(ContactMessage).all():
    print(f'[{msg.id}] {msg.name} <{msg.email}>: {msg.message[:40]}...')

print('\n--- Total Visits ---')
print(db.query(PortfolioVisit).count())
db.close()
"
```

---

## How to Customize Personal Details

All key contact, profile, and project links are centralized at the top of [`src/main.jsx`](file:///Users/tejasck/Downloads/tejas-portfolio-v3/src/main.jsx):

```javascript
const CONFIG = {
  name: "Tejas CK",
  role: "Final-Year Computer Science Student & Aspiring Software Engineer",
  tagline: "Building practical full-stack, mobile, and AI-assisted software.",
  email: "tejasck.dev@gmail.com",                  // Update with your primary email
  github: "https://github.com/tejas388",          // Your GitHub profile
  linkedin: "https://www.linkedin.com/in/tejasck", // Your verified LinkedIn profile
  resumeUrl: null,                                 // Set to "/resume.pdf" once placed in public/
  location: "India · Open to Remote & Relocation",
  statusBadge: "Open to Software Engineering Internships",
  availabilityDetails: "Actively seeking 2025 – 2026 Software Engineering, Full-Stack, Flutter, or AI/ML Internships."
};
```

### 1. Adding a Real Resume
1. Place your final resume PDF in the `public/` directory (e.g. `public/resume.pdf`).
2. In `src/main.jsx`, set:
   ```javascript
   resumeUrl: "/resume.pdf"
   ```
   The "Download Resume" CTA button in the About section will automatically appear!

### 2. Updating Project Case Studies
To modify project details, edit:
- Default client baseline: `DEFAULT_PROJECTS` in [`src/main.jsx`](file:///Users/tejasck/Downloads/tejas-portfolio-v3/src/main.jsx).
- Backend seed records: `DEFAULT_PROJECTS` in [`backend/app/main.py`](file:///Users/tejasck/Downloads/tejas-portfolio-v3/backend/app/main.py).

---

## Manual Browser Testing Checklist

When testing in Chrome, Safari, or Firefox:

1. **Hero Project Selection**:
   - [ ] Click "01 MediSync", "02 RECOVERAI", "03 AI Memory Bot" pills: Title, description, role, stack, and year update smoothly without layout shifts.
   - [ ] Click the floating mobile devices: Clicking a phone activates its project and highlights the phone with a red border/glow.
   - [ ] Click "EXPLORE CASE STUDY ↓": Smoothly scrolls to that project's case study card.
   - [ ] Click "VIEW STUDY ↗" on any phone: Directly navigates to `#case-study-${slug}`.
2. **Keyboard Navigation & Accessibility**:
   - [ ] Press `Tab` through navigation links, switcher pills, buttons, and form inputs.
   - [ ] Verify red focus ring (`:focus-visible`) appears clearly on all active controls.
   - [ ] Press `Enter` or `Space` on switcher pills to toggle projects.
3. **Responsiveness (Resize Browser Window)**:
   - [ ] Desktop (1440px): 2-column hero with floating phones.
   - [ ] Tablet (768px - 960px): Stacks hero copy cleanly above phones without text overlap.
   - [ ] Mobile (375px - 480px): Mobile navigation hamburger menu works, phones scale without horizontal scrolling.
4. **Reduced Motion**:
   - [ ] In macOS System Settings $\rightarrow$ Accessibility $\rightarrow$ Display $\rightarrow$ enable "Reduce motion".
   - [ ] Verify floating drift animations stop and page transitions become instant.
5. **Contact Form Submission**:
   - [ ] Try submitting an invalid email or message under 5 characters: Red validation alert appears.
   - [ ] Submit a valid message: Green success banner appears and form resets.
   - [ ] Inspect `backend/data/portfolio.db` to confirm message is stored.
   - [ ] Send 6 submissions in rapid succession from the same client: The 6th request triggers a 429 rate limit alert.

---

## Features Implemented & Verification Performed

### 1. Visual & Interactive Hero
- **Approved Cinematic Dark Aesthetic**: Graphite and black layered backgrounds (`#0f1012`), clean high-contrast typography (`Space Grotesk`, `DM Mono`, `Manrope`), restrained signal-red accents (`#ff454b`).
- **3D Floating Mobile Mockups**: 3 angled device previews for MediSync, RECOVERAI, and AI Memory Bot with hardware-accelerated CSS animations.
- **Interactive Project Selection**: Clicking any mobile device or switcher pill dynamically updates the hero title (with red accent), description, role, stack, year, and CTA buttons with zero layout jumps.
- **Direct Anchor Navigation**: Clicking a project mockup or caption jumps directly to that project's dedicated case study section (`#case-study-${slug}`).
- **Accessibility & Reduced Motion**: Fully navigable with keyboard (`Tab`, `Enter`, `Space`), `:focus-visible` outlines, and `@media (prefers-reduced-motion: reduce)` that cleanly disables floating drifts.

### 2. Deep Case Studies
- Dedicated sections for **MediSync**, **RECOVERAI**, and **AI Memory Bot**.
- Verified information: Problem statement, intended users, personal contribution, feature list, stack pills, **architecture flow diagrams**, engineering trade-offs, challenges, honest status notes, repository links, and prev/next pagination.

### 3. About, Skills & Engineering Journey
- Professional narrative highlighting practical problem solving and full-stack integration.
- 7 categorized technical skill areas (Languages, Frontend, Mobile, Backend, Databases, AI/ML, Tools).
- 5-stage Engineering Journey timeline tracing academic foundations to systems prototyping.

### 4. Robust Contact Form & Privacy
- Full Name, Valid Email, Optional Company, and Message with live character counter.
- Loading state, duplicate-submission lock, accessible error and success feedback.
- Honeypot bot protection: automated bots filling the hidden `website` field are accepted with HTTP 201 without polluting the database.
- Sliding-window in-memory rate limiting preventing form flooding.
- Explicit submission only: anonymous visits record zero contact details or IP addresses.

### 5. Automated Verification Checks Run
- **Frontend Build**: `npm run build` ran and generated optimized production bundles in 800ms with zero errors.
- **Backend Test Suite**: `backend/test_api.py` executed 7 automated checks:
  1. `GET /api/health` passed (verified DB connection via `SELECT 1`).
  2. `GET /api/projects` passed (verified all 3 projects returned with rich metadata).
  3. `POST /api/contact` passed (valid submission stored in SQLite).
  4. `POST /api/contact` validation passed (rejected invalid email and short messages with HTTP 422).
  5. `POST /api/contact` honeypot passed (spambot submission safely discarded).
  6. `POST /api/contact` rate limiting passed (rapid requests blocked with HTTP 429).
  7. `POST /api/visits` passed (recorded anonymous visitor ID and path without contact details).
- **SQLite Persistence & Privacy**: Verified direct database integrity via Python script confirming records and zero contact leaks in visit table.
