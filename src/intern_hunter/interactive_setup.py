import os
import yaml
import questionary
import psutil
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path

console = Console()

def update_env_file(key, value):
    env_path = ".env"
    if not os.path.exists(env_path):
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as f:
                content = f.read()
            with open(env_path, "w") as f:
                f.write(content)
        else:
            open(env_path, "w").close()

    with open(env_path, "r") as f:
        lines = f.readlines()

    found = False
    with open(env_path, "w") as f:
        for line in lines:
            if line.startswith(f"{key}="):
                f.write(f'{key}="{value}"\n')
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f'{key}="{value}"\n')

def update_yaml_config(filepath, key, value):
    path = Path(filepath)
    data = {}
    if path.exists():
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
    
    data[key] = value
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)

def detect_obsidian_vault() -> str | None:
    common_paths = [
        Path.home() / "Obsidian" / "Internships",
        Path.home() / "Documents" / "Obsidian" / "Internships",
        Path.home() / "vault" / "Internships",
        Path("obsidian_template")
    ]
    for p in common_paths:
        if p.exists():
            return str(p.parent if p.name == "Internships" else p)
    return None

def recommend_ollama_model(ram_gb: float) -> str:
    if ram_gb >= 32:
        return "llama3.3:70b"
    elif ram_gb >= 16:
        return "llama3.1:8b"
    else:
        return "gemma2:9b"

def pull_ollama_model(model_name: str):
    console.print(f"[yellow]Pulling {model_name} (this might take a few minutes)...[/yellow]")
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
        console.print(f"[green]Successfully pulled {model_name}![/green]")
        return True
    except FileNotFoundError:
        console.print("[red]Ollama is not installed. Please install it from ollama.com and run again.[/red]")
        return False
    except subprocess.CalledProcessError:
        console.print(f"[red]Failed to pull {model_name}. You may need to run `ollama pull {model_name}` manually.[/red]")
        return False

def run_wizard():
    console.clear()
    console.print(Panel.fit("🚀 Let's set up InternHunter in under 2 minutes", style="bold cyan"))

    # 1. Obsidian Vault
    console.print("\n[bold cyan][1/6] Obsidian Vault Path[/bold cyan]")
    default_vault = detect_obsidian_vault() or str(Path.home() / "Obsidian")
    vault_path = questionary.path(
        "Where is your Obsidian vault folder?",
        default=default_vault,
    ).ask()
    if vault_path:
        update_env_file("OBSIDIAN_VAULT_PATH", vault_path)

    # 2. Master Resume
    console.print("\n[bold cyan][2/6] Master Resume[/bold cyan]")
    has_resume = os.path.exists("master_resume.md") or os.path.exists("kamyavardhan-dave-resume.pdf")
    if has_resume:
        review = questionary.confirm("→ Found master resume. Want to review/edit it now?").ask()
        if review:
            console.print("[yellow]Please open master_resume.md in your editor. Press Enter when done.[/yellow]")
            input()
    else:
        console.print("[red]→ No master_resume.md found! Please create one.[/red]")

    # 3. Local AI Support
    console.print("\n[bold cyan][3/6] Hardware Detection & Local AI[/bold cyan]")
    ram_gb = psutil.virtual_memory().total / (1024**3)
    
    table = Table(title="Hardware Analysis vs Local Models")
    table.add_column("Your Hardware", style="cyan")
    table.add_column("Recommended Model", style="magenta")
    table.add_column("Expected Quality", style="green")
    
    table.add_row("8-12 GB RAM", "Gemma2 9B", "Good for basic emails/scoring")
    table.add_row("16-24 GB RAM", "Llama 3.1 8B", "Very Fast - Sweet Spot")
    table.add_row("32+ GB RAM", "Llama 3.3 70B Q4", "Close to cloud-level reasoning")
    console.print(table)
    console.print(f"\n[italic]Detected RAM: {ram_gb:.1f} GB[/italic]")

    use_ollama = questionary.confirm("Want to run everything locally with Ollama? (Free & Private)").ask()
    if use_ollama:
        recommended = recommend_ollama_model(ram_gb)
        model_choice = questionary.select(
            "Which model would you like to use?",
            choices=["gemma2:9b", "llama3.1:8b", "llama3.3:70b", "qwen2.5:32b", "phi3.5:mini"],
            default=recommended
        ).ask()
        
        success = pull_ollama_model(model_choice)
        if success:
            update_env_file("LLM_PROVIDER", "ollama")
            update_env_file("OLLAMA_MODEL", model_choice)
        else:
            console.print("[yellow]Falling back to cloud models...[/yellow]")
            update_env_file("LLM_PROVIDER", "groq")
    else:
        update_env_file("LLM_PROVIDER", "groq")

    # 4. API Keys
    console.print("\n[bold cyan][4/6] API Keys (secure input)[/bold cyan]")
    if not use_ollama:
        groq_key = questionary.password("→ Groq API Key (Primary Cloud Provider):").ask()
        if groq_key: update_env_file("GROQ_API_KEY", groq_key)

        gemini_key = questionary.password("→ Gemini API Key (Fallback):").ask()
        if gemini_key: update_env_file("GEMINI_API_KEY", gemini_key)

    tg_token = questionary.password("→ Telegram Bot Token:").ask()
    if tg_token: update_env_file("TELEGRAM_BOT_TOKEN", tg_token)

    gmail_pw = questionary.password("→ Gmail App Password (or SendGrid Key):").ask()
    if gmail_pw: update_env_file("GMAIL_APP_PASSWORD", gmail_pw)

    # 5. Settings
    console.print("\n[bold cyan][5/6] Application Settings[/bold cyan]")
    threshold = questionary.text("→ Confidence Threshold (0-100) [Default: 75]:", default="75").ask()
    if threshold and threshold.isdigit():
        update_yaml_config("config/hunter_config.yaml", "confidence_threshold", int(threshold))

    limit = questionary.text("→ Daily Email Limit [Default: 15]:", default="15").ask()
    if limit and limit.isdigit():
        update_yaml_config("config/hunter_config.yaml", "max_emails_per_day", int(limit))

    console.print("\n[bold green]✅ Setup complete![/bold green]")

    # 6. Self-learning
    console.print("\n[bold cyan][6/6] Obsidian Self-Learning Engine[/bold cyan]")
    if questionary.confirm("Would you like me to learn from your existing Obsidian notes now? (makes everything smarter)").ask():
        from intern_hunter.obsidian_learner import learn_from_obsidian
        learn_from_obsidian()

    console.print("\n🎉 You're all set! Run `intern-hunter start` to begin hunting internships.")
    start_now = questionary.confirm("Ready to start hunting right now? (dry-run mode)").ask()
    if start_now:
        os.system("intern-hunter start --dry-run")
