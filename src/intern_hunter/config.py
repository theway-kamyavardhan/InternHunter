import yaml
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List, Dict, Optional

CONFIG_DIR = Path("config")
DREAM_COMPANIES_PATH = CONFIG_DIR / "dream_companies.yaml"
HUNTER_CONFIG_PATH = CONFIG_DIR / "hunter_config.yaml"

class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str = Field(default="")
    GEMINI_API_KEY: str = Field(default="")
    SENDGRID_API_KEY: str = Field(default="")
    
    # Email configurations
    GMAIL_ADDRESS: str = Field(default="")
    GMAIL_APP_PASSWORD: str = Field(default="")
    IMAP_SERVER: str = Field(default="imap.gmail.com")
    IMAP_PORT: int = Field(default=993)
    IMAP_USERNAME: str = Field(default="")
    IMAP_PASSWORD: str = Field(default="")
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = Field(default="")
    TELEGRAM_CHAT_ID: str = Field(default="")
    
    # Obsidian
    OBSIDIAN_VAULT_PATH: str = Field(default="./obsidian_template")
    
    # Application runtime configurations (Loaded from yaml)
    max_emails_per_day: int = 15
    confidence_threshold: int = 75
    target_roles: List[str] = ["AI Engineer Intern", "Machine Learning Intern", "Research Intern", "Computer Vision Intern", "LLM Intern"]
    dream_companies: List[str] = []
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

def load_yaml_config(path: Path) -> Dict:
    if path.exists():
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

def get_settings() -> Settings:
    settings = Settings()
    
    # Merge YAML config
    yaml_config = load_yaml_config(HUNTER_CONFIG_PATH)
    if "max_emails_per_day" in yaml_config:
        settings.max_emails_per_day = yaml_config["max_emails_per_day"]
    if "confidence_threshold" in yaml_config:
        settings.confidence_threshold = yaml_config["confidence_threshold"]
    if "target_roles" in yaml_config:
        settings.target_roles = yaml_config["target_roles"]
        
    # Merge Dream Companies
    dream_config = load_yaml_config(DREAM_COMPANIES_PATH)
    if "companies" in dream_config:
        settings.dream_companies = dream_config["companies"]
        
    return settings

settings = get_settings()
