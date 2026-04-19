import pytest
from intern_hunter.models import Job

def test_job_model_creation():
    job = Job(
        id="123",
        title="AI Intern",
        company="OpenAI",
        location="Remote",
        description="Great job",
        url="http://example.com"
    )
    assert job.title == "AI Intern"
    assert job.confidence_score == 0
    assert not job.is_dream_company
