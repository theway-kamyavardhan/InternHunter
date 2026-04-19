import os
from intern_hunter.config import settings
from intern_hunter.models import Job
from intern_hunter.core.llm import get_llm_client

class JobScorer:
    def __init__(self):
        self.llm = get_llm_client()

    def score_job(self, job: Job, master_resume: str) -> Job:
        """
        Uses LLM to score the job 0-100 based on the resume.
        """
        prompt = f"""
        Given the following job description and candidate resume, score the candidate's fit for this role from 0 to 100.
        Return ONLY the integer score.
        
        Job Title: {job.title}
        Company: {job.company}
        Job Description: {job.description}
        
        Resume:
        {master_resume}
        """
        
        score = 50 # Default fallback
        try:
            res = self.llm.generate(prompt, temperature=0.0)
            if res.isdigit():
                score = int(res)
            else:
                # Basic extraction if the LLM is chatty
                score_str = "".join(filter(str.isdigit, res))
                if score_str:
                    score = int(score_str)
        except Exception as e:
            print(f"Error scoring job {job.title}: {e}")
            
        if job.is_dream_company:
            score += 15
            
        job.confidence_score = min(score, 100)
        return job
