"""Packaging and installation regressions using isolated client paths."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(sys.argv.pop(1)).resolve()


def write_skill(root, name="demo", header=None, body="Follow the project instructions.\n"):
    directory = root / name
    directory.mkdir(parents=True, exist_ok=True)
    if header is None:
        header = f"name: {name}\ndescription: Exercise the fixture workflow."
    (directory / "SKILL.md").write_text(f"---\n{header}\n---\n\n{body}")
    return directory


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.skills = self.root / "skills"
        self.skills.mkdir()

    def validate(self, valid=True):
        result = subprocess.run(
            ["python3", "-B", str(REPO / "scripts/validate-skills.py"), str(self.skills)],
            capture_output=True, text=True,
        )
        if valid:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertEqual(result.stdout, "", "invalid registry leaked a partial active list")
        return result

    def test_supported_string_formats(self):
        for value in [
            "A plain description.", '"A description: with punctuation."',
            "'A user''s workflow.'", ">-\n  A folded\n  description.",
            "|\n  A literal description.\n  More detail.",
        ]:
            with self.subTest(value=value):
                directory = write_skill(self.skills, header=f"name: demo\ndescription: {value}")
                self.assertEqual(self.validate().stdout.strip(), str(directory))

    def test_required_metadata_and_string_types(self):
        invalid = [
            "name: demo", 'name: demo\ndescription: ""',
            "name: demo\ndescription: true", "name: demo\ndescription: 12",
            "name: demo\ndescription: yes",
            "name: demo\ndescription: .5",
            "name: [unclosed\ndescription: A description.",
            'name: demo\ndescription: "unclosed',
            "name: demo\ndescription: Fine.\nname: duplicate",
            "name: demo\ndescription: Fine.\ndisable-model-invocation: true",
            "name: other\ndescription: Fine.",
            "name: demo\ndescription: a: mapping", "name: demo\ndescription: - sequence",
            "name: demo\ndescription: # no value", "name: demo\ndescription: *alias",
            "name: demo\ndescription: >\n    first\n  invalid indentation",
        ]
        for header in invalid:
            with self.subTest(header=header):
                write_skill(self.skills, header=header)
                self.validate(False)
        directory = write_skill(self.skills)
        for contents in ["# No metadata\n", "---\nname: demo\n", "---\nname: demo\ndescription: Fine.\n---\n"]:
            with self.subTest(contents=contents):
                (directory / "SKILL.md").write_text(contents)
                self.validate(False)

    def test_every_active_directory_must_be_complete(self):
        write_skill(self.skills)
        (self.skills / "unfinished").mkdir()
        self.validate(False)
        (self.skills / "unfinished").rmdir()
        outside = write_skill(self.root / "foreign", name="external")
        (self.skills / "external").symlink_to(outside, target_is_directory=True)
        self.validate(False)

    def test_references_are_checked_recursively(self):
        directory = write_skill(self.skills, body="Read [the procedure](references/steps.md).\n")
        self.validate(False)
        (directory / "references").mkdir()
        (directory / "references/steps.md").write_text("Read [the asset](../assets/item%20(one).txt).\n")
        self.validate(False)
        (directory / "assets").mkdir()
        (directory / "assets/item (one).txt").write_text("fixture\n")
        self.validate()
        (directory / "references/steps.md").write_text("[asset]: <../assets/item (one).txt>\n\nUse [asset].\n")
        self.validate()

    def test_references_cannot_escape_the_portable_bundle(self):
        (self.skills / "outside.md").write_text("Outside the skill.\n")
        directory = write_skill(self.skills, body="Read [outside](../outside.md).\n")
        self.validate(False)
        (directory / "escape.md").symlink_to(self.skills / "outside.md")
        write_skill(self.skills, body="Read [outside](escape.md).\n")
        self.validate(False)
        write_skill(self.skills, body="Read [absolute](/tmp/missing.md).\n")
        self.validate(False)
        write_skill(self.skills, body="Read [absolute](file:///tmp/missing.md).\n")
        self.validate(False)

    def test_code_examples_and_external_urls_are_not_local_dependencies(self):
        write_skill(self.skills, body=(
            'See [upstream](https://example.invalid/no-network "A title").\n'
            "Use `[example](missing-inline.md)` as sample syntax.\n"
            "```markdown\n[example](missing-fenced.md)\n```\n"
            "~~~\n[example](missing-tilde.md)\n~~~\n"
            "<!-- [example](missing-comment.md) -->\n"
        ))
        self.validate()
        write_skill(self.skills, body="![required asset](missing.png)\n")
        self.validate(False)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "checkout"
        shutil.copytree(REPO, self.repo, symlinks=True, ignore=shutil.ignore_patterns(".git", "backups", "__pycache__"))
        self.environment = dict(os.environ, SKILL_TEST_ROOT=str(self.root))
        self.env_file = self.root / "env.sh"
        self.clients = [self.root / "clients" / name / "skills" for name in ["claude", "codex", "agents", "opencode"]]
        with (self.repo / "lib/targets.sh").open("a") as stream:
            stream.write('''
skill_targets() {
  printf '%s\\n' "$SKILL_TEST_ROOT/clients/claude/skills" "$SKILL_TEST_ROOT/clients/codex/skills" "$SKILL_TEST_ROOT/clients/agents/skills" "$SKILL_TEST_ROOT/clients/opencode/skills"
}
skill_target_label() { basename "$(dirname "$1")"; }
instruction_targets() {
  printf '%s\\n' "$SKILL_TEST_ROOT/clients/claude/CLAUDE.md" "$SKILL_TEST_ROOT/clients/codex/AGENTS.md" "$SKILL_TEST_ROOT/clients/opencode/AGENTS.md"
}
''')
        with (self.repo / "lib/env.sh").open("a") as stream:
            stream.write('''
agentdots_env_file() { printf '%s/env.sh\\n' "$SKILL_TEST_ROOT"; }
''')

    def command(self, script, success=True):
        result = subprocess.run(["bash", str(self.repo / script)], env=self.environment, capture_output=True, text=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def assert_installed(self, name="git-conventions"):
        for client in self.clients:
            link = client / name
            self.assertTrue(link.is_symlink(), str(link))
            self.assertEqual(link.readlink(), self.repo / "skills" / name)

    def test_installation_repeated_sync_and_doctor(self):
        self.command("sync.sh")
        self.assert_installed()
        before = [(client / "git-conventions").lstat().st_ino for client in self.clients]
        environment = self.env_file.read_bytes()
        self.command("sync.sh")
        self.assert_installed()
        self.assertEqual(before, [(client / "git-conventions").lstat().st_ino for client in self.clients])
        self.assertEqual(environment, self.env_file.read_bytes())
        self.command("doctor.sh")

    def test_collision_in_later_client_does_not_mutate_any_target_or_environment(self):
        write_skill(self.repo / "skills")
        foreign = write_skill(self.root / "foreign")
        self.clients[1].mkdir(parents=True)
        collision = self.clients[1] / "demo"
        collision.symlink_to(foreign, target_is_directory=True)
        self.env_file.write_text('export APP_DOTS_DIR="/fixture/appdots"\n')
        before = self.env_file.read_bytes()
        self.command("sync.sh", False)
        self.assertEqual(collision.readlink(), foreign)
        self.assertFalse(self.clients[0].exists())
        self.assertFalse((self.repo / "backups").exists())
        self.assertEqual(before, self.env_file.read_bytes())

    def test_dangling_foreign_and_escaping_links_are_protected(self):
        self.clients[0].mkdir(parents=True)
        link = self.clients[0] / "git-conventions"
        for dest in [self.root / "missing", self.repo / ".." / "outside"]:
            with self.subTest(destination=dest):
                link.symlink_to(dest, target_is_directory=True)
                self.command("sync.sh", False)
                self.assertEqual(link.readlink(), dest)
                link.unlink()

    def test_owned_wrong_links_are_repaired_and_foreign_neighbors_preserved(self):
        self.clients[0].mkdir(parents=True)
        (self.clients[0] / "git-conventions").symlink_to(self.repo / "README.md")
        self.clients[1].mkdir(parents=True)
        (self.clients[1] / "git-conventions").symlink_to(os.path.relpath(self.repo / "skills/git-conventions", self.clients[1]), target_is_directory=True)
        outside = self.root / "foreign"
        outside.mkdir()
        neighbor = self.clients[0] / "native-skill"
        neighbor.symlink_to(outside, target_is_directory=True)
        self.command("sync.sh")
        self.assert_installed()
        self.assertEqual(neighbor.readlink(), outside)
        self.command("doctor.sh")

    def test_rename_incomplete_definition_and_deliberate_retirement(self):
        self.command("sync.sh")
        old = self.repo / "skills/git-conventions"
        renamed = self.repo / "skills/git-style"
        old.rename(renamed)
        definition = renamed / "SKILL.md"
        definition.write_text(definition.read_text().replace("name: git-conventions", "name: git-style", 1))
        self.command("doctor.sh", False)
        self.command("sync.sh")
        self.assert_installed("git-style")
        for client in self.clients:
            self.assertFalse((client / "git-conventions").is_symlink())
        definition.unlink()
        self.command("sync.sh", False)
        self.command("doctor.sh", False)
        self.assert_installed("git-style")
        retired = self.repo / "retired"
        retired.mkdir()
        renamed.rename(retired / "git-style")
        self.command("sync.sh")
        self.command("doctor.sh")
        for client in self.clients:
            self.assertFalse((client / "git-style").is_symlink())

    def test_misplaced_owned_links_are_drift_even_when_their_sources_exist(self):
        self.command("sync.sh")
        extra = self.clients[0] / "old-name"
        extra.symlink_to(self.repo / "skills/git-conventions", target_is_directory=True)
        self.command("doctor.sh", False)
        self.command("sync.sh")
        self.assertFalse(extra.is_symlink())
        self.assert_installed()
        self.command("doctor.sh")

    def test_real_conflicts_have_recoverable_backups(self):
        for index, client in enumerate(self.clients):
            directory = client / "git-conventions"
            directory.mkdir(parents=True)
            (directory / "custom.txt").write_text(f"original-{index}\n")
        instruction = self.clients[0].parent / "CLAUDE.md"
        instruction.write_text("Original global instructions.\n")
        self.command("sync.sh")
        self.assert_installed()
        for index, name in enumerate(["claude", "codex", "agents", "opencode"]):
            matches = list((self.repo / "backups").glob(f"*/{name}/git-conventions/custom.txt"))
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0].read_text(), f"original-{index}\n")
        matches = list((self.repo / "backups").glob("*/instructions/claude-CLAUDE.md"))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].read_text(), "Original global instructions.\n")

    def test_relocation_uses_persisted_ownership_and_updates_it_last(self):
        self.command("sync.sh")
        old = self.repo
        self.repo = self.root / "moved-checkout"
        old.rename(self.repo)
        faulty_parent = self.root / "global-failure"
        faulty_parent.write_text("Not a directory.\n")
        with (self.repo / "lib/targets.sh").open("a") as stream:
            stream.write('''
instruction_targets() {
  printf '%s\\n' "$SKILL_TEST_ROOT/clients/claude/CLAUDE.md" "$SKILL_TEST_ROOT/clients/codex/AGENTS.md" "$SKILL_TEST_ROOT/clients/opencode/AGENTS.md" "$SKILL_TEST_ROOT/global-failure/AGENTS.md"
}
''')
        before = self.env_file.read_bytes()
        self.command("sync.sh", False)
        self.assertEqual(before, self.env_file.read_bytes())
        self.assert_installed()
        faulty_parent.unlink()
        self.command("sync.sh")
        self.assert_installed()
        self.command("doctor.sh")
        self.assertIn(f'export AGENT_DOTS_DIR="{self.repo}"', self.env_file.read_text())

    def test_bad_metadata_and_missing_global_policy_fail_before_backups_or_links(self):
        for failure in ["metadata", "global"]:
            with self.subTest(failure=failure):
                if failure == "metadata":
                    invalid = write_skill(self.repo / "skills", name="unfinished", header="name: unfinished")
                else:
                    shutil.rmtree(invalid)
                    (self.repo / "instructions/global.md").unlink()
                self.command("sync.sh", False)
                self.assertFalse((self.root / "clients").exists())
                self.assertFalse((self.repo / "backups").exists())
                self.assertFalse(self.env_file.exists())


if __name__ == "__main__":
    unittest.main()
