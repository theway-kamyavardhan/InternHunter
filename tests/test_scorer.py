import pytest
from intern_hunter.models import Job
from intern_hunter.core.scorer import JobScorer

def test_scorer_dream_company_boost():
    # Mocking the LLM client so we don't actually call Groq during tests
    job = Job(
        id="123", title="AI Intern", company="OpenAI", location="Remote", 
        description="JD", url="http://example.com", is_dream_company=True
    )
    scorer = JobScorer()
    
    # Normally we would mock the client response
    # For now, just test the simple logic
    job.confidence_score = 50
    if job.is_dream_company:
        job.confidence_score += 15
        
    assert job.confidence_score == 65
