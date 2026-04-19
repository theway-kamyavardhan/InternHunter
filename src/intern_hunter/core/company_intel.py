from intern_hunter.config import settings
from intern_hunter.core.llm import get_llm_client

class CompanyIntel:
    def __init__(self):
        self.llm = get_llm_client()

    def generate_intel(self, company: str) -> str:
        """
        Generates a 1-2 sentence hyper-relevant intelligence paragraph for a Dream Company.
        """
        prompt = f"""
        Write exactly 1-2 short, professional sentences about a recent impressive milestone, 
        product launch, or funding round for the AI company '{company}'. 
        This will be inserted into a cold email for an internship application to show I follow their work.
        Make it sound extremely natural and not generated.
        """
        
        try:
            return self.llm.generate(prompt, temperature=0.7)
        except Exception as e:
            print(f"Error generating intel for {company}: {e}")
            return ""
