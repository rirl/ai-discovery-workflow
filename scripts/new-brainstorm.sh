
#!/usr/bin/env bash
#
# Legacy local template generator.
#
# The canonical brainstorm generator is scripts/brainstorm, which calls the
# Python/OpenAI workflow. Keep this script only when an offline template is
# useful.

read -p "Topic: " TOPIC

DATE=$(date +%Y%m%d)
YEAR=$(date +%Y)
MONTH=$(date +%m)

COUNTER_FILE=".brainstorm-counter"

LOCK_FILE=".brainstorm-counter.lock"
(
  flock -n 200 || { echo "Error: Another instance is running. Exiting."; exit 1; }
  if [ ! -f "$COUNTER_FILE" ]; then
    echo "1" > "$COUNTER_FILE"
  fi

  NUM=$(cat "$COUNTER_FILE")
  printf -v PAD "%03d" "$NUM"

  ID="BRAIN-${DATE}-${PAD}"

  NEXT=$((NUM+1))
  echo "$NEXT" > "$COUNTER_FILE"
) 200>$LOCK_FILE

SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g; s/--*/-/g; s/^-//; s/-$//')

DIR="brainstorms/${YEAR}/${MONTH}"
mkdir -p "$DIR"

BRAINFILE="${DIR}/${ID}-${SLUG}.adoc"
PROMPTFILE="${DIR}/prompt-${ID}-${SLUG}.adoc"

cat > "$BRAINFILE" <<EOF
= ${TOPIC}

[metadata]
----
ID: ${ID}
Date: $(date +%F)
Topic: ${TOPIC}
Status: Active
----

== Human Discussion

Paste ChatGPT discussion here.

== Structured Log

Paste ChatGPT structured log here.
EOF

cat > "$PROMPTFILE" <<EOF
= Prompt Artifact

[metadata]
----
ID: ${ID}
Date: $(date +%F)
Topic: ${TOPIC}
ArtifactType: Prompt
RelatedBrainstorm: ${ID}
----

[prompt]
----
brainstorm ${TOPIC}
----
EOF

echo "Created:"
echo "  $BRAINFILE"
echo "  $PROMPTFILE"
