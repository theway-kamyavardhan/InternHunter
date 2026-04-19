import os
import groq
import google.generativeai as genai
from intern_hunter.config import settings
from intern_hunter.models import Job

class JobScorer:
    def __init__(self):
        self.groq_key = settings.GROQ_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY
        
        if self.groq_key:
            self.groq_client = groq.Groq(api_key=self.groq_key)
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')

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
            if self.groq_key:
                response = self.groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                score = int(response.choices[0].message.content.strip())
            elif self.gemini_key:
                response = self.gemini_model.generate_content(prompt)
                score = int(response.text.strip())
        except Exception as e:
            print(f"Error scoring job {job.title}: {e}")
            
        if job.is_dream_company:
            score += 15
            
        job.confidence_score = min(score, 100)
        return job
