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

    # Measured 2026-10-15: outside a heredoc too, printf '%s' 'a\\b' printed a\b, and a\\\\b arrived as a\\b.
    def test_double_backslash_without_heredoc_is_refused(self):
        self.assertIsNotNone(guard.verdict("printf '%s' 'C:" + BS + BS + "Windows'"))
        self.assertIsNotNone(guard.verdict("node -e 'x(\"" + BS + BS + "d\")'"))
        self.assertIsNotNone(guard.verdict("grep x <<< 'a" + BS + BS + "b'"))

    def test_single_backslashes_pass(self):
        self.assertIsNone(guard.verdict("printf 'a" + BS + "nb' && echo $((1 << 2))"))


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


class SettingsPrecheckTests(unittest.TestCase):
    """The shell pre-check in settings.json starts the hook only for a command with a double backslash."""

    def run_precheck(self, command):
        import shutil
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("no bash")
        settings = json.loads((HOOK.parent.parent / "settings.json").read_text(encoding="utf-8"))
        hook = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        hook = hook.replace('"{{UV}}" run --script', '"' + Path(sys.executable).as_posix() + '"')
        hook = hook.replace("{{REPO}}", HOOK.parent.parent.as_posix())
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
        return subprocess.run([bash, "-c", hook], input=payload, capture_output=True, text=True)

    def test_double_backslash_outside_a_heredoc_reaches_the_hook(self):
        res = self.run_precheck("printf '%s' 'a" + BS + BS + "b'")
        self.assertEqual(json.loads(res.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_single_backslash_does_not_start_the_hook(self):
        res = self.run_precheck("printf 'a" + BS + "nb'")
        self.assertEqual((res.returncode, res.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
