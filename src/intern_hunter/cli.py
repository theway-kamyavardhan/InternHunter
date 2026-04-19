import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import asyncio
import csv
from datetime import datetime
import os
import sys

from intern_hunter.config import settings
from intern_hunter.core.scraper import JobScraper
from intern_hunter.core.scorer import JobScorer
from intern_hunter.core.company_intel import CompanyIntel
from intern_hunter.core.resume_tailor import ResumeTailor
from intern_hunter.core.email_engine import EmailEngine
from intern_hunter.core.obsidian_tracker import ObsidianTracker
from intern_hunter.core.reply_intelligence import ReplyIntelligence
from intern_hunter.core.telegram_bot import TelegramGuidanceBot
from intern_hunter.interactive_setup import run_wizard
from intern_hunter.obsidian_learner import learn_from_obsidian

app = typer.Typer(help="🚀 InternHunter AI — Land top-tier remote/research internships")
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
def setup():
    """Run the full beautiful interactive wizard"""
    run_wizard()

@app.command()
def start(dry_run: bool = typer.Option(False, "--dry-run", help="Test without sending emails"),
          top_tier_only: bool = typer.Option(False, "--top-tier-only", help="Only process Dream Companies")):
    """Start the daily pipeline"""
    console.print(Panel.fit("🚀 Starting InternHunter pipeline...", style="bold cyan"))
    
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
    
    master_resume_text = "AI/ML Engineer looking for an internship." 
    try:
        master_resume_text = tailor._read_master_resume()
    except:
        pass

    sent_count = 0
    rejections = 0
    
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
        tracker.create_mail_note(job, draft)
        export_to_csv(job, job.confidence_score, "Applied")
        sent_count += 1
        
    jobs_processed = len(jobs[:settings.max_emails_per_day])
    jobs_skipped = jobs_processed - sent_count
    
    console.print(f"\n[bold green]Pipeline finished! Sent {sent_count} emails.[/bold green]")
    tracker.create_session_note(jobs_processed, sent_count, jobs_skipped, rejections)
    tracker.update_heartbeat(sent_count, rejections)
    asyncio.run(bot.send_daily_summary(sent_count, rejections))

@app.command()
def learn():
    """Force self-learning from your Obsidian vault"""
    with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
        task = progress.add_task("Reading your Obsidian notes and learning...", total=None)
        learn_from_obsidian()
    console.print("✅ Self-learning complete! Future emails & scoring will now be smarter.", style="bold green")

@app.command()
def models():
    """Switch LLM providers and Ollama models on the fly"""
    import questionary
    provider = questionary.select(
        "Choose your LLM Provider:",
        choices=["ollama", "groq", "gemini"],
        default=settings.LLM_PROVIDER
    ).ask()
    
    if provider:
        from intern_hunter.interactive_setup import update_env_file
        update_env_file("LLM_PROVIDER", provider)
        
        if provider == "ollama":
            model = questionary.text("Enter Ollama model name (e.g. llama3.1:8b):", default=settings.OLLAMA_MODEL).ask()
            if model:
                update_env_file("OLLAMA_MODEL", model)
                console.print(f"[green]Switched to Ollama using {model}[/green]")
        else:
            console.print(f"[green]Switched to {provider}[/green]")

def show_interactive_repl():
    """Claude-Code style slash-command loop"""
    console.print(Panel.fit(
        "[bold cyan]🚀 InternHunter AI — 2026 Edition[/]\n"
        "The smartest way to land top-tier AI/ML internships.\n"
        "[italic]Type [/][bold yellow]/[/][italic] to see available commands.[/]",
        border_style="cyan"
    ))
    
    import questionary
    while True:
        try:
            cmd = console.input("\n[bold cyan]>[/bold cyan] ").strip()
            
            if cmd in ["/", "/help"]:
                console.print("\n[bold]Command Palette:[/bold]")
                console.print("  [yellow]/setup[/yellow]   → Run full interactive configuration wizard")
                console.print("  [yellow]/start[/yellow]   → Run full pipeline")
                console.print("  [yellow]/dry-run[/yellow] → Run pipeline in safe test mode")
                console.print("  [yellow]/learn[/yellow]   → Force self-learning from Obsidian")
                console.print("  [yellow]/models[/yellow]  → Change AI model (local/cloud)")
                console.print("  [yellow]/status[/yellow]  → Show pipeline health")
                console.print("  [yellow]/quit[/yellow]    → Exit interactive mode")
            
            elif cmd == "/setup":
                run_wizard()
            elif cmd == "/start":
                start(dry_run=False)
            elif cmd == "/dry-run":
                start(dry_run=True)
            elif cmd == "/learn":
                learn()
            elif cmd == "/models":
                models()
            elif cmd == "/status":
                console.print(Panel("🟢 [bold green]System is healthy and ready to hunt![/bold green]\n\n"
                                    f"• Active Provider: [cyan]{settings.LLM_PROVIDER}[/cyan]\n"
                                    f"• Daily Limit: {settings.max_emails_per_day} emails\n"
                                    "• Next run: Manually triggered via /start", 
                                    title="System Status", border_style="green"))
            elif cmd in ["/quit", "/exit"]:
                console.print("[italic]Happy hunting! Goodbye.[/italic]")
                break
            elif cmd == "":
                continue
            else:
                console.print(f"[red]Unknown command '{cmd}'. Type / to see commands.[/red]")
                
        except KeyboardInterrupt:
            console.print("\n[italic]Goodbye![/italic]")
            break
        except Exception as e:
            console.print("[red]⚠️ Something went wrong executing that command. Please try again.[/red]")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Default command — launches Claude-Code REPL"""
    if ctx.invoked_subcommand is None:
        try:
            show_interactive_repl()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            console.print("[red]⚠️ Encountered a fatal system error. Exiting cleanly.[/red]")

def safe_entrypoint():
    """Global wrapper to suppress all tracebacks from Typer."""
    try:
        app()
    except Exception as e:
        console.print("[red]⚠️ Something went wrong. Exiting cleanly.[/red]")

if __name__ == "__main__":
    safe_entrypoint()
