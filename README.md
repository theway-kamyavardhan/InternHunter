# intern-hunter-ai 🎯

> The most advanced internship cold-email automation system in 2026. Built specifically for AI/ML students targeting OpenAI, Anthropic, Google DeepMind, and other top-tier labs.

![Deploy Status](https://img.shields.io/badge/Deploy-One%20Command-brightgreen) ![License](https://img.shields.io/badge/License-MIT-blue) ![Local First](https://img.shields.io/badge/Architecture-Local_First-orange)

## 🚀 Why this is the #1 tool on GitHub

1. **AI Confidence Scorer**: Scores every scraped job 0-100 based on *your* resume. Only applies to high-signal roles (≥75).
2. **Company Intelligence Injection**: Pulls recent news, funding, or product launches for "Dream Companies" and weaves 1-2 hyper-relevant sentences into the cold email.
3. **Obsidian-Native Kanban Tracking**: Auto-creates beautiful Markdown notes with YAML frontmatter. Real-time Dataview analytics for Win-Rate, Response Time, and Pipeline Health.
4. **Telegram Human-Guidance Mode**: If the "Personal Touch Score" is low, or it's a Dream Company, it pauses the pipeline and sends the draft to Telegram. You reply `APPROVE`, `EDIT: ...`, `SKIP`, or `REWRITE`.
5. **Reply Intelligence**: Connects to your inbox via IMAP. If a company replies "not hiring", it auto-moves them to "Rejected/Ghosted". If they want an interview, it alerts you!

## 💡 How This Got Me Internships at Top-Tier Companies

Before building this, I was sending generic resumes to black-hole portals. With `intern-hunter-ai`, the system:
- Takes my master resume and uses Llama-3 (via Groq) to perfectly rewrite bullets matching the exact keywords of the Job Description.
- Generates a gorgeous, ATS-friendly PDF dynamically using `WeasyPrint` + LaTeX styling.
- Sends hyper-personalized emails via SendGrid/Gmail with randomized human-like delays (45-180s) to avoid spam filters.
- Follows up exactly 8-10 days later with a completely different, value-add angle.

## 📦 One-Command Setup

```bash
git clone https://github.com/yourusername/intern-hunter-ai.git
cd intern-hunter-ai
./setup.sh
```
*Note: Make sure to fill in your `.env` keys after setup!*

### Gmail App Password Guide
If you are using Gmail for sending/reading emails instead of SendGrid:
1. Go to your Google Account -> Security.
2. Enable 2-Step Verification.
3. Search for "App passwords".
4. Create a new App password named "Intern Hunter".
5. Paste the 16-character code into `GMAIL_APP_PASSWORD` and `IMAP_PASSWORD` in your `.env` file.

## 🛠️ Usage

```bash
# Run the complete daily pipeline immediately
intern-hunter start

# Run in Dry-Run mode to see what it WOULD do without sending anything
intern-hunter start --dry-run

# Run only for top-tier companies
intern-hunter start --top-tier-only

# Start the background scheduler (Runs at 8 AM daily, sends report at 8 PM)
intern-hunter schedule
```

## 📸 Screenshots

*(Add screenshots here of the generated PDF, the Obsidian Kanban board, and the Telegram bot in action!)*

## 🤝 Contributing
Read our [Contribution Guide](CONTRIBUTING.md) to see how you can add new scrapers or improve the LLM scoring logic.

## 📝 License
MIT License
