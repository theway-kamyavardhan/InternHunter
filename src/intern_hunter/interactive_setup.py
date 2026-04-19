import os
import yaml
import questionary
import psutil
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path
from rich.prompt import Confirm
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
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
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

def recommend_ollama_model(ram_gb: float) -> str:
    if ram_gb >= 32:
        return "llama3.3:70b"
    elif ram_gb >= 16:
        return "llama3.1:8b"
    else:
        return "gemma2:9b"

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
        
        looks_good = questionary.confirm("Looks good? (Y/n)").ask()
        if not looks_good:
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
    console.print("\n[bold cyan][3/6] Hardware Detection & Local AI[/bold cyan]")
    ram_gb = psutil.virtual_memory().total / (1024**3)
    cpu_cores = psutil.cpu_count(logical=True)
    gpu_info = detect_gpu()
    pulled_models = get_pulled_ollama_models()
    
    spec_panel = f"• **RAM**: {ram_gb:.1f} GB\n• **CPU Cores**: {cpu_cores}\n• **GPU**: {gpu_info}"
    console.print(Panel(Markdown(spec_panel), title="🖥️ Detected Hardware", border_style="blue"))
    
    table = Table(title="Hardware Analysis vs Local Models")
    table.add_column("Your Hardware", style="cyan")
    table.add_column("Recommended Model", style="magenta")
    table.add_column("Expected Quality vs Cloud", style="green")
    
    if ram_gb < 12:
        table.add_row("8-12 GB RAM", "Gemma2 9B", "80% (Good for basic tasks)")
        choices = ["gemma2:9b", "phi3.5:mini"]
    elif ram_gb < 28:
        table.add_row("16-24 GB RAM", "Llama 3.1 8B", "88% (Sweet Spot - Fast & Smart)")
        choices = ["llama3.1:8b", "gemma2:9b", "qwen2.5:14b"]
    else:
        table.add_row("32+ GB RAM", "Llama 3.3 70B Q4", "98% (Cloud-level reasoning)")
        choices = ["llama3.3:70b", "qwen2.5:32b", "llama3.1:8b"]
        
    console.print(table)

    if pulled_models:
        console.print(f"[italic]Already installed models: {', '.join(pulled_models)}[/italic]")

    use_ollama = questionary.confirm("Want to run everything locally with Ollama? (Free & Private)").ask()
    if use_ollama:
        recommended = recommend_ollama_model(ram_gb)
        model_choice = questionary.select(
            "Which model would you like to use?",
            choices=choices,
            default=recommended if recommended in choices else choices[0]
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
            console.print(f"[green]✅ {model_choice} is already pulled![/green]")
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
