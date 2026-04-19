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
    if not model_name:
        return False
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

def _run_wizard_impl():
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
    console.print("\n[bold cyan][3/6] Smart AI Engine Setup[/bold cyan]")
    
    use_cloud_only = False
    
    ai_choice = questionary.select(
        "How would you like to run the AI?",
        choices=[
            "1. Use an already downloaded local model (fastest)",
            "2. Download a specific new Ollama model (type the name)",
            "3. Use Cloud API only (Groq or Gemini - recommended for top-tier accuracy)"
        ]
    ).ask()

    if not ai_choice or ai_choice.startswith("3"):
        use_cloud_only = True
        update_env_file("LLM_PROVIDER", "groq")
        console.print("[green]Using Cloud API mode (Groq).[/green]")
    elif ai_choice.startswith("1"):
        pulled_models = get_pulled_ollama_models()
        if not pulled_models:
            console.print("[yellow]No local models found! Please download one or use Cloud API.[/yellow]")
            use_cloud_only = True
            update_env_file("LLM_PROVIDER", "groq")
        else:
            selected_model = questionary.select(
                "Select a downloaded model:",
                choices=pulled_models
            ).ask()
            if selected_model:
                update_env_file("LLM_PROVIDER", "ollama")
                update_env_file("OLLAMA_MODEL", selected_model)
                console.print(f"[green]✅ Selected local model: {selected_model}[/green]")
            else:
                use_cloud_only = True
                update_env_file("LLM_PROVIDER", "groq")
    elif ai_choice.startswith("2"):
        model_name = questionary.text("Enter exact model name (e.g. llama3.1:8b or qwen2.5:14b):").ask()
        if model_name:
            success = pull_ollama_model(model_name)
            if success:
                update_env_file("LLM_PROVIDER", "ollama")
                update_env_file("OLLAMA_MODEL", model_name)
            else:
                use_cloud_only = True
                update_env_file("LLM_PROVIDER", "groq")
        else:
            use_cloud_only = True
            update_env_file("LLM_PROVIDER", "groq")

    # 4. API Keys
    console.print("\n[bold cyan][4/6] API Keys (secure input)[/bold cyan]")
    if use_cloud_only:
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
    learn_choice = questionary.confirm("Would you like me to learn from your existing Obsidian notes now? (makes everything smarter)").ask()
    if learn_choice:
        with console.status("[yellow]Reading your Obsidian notes and learning...[/yellow]", spinner="dots"):
            from intern_hunter.obsidian_learner import learn_from_obsidian
            learn_from_obsidian()

    console.print("\n🎉 You're all set! Run `intern-hunter start` to begin hunting internships.")
    start_now = questionary.confirm("Ready to start hunting right now? (dry-run mode)").ask()
    if start_now:
        with console.status("[yellow]Running pipeline (dry-run)...[/yellow]", spinner="dots"):
            subprocess.run(["intern-hunter", "start", "--dry-run"], capture_output=True)
            console.print("[green]✅ Pipeline finished successfully![/green]")

def run_wizard():
    try:
        _run_wizard_impl()
    except Exception as e:
        console.print(Panel("⚠️ Something went wrong during setup. Please try again or choose Cloud mode.", border_style="red"))
