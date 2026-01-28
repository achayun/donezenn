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

def header_breadcrumbs(heading_token, heading_text_token, heading_stack):
    level = int(heading_token.tag[1])
    title_text = heading_text_token.content

    # Pop the stack. Remove any headers from the stack that are deeper than (or equal to) the current level.
    updated_stack = [h for h in heading_stack if h['level'] < level]

    # Push the current header to stack
    updated_stack.append({'level': level, 'text': title_text})
    return updated_stack

def iter_tokens_with_section(tokens):
    current_section_status = None
    current_section = None
    breadcrumbs = []

    it = iter(tokens)

    for token in it:
        if token.type == "heading_open":
            next_token = next(it)  # consume the heading content token
            heading_text = next_token.content.strip()

            m = re.match(r"^\s*\[([^\]]*)\]\s*(.*)", heading_text)
            if m:
                current_section_status, current_section = m.groups()
            else:
                current_section_status = None
                current_section = heading_text
            breadcrumbs = header_breadcrumbs(token, next_token, breadcrumbs)
        yield token, current_section_status, current_section, breadcrumbs

def get_staged_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=d"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, check=True,
    )
    return result.stdout.strip().splitlines()

def map_headers_with_status(tokens):
    status_headers = defaultdict()
    for token, status, header, breadcrumbs in iter_tokens_with_section(tokens):
        if status and header:
            status_headers[status] = header
    return status_headers

def headers_to_tags(task, headers):
    new_tags = []
    if headers:
        # Add the section header text as a tag to the task, if not there. Use standard #hashtag syntax
        for header in [h for h in headers if h]:
            header_tag = f"#{re.sub(' ,', '_', header)}"
            if not re.search(rf"{re.escape(header_tag)}", task):
                new_tags.append(header_tag)
    return new_tags

def process_md(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        content = f.read()

    # - 1st phase: Parse the md file as Markdown
    tokens = md.parse(content)
    status_headers = map_headers_with_status(tokens)

    tasks_to_add = defaultdict(list)
    line_ranges_to_remove = []

    # --- First pass: Find tasks with changed status ---
    for token, current_section_status, current_section, breadcrumbs in iter_tokens_with_section(tokens):
        if token.type == "inline":
            task = re.match(r"^\s*\[([^\]]*)\]\s+(.*)", token.content)
            if task:
                status, task_text = task.groups()
                if status and status != current_section_status and status in status_headers:
                    tags = headers_to_tags(task_text, [h['text'] for h in breadcrumbs])
                    task_text += ' ' + ' '.join(tags) if len(tags) else ""

                    # Mark lines to be added under new status sections
                    tasks_to_add[status].append("- [" + status + "] " + task_text)

                    # Mark the line to be removed
                    line_ranges_to_remove.append(token.map)

                    log_moves.append(f"{current_section} -> {status_headers[status]}: {task_text}")

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
    for token, current_section_status, current_section, breadcrumbs in iter_tokens_with_section(tokens):
        if token.type == "heading_open" and current_section_status and token.map:
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
