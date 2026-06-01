
#!/usr/bin/env python3
import os, re, json
from pathlib import Path
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

def next_id(repo):
    counter = repo / ".brainstorm-counter"
    n = 1
    if counter.exists():
        n = int(counter.read_text().strip())
    counter.write_text(str(n + 1))
    return n

def create(topic, repo="."):
    repo = Path(repo)
    now = datetime.now()
    seq = next_id(repo)
    bid = f"BRAIN-{now:%Y%m%d}-{seq:03d}"
    slug = slugify(topic)

    prompt = f"brainstorm {topic}"

    system = """
Respond using the Brainstorm OS format:
1. Human Discussion
2. Structured AsciiDoc Log
"""

    resp = client.responses.create(
        model="gpt-5.5",
        instructions=system,
        input=prompt
    )

    content = resp.output_text

    outdir = repo / "brainstorms" / f"{now:%Y}" / f"{now:%m}"
    outdir.mkdir(parents=True, exist_ok=True)

    brainfile = outdir / f"{bid}-{slug}.adoc"
    promptfile = outdir / f"prompt-{bid}-{slug}.adoc"

    brainfile.write_text(content, encoding="utf-8")

    promptfile.write_text(f"""= Prompt Artifact

[metadata]
----
ID: {bid}
Date: {now:%F}
Topic: {topic}
ArtifactType: Prompt
RelatedBrainstorm: {bid}
----

[prompt]
----
brainstorm {topic}
----
""", encoding="utf-8")

    print(brainfile)
    print(promptfile)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: brainstorm-cli '<topic>'")
        raise SystemExit(1)
    create(sys.argv[1])
