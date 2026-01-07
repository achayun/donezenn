#!/bin/bash
set -e

# If pre-commit hook prepared an action log, append it to the commit message
TASKS_LOG_FILE=".git/hooks/tmp/task_log_commit_msg.txt"
if [ -f "$TASKS_LOG_FILE" ]; then
  echo "" >> "$1"
  cat "$TASKS_LOG_FILE" >> "$1"
fi
