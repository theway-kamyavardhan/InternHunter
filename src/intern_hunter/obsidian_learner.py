import os
import glob
import yaml
from pathlib import Path
from rich.console import Console
from intern_hunter.config import settings
from intern_hunter.core.llm import get_llm_client
from intern_hunter.core.obsidian_tracker import ObsidianTracker
from intern_hunter.core.resume_tailor import ResumeTailor

console = Console()

def read_file_safe(filepath: str) -> str:
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return f.read()
    return ""

def learn_from_obsidian():
    vault_path = settings.OBSIDIAN_VAULT_PATH
    internships_dir = os.path.join(vault_path, "Internships")
    apps_dir = os.path.join(internships_dir, "Applications")
    mail_dir = os.path.join(internships_dir, "Mail-Logs")
    
    console.print(f"🤖 Starting autonomous self-learning from vault: {vault_path}...")
    
    # 1. Read existing Soul and Heartbeat
    soul_content = read_file_safe(os.path.join(internships_dir, "Soul.md"))
    heartbeat_content = read_file_safe(os.path.join(internships_dir, "Heartbeat.md"))
    
    # 2. Read Master Resume
    tailor = ResumeTailor()
    try:
        resume_text = tailor._read_master_resume()
    except:
        resume_text = "Failed to load master resume."
    
    # 3. Read Session Notes (last 5 to save context window)
    session_files = sorted(glob.glob(os.path.join(internships_dir, "Session-*.md")), reverse=True)[:5]
    sessions_data = "\n".join([read_file_safe(f) for f in session_files])
    
    # 4. Read Mail Logs (last 5)
    mail_files = sorted(glob.glob(os.path.join(mail_dir, "*.md")), reverse=True)[:5]
    mails_data = "\n".join([read_file_safe(f) for f in mail_files])
    
    # 5. Extract Application Outcomes
    app_files = glob.glob(os.path.join(apps_dir, "*.md"))
    outcomes = []
    for md in app_files:
        content = read_file_safe(md)
        if content.startswith("---"):
            try:
                end_idx = content.find("---", 3)
                frontmatter = yaml.safe_load(content[3:end_idx])
                if isinstance(frontmatter, dict):
                    status = frontmatter.get('status')
                    if status != "Applied": # Only log actionable statuses
                        outcomes.append(f"{frontmatter.get('company')} | {frontmatter.get('role')} | {status}")
            except:
                pass

    llm = get_llm_client()
    
    prompt = f"""
    You are the 'Soul' of InternHunter AI. Your goal is to analyze the user's history and extract deep insights
    to make future email drafts, scoring algorithms, and resume tailoring highly effective.
    
    Analyze the following context carefully:
    
    [PAST SOUL]:
    {soul_content[:1500]}
    
    [HEARTBEAT LOGS]:
    {heartbeat_content[-1000:]}
    
    [RECENT OUTCOMES]:
    {chr(10).join(outcomes[:50])}
    
    [RECENT MAILS SENT]:
    {mails_data[:2000]}
    
    Task: Extract the user's core identity, strengths, best-performing tone, preferred projects, 
    and identify what types of emails/roles are actually getting replies or rejections.
    Output a beautifully formatted markdown section under the title "🧠 Learned Insights & Winning Patterns"
    that will completely replace the old Soul's insights. Keep it extremely actionable.
    """
    
    try:
        console.print("[cyan]Generating new Soul profile via LLM...[/cyan]")
        insights = llm.generate(prompt, temperature=0.3)
        
        # Clean up output
        if "🧠 Learned Insights & Winning Patterns" in insights:
            insights = insights.split("🧠 Learned Insights & Winning Patterns")[1].strip()
        
        # Update Soul.md in Obsidian
        tracker = ObsidianTracker()
        tracker.update_soul(resume_text, insights)
        
        console.print("[bold green]✅ Autonomous learning complete. Soul.md updated![/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error during autonomous learning: {e}[/red]")
