import imaplib
import email
from email.header import decode_header
from intern_hunter.config import settings
from intern_hunter.core.obsidian_tracker import ObsidianTracker

class ReplyIntelligence:
    def __init__(self):
        self.server = settings.IMAP_SERVER
        self.port = settings.IMAP_PORT
        self.user = settings.IMAP_USERNAME
        self.pw = settings.IMAP_PASSWORD
        self.tracker = ObsidianTracker()
        
    def check_replies(self):
        if not self.user or not self.pw:
            print("IMAP not configured. Skipping reply intelligence.")
            return
            
        try:
            mail = imaplib.IMAP4_SSL(self.server, self.port)
            mail.login(self.user, self.pw)
            mail.select("inbox")
            
            # Search for unseen emails
            status, messages = mail.search(None, "UNSEEN")
            if status != "OK":
                return
                
            for num in messages[0].split():
                status, data = mail.fetch(num, "(RFC822)")
                if status == "OK":
                    msg = email.message_from_bytes(data[0][1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                        
                    sender = msg.get("From")
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                    else:
                        body = msg.get_payload(decode=True).decode()
                        
                    self._analyze_reply(sender, subject, body)
                    
            mail.close()
            mail.logout()
        except Exception as e:
            print(f"IMAP Error: {e}")
            
    def _analyze_reply(self, sender: str, subject: str, body: str):
        # Extremely simple heuristic logic for demo
        body_lower = body.lower()
        rejection_keywords = ["not hiring", "other candidates", "unfortunately", "not a fit"]
        
        is_rejection = any(kw in body_lower for kw in rejection_keywords)
        
        # Extract domain from sender
        try:
            domain = sender.split("@")[1].split(".")[0]
            if is_rejection:
                print(f"Detected rejection from {domain}. Moving to Rejected column.")
                self.tracker.move_to_rejected(domain)
            else:
                print(f"Possible positive reply from {domain}! Please check inbox.")
        except:
            pass
