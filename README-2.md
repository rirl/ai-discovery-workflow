
# Brainstorm OS CLI

Setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_key
chmod +x scripts/brainstorm
```

Usage:

```bash
./scripts/brainstorm "AI Discovery Process"
```

Outputs:

brainstorms/YYYY/MM/
- BRAIN-*.adoc
- prompt-BRAIN-*.adoc
