import json
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

def parse_list_field(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return []
        if v.startswith('[') and v.endswith(']'):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except Exception:
                pass
        if ';' in v:
            return [part.strip() for part in v.split(';') if part.strip()]
        if ',' in v:
            return [part.strip() for part in v.split(',') if part.strip()]
        return [v]
    return []

class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    title: str
    category: str
    summary: str
    description: str
    role: str
    year: str
    stack: list[str] = Field(default_factory=list)
    outcome: Optional[str] = None
    accent: Optional[str] = None
    visual: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    problem: Optional[str] = None
    architecture: Optional[str] = None
    features: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)
    status_note: Optional[str] = None
    sort_order: int

    @field_validator('stack', 'features', 'challenges', mode='before')
    @classmethod
    def validate_list_fields(cls, v: Any) -> list[str]:
        return parse_list_field(v)

class CertificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    issuing_organization: str
    issue_date: Optional[str] = None
    credential_url: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    display_order: int

class AchievementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    organization: str
    date: Optional[str] = None
    category: Optional[str] = None
    description: str
    highlight: Optional[str] = None
    evidence_url: Optional[str] = None
    display_order: int

class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    company: Optional[str] = Field(default=None, max_length=160)
    message: str = Field(min_length=5, max_length=5000)
    website: Optional[str] = Field(default=None, max_length=100)  # Honeypot field for bot spam prevention

    @field_validator('name', 'message', mode='before')
    @classmethod
    def strip_text(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator('company', 'website', mode='before')
    @classmethod
    def strip_optional_text(cls, v: Any) -> Optional[str]:
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v

class HealthOut(BaseModel):
    ok: bool
    service: str
    database: str

class VisitCreate(BaseModel):
    visitor_id: str = Field(min_length=1, max_length=100)
    session_id: Optional[str] = Field(default=None, max_length=100)
    device_category: Optional[str] = Field(default=None, max_length=50)
    page_path: str = Field(default="/", max_length=300)
    referrer: Optional[str] = Field(default=None, max_length=500)
