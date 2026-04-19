import os
import fitz  # PyMuPDF
from weasyprint import HTML, CSS
from jinja2 import Template
import groq
from intern_hunter.config import settings
from intern_hunter.models import Job

class ResumeTailor:
    def __init__(self):
        self.groq_key = settings.GROQ_API_KEY
        if self.groq_key:
            self.client = groq.Groq(api_key=self.groq_key)
            
    def _read_master_resume(self) -> str:
        md_path = "master_resume.md"
        pdf_path = "kamyavardhan-dave-resume.pdf"
        
        if os.path.exists(md_path):
            with open(md_path, "r") as f:
                return f.read()
                
        if os.path.exists(pdf_path):
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
            
        return ""

    def tailor(self, job: Job) -> str:
        """
        Rewrites the master resume to match the job description.
        Returns path to generated PDF.
        """
        master_content = self._read_master_resume()
        if not master_content:
            print("No master resume found!")
            return ""
            
        # 1. Rewrite using LLM
        prompt = f"""
        Rewrite this resume to highlight skills and experiences most relevant to the following job description.
        Keep the core facts truthful, but adjust the phrasing and emphasize keywords from the JD.
        Format the output in strict HTML suitable for WeasyPrint conversion. Use professional clean styling.
        
        Job: {job.title} at {job.company}
        JD: {job.description}
        
        Original Resume:
        {master_content}
        """
        
        html_content = "<h1>Kamyavardhan Dave</h1><p>Failed to generate tailored resume.</p>"
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                html_content = response.choices[0].message.content.strip()
                # Remove markdown code block markers if present
                if html_content.startswith("```html"):
                    html_content = html_content[7:-3]
            except Exception as e:
                print(f"Error tailoring resume: {e}")
                
        # 2. Generate PDF
        date_str = job.posted_at.strftime("%Y%m%d") if job.posted_at else "today"
        pdf_name = f"Kamyavardhan_Dave_AI_Intern_{job.company.replace(' ', '_')}_{date_str}.pdf"
        pdf_path = os.path.join("exports", pdf_name)
        
        css = CSS(string='''
            @page { margin: 1in; }
            body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.4; }
            h1 { font-size: 24pt; border-bottom: 1px solid #000; padding-bottom: 5px; }
            h2 { font-size: 14pt; margin-top: 15px; border-bottom: 1px solid #ccc; }
            p, li { font-size: 11pt; }
        ''')
        
        HTML(string=html_content).write_pdf(pdf_path, stylesheets=[css])
        return pdf_path
