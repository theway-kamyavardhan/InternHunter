# Contributing to intern-hunter-ai

Thank you for your interest! We are building the ultimate local-first AI agent for internship hunting. 

## Getting Started
1. Fork the repository
2. Run `./setup.sh` to install Poetry dependencies and set up the local environment.
3. Create a branch for your feature.
4. Submit a Pull Request!

## Areas for Contribution
- **Scrapers**: We currently support RemoteOK, LinkedIn (via search filters), etc. We need robust Playwright scripts for Wellfound, Internshala, and YC Work at a Startup.
- **LLM Prompts**: Our prompts in `src/intern_hunter/core/` can always be optimized to yield more human-sounding cold emails and better tailored resume bullets.
- **Obsidian Dataviews**: If you are a Dataview wizard, feel free to add more advanced analytics to `Kanban.md`.

Please ensure you write tests for any new core logic!
