#!/usr/bin/env python3
import os
import re
from markdown_it import MarkdownIt
import subprocess
from collections import defaultdict
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

TODO_FILE = "todo.md"
LOG_FILE = ".git/hooks/tmp/task_log_commit_msg.txt"

# TODO: Check todo.md is staged
if not os.path.exists(TODO_FILE):
    exit(0)

with open(TODO_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# First thing, normalize TBD's
import dateparser
from datetime import datetime

def parse_natural_date(text: str) -> str | None:
    settings = {
        "PREFER_DATES_FROM": "future",
        "RELATIVE_BASE": datetime.now(),
        "STRICT_PARSING": False,
    }

    return dateparser.parse(text, settings=settings)

def replace_tbd(match) -> str:
    raw_date = match.group(1)
    parsed = parse_natural_date(raw_date)
    isodate = parsed.date().isoformat()
    if parsed and isodate != raw_date:
        print(f"[TBD] Found. Will replace {raw_date} with {parsed}")
        return f"[TBD:{isodate}]"
    else:
        return match.group(0)  # leave unchanged if unparseable

def normalize_tbd_tags(line: str) -> str:
    return re.sub(r"\[TBD:\s*([^\]]+)\s*\]", replace_tbd, line)

content = "\n".join(normalize_tbd_tags(line) for line in content.splitlines())

import yaml
from yaml.loader import SafeLoader
from pathlib import Path

# load config YAML file in same folder as this script
script_dir = Path(__file__).resolve().parent
yaml_path = script_dir / "config.yaml"

with open(yaml_path, "r", encoding="utf‑8") as f:
    data = yaml.load(f, Loader=SafeLoader)

section_headers = data.get("section_headers", [])
groups = data.get("groups", {})

# Initialize AST parser
md = MarkdownIt()
tokens = md.parse(content)

# Store moved tasks per section
tasks_to_add = defaultdict(list)

# Store where sections are in the content
section_lines = {}

# When we find items to move, register where to remove from
line_ranges_to_remove = []

log_moves = []

# --- First pass: Moved tasks ---
#TODO: Refactor to yielding iterator so the current_section state finder can be reused later
current_section = None
for i, token in enumerate(tokens):
    if token.type == "heading_open":
        next_token = tokens[i + 1]
        heading_text = next_token.content.strip()
        current_section = section_headers.get(heading_text)

    elif token.type == "inline" and current_section:
        match = re.match(r"^\s*\[([^\]]*)\]\s+(.*)", token.content)
        if match:
            state, task_text = match.groups()
            new_section = groups.get(state)
            if new_section and new_section != current_section:
                tasks_to_add[new_section].append("- " + token.content)

                print(f"{current_section} -> {new_section}: {task_text}")
                log_moves.append(f"{current_section} -> {new_section}: {task_text}")
                # Remove the line
                line_ranges_to_remove.append(token.map)


# After parsing, move to line-based processing to mend the file
lines = content.splitlines()

# --- Remove moved lines ---
for start, end in sorted(line_ranges_to_remove, reverse=True):
    del lines[start:end]

# --- Second pass: Map where headers are now after removal of tasks ---
content = "\n".join(lines) + "\n"
tokens = md.parse(content)

current_section = None
for i, token in enumerate(tokens):
    if token.type == "heading_open":
        next_token = tokens[i + 1]
        heading_text = next_token.content.strip()
        current_section = section_headers.get(heading_text)
        if current_section and token.map:
            print(f"Found section {current_section} in line {token.map[1]}")
            section_lines[current_section] = token.map[1]

# --- Add moved tasks to new sections ---
for section, insert_at in sorted(section_lines.items(), key=lambda x: x[1], reverse=True):
    if section in tasks_to_add:
        lines[insert_at:insert_at] = tasks_to_add[section]

updated_content = "\n".join(lines) + "\n"

# Write back modified todo.md
with open(TODO_FILE, "w", encoding="utf-8") as f:
    f.write(updated_content)

# Stage the updated file
subprocess.run(["git", "add", TODO_FILE])

# Log moves
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.writelines(line + "\n" for line in log_moves)
