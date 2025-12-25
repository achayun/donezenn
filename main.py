import io
import os
import re
import sys
import dateparser
import subprocess
from datetime import datetime
from markdown_it import MarkdownIt
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

LOG_FILE = ".git/hooks/tmp/task_log_commit_msg.txt"

log_moves = []
md = MarkdownIt()

def parse_natural_date(text: str) -> str | None:
    settings = {
        "PREFER_DATES_FROM": "future",
        "RELATIVE_BASE": datetime.now(),
        "STRICT_PARSING": False,
    }

    return dateparser.parse(text, settings=settings)

def replace_tbd(match) -> str:
    label = match.group(1)
    raw_date = match.group(2)
    parsed = parse_natural_date(raw_date)
    isodate = parsed.date().isoformat()
    if parsed and isodate != raw_date:
        log_moves.append(f"[{label}] {raw_date} -> {isodate}")
        return f"[{label}:{isodate}]"
    else:
        return match.group(0)  # leave unchanged

def normalize_tbd_tags(line: str) -> str:
    return re.sub(r"\[(TBD):\s*([^\]]+)\s*\]", replace_tbd, line)

def get_staged_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, check=True,
    )
    return result.stdout.strip().splitlines()

def process_md(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        content = f.read()

    # - 1st phase: Parse the md file as Markdown
    # Initialize AST parser
    tokens = md.parse(content)

    # --- First pass: Map headers with status
    status_headers = defaultdict()
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            next_token = tokens[i + 1]
            heading_text = next_token.content.strip()
            status_heading = re.match(r"^\s*\[([^\]]*)\]\s*(.*)", heading_text)
            if status_heading:
                current_section_status, current_section = status_heading.groups()
                status_headers[current_section_status] = current_section

    tasks_to_add = defaultdict(list)
    line_ranges_to_remove = []

    # --- First pass: Find tasks with changed status ---
    #TODO: Refactor to yielding iterator so the current_section state finder can be reused later
    current_section = None
    current_section_status = None
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            next_token = tokens[i + 1]
            heading_text = next_token.content.strip()
            status_heading = re.match(r"^\s*\[([^\]]*)\]\s*(.*)", heading_text)
            if status_heading:
                current_section_status, current_section = status_heading.groups()
            else:
                current_section_status = None
                current_section = heading_text

        elif token.type == "inline":
            task = re.match(r"^\s*\[([^\]]*)\]\s+(.*)", token.content)
            if task:
                status, task_text = task.groups()
                if status and status != current_section_status and status in status_headers:
                    task_content = token.content
                    # Add the section header text as a tag to the task, if not there
                    if current_section and not re.match(rf".*\[\s*{re.escape(current_section)}\s*\].*", task_content):
                        task_content+= f" [{current_section}]"
                    # Mark lines to be added under new status sections
                    tasks_to_add[status].append("- " + task_content)

                    # Mark the line to be removed
                    line_ranges_to_remove.append(token.map)

                    log_moves.append(f"{current_section} -> {status_headers[status]}: {task_text}")
                    print(log_moves[-1])


    # - 2nd phase: Line based processing to update the file
    lines = content.splitlines()

    # First thing, normalize TBD
    lines = [normalize_tbd_tags(line) for line in lines]

    # --- Status change: First remove moved lines ---
    for start, end in sorted(line_ranges_to_remove, reverse=True):
        del lines[start:end]

    # --- Second pass: Map where headers are now after removal of tasks ---
    content = "\n".join(lines) + "\n"
    tokens = md.parse(content)

    section_lines = {}
    current_section = None
    current_section_status = None
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            next_token = tokens[i + 1]
            heading_text = next_token.content.strip()
            status_heading = re.match(r"^\s*\[([^\]]*)\]\s*(.*)", heading_text)
            if status_heading:
                current_section_status, current_section = status_heading.groups()
            else:
                current_section_status = None
                current_section = heading_text
            if current_section_status and token.map:
                section_lines[current_section_status] = token.map[1]

    # --- Add moved tasks to new sections, reverse iterate so the line numbers are always coherent ---
    for section, insert_at in sorted(section_lines.items(), key=lambda x: x[1], reverse=True):
        if section in tasks_to_add:
            lines[insert_at:insert_at] = tasks_to_add[section]

    # Log moves
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.writelines(line + "\n" for line in log_moves)

    # - 3rd phase: Finally write the updated content and stage it
    updated_content = "\n".join(lines) + "\n"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(updated_content)
    subprocess.run(["git", "add", file_name])

def main():
    markdown_files = [f for f in get_staged_files() if f.endswith(".md")]
    [process_md(f) for f in markdown_files]

if __name__ == '__main__':
    main()
