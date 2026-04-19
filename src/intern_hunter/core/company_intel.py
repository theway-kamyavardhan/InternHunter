import groq
from intern_hunter.config import settings

class CompanyIntel:
    def __init__(self):
        self.groq_key = settings.GROQ_API_KEY
        if self.groq_key:
            self.client = groq.Groq(api_key=self.groq_key)

    def generate_intel(self, company: str) -> str:
        """
        Generates a 1-2 sentence hyper-relevant intelligence paragraph for a Dream Company.
        """
        if not self.groq_key:
            return ""
            
        prompt = f"""
        Write exactly 1-2 short, professional sentences about a recent impressive milestone, 
        product launch, or funding round for the AI company '{company}'. 
        This will be inserted into a cold email for an internship application to show I follow their work.
        Make it sound extremely natural and not generated.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating intel for {company}: {e}")
            return ""
