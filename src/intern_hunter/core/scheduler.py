from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import asyncio
import pytz

def run_daily_pipeline():
    print(f"[{datetime.now()}] Running daily Intern-Hunter pipeline...")
    # Import and run the main cli `start` command logic here
    # from intern_hunter.cli import start
    # start(dry_run=False, top_tier_only=False)

def send_evening_report():
    print(f"[{datetime.now()}] Sending evening Telegram report...")
    # Trigger telegram_bot daily summary

def start_scheduler():
    scheduler = BlockingScheduler(timezone=pytz.timezone('Asia/Kolkata'))
    
    # 8 AM IST Pipeline
    scheduler.add_job(run_daily_pipeline, 'cron', hour=8, minute=0)
    
    # 8 PM IST Summary
    scheduler.add_job(send_evening_report, 'cron', hour=20, minute=0)
    
    print("Scheduler started. Waiting for next execution...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
