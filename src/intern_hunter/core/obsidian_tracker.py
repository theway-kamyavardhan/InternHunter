import os
import yaml
from datetime import datetime
from intern_hunter.config import settings
from intern_hunter.models import Job

class ObsidianTracker:
    def __init__(self):
        self.vault_path = settings.OBSIDIAN_VAULT_PATH
        self.internships_dir = os.path.join(self.vault_path, "Internships")
        self.notes_dir = os.path.join(self.internships_dir, "Applications")
        self.mail_logs_dir = os.path.join(self.internships_dir, "Mail-Logs")
        
        os.makedirs(self.notes_dir, exist_ok=True)
        os.makedirs(self.mail_logs_dir, exist_ok=True)
        
    def create_note(self, job: Job, status: str = "Applied"):
        safe_company = job.company.replace("/", "_").replace("\\", "_")
        safe_title = job.title.replace("/", "_").replace("\\", "_")
        filename = f"{safe_company} - {safe_title}.md"
        filepath = os.path.join(self.notes_dir, filename)
        
        frontmatter = {
            "company": job.company,
            "role": job.title,
            "status": status,
            "url": job.url,
            "date_applied": datetime.now().strftime("%Y-%m-%d"),
            "confidence_score": job.confidence_score,
            "is_dream_company": job.is_dream_company
        }
        
        content = f"""---
{yaml.dump(frontmatter, default_flow_style=False)}---

# {job.company} - {job.title}

## Job Description
{job.description}

## Notes
- Tailored PDF generated.
- Follow up in 8 days if no reply.
"""
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created Obsidian note: {filepath}")

    def create_session_note(self, jobs_processed: int, jobs_applied: int, jobs_skipped: int, rejections: int):
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
        filename = f"Session-{timestamp}.md"
        filepath = os.path.join(self.internships_dir, filename)
        
        content = f"""---
date: {datetime.now().strftime("%Y-%m-%d")}
time: {datetime.now().strftime("%H:%M")}
type: session
jobs_processed: {jobs_processed}
jobs_applied: {jobs_applied}
jobs_skipped: {jobs_skipped}
rejections_found: {rejections}
---

# Pipeline Session: {timestamp}

## Summary
- **Processed**: {jobs_processed}
- **Applied**: {jobs_applied}
- **Skipped**: {jobs_skipped}
- **Rejections detected**: {rejections}

## Learnings & Observations
- Auto-generated session log for continuous learning context.
"""
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created Session Note: {filepath}")

    def create_mail_note(self, job: Job, draft):
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        safe_company = job.company.replace("/", "_").replace("\\", "_")
        filename = f"Mail-{safe_company}-{timestamp}.md"
        filepath = os.path.join(self.mail_logs_dir, filename)
        
        content = f"""---
company: {job.company}
role: {job.title}
date: {datetime.now().strftime("%Y-%m-%d %H:%M")}
score: {job.confidence_score}
personal_touch_score: {draft.personal_touch_score}
---

# Sent Email to {job.company}

## Subject
**{draft.subject}**

## Body
{draft.body}

## Attachments
- {draft.pdf_path}

## Context / Intel Used
{job.company_intel if job.company_intel else 'None'}
"""
        with open(filepath, "w") as f:
            f.write(content)

    def update_heartbeat(self, total_applied: int, new_rejections: int):
        filepath = os.path.join(self.internships_dir, "Heartbeat.md")
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                f.write("# InternHunter System Heartbeat\n\n## Daily Logs\n")
                
        log_entry = f"\n### {date_str}\n- **New Applications**: {total_applied}\n- **New Rejections**: {new_rejections}\n- **Status**: Pipeline executed successfully.\n"
        
        with open(filepath, "a") as f:
            f.write(log_entry)

    def update_soul(self, resume_text: str, insights: str):
        filepath = os.path.join(self.internships_dir, "Soul.md")
        
        frontmatter = {
            "type": "system_soul",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        content = f"""---
{yaml.dump(frontmatter, default_flow_style=False)}---

# User Soul / Master Profile
*This note is autonomously managed by InternHunter.*

## 🧠 Learned Insights & Winning Patterns
{insights}

## 📄 Master Resume / Base Knowledge
```text
{resume_text}
```
"""
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Updated Soul.md at {filepath}")

    def move_to_rejected(self, company: str):
        for filename in os.listdir(self.notes_dir):
            if company.lower() in filename.lower():
                filepath = os.path.join(self.notes_dir, filename)
                with open(filepath, "r") as f:
                    content = f.read()
                
                content = content.replace('status: "Applied"', 'status: "Rejected / Ghosted"')
                content = content.replace('status: "Follow-up"', 'status: "Rejected / Ghosted"')
                
                with open(filepath, "w") as f:
                    f.write(content)
                print(f"Moved {company} to Rejected / Ghosted in Obsidian.")
                break
