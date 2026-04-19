import random
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import base64
import smtplib
from email.message import EmailMessage
from intern_hunter.config import settings
from intern_hunter.models import Job, EmailDraft
from intern_hunter.core.llm import get_llm_client

class EmailEngine:
    def __init__(self):
        self.sg_key = settings.SENDGRID_API_KEY
        self.gmail = settings.GMAIL_ADDRESS
        self.gmail_pw = settings.GMAIL_APP_PASSWORD
        self.llm = get_llm_client()

    def generate_draft(self, job: Job, pdf_path: str) -> EmailDraft:
        subjects = [
            f"AI/ML Intern Candidate - {job.title} - Kamyavardhan Dave",
            f"Passionate about {job.company}'s mission - AI Intern Candidate",
            f"Strong fit for {job.title} at {job.company} - Kamyavardhan Dave"
        ]
        chosen_subject = random.choice(subjects)
        
        intel_paragraph = f"\n\n{job.company_intel}\n\n" if job.company_intel else "\n\n"
        
        prompt = f"""
        Write a short, highly compelling cold email for an internship application.
        Target: {job.title} at {job.company}.
        Tone: Professional, eager, highly competent, slightly conversational. NOT spammy.
        Include this specific context naturally:{intel_paragraph}
        Keep it under 150 words.
        Mention that the resume is attached.
        Sign off as Kamyavardhan Dave.
        """
        
        body = "Hi team,\n\nI am applying for the role.\n\nBest, Kamya"
        try:
            res = self.llm.generate(prompt, temperature=0.6)
            if res:
                body = res
        except Exception as e:
            print(f"Error generating email: {e}")
                
        score = random.randint(60, 100) if not job.is_dream_company else 100
        
        return EmailDraft(
            subject=chosen_subject,
            body=body,
            pdf_path=pdf_path,
            personal_touch_score=score
        )

    def send_email(self, to_email: str, draft: EmailDraft):
        print("Sleeping for human-like delay (45-180s)...")
        # time.sleep(random.randint(45, 180)) # Commented out for dev speed
        
        if self.sg_key:
            self._send_via_sendgrid(to_email, draft)
        elif self.gmail and self.gmail_pw:
            self._send_via_gmail(to_email, draft)
        else:
            print("No email credentials configured!")
            
    def _send_via_sendgrid(self, to_email: str, draft: EmailDraft):
        sg = sendgrid.SendGridAPIClient(api_key=self.sg_key)
        from_email = Email(self.gmail if self.gmail else "test@example.com")
        to = To(to_email)
        content = Content("text/plain", draft.body)
        mail = Mail(from_email, to, draft.subject, content)
        
        if draft.pdf_path:
            with open(draft.pdf_path, 'rb') as f:
                data = f.read()
            encoded_file = base64.b64encode(data).decode()
            attachedFile = Attachment(
                FileContent(encoded_file),
                FileName(draft.pdf_path.split('/')[-1]),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            mail.attachment = attachedFile
            
        try:
            sg.client.mail.send.post(request_body=mail.get())
            print(f"Sent via SendGrid to {to_email}")
        except Exception as e:
            print(f"SendGrid error: {e}")

    def _send_via_gmail(self, to_email: str, draft: EmailDraft):
        msg = EmailMessage()
        msg['Subject'] = draft.subject
        msg['From'] = self.gmail
        msg['To'] = to_email
        msg.set_content(draft.body)
        
        if draft.pdf_path:
            with open(draft.pdf_path, 'rb') as f:
                pdf_data = f.read()
            msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=draft.pdf_path.split('/')[-1])
            
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(self.gmail, self.gmail_pw)
                smtp.send_message(msg)
            print(f"Sent via Gmail SMTP to {to_email}")
        except Exception as e:
            print(f"Gmail error: {e}")
