import React, { useEffect, useState, useRef } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowDownRight,
  ArrowUpRight,
  ArrowRight,
  ArrowLeft,
  Github,
  Mail,
  Menu,
  X,
  Smartphone,
  Database,
  BrainCircuit,
  Layers3,
  Code2,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Terminal,
  Send,
  ShieldCheck,
  Workflow,
  Award,
  Cpu,
  LineChart,
  FileText,
  Sparkles,
  Lightbulb,
  Linkedin,
  ZoomIn,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import "./styles.css";

// Central Portfolio Configuration
const CONFIG = {
  name: "Tejas C K",
  role: "Computer Science Engineering Student | Aspiring Software Engineer",
  tagline: "Building practical software products across full-stack development, mobile applications, and AI.",
  email: "tejas2005patel@gmail.com",
  github: "https://github.com/tejas388",
  linkedinPath: "/linkedin-unavailable",
  resumeUrl: "https://drive.google.com/file/d/1bCQ9StMwQCMWMKj9Wf9ZDjLXcPZWeJMf/view?usp=drivesdk",
  location: "Hassan, Karnataka, India · Open to Remote & Relocation",
  statusBadge: "Open to Software Engineering Opportunities",
  college: "Malnad College of Engineering",
  degree: "Computer Science Engineering — Bachelor's Degree",
  expectedGraduation: "2027",
  cgpa: "8.0 / 10",
  shortIntro:
    "I'm a final-year Computer Science Engineering student at Malnad College of Engineering, interested in building practical software products across full-stack development, mobile applications, and AI. I enjoy turning ideas into working applications and learning by building projects.",
  aboutSummary:
    "I'm a Computer Science Engineering student at Malnad College of Engineering, graduating in 2027. I enjoy developing practical software applications and exploring how full-stack engineering, mobile development, and AI can solve real-world problems. Through my projects, I have been learning to connect frontend experiences with backend services, APIs, databases, and intelligent application features. I'm looking for opportunities to learn from experienced engineers and contribute to meaningful software products."
};

const PORTRAIT_SRC = "/tejas-portrait.jpg";

const API = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

// Verified baseline project case studies
const DEFAULT_PROJECTS = [
  {
    id: "medisync",
    slug: "medisync",
    number: "01",
    title: "MediSync",
    category: "MOBILE PRODUCT / IOT",
    summary: "A connected medication adherence system linking a Flutter mobile app, FastAPI backend services, and a smart ESP32 dispenser prototype.",
    description: "MediSync was developed to tackle medication non-adherence by combining time-sensitive mobile reminders, dosage logs, and a physical ESP32 dispenser integration that confirms physical pill distribution.",
    role: "Flutter & Backend Developer",
    year: "2026",
    stack: ["Flutter", "Dart", "FastAPI", "SQLite", "ESP32", "REST APIs"],
    outcome: "Cross-platform mobile app + IoT dispenser prototype",
    accent: "red",
    visual: "medisync",
    github_url: "https://github.com/tejas388/MediSync",
    demo_url: null, // Genuine state: local prototype, not deployed on app stores
    problem: "Patients managing multiple prescription schedules frequently forget doses or cannot confirm whether a scheduled pill was consumed. Standard pillboxes offer zero telemetry, and mobile-only alarm apps are easily dismissed without action.",
    target_users: "Individuals on chronic medication routines, elderly patients, and caregivers needing verifiable adherence tracking.",
    contribution: "Designed and built the Flutter mobile interface; implemented dosage scheduling and offline notification caching; created FastAPI REST endpoints for dose logging; integrated ESP32 breadboard communication for dispensing triggers.",
    features: [
      "Customizable daily prescription schedules with specific intake timings and meal relations",
      "Visual adherence tracking dashboard showing compliance history",
      "Bi-directional hardware synchronization with ESP32 microcontroller dispenser",
      "Idempotent dose-logging API endpoints preventing duplicate triggers on flaky connections",
      "Local notifications and offline cache in Flutter when network is unavailable"
    ],
    architecture_steps: [
      { name: "Flutter Mobile App", desc: "User UI, scheduling logic, local alarms, and adherence history views" },
      { name: "REST API (FastAPI)", desc: "Central schedule coordinator, dose verification, and dispenser state management" },
      { name: "Persistence (SQLite)", desc: "Stores prescription metadata, dose timestamps, and dispensing audit logs" },
      { name: "ESP32 Dispenser Rig", desc: "Listens for dispense commands, activates servo/stepper, sends delivery confirmation" }
    ],
    engineering_decisions: [
      "Chose Flutter for rapid cross-platform UI iteration and reliable local background scheduling services.",
      "Used SQLite locally for zero-configuration development and lightweight database portability.",
      "Structured API endpoints to be strictly idempotent to avoid duplicate physical medicine dispensing during network retries."
    ],
    challenges: [
      "Network latency and dropped packets between the ESP32 and local server required a heartbeat mechanism and status reconciliation loop.",
      "Designing a clean UI that non-technical or elderly users can navigate without confusion."
    ],
    status_note: "Verified prototype: The Flutter app and backend APIs run locally. Hardware integration was demonstrated on an ESP32 breadboard prototype. Not published to commercial app stores.",
    learning: "Deepened my understanding of cross-platform state management in Flutter and asynchronous networking with FastAPI. Learned the necessity of idempotent endpoints and status reconciliation when communicating with physical IoT hardware over unreliable wireless links.",
    next_steps: [
      "Add Bluetooth Low Energy (BLE) provisioning for direct phone-to-dispenser pairing.",
      "Implement push notification services (FCM) for remote caregiver alerts on missed doses."
    ]
  },
  {
    id: "recoverai",
    slug: "recoverai",
    number: "02",
    title: "RECOVERAI",
    category: "AI / DATA RECOVERY",
    summary: "An intelligent data recovery and file validation platform with a React web interface and Python FastAPI backend for inspecting and reconstructing damaged files.",
    description: "RECOVERAI explores programmatic file recovery workflows. It provides byte-level header analysis, magic-number validation, and automated reconstruction pipelines for corrupted media and document files.",
    role: "Full-Stack Developer",
    year: "2026",
    stack: ["React", "JavaScript", "FastAPI", "Python", "Hex Analysis", "File Signatures"],
    outcome: "File recovery pipeline & diagnostic UI",
    accent: "graphite",
    visual: "recoverai",
    github_url: "https://github.com/tejas388/RECOVERAI",
    demo_url: null, // Genuine state: local research prototype
    problem: "File corruption caused by sudden disconnects, power losses, or disk sector errors leaves documents and images unopenable. Most consumers face intimidating command-line tools that offer no insight into what can realistically be rescued.",
    target_users: "Users attempting to recover partially damaged image and document files, and developers analyzing corrupted file containers.",
    contribution: "Built the responsive React web dashboard with drag-and-drop file ingestion; wrote Python backend routines for inspecting file magic bytes; implemented structured diagnostic logs explaining repair feasibility.",
    features: [
      "File header and magic-byte integrity inspection for common formats (PNG, JPEG, PDF, DOCX)",
      "Automated header rebuilding for truncated or partially overwritten file signatures",
      "Visual recovery feasibility assessment based on container structure",
      "Interactive hexadecimal previewer displaying file byte offset headers",
      "Downloadable restored file artifacts with validation checksums"
    ],
    architecture_steps: [
      { name: "React Web Dashboard", desc: "Drag-and-drop upload, real-time recovery progress, and hex inspection view" },
      { name: "FastAPI Processing Core", desc: "Validates file buffer streams, performs chunked processing, and routes to analyzers" },
      { name: "Signature Engine", desc: "Compares file byte offsets against signature databases to locate corrupt segments" },
      { name: "Reconstruction Pipeline", desc: "Rebuilds essential file headers and extracts usable data payloads safely" }
    ],
    engineering_decisions: [
      "Decoupled file signature analysis into modular Python analyzers for straightforward addition of new file formats.",
      "Strictly differentiated deterministic header repair from experimental content reconstruction to avoid misleading users.",
      "Enforced payload size limits on API endpoints to prevent server memory exhaustion from oversized files."
    ],
    challenges: [
      "Distinguishing recoverable header damage from irreversible payload entropy loss (e.g. encrypted or zeroed blocks).",
      "Ensuring user expectations are handled transparently by providing honest recovery feasibility indicators."
    ],
    status_note: "Verified prototype: Deterministic header restoration works reliably for targeted image formats. Advanced neural payload reconstruction remains exploratory.",
    learning: "Gained low-level insight into binary file containers, byte offsets, and magic number validation. Learned to build modular Python parsing pipelines and structure honest diagnostic interfaces that distinguish recoverable corruption from permanent data loss.",
    next_steps: [
      "Support additional archive container formats like ZIP and TAR.",
      "Introduce client-side WebAssembly parsing for pre-flight header checks prior to network upload."
    ]
  },
  {
    id: "ai-memory-bot",
    slug: "ai-memory-bot",
    number: "03",
    title: "AI Memory Bot",
    category: "LLM / CONVERSATIONAL AI",
    summary: "A conversational assistant exploring stateful conversational memory, context retention, and multi-turn retrieval mechanisms using Python and LLM APIs.",
    description: "AI Memory Bot addresses the limitation of stateless conversational systems. It extracts user preferences, constraints, and project details across interactions, selectively retrieving context to produce informed multi-turn responses.",
    role: "AI & Python Developer",
    year: "2025–2026",
    stack: ["Python", "LLM APIs", "Context Management", "Vector Embeddings", "Prompt Engineering"],
    outcome: "Context-aware conversational prototype",
    accent: "light",
    visual: "memory",
    github_url: "https://github.com/tejas388/AI_Memory_Bot",
    demo_url: null, // Genuine state: local conversational prototype
    problem: "Standard conversational bots operate in stateless isolation, requiring users to repeatedly restate background details, personal preferences, and project guidelines across separate dialogue sessions.",
    target_users: "Developers and students who want persistent context retention for ongoing research and multi-turn workflows.",
    contribution: "Implemented conversational context extraction heuristics in Python; structured memory storage schema for persistent facts; designed prompt injection templates that dynamically inject pertinent memories into model context.",
    features: [
      "Automatic fact and preference extraction from conversational dialogue turns",
      "Semantic similarity scoring to retrieve only relevant memories for the current prompt",
      "Explicit memory control panel allowing users to inspect, edit, or delete stored facts",
      "Token-budget management preventing context window bloat and runaway API token costs",
      "Fallbacks to stateless mode if memory retrieval yields low-confidence matches"
    ],
    architecture_steps: [
      { name: "Chat Interface / CLI", desc: "User prompt input stream and conversation history view" },
      { name: "Memory Ingestion Layer", desc: "Analyzes conversational turns to extract candidate long-term facts" },
      { name: "Memory Index & Store", desc: "Stores categorized facts with embedding vectors for fast similarity retrieval" },
      { name: "Prompt Synthesis Engine", desc: "Injects selected relevant facts into LLM system prompts within token budgets" }
    ],
    engineering_decisions: [
      "Focused on selective retrieval rather than dumping raw conversation history to conserve token budgets and reduce latency.",
      "Gave users clear visibility into stored memory items to maintain privacy and allow deletion of stale facts.",
    ],
    challenges: [
      "Preventing 'memory hallucination' where outdated or weakly-related context distorts the model's current reasoning.",
      "Balancing retrieval sensitivity so the model uses context when helpful but does not force it awkwardly."
    ],
    status_note: "Exploratory research prototype: Context extraction and prompt synthesis routines are implemented and evaluated locally. Multi-tenant distributed storage is planned for future phases.",
    learning: "Explored long-term context engineering for conversational LLMs. Learned the trade-offs between memory retrieval recall and token budget constraints, and developed strategies to mitigate context drift and hallucination across multi-turn interactions.",
    next_steps: [
      "Integrate vector database indexing for scaling to thousands of stored memory items.",
      "Add automated contradiction detection to prune stale or invalidated user facts."
    ]
  }
];

// Additional Projects Carousel Data (Projects 04, 05, and 06)
const ADDITIONAL_PROJECTS = [
  {
    id: "fresh-from-farm",
    number: "04",
    title: "Fresh From Farm",
    category: "FARM-TO-HOME / FLUTTER",
    categoryLabel: "Mobile Application",
    timeline: null, // Year omitted as not documented in existing data
    description: "Fresh From Farm is a Flutter application concept focused on connecting customers with farm-fresh products through a convenient digital shopping experience. The project explores a mobile-first approach to making farm-to-home purchasing easier, with an emphasis on a clear product-browsing experience and accessible mobile interactions.",
    technologies: ["Flutter", "Dart"],
    details: "Focuses on clean mobile UX design, structured product catalog presentation, responsive item filtering, and intuitive navigation flows tailored for straightforward local produce shopping."
  },
  {
    id: "cybersecurity-project",
    number: "05",
    title: "Cybersecurity Project",
    category: "CYBERSECURITY",
    categoryLabel: "Academic Study",
    timeline: "2024",
    description: "An academic exploration of cybersecurity fundamentals, focusing on understanding common security threats, network security concepts, threat assessment, and secure coding practices. The project reflects an interest in identifying potential vulnerabilities and understanding how security principles can help build more dependable software.",
    technologies: ["Security Fundamentals", "Network Security", "Threat Assessment", "Secure Coding Practices"],
    details: "Explores defensive software engineering principles, secure input handling patterns, network traffic inspection fundamentals, and threat modeling methodologies for resilient application design."
  },
  {
    id: "ev-project",
    number: "06",
    title: "EV Project",
    category: "ELECTRIC VEHICLES / EV",
    categoryLabel: "Engineering Exploration",
    timeline: "2024–2025",
    description: "An engineering exploration of electric vehicle systems, focusing on electric powertrain concepts, battery management principles, telemetry, and embedded monitoring fundamentals. The project represents an interest in understanding how software and electronic systems contribute to electric vehicle operation.",
    technologies: ["EV Systems", "Battery Management Concepts", "Embedded Systems", "Telemetry"],
    details: "Investigates powertrain architecture, sensor telemetry collection, battery pack state estimation logic, and embedded communication concepts essential for monitoring electric vehicle subsystems."
  }
];

// Verified Technical Skills aligned directly with resume
const SKILL_CATEGORIES = [
  {
    title: "Programming Languages",
    icon: Code2,
    skills: ["Python", "Java", "C", "JavaScript", "SQL", "Dart"]
  },
  {
    title: "Backend and APIs",
    icon: Database,
    skills: ["FastAPI", "REST APIs", "Node.js", "PHP"]
  },
  {
    title: "Frontend and Mobile",
    icon: Smartphone,
    skills: ["React.js", "Next.js", "HTML", "CSS", "Flutter"]
  },
  {
    title: "Databases",
    icon: Database,
    skills: ["PostgreSQL", "SQLite", "MongoDB", "Firebase"]
  },
  {
    title: "AI and Generative AI",
    icon: BrainCircuit,
    skills: [
      "Google Gemini API",
      "Mem0",
      "LLM API Integration",
      "Prompt Construction",
      "Persistent Memory Retrieval"
    ]
  },
  {
    title: "Core Competencies",
    icon: ShieldCheck,
    skills: [
      "Data Structures and Algorithms",
      "API Integration",
      "Debugging",
      "Integration Testing"
    ]
  }
];

// Truthful Project-Driven Development Journey (Honest academic & project progression)
const JOURNEY_STEPS = [
  {
    period: "2023 – 2027",
    title: "Computer Science Engineering Education",
    tagline: "Academic Coursework at Malnad College of Engineering (Expected 2027)",
    description: "Pursuing undergraduate degree in Computer Science Engineering. Building rigorous foundations in Data Structures and Algorithms, Database Management Systems, Operating Systems, Computer Networks, and Software Engineering."
  },
  {
    period: "MOBILE & IOT",
    title: "MediSync — Connected Medication Adherence",
    tagline: "Flutter Mobile UI, FastAPI Backend & ESP32 Microcontroller",
    description: "Developed MediSync to solve prescription non-adherence. Implemented cross-platform Flutter state management, local notification caching, idempotent REST endpoints with FastAPI, and hardware breadboard integration with an ESP32 dispenser."
  },
  {
    period: "FULL-STACK & FORENSICS",
    title: "RECOVERAI — File Analysis & Diagnostics",
    tagline: "React/Vite Web Interface & Python File Forensics Core",
    description: "Engineered a file recovery and validation platform. Built a responsive React dashboard for drag-and-drop file inspection and developed Python backend routines to inspect file headers, parse magic numbers, and rebuild corrupted containers."
  },
  {
    period: "STATEFUL AI",
    title: "AI Memory Bot — Conversational Context",
    tagline: "Context Engineering with Python, Gemini API & Mem0",
    description: "Explored long-term conversational context retention for LLMs. Structured memory extraction heuristics, semantic relevance retrieval, and prompt synthesis under strict token-budget limits."
  },
  {
    period: "HACKATHONS",
    title: "Hackathon & Ideathon Participation",
    tagline: "ClamStack 24-Hour Hackathon & Avishkar Manthan Ideathon",
    description: "Engaged in collaborative engineering hackathons: ClamStack 24-Hour Hackathon (Dept of CSE, MCE) and Avishkar Manthan Ideathon (IUCEE). Collaborated under tight deadlines to decompose problems, prototype architectures, and present feasibility evaluations."
  },
  {
    period: "CURRENT GOAL",
    title: "Seeking Software Engineering Opportunities",
    tagline: "Preparing for Production Engineering Roles & Internships",
    description: "Actively seeking software engineering, full-stack, mobile, or AI/ML internship opportunities where I can contribute to meaningful products, learn from experienced engineering teams, and expand industry-ready skills."
  }
];

// Verified Achievements & Events Participation
const ACHIEVEMENTS = [
  {
    event: "ClamStack — 24-Hour Hackathon",
    title: "ClamStack — 24-Hour Hackathon",
    organizer: "Department of CSE, Malnad College of Engineering",
    category: "HACKATHON PARTICIPATION",
    description: "Participated in an intensive 24-hour collegiate hackathon focused on rapid problem breakdown, collaborative software prototyping, and sprint execution under tight deadlines.",
    highlight: "24-Hour Rapid Prototyping & System Design",
    certificateUrl: "https://drive.google.com/file/d/1ehgKaX6Yc_Gd2VDvpDT0l5QIUlgStkXu/view?usp=drivesdk"
  },
  {
    event: "Avishkar Manthan Ideathon",
    title: "Avishkar Manthan Ideathon",
    organizer: "IUCEE",
    category: "IDEATHON PARTICIPATION",
    description: "Participated in the regional engineering ideathon evaluating real-world problem statements, formulating technology-driven proposals, and presenting structured engineering feasibility analyses.",
    highlight: "Engineering Ideation & Feasibility Analysis",
    certificateUrl: "https://drive.google.com/file/d/1TaxiQRpLRnEtNQTVzquQk0XmuWPOT4b9/view?usp=drivesdk"
  }
];

// Verified Certifications & Coursework
const CERTIFICATIONS = [
  {
    name: "Full Stack Web Development Bootcamp",
    provider: "Udemy",
    category: "WEB DEVELOPMENT",
    description: "Comprehensive coursework covering modern frontend frameworks, responsive UI layout patterns, RESTful API architecture, backend services, and database persistence.",
    certificateUrl: "https://drive.google.com/file/d/18X_tBdDX8mUPl-qH5lhlpmUJ0YNSzi4u/view?usp=drivesdk"
  },
  {
    name: "Soft Skills Development",
    provider: "NPTEL, IIT Kharagpur",
    category: "PROFESSIONAL COMMUNICATION",
    description: "Academic certification focusing on interpersonal communication, technical presentations, engineering teamwork dynamics, and collaborative workplace effectiveness.",
    certificateUrl: "https://drive.google.com/file/d/1UrQ-tQuvUACxnc48MdFN-sdGkKV6gDaS/view?usp=drivesdk"
  },
  {
    name: "Human–Computer Interaction",
    provider: "IIT Madras",
    category: "UI/UX & ERGONOMICS",
    description: "Rigorous coursework exploring user-centered design, cognitive psychology in interfaces, heuristic evaluation, usability metrics, and interactive software ergonomics.",
    certificateUrl: null
  },
  {
    name: "Getting Started with Artificial Intelligence",
    provider: "IBM",
    category: "AI & MACHINE LEARNING",
    description: "Foundational training covering artificial intelligence principles, machine learning pipelines, deep learning concepts, natural language processing, and ethical AI deployment.",
    certificateUrl: null
  },
  {
    name: "Big Data Analysis",
    provider: "Infosys",
    category: "DATA & ANALYTICS",
    description: "Coursework covering big data fundamentals, distributed data processing concepts, large-scale data storage mechanisms, and analytics pipelines.",
    certificateUrl: "https://drive.google.com/file/d/1LgPt7R5ytDGHaF3tB8e-hFvLzANOIMgY/view?usp=drivesdk"
  }
];

// Verified Technical Interests & Evidence-Based Strengths
const INTERESTS = [
  {
    title: "Artificial Intelligence and Machine Learning",
    icon: BrainCircuit,
    description: "Investigating conversational context retention, LLM prompt engineering, vector retrieval strategies, and practical AI integrations into web and mobile products."
  },
  {
    title: "Full-Stack Development",
    icon: Layers3,
    description: "Building responsive, decoupled web applications using modern React, clean CSS architectures, FastAPI microservices, and reliable database schemas."
  },
  {
    title: "Flutter and Mobile Application Development",
    icon: Smartphone,
    description: "Creating fluid, cross-platform mobile experiences with Flutter, emphasizing offline-first caching, local background services, and hardware-device communication."
  },
  {
    title: "Data Analysis",
    icon: LineChart,
    description: "Analyzing structured telemetry, parsing binary byte containers, and ensuring data integrity through validation checksums and systematic inspection."
  }
];

const PROFESSIONAL_STRENGTHS = [
  {
    title: "End-to-End System Prototyping",
    evidence: "Proven through projects like MediSync, where I unified a Flutter mobile interface, a FastAPI backend, and an ESP32 hardware dispenser rig into a working prototype."
  },
  {
    title: "Defensive Engineering Mindset",
    evidence: "Prioritizing idempotent API endpoints, offline caching, and graceful failure modes over optimistic assumptions (e.g. handling dropped dispenser packets or corrupt file headers)."
  },
  {
    title: "Self-Directed Technical Curiosity",
    evidence: "Quickly learning new paradigms independently—from byte-level hexadecimal analysis in RECOVERAI to context retrieval heuristics in AI Memory Bot."
  }
];

// Visual UI Mockups for Case Studies & Hero (Clearly presented as concept mockups)
function Visual({ kind }) {
  if (kind === "medisync") {
    return (
      <div className="visual visual-med" aria-label="MediSync UI Preview (Concept Mockup)">
        <div className="mockup-indicator-tag">CONCEPT UI MOCKUP</div>
        <div className="phone">
          <div className="phone-speaker"></div>
          <p className="greeting">Good morning<small>Prescription Schedule</small></p>
          <div className="med">
            <i>✚</i>
            <div>
              <b>Vitamin D3 · 1000 IU</b>
              <small>After breakfast · 08:00 AM</small>
            </div>
            <em>✓ Taken</em>
          </div>
          <div className="med faded">
            <i>◷</i>
            <div>
              <b>Omega 3 · Capsule</b>
              <small>With lunch · 01:30 PM</small>
            </div>
          </div>
          <div className="phone-mini-stat">
            <span>TODAY'S DOSES</span>
            <strong>2 of 2 Completed</strong>
          </div>
          <div className="phone-nav">
            <i>⌂</i><i>◷</i><i>▤</i><i>●</i>
          </div>
        </div>
        <b className="stamp">CARE<br />IN SYNC</b>
      </div>
    );
  }

  if (kind === "recoverai") {
    return (
      <div className="visual visual-recover" aria-label="RECOVERAI UI Preview (Concept Mockup)">
        <div className="mockup-indicator-tag">CONCEPT UI MOCKUP</div>
        <div className="file-window">
          <div className="window-bar">
            <i></i><i></i><i></i>
            <b>RECOVERY_CORE // BYTE_ANALYZER</b>
          </div>
          <div className="scan-label">
            SCAN STATUS <strong>SIGNATURE VALIDATED</strong>
          </div>
          <div className="scan-line">
            <i></i>
          </div>
          <div className="file-row">
            <span>PNG</span>
            <div>
              <b>sample_corrupt_file.png</b>
              <small>Magic Header 89 50 4E 47 Restored</small>
            </div>
            <strong>RESTORED</strong>
          </div>
          <div className="file-row">
            <span>PDF</span>
            <div>
              <b>project_report.pdf</b>
              <small>Trailer dictionary reconstruction</small>
            </div>
            <strong>QUEUED</strong>
          </div>
          <div className="terminal">
            › validating byte stream offsets...<br />
            › reconstructing container metadata...<br />
            › CRC checksum matched successfully.
          </div>
        </div>
        <b className="crosshair">+</b>
      </div>
    );
  }

  return (
    <div className="visual visual-memory" aria-label="AI Memory Bot Preview (Concept Mockup)">
      <div className="mockup-indicator-tag">CONCEPT UI MOCKUP</div>
      <div className="orbit orbit-a"></div>
      <div className="orbit orbit-b"></div>
      <div className="memory-core">
        <BrainCircuit size={40} />
      </div>
      <div className="node node-one">Fact Extracted <b>01</b></div>
      <div className="node node-two">Semantic Match <b>02</b></div>
      <div className="node node-three">Context Injected <b>03</b></div>
      <b className="memory-caption">CONTEXTUAL<br />PERSISTENCE</b>
    </div>
  );
}

// Styled title helper ensuring signal-red highlight on key words
function renderStyledTitle(title) {
  if (title === "MediSync") {
    return <>Medi<span className="case-x">Sync</span></>;
  }
  if (title === "RECOVERAI") {
    return <>RECOVER<span className="case-x">AI</span></>;
  }
  if (title === "AI Memory Bot") {
    return <>AI Memory <span className="case-x">Bot</span></>;
  }
  const parts = title.split(" ");
  if (parts.length > 1) {
    const last = parts.pop();
    return <>{parts.join(" ")} <span className="case-x">{last}</span></>;
  }
  return <>{title.slice(0, -3)}<span className="case-x">{title.slice(-3)}</span></>;
}

// Safely normalize any input (arrays, JSON strings, comma/semicolon/newline-delimited text) into an array of strings
function normalizeArray(val, fallback = []) {
  if (Array.isArray(val)) {
    return val.filter(item => item !== null && item !== undefined && String(item).trim() !== "");
  }
  if (typeof val === "string") {
    const trimmed = val.trim();
    if (!trimmed) return Array.isArray(fallback) ? fallback : [];
    if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
      try {
        const parsed = JSON.parse(trimmed);
        if (Array.isArray(parsed)) {
          return parsed.filter(item => item !== null && item !== undefined && String(item).trim() !== "");
        }
      } catch {
        // Fall back to text splitting
      }
    }
    if (trimmed.includes("\n")) {
      return trimmed.split("\n").map(s => s.replace(/^[•\-\*›]\s*/, "").trim()).filter(Boolean);
    }
    if (trimmed.includes(";")) {
      return trimmed.split(";").map(s => s.trim()).filter(Boolean);
    }
    if (trimmed.includes(",")) {
      return trimmed.split(",").map(s => s.trim()).filter(Boolean);
    }
    return [trimmed];
  }
  return Array.isArray(fallback) ? fallback : [];
}

// Dedicated LinkedIn Profile Restriction Page (/linkedin-unavailable)
function LinkedInUnavailablePage({ onBack, resumeUrl, email }) {
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "instant" });
  }, []);

  return (
    <div className="shell linkedin-page-shell">
      <header className="topbar">
        <button
          type="button"
          className="brand brand-btn"
          onClick={onBack}
          aria-label="Back to Tejas C K Portfolio"
        >
          <b>T<span>.</span></b>
          <div className="brand-text">
            <strong>TEJAS C K</strong>
            <small>SOFTWARE DEVELOPER</small>
          </div>
        </button>

        <button type="button" className="nav-talk-btn" onClick={onBack}>
          <ArrowLeft size={14} /> Back to Portfolio
        </button>
      </header>

      <main className="linkedin-main wrap">
        <div className="linkedin-card reveal visible">
          <div className="linkedin-badge-row">
            <span className="linkedin-status-badge">
              <span className="live-dot amber" aria-hidden="true"></span>
              ACCOUNT RESTRICTION NOTICE
            </span>
            <span className="linkedin-code-tag">NOTICE // LI-RESTRICTED</span>
          </div>

          <div className="linkedin-icon-banner" aria-hidden="true">
            <Linkedin size={32} />
          </div>

          <h1 className="linkedin-title">LinkedIn Profile Temporarily Unavailable</h1>

          <div className="linkedin-copy">
            <p>
              Thank you for your interest in connecting with me. My LinkedIn profile is currently inaccessible due to an account restriction, and I am unable to access or restore it at this time. I apologize for the inconvenience.
            </p>
            <p>
              In the meantime, you can review my resume to learn more about my education, technical skills, and projects. You are also welcome to contact me directly by email.
            </p>
          </div>

          <div className="linkedin-actions">
            <a
              href={resumeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="button primary"
            >
              <FileText size={16} /> View My Resume <ExternalLink size={14} />
            </a>

            <a
              href={`mailto:${email}`}
              className="button secondary"
            >
              <Mail size={16} /> Contact Me by Email <ArrowUpRight size={14} />
            </a>

            <button
              type="button"
              onClick={onBack}
              className="button ghost"
            >
              <ArrowLeft size={16} /> Back to Portfolio
            </button>
          </div>

          <div className="linkedin-note-box">
            <small>
              Direct contact channels: Email (<a href={`mailto:${email}`}>{email}</a>) · GitHub (<a href="https://github.com/tejas388" target="_blank" rel="noopener noreferrer">github.com/tejas388</a>)
            </small>
          </div>
        </div>
      </main>

      <footer className="footer-section wrap">
        <div className="footer-bottom">
          <span>TEJAS C K · PORTFOLIO 2026</span>
          <button type="button" onClick={onBack} className="back-to-top">
            ← BACK TO PORTFOLIO
          </button>
          <small>© {new Date().getFullYear()} Tejas C K. All rights reserved.</small>
        </div>
      </footer>
    </div>
  );
}

// Design C: Revolving Interactive Project-Card Carousel
function MoreProjectsCarousel({ projects }) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [expandedId, setExpandedId] = useState(null);
  const [touchStartX, setTouchStartX] = useState(null);
  const [touchEndX, setTouchEndX] = useState(null);

  const total = projects.length;

  const nextProject = () => {
    setActiveIndex((prev) => (prev + 1) % total);
  };

  const prevProject = () => {
    setActiveIndex((prev) => (prev - 1 + total) % total);
  };

  const handleCardClick = (idx) => {
    if (idx !== activeIndex) {
      setActiveIndex(idx);
    }
  };

  const toggleExpand = (id, e) => {
    e.stopPropagation();
    setExpandedId((prev) => (prev === id ? null : id));
  };

  const handleKeyDown = (e) => {
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      prevProject();
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      nextProject();
    }
  };

  const handleTouchStart = (e) => {
    if (e.touches && e.touches[0]) {
      setTouchStartX(e.touches[0].clientX);
      setTouchEndX(null);
    }
  };

  const handleTouchMove = (e) => {
    if (e.touches && e.touches[0]) {
      setTouchEndX(e.touches[0].clientX);
    }
  };

  const handleTouchEnd = () => {
    if (touchStartX !== null && touchEndX !== null) {
      const distance = touchStartX - touchEndX;
      if (distance > 45) {
        nextProject();
      } else if (distance < -45) {
        prevProject();
      }
    }
    setTouchStartX(null);
    setTouchEndX(null);
  };

  return (
    <div
      className="carousel-wrapper"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      role="region"
      aria-roledescription="carousel"
      aria-label="Additional Projects Revolving Carousel"
    >
      <div className="carousel-stage">
        {projects.map((proj, idx) => {
          // Revolving relative position: 0 = center/active, 1 = right/next, 2 = left/prev
          const diff = (idx - activeIndex + total) % total;
          const isActive = diff === 0;
          const isNext = diff === 1;
          const isPrev = diff === 2;
          const isExpanded = expandedId === proj.id;

          let positionClass = "carousel-item-hidden";
          if (isActive) positionClass = "carousel-item-active";
          else if (isPrev) positionClass = "carousel-item-prev";
          else if (isNext) positionClass = "carousel-item-next";

          return (
            <article
              key={proj.id}
              className={`carousel-card ${positionClass} ${isExpanded ? "expanded" : ""}`}
              onClick={() => handleCardClick(idx)}
              role="group"
              aria-roledescription="slide"
              aria-label={`${proj.number}: ${proj.title}`}
              aria-hidden={!isActive}
            >
              <div className="carousel-card-inner">
                {/* Header Metadata */}
                <div className="carousel-card-header">
                  <div className="carousel-card-meta">
                    <span className="carousel-proj-number">{proj.number}</span>
                    <span className="carousel-proj-cat-badge">{proj.category}</span>
                  </div>
                  {proj.timeline && (
                    <span className="carousel-proj-timeline">{proj.timeline}</span>
                  )}
                </div>

                {/* Project Title */}
                <h3 className="carousel-proj-title">{proj.title}</h3>

                {/* Category Type Label */}
                <div className="carousel-cat-label-row">
                  <span className="carousel-cat-type-pill">{proj.categoryLabel}</span>
                </div>

                {/* Purpose / Scope Description */}
                <p className="carousel-proj-desc">{proj.description}</p>

                {/* Inline Expanded Detail Panel */}
                {isExpanded && (
                  <div className="carousel-card-expanded-content">
                    <div className="carousel-expanded-divider"></div>
                    <div className="carousel-expanded-block">
                      <span className="carousel-expanded-heading">SCOPE & ARCHITECTURAL FOCUS</span>
                      <p className="carousel-expanded-text">{proj.details}</p>
                    </div>
                  </div>
                )}

                {/* Verified Technologies / Focus Chips */}
                <div className="carousel-tech-stack">
                  <span className="carousel-tech-label">CORE TECHNOLOGIES & FOCUS</span>
                  <div className="carousel-tech-chips">
                    {proj.technologies.map((tech) => (
                      <span key={tech} className="carousel-tech-chip">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Card Action Controls */}
                <div className="carousel-card-footer">
                  <button
                    type="button"
                    className="carousel-expand-btn"
                    onClick={(e) => toggleExpand(proj.id, e)}
                    aria-expanded={isExpanded}
                    aria-label={isExpanded ? `Collapse ${proj.title} details` : `Explore ${proj.title} details`}
                  >
                    {isExpanded ? (
                      <>
                        <span>COLLAPSE DETAILS</span>
                        <ArrowUpRight size={14} className="expand-icon" />
                      </>
                    ) : (
                      <>
                        <span>EXPLORE PROJECT</span>
                        <ArrowDownRight size={14} className="expand-icon" />
                      </>
                    )}
                  </button>
                  <span className="carousel-action-hint">
                    {isActive
                      ? isExpanded
                        ? "Details revealed inline"
                        : "Click to expand details"
                      : "Click card to focus"}
                  </span>
                </div>
              </div>
            </article>
          );
        })}
      </div>

      {/* Carousel Navigation Controls */}
      <div className="carousel-controls">
        <button
          type="button"
          className="carousel-nav-btn prev"
          onClick={prevProject}
          aria-label="Previous project in carousel"
        >
          <ChevronLeft size={18} />
        </button>

        {/* Position Indicators / Clickable Dots */}
        <div className="carousel-indicators" role="tablist" aria-label="Select carousel project">
          {projects.map((proj, idx) => (
            <button
              key={proj.id}
              type="button"
              role="tab"
              aria-selected={activeIndex === idx}
              aria-label={`Jump to project ${proj.number}: ${proj.title}`}
              className={`carousel-dot-btn ${activeIndex === idx ? "active" : ""}`}
              onClick={() => setActiveIndex(idx)}
            >
              <span className="dot-index">{proj.number}</span>
              <span className="dot-indicator" aria-hidden="true"></span>
            </button>
          ))}
        </div>

        <span className="carousel-counter" aria-live="polite">
          0{activeIndex + 1} / 0{total}
        </span>

        <button
          type="button"
          className="carousel-nav-btn next"
          onClick={nextProject}
          aria-label="Next project in carousel"
        >
          <ChevronRight size={18} />
        </button>
      </div>
    </div>
  );
}

// Complete Main Portfolio View
function PortfolioView({
  projects,
  certifications = CERTIFICATIONS,
  achievements = ACHIEVEMENTS,
  activeSlug,
  setActiveSlug,
  activeSection,
  setActiveSection,
  menu,
  setMenu,
  lightboxOpen,
  setLightboxOpen,
  imgFailed,
  setImgFailed,
  form,
  setForm,
  status,
  submitContact,
  scrollToSection,
  onNavigateToLinkedIn,
  currentYear
}) {
  const activeProject = projects.find(p => p.slug === activeSlug) || projects[0] || DEFAULT_PROJECTS[0];
  const displayAchievements = (Array.isArray(achievements) && achievements.length > 0)
    ? achievements
    : ACHIEVEMENTS;
  const displayCertifications = (Array.isArray(certifications) && certifications.length > 0)
    ? certifications
    : CERTIFICATIONS;

  const handleDeviceSelect = (slug) => {
    setActiveSlug(slug);
  };

  // IntersectionObserver for active navigation section tracking
  useEffect(() => {
    const sectionIds = [
      "about",
      "about-details",
      "projects",
      "case-studies",
      "more-projects",
      "skills",
      "journey",
      "achievements",
      "certifications",
      "interests",
      "contact"
    ];

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            if (id === "about-details") {
              setActiveSection("about");
            } else if (id === "case-studies" || id === "more-projects") {
              setActiveSection("projects");
            } else {
              setActiveSection(id);
            }
          }
        });
      },
      { threshold: 0.15, rootMargin: "-80px 0px -40% 0px" }
    );

    sectionIds.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [setActiveSection]);

  // IntersectionObserver for scroll reveals: immediately reveals visible viewport nodes, then observes remainder
  useEffect(() => {
    const nodes = document.querySelectorAll("[data-reveal]");
    if (!("IntersectionObserver" in window)) {
      nodes.forEach(n => n.classList.add("visible"));
      return;
    }

    // Immediately reveal elements that are already in the visible viewport
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
    nodes.forEach(node => {
      const rect = node.getBoundingClientRect();
      if (rect.top < viewportHeight && rect.bottom > 0) {
        node.classList.add("visible");
      }
    });

    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(e => {
          if (e.isIntersecting) {
            e.target.classList.add("visible");
            observer.unobserve(e.target);
          }
        });
      },
      { threshold: 0.05, rootMargin: "60px 0px 60px 0px" }
    );

    nodes.forEach(n => {
      if (!n.classList.contains("visible")) {
        observer.observe(n);
      }
    });

    return () => observer.disconnect();
  }, [projects]);

  return (
    <div className="shell">
      {/* Top Navigation */}
      <header className="topbar">
        <a
          className="brand"
          href="#about"
          onClick={(e) => {
            e.preventDefault();
            scrollToSection("#about");
          }}
          aria-label="Tejas C K Home"
        >
          <b>T<span>.</span></b>
          <div className="brand-text">
            <strong>TEJAS C K</strong>
            <small>SOFTWARE DEVELOPER</small>
          </div>
        </a>

        <nav className={menu ? "nav open" : "nav"} aria-label="Main Navigation">
          <a
            href="#about"
            className={activeSection === "about" ? "active" : ""}
            onClick={(e) => { e.preventDefault(); scrollToSection("#about"); }}
          >
            About
          </a>
          <a
            href="#projects"
            className={activeSection === "projects" ? "active" : ""}
            onClick={(e) => { e.preventDefault(); scrollToSection("#projects"); }}
          >
            Projects <sup>03</sup>
          </a>
          <a
            href="#skills"
            className={activeSection === "skills" ? "active" : ""}
            onClick={(e) => { e.preventDefault(); scrollToSection("#skills"); }}
          >
            Skills
          </a>
          <a
            href="#journey"
            className={activeSection === "journey" ? "active" : ""}
            onClick={(e) => { e.preventDefault(); scrollToSection("#journey"); }}
          >
            Journey
          </a>
          <a
            href="#achievements"
            className={activeSection === "achievements" ? "active" : ""}
            onClick={(e) => { e.preventDefault(); scrollToSection("#achievements"); }}
          >
            Achievements
          </a>
          <a
            href="#certifications"
            className={activeSection === "certifications" ? "active" : ""}
            onClick={(e) => { e.preventDefault(); scrollToSection("#certifications"); }}
          >
            Certifications
          </a>
          <a
            href="#interests"
            className={activeSection === "interests" ? "active" : ""}
            onClick={(e) => { e.preventDefault(); scrollToSection("#interests"); }}
          >
            Interests
          </a>
          <a
            href="#contact"
            className={activeSection === "contact" ? "active" : ""}
            onClick={(e) => { e.preventDefault(); scrollToSection("#contact"); }}
          >
            Contact
          </a>
          {CONFIG.resumeUrl && (
            <a
              href={CONFIG.resumeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="nav-resume-link"
              aria-label="View Resume in Google Drive (opens in new tab)"
            >
              Resume ↗
            </a>
          )}
          <button className="nav-talk-btn" onClick={() => scrollToSection("#contact")}>
            Let's Talk <ArrowUpRight size={14} />
          </button>
        </nav>

        <button
          className="mobile-menu"
          aria-label={menu ? "Close Navigation Menu" : "Open Navigation Menu"}
          aria-expanded={menu}
          onClick={() => setMenu(!menu)}
        >
          {menu ? <X size={22} /> : <Menu size={22} />}
        </button>
      </header>

      <main id="top">
        {/* SECTION 1: ABOUT ME & PERSONAL INTRODUCTION */}
        <section className="personal-hero" id="about" aria-label="About Me & Personal Introduction">
          <div className="personal-hero-container reveal visible">
            {/* Top-left area: Profile portrait thumbnail & kicker */}
            <div className="hero-profile-row">
              <button
                type="button"
                className="portrait-thumbnail-btn"
                onClick={() => setLightboxOpen(true)}
                aria-label="View full-size portrait of Tejas C K"
                title="Click to view full portrait"
              >
                {!imgFailed ? (
                  <img
                    src={PORTRAIT_SRC}
                    alt="Tejas C K — Portrait"
                    className="portrait-img"
                    onError={() => setImgFailed(true)}
                  />
                ) : (
                  <div className="portrait-fallback" aria-hidden="true">
                    TC<span className="tck-dot">K</span>
                  </div>
                )}
                <span className="portrait-zoom-hint" aria-hidden="true">
                  <ZoomIn size={12} />
                </span>
              </button>

              <div className="hero-profile-meta">
                <div className="hero-kicker-tag">
                  <span className="live-dot" aria-hidden="true"></span>
                  <span>PERSONAL PORTFOLIO // 2026</span>
                </div>
                <div className="hero-status-pill">
                  <span>{CONFIG.statusBadge}</span>
                </div>
              </div>
            </div>

            {/* Primary Page Heading */}
            <h1>
              Tejas C <span className="accent-k">K</span>
            </h1>

            {/* Clear Role Headline */}
            <p className="hero-role-headline">
              <span>Computer Science Engineering Student</span>
              <span className="role-divider">|</span>
              <span>Aspiring Software Engineer</span>
            </p>

            {/* Short Introduction Paragraph */}
            <p className="hero-intro-text">
              {CONFIG.shortIntro}
            </p>

            {/* Action Buttons: Explore Work, View Resume, Contact */}
            <div className="hero-actions-row">
              <button
                type="button"
                className="button primary hero-cta-btn"
                onClick={() => scrollToSection("#projects")}
              >
                Explore Projects <ArrowDownRight size={16} />
              </button>

              {CONFIG.resumeUrl && (
                <a
                  className="button secondary hero-cta-btn"
                  href={CONFIG.resumeUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <FileText size={15} /> View Resume <ExternalLink size={14} />
                </a>
              )}

              <button
                type="button"
                className="button ghost hero-cta-btn"
                onClick={() => scrollToSection("#contact")}
              >
                Get In Touch <ArrowUpRight size={15} />
              </button>
            </div>

            {/* Down cue directing visitors to the candidate snapshot & about details */}
            <button
              type="button"
              className="showcase-scroll-cue"
              onClick={() => scrollToSection("#about-details")}
              aria-label="Scroll to candidate snapshot and about details"
            >
              <span>CANDIDATE SNAPSHOT & BACKGROUND</span>
              <i>↓</i>
            </button>
          </div>
        </section>

        {/* SECTION 1.B: ABOUT ME DETAILS & CANDIDATE SNAPSHOT */}
        <section className="about-section wrap" id="about-details" aria-label="About Me Details">
          <div className="section-header reveal" data-reveal>
            <p className="eyebrow">ABOUT ME</p>
            <h2>
              Building software with <span>curiosity<span className="red">.</span></span>
            </h2>
            <p className="section-lead">
              Computer Science Engineering student at Malnad College of Engineering (graduating 2027), focused on building dependable digital products across full-stack web, Flutter mobile applications, and practical AI/ML integrations.
            </p>
          </div>

          <div className="about-grid">
            <div className="about-content reveal" data-reveal>
              <p>
                {CONFIG.aboutSummary}
              </p>
              <p>
                My approach to software engineering centers on <strong>building end-to-end solutions</strong>. Rather than treating frontend design, backend architecture, and data persistence as disconnected silos, I enjoy connecting every layer—from responsive user interfaces down to database tables and hardware signals.
              </p>
              <p>
                Currently maintaining an <strong>8.0 / 10 CGPA</strong> while directing time toward hands-on software development. I hold <strong>no formal industry experience yet</strong> — my technical growth is fueled by academic coursework, building full-stack and mobile prototypes, and exploring applied AI. I value code clarity, thoughtful API contracts, and collaborative teamwork.
              </p>

              <div className="about-highlights">
                <div className="highlight-item">
                  <CheckCircle2 size={18} className="highlight-icon" />
                  <div>
                    <strong>Practical Problem Solving</strong>
                    <small>Focused on real human needs, not toy implementations.</small>
                  </div>
                </div>
                <div className="highlight-item">
                  <CheckCircle2 size={18} className="highlight-icon" />
                  <div>
                    <strong>Full-Stack & Mobile Breadth</strong>
                    <small>Flutter, React.js, FastAPI, Python, PostgreSQL, and SQLite.</small>
                  </div>
                </div>
                <div className="highlight-item">
                  <CheckCircle2 size={18} className="highlight-icon" />
                  <div>
                    <strong>Honest Engineering Mindset</strong>
                    <small>Transparent about trade-offs, limitations, and areas to improve.</small>
                  </div>
                </div>
              </div>

              <div className="about-actions">
                <button
                  type="button"
                  className="button primary"
                  onClick={() => scrollToSection("#projects")}
                >
                  Explore Featured Projects <ArrowDownRight size={15} />
                </button>
                {CONFIG.resumeUrl && (
                  <a
                    className="button secondary"
                    href={CONFIG.resumeUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View Resume <ExternalLink size={14} />
                  </a>
                )}
                <button
                  type="button"
                  className="button ghost"
                  onClick={() => scrollToSection("#contact")}
                >
                  Get In Touch <ArrowUpRight size={15} />
                </button>
              </div>
            </div>

            <div className="about-card reveal" data-reveal>
              <div className="card-badge">CANDIDATE SNAPSHOT</div>
              <ul className="snapshot-list">
                <li>
                  <span>Degree & College</span>
                  <strong>Computer Science Engineering · Malnad College of Engineering</strong>
                </li>
                <li>
                  <span>Graduation Year</span>
                  <strong>2027 (Expected)</strong>
                </li>
                <li>
                  <span>Academic Record</span>
                  <strong>8.0 / 10 CGPA</strong>
                </li>
                <li>
                  <span>Professional Experience</span>
                  <strong>No formal industry experience yet (Project-driven development)</strong>
                </li>
                <li>
                  <span>Current Focus</span>
                  <strong>Personal & academic projects, technical skill development</strong>
                </li>
                <li>
                  <span>Target Roles</span>
                  <strong>Software Engineering Intern, Full-Stack, Flutter, AI/ML</strong>
                </li>
                <li>
                  <span>Location</span>
                  <strong>{CONFIG.location}</strong>
                </li>
                <li>
                  <span>Core Languages</span>
                  <strong>Python, Java, C, JavaScript, SQL, Dart</strong>
                </li>
                <li>
                  <span>Primary Stacks</span>
                  <strong>Flutter, React.js, FastAPI, PostgreSQL, SQLite</strong>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* SECTION 2: HERO WITH FLOATING DEVICES & INTERACTIVE PROJECT SELECTOR */}
        <section className="case-hero" id="projects" aria-label="Featured Projects Hero">
          <div className="case-hero-copy">
            <div className="case-kicker">
              <span className="live-dot" aria-hidden="true"></span>
              <span>CASE STUDIES / FEATURED WORK</span>
            </div>

            {/* Project Switcher Bar */}
            <div className="hero-switcher" role="tablist" aria-label="Select featured project">
              {projects.map((p, idx) => (
                <button
                  key={p.slug}
                  role="tab"
                  id={`tab-${p.slug}`}
                  aria-selected={activeSlug === p.slug}
                  aria-controls={`case-study-${p.slug}`}
                  className={`switcher-pill ${activeSlug === p.slug ? "active" : ""}`}
                  onClick={() => setActiveSlug(p.slug)}
                >
                  <span className="pill-idx">0{idx + 1}</span>
                  <span className="pill-title">{p.title}</span>
                </button>
              ))}
            </div>

            {/* Dynamic Featured Project Title with Stable Container Height */}
            <div className="hero-title-container">
              <h2 className="hero-title" key={activeProject.slug}>
                {renderStyledTitle(activeProject.title)}
              </h2>
            </div>

            <p className="case-subtitle" key={`sub-${activeProject.slug}`}>
              {activeProject.summary}
            </p>

            {/* Project Metadata */}
            <div className="case-meta" key={`meta-${activeProject.slug}`}>
              <div>
                <small>ROLE</small>
                <b>{activeProject.role}</b>
              </div>
              <div>
                <small>CATEGORY</small>
                <b>{activeProject.category}</b>
              </div>
              <div>
                <small>TIMELINE</small>
                <b>{activeProject.year}</b>
              </div>
              <div>
                <small>STATUS</small>
                <b className="status-highlight">{CONFIG.statusBadge}</b>
              </div>
            </div>

            {/* Hero Actions */}
            <div className="hero-actions">
              <button
                className="case-explore"
                onClick={() => scrollToSection(`#case-study-${activeProject.slug}`)}
                aria-label={`Explore ${activeProject.title} case study`}
              >
                EXPLORE CASE STUDY <ArrowDownRight size={16} />
              </button>

              {activeProject.github_url && (
                <a
                  className="hero-github"
                  href={activeProject.github_url}
                  target="_blank"
                  rel="noreferrer"
                  aria-label={`View ${activeProject.title} source code on GitHub`}
                >
                  <Github size={15} /> SOURCE CODE <ArrowUpRight size={14} />
                </a>
              )}

              <button
                className="hero-quiet-btn"
                onClick={() => scrollToSection("#case-studies")}
              >
                CASE STUDIES ({projects.length}) ↓
              </button>

              <button
                className="hero-quiet-btn hero-more-btn"
                onClick={() => scrollToSection("#more-projects")}
                aria-label="View more projects"
              >
                MORE PROJECTS (0{ADDITIONAL_PROJECTS.length}) ↓
              </button>
            </div>
          </div>

          {/* Right: Floating Mobile Devices */}
          <div className="floating-devices" aria-label="Interactive 3D mobile project mockups">
            {/* Device 1: MediSync */}
            <div
              className={`device-link device-one ${activeSlug === "medisync" ? "device-active" : ""}`}
              onClick={() => handleDeviceSelect("medisync")}
            >
              <button
                type="button"
                className="device-phone-btn"
                aria-label="Select MediSync project preview"
                aria-pressed={activeSlug === "medisync"}
                onClick={(e) => { e.stopPropagation(); handleDeviceSelect("medisync"); }}
              >
                <div className="device-phone">
                  <div className="device-notch"></div>
                  <div className="device-brand">
                    MediSync <span>+</span>
                  </div>
                  <div className="device-label">MEDICATION SCHEDULE</div>
                  <div className="device-card med-card">
                    <i>✚</i>
                    <span>
                      <b>Daily medicine</b>
                      <small>Vitamin D3 · 08:00 AM</small>
                    </span>
                    <em>✓ Taken</em>
                  </div>
                  <div className="device-card med-card">
                    <i>◷</i>
                    <span>
                      <b>Next reminder</b>
                      <small>Omega 3 · 01:30 PM</small>
                    </span>
                  </div>
                  <div className="device-chart" aria-hidden="true">
                    <span></span><span></span><span></span><span></span><span></span><span></span>
                  </div>
                  <div className="device-nav" aria-hidden="true">
                    <i>⌂</i><i>◷</i><i>▤</i><i>●</i>
                  </div>
                </div>
              </button>
              <div className="device-caption-row">
                <span className="device-caption-label">01 / MEDISYNC</span>
                <a
                  className="device-jump-link"
                  href="#case-study-medisync"
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveSlug("medisync");
                    scrollToSection("#case-study-medisync");
                  }}
                  aria-label="Navigate to MediSync case study"
                >
                  VIEW STUDY ↗
                </a>
              </div>
            </div>

            {/* Device 2: RECOVERAI */}
            <div
              className={`device-link device-two ${activeSlug === "recoverai" ? "device-active" : ""}`}
              onClick={() => handleDeviceSelect("recoverai")}
            >
              <button
                type="button"
                className="device-phone-btn"
                aria-label="Select RECOVERAI project preview"
                aria-pressed={activeSlug === "recoverai"}
                onClick={(e) => { e.stopPropagation(); handleDeviceSelect("recoverai"); }}
              >
                <div className="device-phone recover-screen">
                  <div className="device-notch"></div>
                  <div className="device-brand">
                    RECOVER<span>AI</span>
                  </div>
                  <div className="recover-orb" aria-hidden="true">↻</div>
                  <div className="recover-progress" aria-hidden="true">
                    <span></span>
                  </div>
                  <div className="recover-line">
                    <b>image_corrupt_042.png</b>
                    <small>PNG Magic Repaired</small>
                    <em>RESTORED</em>
                  </div>
                  <div className="recover-line">
                    <b>document_final.pdf</b>
                    <small>Trailer Reconstruction</small>
                    <em>QUEUED</em>
                  </div>
                  <div className="device-nav" aria-hidden="true">
                    <i>⌂</i><i>⌕</i><i>▤</i><i>●</i>
                  </div>
                </div>
              </button>
              <div className="device-caption-row">
                <span className="device-caption-label">02 / RECOVERAI</span>
                <a
                  className="device-jump-link"
                  href="#case-study-recoverai"
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveSlug("recoverai");
                    scrollToSection("#case-study-recoverai");
                  }}
                  aria-label="Navigate to RECOVERAI case study"
                >
                  VIEW STUDY ↗
                </a>
              </div>
            </div>

            {/* Device 3: AI Memory Bot */}
            <div
              className={`device-link device-three ${activeSlug === "ai-memory-bot" ? "device-active" : ""}`}
              onClick={() => handleDeviceSelect("ai-memory-bot")}
            >
              <button
                type="button"
                className="device-phone-btn"
                aria-label="Select AI Memory Bot project preview"
                aria-pressed={activeSlug === "ai-memory-bot"}
                onClick={(e) => { e.stopPropagation(); handleDeviceSelect("ai-memory-bot"); }}
              >
                <div className="device-phone memory-screen">
                  <div className="device-notch"></div>
                  <div className="device-brand">
                    Memory Bot <span>✳</span>
                  </div>
                  <div className="chat-bubble bot-bubble">
                    Welcome back! I retained your project constraints.
                  </div>
                  <div className="chat-bubble user-bubble">
                    What database were we testing?
                  </div>
                  <div className="memory-tag">
                    RECALLED CONTEXT: SQLite local <b>✓</b>
                  </div>
                  <div className="chat-input" aria-hidden="true">
                    Ask anything… <span>↑</span>
                  </div>
                  <div className="device-nav" aria-hidden="true">
                    <i>⌂</i><i>◌</i><i>▤</i><i>●</i>
                  </div>
                </div>
              </button>
              <div className="device-caption-row">
                <span className="device-caption-label">03 / AI MEMORY BOT</span>
                <a
                  className="device-jump-link"
                  href="#case-study-ai-memory-bot"
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveSlug("ai-memory-bot");
                    scrollToSection("#case-study-ai-memory-bot");
                  }}
                  aria-label="Navigate to AI Memory Bot case study"
                >
                  VIEW STUDY ↗
                </a>
              </div>
            </div>

            <div className="device-orbit orbit-left" aria-hidden="true"></div>
            <div className="device-orbit orbit-right" aria-hidden="true"></div>
          </div>

          <div className="case-hero-footer">
            <span>SCROLL TO EXPLORE CASE STUDIES <i>↓</i></span>
            <button
              type="button"
              className="case-hero-more-btn"
              onClick={() => scrollToSection("#more-projects")}
              aria-label="Explore more projects (Projects 04, 05, and 06)"
            >
              MORE PROJECTS (04–06) <i>↓</i>
            </button>
            <span>MOBILE · FULL-STACK · AI/ML</span>
          </div>
        </section>

        {/* SECTION 2.B: FEATURED PROJECT CASE STUDIES */}
        <section className="case-studies-section wrap" id="case-studies" aria-label="Featured Project Case Studies">
          <div className="section-header reveal" data-reveal>
            <p className="eyebrow">FEATURED CASE STUDIES</p>
            <h2>
              Deep dives into <span>the build<span className="red">.</span></span>
            </h2>
            <p className="section-lead">
              Comprehensive architectural breakdowns, technical decisions, and lessons learned from three selected projects.
            </p>
          </div>

          <div className="case-studies-container">
            {projects.map((p, idx) => {
              const prevProject = projects[(idx - 1 + projects.length) % projects.length];
              const nextProject = projects[(idx + 1) % projects.length];

              return (
                <article
                  id={`case-study-${p.slug}`}
                  key={p.slug}
                  className={`case-study-card reveal ${p.accent || "red"}`}
                  data-reveal
                >
                  {/* Case Study Card Header */}
                  <div className="case-header">
                    <div className="case-top-meta">
                      <span className="case-number">{p.number}</span>
                      <span className="case-cat-badge">{p.category}</span>
                      <span className="case-year">{p.year}</span>
                    </div>
                    <h3 className="case-card-title">{p.title}</h3>
                    <p className="case-card-summary">{p.summary}</p>

                    <div className="case-stack-pills">
                      {(Array.isArray(p.stack) ? p.stack : []).map(tech => (
                        <span key={tech} className="stack-pill">{tech}</span>
                      ))}
                    </div>
                  </div>

                  {/* Case Study Body: Split Columns */}
                  <div className="case-body-grid">
                    {/* Left Column: Problem, Contribution, Features, Architecture */}
                    <div className="case-main-col">
                      {/* Problem Statement */}
                      <div className="case-block">
                        <h4>
                          <AlertCircle size={16} /> Problem & Intended Users
                        </h4>
                        <p>{p.problem}</p>
                        {p.target_users && (
                          <div className="target-users-box">
                            <strong>Target Audience:</strong> {p.target_users}
                          </div>
                        )}
                      </div>

                      {/* My Contribution */}
                      <div className="case-block">
                        <h4>
                          <Code2 size={16} /> My Contribution
                        </h4>
                        <p>{p.contribution}</p>
                      </div>

                      {/* Key Features */}
                      {Array.isArray(p.features) && p.features.length > 0 && (
                        <div className="case-block">
                          <h4>
                            <CheckCircle2 size={16} /> Key Features
                          </h4>
                          <ul className="features-list">
                            {p.features.map((feat, fIdx) => (
                              <li key={fIdx}>
                                <i>›</i> <span>{feat}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Architecture Flow Diagram */}
                      {Array.isArray(p.architecture_steps) && p.architecture_steps.length > 0 && (
                        <div className="case-block">
                          <h4>
                            <Workflow size={16} /> Architecture & System Flow
                          </h4>
                          <div className="architecture-flow">
                            {p.architecture_steps.map((step, sIdx) => (
                              <div key={sIdx} className="arch-step-wrapper">
                                <div className="arch-step-box">
                                  <div className="arch-step-num">0{sIdx + 1}</div>
                                  <div className="arch-step-content">
                                    <strong>{step.name}</strong>
                                    <small>{step.desc}</small>
                                  </div>
                                </div>
                                {sIdx < p.architecture_steps.length - 1 && (
                                  <div className="arch-connector" aria-hidden="true">
                                    <span>↓</span>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Engineering Decisions & Trade-offs */}
                      {Array.isArray(p.engineering_decisions) && p.engineering_decisions.length > 0 && (
                        <div className="case-block">
                          <h4>
                            <ShieldCheck size={16} /> Key Engineering Decisions
                          </h4>
                          <ul className="decisions-list">
                            {p.engineering_decisions.map((dec, dIdx) => (
                              <li key={dIdx}>{dec}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Challenges & Limitations */}
                      <div className="case-block challenges-block">
                        <h4>
                          <AlertCircle size={16} /> Challenges & Current Status
                        </h4>
                        {Array.isArray(p.challenges) && p.challenges.length > 0 && (
                          <ul className="challenges-list">
                            {p.challenges.map((ch, cIdx) => (
                              <li key={cIdx}>{ch}</li>
                            ))}
                          </ul>
                        )}
                        <div className="status-note-box">
                          <strong>Current Status:</strong> {p.status_note}
                        </div>
                      </div>

                      {/* What I Learned & Key Takeaways */}
                      {p.learning && (
                        <div className="case-block learning-block">
                          <h4>
                            <Lightbulb size={16} /> What I Learned & Key Takeaways
                          </h4>
                          <p>{p.learning}</p>
                        </div>
                      )}
                    </div>

                    {/* Right Column: Interactive UI Visual & Action Links */}
                    <div className="case-side-col">
                      <div className="case-visual-frame">
                        <div className="frame-bar">
                          <span className="frame-dot"></span>
                          <span className="frame-dot"></span>
                          <span className="frame-dot"></span>
                          <small>PREVIEW // {p.title.toUpperCase()}</small>
                        </div>
                        <Visual kind={p.visual || "medisync"} />
                      </div>

                      {/* Action Links & Verification */}
                      <div className="case-links-card">
                        <div className="card-row">
                          <span>SOURCE CODE</span>
                          {p.github_url ? (
                            <a
                              href={p.github_url}
                              target="_blank"
                              rel="noreferrer"
                              className="link-badge verified"
                            >
                              <Github size={14} /> GitHub Repository <ArrowUpRight size={13} />
                            </a>
                          ) : (
                            <span className="link-badge disabled">Repository Private</span>
                          )}
                        </div>

                        <div className="card-row">
                          <span>DEPLOYMENT</span>
                          {p.demo_url ? (
                            <a
                              href={p.demo_url}
                              target="_blank"
                              rel="noreferrer"
                              className="link-badge verified"
                            >
                              Live Prototype <ExternalLink size={13} />
                            </a>
                          ) : (
                            <span className="link-badge local">
                              Local Development Prototype
                            </span>
                          )}
                        </div>

                        <div className="case-disclaimer">
                          <i>ℹ</i> Verified repository and implementation details. Illustrative mockups represent interface prototypes.
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Case Study Pagination */}
                  <div className="case-pagination">
                    <button
                      className="pagination-btn prev"
                      onClick={() => {
                        setActiveSlug(prevProject.slug);
                        scrollToSection(`#case-study-${prevProject.slug}`);
                      }}
                      aria-label={`Go to previous case study: ${prevProject.title}`}
                    >
                      <ArrowLeft size={15} /> Previous: {prevProject.title}
                    </button>

                    <span className="pagination-current">{p.number} of 0{projects.length}</span>

                    <button
                      className="pagination-btn next"
                      onClick={() => {
                        setActiveSlug(nextProject.slug);
                        scrollToSection(`#case-study-${nextProject.slug}`);
                      }}
                      aria-label={`Go to next case study: ${nextProject.title}`}
                    >
                      Next: {nextProject.title} <ArrowRight size={15} />
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        {/* SECTION 2.C: ADDITIONAL PROJECTS REVOLVING CAROUSEL (04, 05, 06) */}
        <section className="more-projects-section wrap" id="more-projects" aria-label="Additional Projects">
          <div className="section-header reveal" data-reveal>
            <p className="eyebrow">EXPLORATORY & DOMAIN WORK</p>
            <h2>
              More <span>projects<span className="red">.</span></span>
            </h2>
            <p className="section-lead">
              A closer look at additional projects spanning mobile applications, full-stack development, cybersecurity, and electric vehicle systems.
            </p>
          </div>

          <MoreProjectsCarousel projects={ADDITIONAL_PROJECTS} />
        </section>

        {/* SECTION 3.E: TECHNICAL SKILLS */}
        <section className="skills-section wrap" id="skills">
          <div className="section-header reveal" data-reveal>
            <p className="eyebrow">TECHNICAL SKILLS</p>
            <h2>
              Verified <span>toolkit<span className="red">.</span></span>
            </h2>
            <p className="section-lead">
              Technologies and tools I have actively worked with in development projects. Grouped by domain for clarity.
            </p>
          </div>

          <div className="skills-grid">
            {SKILL_CATEGORIES.map((cat, idx) => (
              <div key={cat.title} className="skill-category-card reveal" data-reveal>
                <div className="skill-cat-header">
                  <cat.icon size={22} className="skill-cat-icon" />
                  <div>
                    <span className="skill-cat-num">0{idx + 1}</span>
                    <h3>{cat.title}</h3>
                  </div>
                </div>
                <div className="skills-pill-group">
                  {cat.skills.map(s => (
                    <span key={s} className="skill-item-pill">{s}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* SECTION 3.F: ENGINEERING JOURNEY */}
        <section className="journey-section wrap" id="journey">
          <div className="section-header reveal" data-reveal>
            <p className="eyebrow">LEARNING TIMELINE</p>
            <h2>
              Engineering <span>journey<span className="red">.</span></span>
            </h2>
            <p className="section-lead">
              A truthful timeline tracing my academic coursework, project explorations, and engineering milestones.
            </p>
          </div>

          <div className="journey-timeline">
            {JOURNEY_STEPS.map((step) => (
              <div key={step.title} className="journey-item reveal" data-reveal>
                <div className="journey-marker" aria-hidden="true">
                  <span className="marker-dot"></span>
                  <span className="marker-line"></span>
                </div>
                <div className="journey-content">
                  <span className="journey-period">{step.period}</span>
                  <h3 className="journey-title">{step.title}</h3>
                  <p className="journey-tagline">{step.tagline}</p>
                  <p className="journey-desc">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ACHIEVEMENTS & HACKATHONS */}
        <section className="achievements-section wrap" id="achievements">
          <div className="section-header reveal" data-reveal>
            <p className="eyebrow">ACHIEVEMENTS & EVENTS</p>
            <h2>
              Collaborative <span>events<span className="red">.</span></span>
            </h2>
            <p className="section-lead">
              Competitive hackathons and engineering ideathons where I applied rapid system design, teamwork, and prototyping under tight deadlines.
            </p>
          </div>

          <div className="achievements-grid">
            {displayAchievements.map((item, idx) => (
              <div key={item.event || item.title || idx} className="achievement-card reveal" data-reveal>
                <div className="achievement-badge">{item.category}</div>
                <h3 className="achievement-title">{item.event || item.title}</h3>
                <div className="achievement-organizer">
                  <Award size={14} />
                  <span>{item.organizer}</span>
                </div>
                <p className="achievement-desc">{item.description}</p>
                <div className="achievement-highlight">
                  <Sparkles size={14} />
                  <span>{item.highlight}</span>
                </div>
                {item.certificateUrl && (
                  <div className="achievement-action">
                    <a
                      href={item.certificateUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="achievement-cert-btn"
                      aria-label={`View participation certificate for ${item.event || item.title}`}
                    >
                      <FileText size={14} />
                      <span>View Participation Certificate</span>
                      <ExternalLink size={13} />
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* CERTIFICATIONS & COURSES */}
        <section className="certifications-section wrap" id="certifications">
          <div className="section-header reveal" data-reveal>
            <p className="eyebrow">CONTINUOUS LEARNING</p>
            <h2>
              Certifications & <span>courses<span className="red">.</span></span>
            </h2>
            <p className="section-lead">
              Structured coursework and specialized credentials reinforcing full-stack development, AI, HCI, and professional communication.
            </p>
          </div>

          <div className="certifications-grid">
            {displayCertifications.map((cert, idx) => (
              <div key={cert.name || cert.title || idx} className="certification-card reveal" data-reveal>
                <div className="cert-top">
                  <span className="cert-cat-pill">{cert.category}</span>
                  <span className="cert-provider">{cert.provider}</span>
                </div>
                <h3 className="cert-title">{cert.name}</h3>
                <p className="cert-desc">{cert.description}</p>
                {cert.certificateUrl && (
                  <div className="cert-action">
                    <a
                      href={cert.certificateUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="cert-link-btn"
                      aria-label={`View certificate for ${cert.name}`}
                    >
                      <FileText size={13} />
                      <span>View Certificate</span>
                      <ExternalLink size={12} />
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* INTERESTS & PROFESSIONAL STRENGTHS */}
        <section className="interests-section wrap" id="interests">
          <div className="section-header reveal" data-reveal>
            <p className="eyebrow">CORE FOCUS AREAS</p>
            <h2>
              Interests & <span>strengths<span className="red">.</span></span>
            </h2>
            <p className="section-lead">
              Technical domains I am actively exploring alongside the engineering habits that guide my work.
            </p>
          </div>

          <div className="interests-grid">
            {INTERESTS.map((item) => (
              <div key={item.title} className="interest-card reveal" data-reveal>
                <div className="interest-icon-box">
                  <item.icon size={22} />
                </div>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </div>
            ))}
          </div>

          <div className="strengths-wrapper reveal" data-reveal>
            <div className="strengths-header">
              <span className="strengths-eyebrow">EVIDENCE-BASED ATTRIBUTES</span>
              <h3>Professional Strengths</h3>
            </div>
            <div className="strengths-grid">
              {PROFESSIONAL_STRENGTHS.map((strength) => (
                <div key={strength.title} className="strength-card">
                  <span className="strength-tag">OBSERVED STRENGTH</span>
                  <h3>{strength.title}</h3>
                  <p>{strength.evidence}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* SECTION 3.G: CONTACT ME */}
        <section className="contact-section" id="contact">
          <div className="wrap contact-grid">
            <div className="contact-info reveal" data-reveal>
              <p className="eyebrow">GET IN TOUCH</p>
              <h2>
                Let's discuss an <span>internship<span className="red">.</span></span>
              </h2>
              <p className="contact-subtext">
                Whether you have an internship opening, a project to collaborate on, or engineering questions about my work, I'd welcome the opportunity to speak with you.
              </p>

              <div className="direct-contact-list">
                <div className="contact-method">
                  <div className="method-icon"><Mail size={20} /></div>
                  <div>
                    <small>DIRECT EMAIL</small>
                    <a href={`mailto:${CONFIG.email}`}>{CONFIG.email} <ArrowUpRight size={14} /></a>
                  </div>
                </div>

                <div className="contact-method">
                  <div className="method-icon"><Github size={20} /></div>
                  <div>
                    <small>GITHUB PROFILE</small>
                    <a href={CONFIG.github} target="_blank" rel="noreferrer">
                      github.com/tejas388 <ArrowUpRight size={14} />
                    </a>
                  </div>
                </div>

                {CONFIG.resumeUrl && (
                  <div className="contact-method">
                    <div className="method-icon"><FileText size={20} /></div>
                    <div>
                      <small>CURRICULUM VITAE</small>
                      <a href={CONFIG.resumeUrl} target="_blank" rel="noopener noreferrer">
                        View Resume (Google Drive) <ArrowUpRight size={14} />
                      </a>
                    </div>
                  </div>
                )}

                <div className="contact-method">
                  <div className="method-icon"><Linkedin size={20} /></div>
                  <div>
                    <small>LINKEDIN PROFILE</small>
                    <a
                      href={CONFIG.linkedinPath}
                      onClick={(e) => {
                        e.preventDefault();
                        onNavigateToLinkedIn();
                      }}
                      title="LinkedIn Profile Temporarily Unavailable"
                    >
                      Status: Temporarily Inaccessible <ArrowUpRight size={14} />
                    </a>
                  </div>
                </div>
              </div>

              <div className="privacy-card">
                <strong>Privacy Assurance</strong>
                <p>
                  Your details are sent to the FastAPI backend only upon clicking "Send Message". Anonymous website visits do not capture contact details or personal identity.
                </p>
              </div>
            </div>

            {/* Contact Form with Honeypot Spam Protection */}
            <form className="contact-form-card reveal" data-reveal onSubmit={submitContact}>
              <div className="form-card-header">
                <span>CONTACT INQUIRY FORM</span>
                <small>* REQUIRED FIELDS</small>
              </div>

              {/* Bot Honeypot Field (Hidden from real users) */}
              <input
                type="text"
                name="website"
                style={{ display: "none" }}
                tabIndex={-1}
                autoComplete="off"
                aria-hidden="true"
                value={form.website}
                onChange={e => setForm({ ...form, website: e.target.value })}
              />

              <div className="form-field">
                <label htmlFor="form-name">
                  Your Full Name <b>*</b>
                </label>
                <input
                  id="form-name"
                  required
                  maxLength={120}
                  autoComplete="name"
                  placeholder="e.g. Sarah Connor"
                  value={form.name}
                  onChange={e => setForm({ ...form, name: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label htmlFor="form-email">
                  Email Address <b>*</b>
                </label>
                <input
                  id="form-email"
                  type="email"
                  required
                  maxLength={254}
                  autoComplete="email"
                  placeholder="e.g. sarah@company.com"
                  value={form.email}
                  onChange={e => setForm({ ...form, email: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label htmlFor="form-company">
                  Company / Organization <small>OPTIONAL</small>
                </label>
                <input
                  id="form-company"
                  maxLength={160}
                  autoComplete="organization"
                  placeholder="e.g. Acme Tech"
                  value={form.company}
                  onChange={e => setForm({ ...form, company: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label htmlFor="form-message">
                  Message <b>*</b>
                  <span className="char-count">({form.message.length}/5000)</span>
                </label>
                <textarea
                  id="form-message"
                  required
                  minLength={5}
                  maxLength={5000}
                  rows={5}
                  placeholder="Tell me about your team, internship opportunity, or project inquiry…"
                  value={form.message}
                  onChange={e => setForm({ ...form, message: e.target.value })}
                />
              </div>

              <button
                type="submit"
                className="submit-btn"
                disabled={status.kind === "sending"}
              >
                {status.kind === "sending" ? "Transmitting Message…" : "Send Message"}
                <Send size={16} />
              </button>

              {status.message && (
                <div
                  className={`form-feedback ${status.kind}`}
                  role="status"
                  aria-live="polite"
                >
                  {status.kind === "success" && <CheckCircle2 size={16} />}
                  {status.kind === "error" && <AlertCircle size={16} />}
                  <span>{status.message}</span>
                </div>
              )}
            </form>
          </div>
        </section>
      </main>

      {/* SECTION 3.H: FOOTER */}
      <footer className="footer-section wrap">
        <div className="footer-top">
          <a
            className="brand"
            href="#about"
            onClick={(e) => {
              e.preventDefault();
              scrollToSection("#about");
            }}
            aria-label="Tejas C K Home"
          >
            <b>T<span>.</span></b>
            <div className="brand-text">
              <strong>TEJAS C K</strong>
              <small>PORTFOLIO 2026</small>
            </div>
          </a>

          <div className="footer-nav">
            <a href="#about" onClick={(e) => { e.preventDefault(); scrollToSection("#about"); }}>About</a>
            <a href="#projects" onClick={(e) => { e.preventDefault(); scrollToSection("#projects"); }}>Projects</a>
            <a href="#skills" onClick={(e) => { e.preventDefault(); scrollToSection("#skills"); }}>Skills</a>
            <a href="#journey" onClick={(e) => { e.preventDefault(); scrollToSection("#journey"); }}>Journey</a>
            <a href="#achievements" onClick={(e) => { e.preventDefault(); scrollToSection("#achievements"); }}>Achievements</a>
            <a href="#certifications" onClick={(e) => { e.preventDefault(); scrollToSection("#certifications"); }}>Certifications</a>
            <a href="#interests" onClick={(e) => { e.preventDefault(); scrollToSection("#interests"); }}>Interests</a>
            <a href="#contact" onClick={(e) => { e.preventDefault(); scrollToSection("#contact"); }}>Contact</a>
          </div>

          <div className="footer-social">
            <a href={CONFIG.github} target="_blank" rel="noreferrer" aria-label="GitHub Profile">
              <Github size={16} />
            </a>
            {CONFIG.resumeUrl && (
              <a href={CONFIG.resumeUrl} target="_blank" rel="noopener noreferrer" aria-label="Resume Google Drive">
                <FileText size={16} />
              </a>
            )}
            <a
              href={CONFIG.linkedinPath}
              onClick={(e) => {
                e.preventDefault();
                onNavigateToLinkedIn();
              }}
              aria-label="LinkedIn Profile Temporarily Unavailable"
              title="LinkedIn Profile Notice"
            >
              <Linkedin size={16} />
            </a>
          </div>
        </div>

        <div className="footer-bottom">
          <span>DESIGNED & CODED WITH INTENT · FASTAPI + SQLITE + REACT</span>
          <a
            href="#about"
            onClick={(e) => {
              e.preventDefault();
              scrollToSection("#about");
            }}
            className="back-to-top"
          >
            BACK TO TOP ↑
          </a>
          <small>© {currentYear} Tejas C K. All rights reserved.</small>
        </div>
      </footer>

      {/* Profile Photo Lightbox Modal */}
      {lightboxOpen && (
        <div
          className="lightbox-overlay"
          role="dialog"
          aria-modal="true"
          aria-label="Profile photo of Tejas C K"
          onClick={(e) => {
            if (e.target === e.currentTarget) setLightboxOpen(false);
          }}
        >
          <div className="lightbox-dialog" tabIndex={-1}>
            <div className="lightbox-header">
              <span>TEJAS C K // PORTRAIT</span>
              <button
                type="button"
                className="lightbox-close-btn"
                onClick={() => setLightboxOpen(false)}
                aria-label="Close portrait lightbox"
              >
                <X size={18} />
              </button>
            </div>

            <div className="lightbox-body">
              <div className="lightbox-img-frame">
                {!imgFailed ? (
                  <img
                    src={PORTRAIT_SRC}
                    alt="Tejas C K — Full Portrait"
                    className="lightbox-full-img"
                    onError={() => setImgFailed(true)}
                  />
                ) : (
                  <div className="lightbox-fallback-box">
                    <div className="lightbox-fallback-avatar">TCK</div>
                    <p style={{ margin: 0, fontSize: "13px", color: "var(--muted)" }}>
                      Portrait file placed at <code>public/tejas-portrait.jpg</code>
                    </p>
                  </div>
                )}
              </div>

              <div className="lightbox-caption">
                <strong>Tejas C K</strong>
                <small>Computer Science Engineering Student · Malnad College of Engineering</small>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function formatContactApiError(statusCode, data, error) {
  if (error && error.name === "AbortError") {
    return "Request timed out (12s). Please check your internet connection or email directly.";
  }

  if (data && data.detail) {
    if (typeof data.detail === "string") {
      return data.detail;
    }
    if (Array.isArray(data.detail)) {
      const messages = data.detail
        .map((err) => {
          if (!err) return null;
          if (typeof err === "string") return err;
          const loc = Array.isArray(err.loc) ? err.loc : [];
          const rawField = loc.length > 0 ? loc[loc.length - 1] : "";
          const fieldName = (rawField && rawField !== "body")
            ? `${rawField.charAt(0).toUpperCase() + rawField.slice(1)}: `
            : "";
          let msg = err.msg || "Invalid value";
          msg = msg.replace(/^Value error,\s*/i, "");
          if (msg.startsWith("value is not a valid email address:")) {
            msg = msg.replace("value is not a valid email address:", "Invalid email format:").trim();
          }
          return `${fieldName}${msg}`;
        })
        .filter(Boolean);

      if (messages.length > 0) {
        return messages.join(" • ");
      }
    }
    if (typeof data.detail === "object") {
      if (data.detail.message && typeof data.detail.message === "string") {
        return data.detail.message;
      }
      try {
        return JSON.stringify(data.detail);
      } catch (_) {}
    }
  }

  if (statusCode === 429) {
    return "Rate limit reached (max 5 submissions per minute). Please wait a moment before sending another message.";
  }
  if (statusCode === 422) {
    return "Please check the form fields: name, a valid email address, and a message of at least 5 characters are required.";
  }
  if (statusCode >= 500) {
    return "Server error while saving your message. Please try again or reach out directly via email.";
  }

  if (error && error.message && error.message !== "Failed to fetch") {
    return error.message;
  }

  return `Could not connect to the backend service. Please try again or reach out directly at ${CONFIG.email}.`;
}

function App() {
  const [currentPath, setCurrentPath] = useState(
    typeof window !== "undefined" ? window.location.pathname : "/"
  );
  const [projects, setProjects] = useState(DEFAULT_PROJECTS);
  const [certifications, setCertifications] = useState(CERTIFICATIONS);
  const [achievements, setAchievements] = useState(ACHIEVEMENTS);
  const [activeSlug, setActiveSlug] = useState("medisync");
  const [activeSection, setActiveSection] = useState("about");
  const [menu, setMenu] = useState(false);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [imgFailed, setImgFailed] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", company: "", message: "", website: "" });
  const [status, setStatus] = useState({ kind: "", message: "" });
  const isSubmittingRef = useRef(false);
  const currentYear = new Date().getFullYear();

  // Synchronize client route with browser back/forward buttons
  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  const navigateTo = (path) => {
    if (typeof window !== "undefined") {
      window.history.pushState({}, "", path);
      setCurrentPath(path);
      window.scrollTo({ top: 0, behavior: "instant" });
    }
  };

  // Keyboard Escape listener & body scroll lock for portrait lightbox
  useEffect(() => {
    if (!lightboxOpen) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const handleKeyDown = (e) => {
      if (e.key === "Escape") setLightboxOpen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [lightboxOpen]);

  // Fetch projects from FastAPI backend, smoothly falling back to verified defaults
  useEffect(() => {
    let cancelled = false;
    fetch(`${API}/api/projects`)
      .then(r => {
        if (!r.ok) throw new Error("API request failed");
        return r.json();
      })
      .then(data => {
        if (!cancelled && Array.isArray(data) && data.length) {
          const merged = data.map((apiItem, idx) => {
            const fallback = DEFAULT_PROJECTS.find(d => d.slug === apiItem.slug) || DEFAULT_PROJECTS[idx % DEFAULT_PROJECTS.length];
            return {
              ...fallback,
              ...apiItem,
              number: String(idx + 1).padStart(2, "0"),
              stack: normalizeArray(apiItem.stack, fallback.stack),
              features: normalizeArray(apiItem.features, fallback.features),
              challenges: normalizeArray(apiItem.challenges, fallback.challenges),
              engineering_decisions: normalizeArray(apiItem.engineering_decisions, fallback.engineering_decisions),
              architecture_steps: Array.isArray(apiItem.architecture_steps) && apiItem.architecture_steps.length > 0
                ? apiItem.architecture_steps
                : fallback.architecture_steps,
              learning: apiItem.learning || fallback.learning,
              next_steps: normalizeArray(apiItem.next_steps, fallback.next_steps)
            };
          });
          setProjects(merged);
        }
      })
      .catch(() => {
        // Graceful fallback: Keep DEFAULT_PROJECTS active
      });
    return () => { cancelled = true; };
  }, []);

  // Fetch certifications from FastAPI backend, smoothly falling back to verified defaults
  useEffect(() => {
    let cancelled = false;
    fetch(`${API}/api/certifications`)
      .then(r => {
        if (!r.ok) throw new Error("API request failed");
        return r.json();
      })
      .then(data => {
        if (!cancelled && Array.isArray(data) && data.length) {
          const mapped = data.map((item, idx) => {
            const fallback = CERTIFICATIONS[idx] || {};
            return {
              name: item.title || fallback.name,
              provider: item.issuing_organization || fallback.provider,
              category: item.category || fallback.category,
              description: item.description || fallback.description,
              certificateUrl: item.credential_url !== undefined ? item.credential_url : fallback.certificateUrl
            };
          });
          setCertifications(mapped);
        }
      })
      .catch(() => {
        // Fallback: keep CERTIFICATIONS default
      });
    return () => { cancelled = true; };
  }, []);

  // Fetch achievements from FastAPI backend, smoothly falling back to verified defaults
  useEffect(() => {
    let cancelled = false;
    fetch(`${API}/api/achievements`)
      .then(r => {
        if (!r.ok) throw new Error("API request failed");
        return r.json();
      })
      .then(data => {
        if (!cancelled && Array.isArray(data) && data.length) {
          const mapped = data.map((item, idx) => {
            const fallback = ACHIEVEMENTS[idx] || {};
            return {
              event: item.title || fallback.event,
              organizer: item.organization || fallback.organizer,
              category: item.category || fallback.category,
              description: item.description || fallback.description,
              highlight: item.highlight || fallback.highlight,
              certificateUrl: item.evidence_url !== undefined ? item.evidence_url : fallback.certificateUrl
            };
          });
          setAchievements(mapped);
        }
      })
      .catch(() => {
        // Fallback: keep ACHIEVEMENTS default
      });
    return () => { cancelled = true; };
  }, []);

  // Anonymous visit telemetry: Records only visitor_id, session_id, device_category, page_path, referrer. No contact details collected.
  useEffect(() => {
    try {
      if (sessionStorage.getItem("portfolio_visit_recorded")) return;
      let visitorId = localStorage.getItem("portfolio_visitor_id");
      if (!visitorId) {
        visitorId = (typeof crypto !== "undefined" && crypto.randomUUID)
          ? crypto.randomUUID()
          : `v-${Math.random().toString(36).slice(2)}-${Date.now()}`;
        localStorage.setItem("portfolio_visitor_id", visitorId);
      }
      let sessionId = sessionStorage.getItem("portfolio_session_id");
      if (!sessionId) {
        sessionId = (typeof crypto !== "undefined" && crypto.randomUUID)
          ? `s-${crypto.randomUUID()}`
          : `s-${Math.random().toString(36).slice(2)}-${Date.now()}`;
        sessionStorage.setItem("portfolio_session_id", sessionId);
      }

      const width = typeof window !== "undefined" ? window.innerWidth : 1200;
      const deviceCategory = width <= 540 ? "mobile" : (width <= 960 ? "tablet" : "desktop");

      fetch(`${API}/api/visits`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          visitor_id: visitorId,
          session_id: sessionId,
          device_category: deviceCategory,
          page_path: window.location.pathname || "/",
          referrer: document.referrer || null
        })
      })
        .then(r => {
          if (r.ok) sessionStorage.setItem("portfolio_visit_recorded", "1");
        })
        .catch(() => {});
    } catch (_) {}
  }, []);

  const scrollToSection = (id) => {
    setMenu(false);
    const target = document.querySelector(id);
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  };

  const submitContact = async (e) => {
    e.preventDefault();
    if (isSubmittingRef.current || status.kind === "sending") return;

    const trimmedName = (form.name || "").trim();
    const trimmedEmail = (form.email || "").trim();
    const trimmedCompany = (form.company || "").trim() || null;
    const trimmedMessage = (form.message || "").trim();
    const honeypotVal = (form.website || "").trim() || null;

    if (!trimmedName) {
      setStatus({ kind: "error", message: "Please provide your full name." });
      return;
    }
    if (!trimmedEmail || !trimmedEmail.includes("@") || !trimmedEmail.split("@")[1]?.includes(".")) {
      setStatus({ kind: "error", message: "Please provide a valid email address with a domain (e.g. sarah@company.com)." });
      return;
    }
    if (trimmedMessage.length < 5) {
      setStatus({ kind: "error", message: "Please enter a message of at least 5 characters." });
      return;
    }

    isSubmittingRef.current = true;
    setStatus({ kind: "sending", message: "Transmitting your message securely…" });

    const controller = typeof AbortController !== "undefined" ? new AbortController() : null;
    const timeoutId = controller ? setTimeout(() => controller.abort(), 12000) : null;

    try {
      const response = await fetch(`${API}/api/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller ? controller.signal : undefined,
        body: JSON.stringify({
          name: trimmedName,
          email: trimmedEmail,
          company: trimmedCompany,
          message: trimmedMessage,
          website: honeypotVal
        })
      });

      if (timeoutId) clearTimeout(timeoutId);

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const errorMsg = formatContactApiError(response.status, data, null);
        setStatus({ kind: "error", message: errorMsg });
        return;
      }

      setStatus({
        kind: "success",
        message: data.message || "Message received! Thank you for reaching out — I'll get back to you shortly."
      });
      setForm({ name: "", email: "", company: "", message: "", website: "" });
    } catch (err) {
      if (timeoutId) clearTimeout(timeoutId);
      const errorMsg = formatContactApiError(0, null, err);
      setStatus({ kind: "error", message: errorMsg });
    } finally {
      isSubmittingRef.current = false;
    }
  };

  const isLinkedInRoute = (path) => {
    if (!path) return false;
    const clean = path.replace(/\/+$/, "");
    return clean === "/linkedin-unavailable";
  };

  if (isLinkedInRoute(currentPath)) {
    return (
      <LinkedInUnavailablePage
        onBack={() => navigateTo("/")}
        resumeUrl={CONFIG.resumeUrl}
        email={CONFIG.email}
      />
    );
  }

  return (
    <PortfolioView
      projects={projects}
      certifications={certifications}
      achievements={achievements}
      activeSlug={activeSlug}
      setActiveSlug={setActiveSlug}
      activeSection={activeSection}
      setActiveSection={setActiveSection}
      menu={menu}
      setMenu={setMenu}
      lightboxOpen={lightboxOpen}
      setLightboxOpen={setLightboxOpen}
      imgFailed={imgFailed}
      setImgFailed={setImgFailed}
      form={form}
      setForm={setForm}
      status={status}
      submitContact={submitContact}
      scrollToSection={scrollToSection}
      onNavigateToLinkedIn={() => navigateTo(CONFIG.linkedinPath)}
      currentYear={currentYear}
    />
  );
}

// Protective Error Boundary to capture runtime exceptions cleanly without blanking the screen
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an unhandled render error:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#0d0f12",
          color: "#e6edf3",
          fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
          padding: "24px"
        }}>
          <div style={{
            maxWidth: "540px",
            background: "#161b22",
            border: "1px solid #30363d",
            borderRadius: "12px",
            padding: "32px",
            textAlign: "center"
          }}>
            <h2 style={{ color: "#ff4d4d", marginBottom: "12px", fontSize: "20px" }}>Portfolio View Alert</h2>
            <p style={{ color: "#8b949e", fontSize: "14px", lineHeight: "1.6", marginBottom: "24px" }}>
              {this.state.error?.message || "An unexpected interface rendering exception occurred."}
            </p>
            <button
              onClick={() => window.location.reload()}
              style={{
                backgroundColor: "#e63946",
                color: "#ffffff",
                border: "none",
                borderRadius: "6px",
                padding: "10px 20px",
                fontWeight: "600",
                fontSize: "14px",
                cursor: "pointer"
              }}
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

const rootElement = document.getElementById("root");
if (rootElement) {
  createRoot(rootElement).render(
    <React.StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </React.StrictMode>
  );
}