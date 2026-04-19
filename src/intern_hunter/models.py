from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    url: str
    posted_at: Optional[datetime] = None
    
    # Hunter enrichment
    confidence_score: int = 0
    is_dream_company: bool = False
    company_intel: Optional[str] = None
    
    def __str__(self):
        return f"{self.title} @ {self.company} (Score: {self.confidence_score})"

class EmailDraft(BaseModel):
    subject: str
    body: str
    pdf_path: Optional[str] = None
    personal_touch_score: int = 0
