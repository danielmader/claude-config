#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""PreToolUse hook for Bash: refuse a heredoc that carries a double backslash.

On this Windows machine the Bash tool turns a double backslash in a heredoc body into a single one, while a
single backslash passes (measured 2026-10-07). A Python or JavaScript string literal needs the double one, so
"\\b" arrived as "\b" and wrote a backspace byte into a source file; earlier a regex became a NUL byte and
'C:\\Windows' became 'C:Windows' (see rules/windows-shell.md). The way out is to write the script with the
Write tool and run the file, or to edit with the Edit tool; both pass backslashes unchanged.
"""
import json
import re
import sys

HEREDOC = re.compile(r"(?<!<)<<-?(?!<)\s*['\"]?[A-Za-z_]")
DOUBLE_BACKSLASH = "\\\\"

REASON = (
    "This command has a heredoc and a double backslash. The Bash tool turns a double backslash in a heredoc "
    "into a single one, which silently corrupts string literals and regexes. Write the script with the Write "
    "tool into the scratchpad and run that file, or change files with the Edit tool."
)


def verdict(command: str):
    """The reason to refuse the command, or None to let it run."""
    if HEREDOC.search(command) and DOUBLE_BACKSLASH in command:
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
