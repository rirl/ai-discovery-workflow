
#!/usr/bin/env python3
import argparse
import fcntl
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

DEFAULT_MODEL = "gpt-5.5"
MAX_SLUG_LENGTH = 50

def slugify(s, max_length=MAX_SLUG_LENGTH):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s[:max_length]

def next_id(repo):
    counter = repo / ".brainstorm-counter"
    lock_file = repo / ".brainstorm-counter.lock"

    with open(lock_file, 'w') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            n = 1
            if counter.exists():
                n = int(counter.read_text().strip())
            counter.write_text(str(n + 1))
            return n
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            lock_file.unlink(missing_ok=True)

def validate_inputs(topic, api_key):
    """Validate required inputs and environment."""
    if not topic or not topic.strip():
        raise SystemExit("Error: Topic is required. Usage: brainstorm-cli '<topic>'")
    if not api_key:
        raise SystemExit("Error: OPENAI_API_KEY environment variable is required")
    return topic.strip()

def get_client(api_key):
    """Create OpenAI client with error handling."""
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        raise SystemExit(f"Error: Failed to initialize OpenAI client: {e}")

def generate_response(client, topic, model):
    """Call OpenAI API and return response content."""
    prompt = f"brainstorm {topic}"
    system = """
    Respond using the Brainstorm OS format:
    1. Human Discussion
    2. Structured AsciiDoc Log
    """

    try:
        resp = client.responses.create(
            model=model,
            instructions=system,
            input=prompt
        )
        return resp.output_text
    except RateLimitError:
        raise SystemExit("Error: API rate limit exceeded. Please try again later.")
    except APIConnectionError as e:
        raise SystemExit(f"Error: Failed to connect to OpenAI API: {e}")
    except APIError as e:
        raise SystemExit(f"Error: OpenAI API error: {e}")

def write_outputs(repo, bid, topic, now, content):
    """Write brainstorm and prompt files to disk."""
    outdir = repo / "brainstorms" / f"{now:%Y}" / f"{now:%m}"
    try:
        outdir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise SystemExit(f"Error: Permission denied creating directory: {outdir}")
    except OSError as e:
        raise SystemExit(f"Error: Failed to create directory {outdir}: {e}")

    brainfile = outdir / f"{bid}-{slugify(topic)}.adoc"
    promptfile = outdir / f"prompt-{bid}-{slugify(topic)}.adoc"

    try:
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
    except PermissionError:
        raise SystemExit(f"Error: Permission denied writing to {brainfile}")
    except OSError as e:
        raise SystemExit(f"Error: Failed to write files: {e}")

    return brainfile, promptfile

def create(topic, repo=".", model=None):
    api_key = os.environ.get("OPENAI_API_KEY")
    topic = validate_inputs(topic, api_key)

    client = get_client(api_key)
    model = model or os.environ.get("BRAINSTORM_MODEL", DEFAULT_MODEL)

    repo = Path(repo)
    if not repo.exists():
        raise SystemExit(f"Error: Repository path does not exist: {repo}")

    now = datetime.now()
    seq = next_id(repo)
    bid = f"BRAIN-{now:%Y%m%d}-{seq:03d}"

    content = generate_response(client, topic, model)
    brainfile, promptfile = write_outputs(repo, bid, topic, now, content)

    print(brainfile)
    print(promptfile)

def main():
    parser = argparse.ArgumentParser(
        description="Create a new brainstorm document using OpenAI"
    )
    parser.add_argument("topic", help="The topic to brainstorm about")
    parser.add_argument("-r", "--repo", default=".", help="Repository path (default: .)")
    parser.add_argument("-m", "--model", help=f"OpenAI model (default: {DEFAULT_MODEL})")

    args = parser.parse_args()
    create(args.topic, repo=args.repo, model=args.model)

if __name__ == "__main__":
    main()
