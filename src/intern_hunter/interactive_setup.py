import os
import sys
import yaml
import questionary
import psutil
import subprocess
import platform
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
from rich.markdown import Markdown

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

def detect_gpu():
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"], 
            capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().replace(", ", " - ")
    except FileNotFoundError:
        pass
    return "None Detected"

def get_pulled_ollama_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]
            return [line.split()[0] for line in lines if line]
    except FileNotFoundError:
        pass
    return []

def pull_ollama_model(model_name: str):
    with console.status(f"[yellow]Pulling {model_name} (this might take a few minutes)...[/yellow]", spinner="dots"):
        try:
            subprocess.run(["ollama", "pull", model_name], check=True, capture_output=True)
            console.print(f"[green]✅ Successfully pulled {model_name}![/green]")
            return True
        except FileNotFoundError:
            console.print("[red]❌ Ollama is not installed. Please install it from ollama.com and run again.[/red]")
            return False
        except subprocess.CalledProcessError:
            console.print(f"[red]❌ Failed to pull {model_name}. You may need to run `ollama pull {model_name}` manually.[/red]")
            return False

def interactive_resume_editor():
    if os.path.exists("master_resume.md"):
        with open("master_resume.md", "r") as f:
            content = f.read()
            
        console.print(Panel(Markdown(content[:1500] + "\n\n*(Truncated for display)*"), title="📄 Resume Summary", border_style="cyan"))
        
        action = questionary.select(
            "Does this look correct?",
            choices=["Yes (Proceed)", "No (Skip)", "Edit (Section-by-section)"]
        ).ask()
        
        if action == "Edit (Section-by-section)":
            console.print("[yellow]Let's edit your resume interactively.[/yellow]")
            new_content = ""
            
            sections = ["Education", "Experience", "Projects", "Skills"]
            for section in sections:
                val = questionary.text(f"Enter your {section} (leave empty to skip):").ask()
                if val:
                    new_content += f"\n## {section}\n{val}\n"
            
            if new_content.strip():
                with open("master_resume.md", "w") as f:
                    f.write(new_content)
                console.print("[green]✅ Master resume updated![/green]")
    else:
        console.print("[red]→ No master_resume.md found! Please create one.[/red]")

def run_wizard():
    console.clear()
    console.print(Panel.fit("🚀 Let's set up InternHunter in under 2 minutes", style="bold cyan"))

    # 0. PC Specs
    console.print("\n[bold cyan][0/6] Detected System Specs[/bold cyan]")
    ram_gb = psutil.virtual_memory().total / (1024**3)
    cpu_cores = psutil.cpu_count(logical=True)
    gpu_info = detect_gpu()
    os_name = f"{platform.system()} {platform.release()}"

    spec_table = Table(show_header=False, box=None)
    spec_table.add_row("Total RAM:", f"[bold]{ram_gb:.1f} GB[/bold]")
    spec_table.add_row("CPU Cores:", f"[bold]{cpu_cores}[/bold]")
    spec_table.add_row("GPU:", f"[bold]{gpu_info}[/bold]")
    spec_table.add_row("Detected OS:", f"[bold]{os_name}[/bold]")
    console.print(Panel(spec_table, border_style="blue", title="🖥️ Hardware Profile"))

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
    interactive_resume_editor()

    # 3. Local AI Support
    console.print("\n[bold cyan][3/6] Smart Ollama Model Setup[/bold cyan]")
    pulled_models = get_pulled_ollama_models()
    
    model_table = Table(title="Available 2026 Models for your Hardware")
    model_table.add_column("Model Name", style="cyan")
    model_table.add_column("Size", style="yellow")
    model_table.add_column("Est. Accuracy vs Cloud", style="green")
    model_table.add_column("Recommended", style="magenta")
    
    choices = []
    default_model = "gemma2:9b"
    
    if ram_gb < 12:
        model_table.add_row("gemma2:9b", "5.5 GB", "80%", "Yes (Sweet Spot)")
        model_table.add_row("phi3.5:mini", "2.2 GB", "75%", "For low-end PCs")
        choices = ["gemma2:9b", "phi3.5:mini"]
        default_model = "gemma2:9b"
    elif ram_gb < 28:
        model_table.add_row("llama3.1:8b", "4.7 GB", "88%", "Yes (Sweet Spot)")
        model_table.add_row("gemma2:9b", "5.5 GB", "80%", "Alternative")
        model_table.add_row("qwen2.5:14b", "8.0 GB", "90%", "Heavier")
        choices = ["llama3.1:8b", "gemma2:9b", "qwen2.5:14b"]
        default_model = "llama3.1:8b"
    else:
        model_table.add_row("llama3.3:70b", "40.0 GB", "98%", "Yes (Cloud-level)")
        model_table.add_row("qwen2.5:32b", "20.0 GB", "95%", "Very fast & smart")
        model_table.add_row("llama3.1:8b", "4.7 GB", "88%", "Lightweight fallback")
        choices = ["llama3.3:70b", "qwen2.5:32b", "llama3.1:8b"]
        default_model = "llama3.3:70b"
        
    console.print(model_table)

    if pulled_models:
        console.print(f"[italic]You already have: {', '.join(pulled_models)}[/italic]")

    use_ollama = questionary.confirm("Want to run everything locally with Ollama? (Free & Private)").ask()
    if use_ollama:
        model_choice = questionary.select(
            "Which model would you like to use?",
            choices=choices,
            default=default_model if default_model in choices else choices[0]
        ).ask()
        
        if model_choice not in pulled_models:
            success = pull_ollama_model(model_choice)
            if not success:
                console.print("[yellow]Falling back to cloud models...[/yellow]")
                update_env_file("LLM_PROVIDER", "groq")
                use_ollama = False
            else:
                update_env_file("LLM_PROVIDER", "ollama")
                update_env_file("OLLAMA_MODEL", model_choice)
        else:
            console.print(f"[green]✅ {model_choice} is already ready to go![/green]")
            update_env_file("LLM_PROVIDER", "ollama")
            update_env_file("OLLAMA_MODEL", model_choice)
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
        with console.status("[yellow]Reading your Obsidian notes and learning...[/yellow]", spinner="dots"):
            from intern_hunter.obsidian_learner import learn_from_obsidian
            learn_from_obsidian()

    console.print("\n🎉 You're all set! Run `intern-hunter start` to begin hunting internships.")
    start_now = questionary.confirm("Ready to start hunting right now? (dry-run mode)").ask()
    if start_now:
        with console.status("[yellow]Running pipeline (dry-run)...[/yellow]", spinner="dots"):
            subprocess.run(["intern-hunter", "start", "--dry-run"], capture_output=True)
            console.print("[green]✅ Pipeline finished successfully![/green]")
