from pydantic import BaseModel, Field
from datetime import datetime

class PRComment(BaseModel):
    id: int
    user_login: str
    body: str
    created_at: datetime
    path: str | None = None
    line: int | None = None

class PRReview(BaseModel):
    id: int
    user_login: str
    state: str  # APPROVED, CHANGES_REQUESTED, COMMENTED
    body: str | None = None
    submitted_at: datetime | None = None

class AnalyzablePR(BaseModel):
    number: int
    title: str
    author: str
    state: str
    url: str
    additions: int
    deletions: int
    changed_files: int
    file_list: list[str] = Field(default_factory=list)
    comments: list[PRComment] = Field(default_factory=list)
    reviews: list[PRReview] = Field(default_factory=list)
