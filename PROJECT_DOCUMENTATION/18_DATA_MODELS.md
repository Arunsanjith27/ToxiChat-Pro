# Pydantic Data Models

ToxiChat leverages Pydantic (v2) extensively within FastAPI to validate incoming HTTP requests and serialize outgoing JSON responses. These models serve as the definitive contract between the React frontend and the Python backend.

All models are defined in `backend/models.py`.

## Authentication Models

```python
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserLogin(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    username: str
    display_name: str
    role: str
    avatar_url: Optional[str] = None
    reputation_score: int = 100
```

## AI Inference Request Models

```python
class ToxicityRequest(BaseModel):
    text: str

class RewriteRequest(BaseModel):
    text: str

class EscalationRequest(BaseModel):
    text: str
    partner: str
```

## Core AI Telemetry Response Models

These models define the deeply nested JSON objects returned by the machine learning orchestrators. Note the inclusion of multi-modal specific fields (e.g., `ocr`, `vision`, `transcript`).

```python
class ToxicityResult(BaseModel):
    text: str
    score: float
    label: str
    is_flagged: bool
    toxic_words: List[str] = []
    highlighted_words: List[str] = []
    emotion: str = "neutral"
    emotion_confidence: float = 0.0
    contains_pii: bool = False
    pii_entities: List[str] = []
    rewrite: Optional[str] = None
    embedding: Optional[List[float]] = None

class EscalationPredictionResponse(BaseModel):
    prediction: dict  # Contains current_state, target_state, confidence
    timeline: dict    # Array of historical snapshots
    factors: List[str]
    recommendation: str
    model_used: str
    generation_time_ms: int

class ImageAnalysisResponse(BaseModel):
    image: dict
    ocr: dict
    vision: dict
    text_analysis: dict
    risk: dict
    explanation: dict

class AudioAnalysisResponse(BaseModel):
    audio: dict
    transcript: dict
    text_analysis: dict
    risk: dict
    explanation: dict
    metadata: dict
```

## Incident & Compliance Models

```python
class AddIncidentNoteRequest(BaseModel):
    content: str
    internal_only: bool = False

class GenerateReportRequest(BaseModel):
    incident_id: str

class AdminAction(BaseModel):
    username: str
    action: str  # e.g., 'mute', 'unmute', 'promote_admin'
```

## Database Schema vs Pydantic
While Pydantic enforces the schema at the API boundary, MongoDB strictly uses Python dictionaries (`motor`). The backend relies on FastAPI's `.model_dump()` to convert Pydantic objects into BSON-compatible dictionaries before insertion.

Because AI outputs evolve rapidly (e.g., adding a new `sarcasm_score` to the ML output), the MongoDB schema is intentionally flexible, while the Pydantic models act as the strict serialization boundary sent back to the React client.
