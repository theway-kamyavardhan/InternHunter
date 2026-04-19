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
        os.makedirs(self.notes_dir, exist_ok=True)
        
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
        
    def move_to_rejected(self, company: str):
        # Implementation for updating the frontmatter status to "Rejected / Ghosted"
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
