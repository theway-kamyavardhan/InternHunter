import asyncio
from playwright.async_api import async_playwright
from typing import List
from bs4 import BeautifulSoup
from datetime import datetime
import uuid

from intern_hunter.models import Job
from intern_hunter.config import settings

class JobScraper:
    def __init__(self):
        self.target_roles = settings.target_roles
        self.dream_companies = [c.lower() for c in settings.dream_companies]
        
    async def scrape_remoteok(self) -> List[Job]:
        # For remoteok, we could use Playwright or just aiohttp. We'll use Playwright for robustness.
        jobs = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto("https://remoteok.com/remote-ai-jobs", timeout=15000)
                await page.wait_for_selector("tr.job", timeout=5000)
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                
                for row in soup.find_all("tr", class_="job"):
                    title_elem = row.find("h2", itemprop="title")
                    company_elem = row.find("h3", itemprop="name")
                    url_elem = row.find("a", itemprop="url")
                    
                    if title_elem and company_elem and url_elem:
                        title = title_elem.text.strip()
                        company = company_elem.text.strip()
                        url = "https://remoteok.com" + url_elem["href"]
                        
                        # Basic filtering
                        if any(role.lower() in title.lower() for role in self.target_roles):
                            is_dream = company.lower() in self.dream_companies
                            job = Job(
                                id=str(uuid.uuid4()),
                                title=title,
                                company=company,
                                location="Remote",
                                description=f"Scraped from RemoteOK. Role: {title}", # Ideally fetch full JD by clicking, but keeping it simple for now
                                url=url,
                                posted_at=datetime.now(),
                                is_dream_company=is_dream
                            )
                            jobs.append(job)
            except Exception as e:
                print(f"Failed to scrape RemoteOK: {e}")
            finally:
                await browser.close()
        return jobs
        
    async def run(self) -> List[Job]:
        print("Starting Playwright scraper for RemoteOK...")
        jobs = await self.scrape_remoteok()
        print(f"Scraped {len(jobs)} jobs.")
        return jobs
