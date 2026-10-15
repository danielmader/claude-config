#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""PreToolUse hook for Bash: refuse a command that carries a double backslash.

On Windows the Bash tool turns every double backslash of a command into a single one, while a single
backslash passes. That holds in a heredoc body (measured 2026-10-07) and also in single quotes, double quotes and
plain arguments (measured 2026-10-15: printf '%s' 'a\\b' printed a\b, and a\\\\b arrived as a\\b). A Python or
JavaScript string literal needs the double one, so "\\b" arrived as "\b" and wrote a backspace byte into a source file.
The way out is to write the script with the Write tool and run the file, or to edit with the Edit tool; both pass
backslashes unchanged. The hook sees the command before the loss, so it can refuse it.
"""
import json
import sys

DOUBLE_BACKSLASH = "\\\\"

REASON = (
    "This command has a double backslash. On Windows the Bash tool turns every double backslash into a single one, "
    "in a heredoc as well as in quotes and arguments, which silently corrupts string literals, regexes and paths. "
    "Write the script with the Write tool into the scratchpad and run that file, or change files with the Edit tool."
)


def verdict(command: str):
    """The reason to refuse the command, or None to let it run."""
    if DOUBLE_BACKSLASH in command:
        return REASON
    return None


def main() -> None:
    payload = json.load(sys.stdin)
    reason = verdict((payload.get("tool_input") or {}).get("command") or "")
    if reason:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))


if __name__ == "__main__":
    main()
