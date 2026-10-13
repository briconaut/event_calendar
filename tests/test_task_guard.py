"""Tests für .claude/hooks/task-guard.py gegen einen temporären taskctl-Store."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOOK = REPO / ".claude" / "hooks" / "task-guard.py"
ARCH = Path(os.environ.get("ARCH_TOOLS_DIR", Path.home() / "ai-architecture-tools"))


@unittest.skipUnless((ARCH / "architecture/scripts/taskctl.py").exists(), "ai-architecture-tools nicht vorhanden")
class TestTaskGuard(unittest.TestCase):
    def setUp(self):
        self.proj = Path(tempfile.mkdtemp())
        (self.proj / "tools").mkdir()
        shutil.copy(REPO / "tools" / "taskctl", self.proj / "tools" / "taskctl")
        self.env = {**os.environ, "CLAUDE_PROJECT_DIR": str(self.proj), "ARCH_TOOLS_DIR": str(ARCH)}
        self.tc("add-phase", "P")
        self.a = self.add("Erste")
        self.b = self.add("Zweite")

    def tearDown(self):
        shutil.rmtree(self.proj)

    def tc(self, *args):
        r = subprocess.run([str(self.proj / "tools" / "taskctl"), "--root", "docs", *args],
                           cwd=self.proj, env=self.env, capture_output=True, text=True, check=True)
        return r.stdout

    def add(self, name, review="user"):
        self.tc("add", "--phase", "P", "--name", name, "--review", review)
        return json.loads(self.tc("--json", "list"))[-1]["id"]

    def hook(self, tool="Bash", **tool_input):
        r = subprocess.run(["python3", str(HOOK)], input=json.dumps({"tool_name": tool, "tool_input": tool_input}),
                           env=self.env, capture_output=True, text=True)
        return r.returncode, r.stderr

    def bash(self, command):
        return self.hook(command=command)[0]

    def test_claim_next_task_allowed(self):
        self.assertEqual(self.bash(f'tools/taskctl --root docs set-status {self.a} "~" --message go'), 0)

    def test_claim_other_task_denied(self):
        rc, err = self.hook(command=f'tools/taskctl --root docs set-status {self.b} "~" --message go')
        self.assertEqual(rc, 2)
        self.assertIn("nicht dran", err)

    def test_blocked_plan_denies_later_claim(self):
        self.tc("set-status", self.a, "~", "--message", "go")
        self.tc("set-status", self.a, "R", "--message", "review")
        rc, err = self.hook(command=f'tools/taskctl --root docs set-status {self.b} "~" --message go')
        self.assertEqual(rc, 2)
        self.assertIn("Plan blockiert", err)
        # Nacharbeit an der blockierenden Task selbst bleibt erlaubt
        self.assertEqual(self.bash(f'tools/taskctl --root docs set-status {self.a} "~" --message rework'), 0)

    def test_approval_reserved_for_user(self):
        self.tc("set-status", self.a, "~", "--message", "go")
        self.tc("set-status", self.a, "R", "--message", "review")
        rc, err = self.hook(command=f"tools/taskctl --root docs set-status {self.a} X --message ok")
        self.assertEqual(rc, 2)
        self.assertIn("Nutzer", err)

    def test_force_and_set_status_denied(self):
        self.assertEqual(self.bash(f"tools/taskctl --root docs set-status {self.b} X --force --message x"), 2)
        self.assertEqual(self.bash("tools/taskctl --root docs add --phase P --name n --set-status X"), 2)

    def test_variable_ids_and_chains_checked(self):
        self.assertEqual(self.bash('f() { $TC set-status $1 "~" --message s; }; f abc'), 2)
        self.assertEqual(self.bash(f'echo hi && tools/taskctl --root docs set-status {self.b} "~" --message go'), 2)

    def test_direct_edits_of_task_files_denied(self):
        self.assertEqual(self.hook("Edit", file_path=str(self.proj / "docs/tasks/001-P/x.md"))[0], 2)
        self.assertEqual(self.bash("sed -i s/a/b/ docs/tasks/001-P/x.md"), 2)
        self.assertEqual(self.bash("ls docs/tasks"), 0)
        self.assertEqual(self.hook("Edit", file_path=str(self.proj / "README.md"))[0], 0)

    def test_unrelated_commands_pass(self):
        self.assertEqual(self.bash("python3 tools/ec.py validate"), 0)
        self.assertEqual(self.bash("tools/taskctl --root docs --json next"), 0)


if __name__ == "__main__":
    unittest.main()
