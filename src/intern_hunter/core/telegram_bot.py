from telegram import Bot
import asyncio
from intern_hunter.config import settings

class TelegramGuidanceBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        if self.token:
            self.bot = Bot(token=self.token)
        else:
            self.bot = None

    async def request_approval(self, job_title: str, company: str, draft_body: str) -> bool:
        """
        Sends draft to Telegram. Waits for 'APPROVE'. 
        (Mocking the wait for simplicity, normally requires a webhook or polling loop).
        """
        if not self.bot or not self.chat_id:
            print("Telegram bot not configured. Auto-approving.")
            return True
            
        message = f"🚨 *Approval Needed* 🚨\n\n*Role:* {job_title}\n*Company:* {company}\n\n*Draft:*\n{draft_body}\n\nReply APPROVE, SKIP, or EDIT."
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode="Markdown")
            print(f"Sent approval request to Telegram for {company}.")
            # In a real scenario, we would block and wait for the user's reply via webhook.
            # For this MVP, we just send it and assume it requires manual intervention later.
            return False # Pipeline pauses for this job
        except Exception as e:
            print(f"Telegram error: {e}")
            return True

    async def send_daily_summary(self, sent_count: int, rejections: int):
        if not self.bot or not self.chat_id:
            return
            
        message = f"📊 *Intern-Hunter Daily Summary* 📊\n\nEmails Sent: {sent_count}\nNew Rejections: {rejections}\nWin Rate: TBA%\n\nKeep hunting!"
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode="Markdown")
        except Exception as e:
            pass
