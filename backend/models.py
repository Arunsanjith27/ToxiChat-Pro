from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=4)
    display_name: Optional[str] = None
    email: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class ForgotPasswordRequest(BaseModel):
    username: str
    email: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=4)


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=200)


class UserOut(BaseModel):
    username: str
    display_name: str
    created_at: str
    is_online: bool = False
    warnings_count: int = 0
    is_muted: bool = False
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    reputation_score: int = 100
    reputation_tier: str = "excellent"
    role: str = "user"


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    display_name: str
    role: str = "user"
    avatar_url: Optional[str] = None
    reputation_score: int = 100


class MessageIn(BaseModel):
    text: str
    receiver: str
    is_group: bool = False


class MessageOut(BaseModel):
    id: str
    sender: str
    receiver: str
    text: str
    timestamp: str
    is_group: bool = False
    toxicity_score: float = 0.0
    toxicity_label: str = "low"
    is_flagged: bool = False
    toxic_words: List[str] = []
    status: str = "sent"
    reactions: Dict[str, List[str]] = {}
    edited: bool = False
    emotion: str = "neutral"
    emotion_confidence: float = 0.0


class ToxicityRequest(BaseModel):
    text: str


class ToxicityResult(BaseModel):
    text: str
    score: float
    label: str
    is_flagged: bool
    toxic_words: List[str] = []
    emotion: str = "neutral"
    emotion_confidence: float = 0.0
    highlighted_words: List[str] = []
    rewrite: Optional[str] = None
    escalation: Optional[dict] = None


class EscalationRequest(BaseModel):
    text: str
    partner: str


class EscalationResult(BaseModel):
    text: str
    score: float
    label: str
    is_flagged: bool
    toxic_words: List[str] = []
    emotion: str = "neutral"
    emotion_confidence: float = 0.0
    rewrite: Optional[str] = None
    escalation: dict
    conversation_health: int = 100


class AdminAction(BaseModel):
    username: str
    action: str = Field(..., pattern="^(unmute|reset_warnings|promote_admin|demote_admin)$")


class ConversationHealth(BaseModel):
    partner: str
    health_score: int
    escalation_level: str
    trend: str
    total_messages: int
    toxic_messages: int


class RewriteRequest(BaseModel):
    text: str


class DashboardStats(BaseModel):
    total_messages: int
    toxic_count: int
    non_toxic_count: int
    toxicity_rate: float
    total_users: int = 0
    online_users: int = 0
    most_toxic_users: List[dict]
    hourly_trend: List[dict]
    daily_trend: List[dict] = []
    flagged_messages: List[dict] = []
    conversation_health_avg: float = 100.0
    escalation_events: int = 0


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    members: List[str]
