import typer
from rich.console import Console
from rich.panel import Panel
import asyncio
import csv
from datetime import datetime
import os

from intern_hunter.config import settings
from intern_hunter.core.scraper import JobScraper
from intern_hunter.core.scorer import JobScorer
from intern_hunter.core.company_intel import CompanyIntel
from intern_hunter.core.resume_tailor import ResumeTailor
from intern_hunter.core.email_engine import EmailEngine
from intern_hunter.core.obsidian_tracker import ObsidianTracker
from intern_hunter.core.reply_intelligence import ReplyIntelligence
from intern_hunter.core.telegram_bot import TelegramGuidanceBot

app = typer.Typer(help="Intern-Hunter-AI: Automated AI/ML Internship Outreach")
console = Console()

def export_to_csv(job, score, status):
    date_str = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("exports", exist_ok=True)
    csv_file = f"exports/pipeline_{date_str}.csv"
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Date', 'Company', 'Title', 'Score', 'Status'])
        writer.writerow([date_str, job.company, job.title, score, status])

@app.command()
def start(dry_run: bool = typer.Option(False, "--dry-run", help="Run without sending emails or writing notes"),
          top_tier_only: bool = typer.Option(False, "--top-tier-only", help="Only process Dream Companies")):
    """
    Run the complete daily pipeline immediately.
    """
    console.print(Panel.fit("[bold green]Starting Intern-Hunter-AI Pipeline[/bold green] 🚀"))
    
    # 1. Scrape
    console.print("[cyan]Scraping jobs...[/cyan]")
    scraper = JobScraper()
    jobs = asyncio.run(scraper.run())
    console.print(f"Found {len(jobs)} total jobs.")
    
    if top_tier_only:
        jobs = [j for j in jobs if j.is_dream_company]
        console.print(f"Filtered to {len(jobs)} dream company jobs.")
        
    # Instantiate core engines
    scorer = JobScorer()
    intel = CompanyIntel()
    tailor = ResumeTailor()
    email_engine = EmailEngine()
    tracker = ObsidianTracker()
    bot = TelegramGuidanceBot()
    
    # Needs a dummy master resume text for scoring if PyMuPDF not fully used yet
    master_resume_text = "AI/ML Engineer looking for an internship." 
    try:
        master_resume_text = tailor._read_master_resume()
    except:
        pass

    sent_count = 0
    rejections = 0 # Dummy count for now
    
    for job in jobs[:settings.max_emails_per_day]:
        console.print(f"\n[bold]Evaluating:[/bold] {job.title} @ {job.company}")
        
        # 2. Score
        job = scorer.score_job(job, master_resume_text)
        console.print(f"Confidence Score: {job.confidence_score}")
        
        if job.confidence_score < settings.confidence_threshold and not job.is_dream_company:
            console.print("[yellow]Score too low. Skipping.[/yellow]")
            export_to_csv(job, job.confidence_score, "Skipped - Low Score")
            continue
            
        # 3. Company Intel
        if job.is_dream_company:
            console.print(f"[magenta]Dream Company Detected![/magenta] Generating Intel...")
            job.company_intel = intel.generate_intel(job.company)
            
        if dry_run:
            console.print("[yellow]DRY RUN: Skipping PDF generation and Email sending.[/yellow]")
            export_to_csv(job, job.confidence_score, "Dry Run")
            continue
            
        # 4. Tailor Resume
        console.print("[cyan]Tailoring resume & generating PDF...[/cyan]")
        pdf_path = tailor.tailor(job)
        
        # 5. Draft Email
        console.print("[cyan]Drafting Email...[/cyan]")
        draft = email_engine.generate_draft(job, pdf_path)
        
        # 6. Telegram Approval
        if job.is_dream_company or draft.personal_touch_score < 70:
            console.print("[yellow]Requesting Telegram Approval...[/yellow]")
            approved = asyncio.run(bot.request_approval(job.title, job.company, draft.body))
            if not approved:
                console.print("[yellow]Paused for manual approval. Skipping for now.[/yellow]")
                export_to_csv(job, job.confidence_score, "Pending Telegram Approval")
                continue
                
        # 7. Send & Track
        console.print(f"[green]Sending email for {job.company}...[/green]")
        email_engine.send_email("dummy_recruiter@example.com", draft)
        tracker.create_note(job)
        export_to_csv(job, job.confidence_score, "Applied")
        sent_count += 1
        
    console.print(f"\n[bold green]Pipeline finished! Sent {sent_count} emails.[/bold green]")
    asyncio.run(bot.send_daily_summary(sent_count, rejections))

@app.command()
def scrape():
    scraper = JobScraper()
    jobs = asyncio.run(scraper.run())
    for j in jobs:
        console.print(f"{j.title} @ {j.company}")

@app.command()
def report():
    console.print("[bold magenta]Checking replies and generating report...[/bold magenta]")
    reply_intel = ReplyIntelligence()
    reply_intel.check_replies()
    console.print("Check your Obsidian Kanban for updates!")

@app.command()
def schedule():
    console.print("[bold yellow]Starting background scheduler...[/bold yellow]")
    from intern_hunter.core.scheduler import start_scheduler
    start_scheduler()

if __name__ == "__main__":
    app()
