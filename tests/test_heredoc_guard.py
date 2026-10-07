import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "heredoc_guard.py"
spec = importlib.util.spec_from_file_location("heredoc_guard", HOOK)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

BS = chr(92)


class VerdictTests(unittest.TestCase):
    def test_heredoc_with_double_backslash_is_refused(self):
        cmd = "python - <<'PY'\ns = \"" + BS + BS + "b\"\nPY"
        self.assertIsNotNone(guard.verdict(cmd))

    def test_heredoc_without_double_backslash_passes(self):
        cmd = "cat <<'EOF'\nplain text with one " + BS + "n\nEOF"
        self.assertIsNone(guard.verdict(cmd))

    def test_double_backslash_without_heredoc_passes(self):
        cmd = "printf '%s' 'C:" + BS + BS + "Windows'"
        self.assertIsNone(guard.verdict(cmd))

    def test_here_string_and_shift_are_not_heredocs(self):
        self.assertIsNone(guard.verdict("grep x <<< 'a" + BS + BS + "b'"))
        self.assertIsNone(guard.verdict("echo $((1 << 2)) '" + BS + BS + "'"))


class HookOutputTests(unittest.TestCase):
    def run_hook(self, command):
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
        return subprocess.run([sys.executable, str(HOOK)], input=payload, capture_output=True, text=True)

    def test_refusal_is_a_pretooluse_deny_with_the_way_out(self):
        res = self.run_hook("cat <<'EOF'\n" + BS + BS + "\nEOF")
        self.assertEqual(res.returncode, 0)
        out = json.loads(res.stdout)["hookSpecificOutput"]
        self.assertEqual(out["hookEventName"], "PreToolUse")
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("Write", out["permissionDecisionReason"])

    def test_allowed_command_prints_nothing(self):
        res = self.run_hook("ls -la")
        self.assertEqual((res.returncode, res.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
