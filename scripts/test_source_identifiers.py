"""Reject original organization identifiers in *tracked current-tree* source and docs.

This does NOT cleanse Git history, forks, cached PR refs or previously published
artifacts. Those require a separate source provenance and history review.
"""
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {
    ".rb", ".py", ".sh", ".ts", ".tsx", ".js", ".mjs", ".json",
    ".yml", ".yaml", ".css", ".md", ".txt", ".xml", ".html", ".toml",
}
# Keep the detector operational without embedding the prohibited brand as
# one contiguous identifier in the public repository's active source.
SOURCE_SPECIFIC_NAME = re.compile("raka" + "min", re.IGNORECASE)


def tracked_source_identifiers():
    process = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT, capture_output=True, check=True,
    )
    findings = []
    for raw in process.stdout.split(b"\0"):
        if not raw:
            continue
        relative = raw.decode("utf-8", errors="replace")
        path = ROOT / relative
        if not path.is_file() or path.suffix not in TEXT_EXTENSIONS:
            continue
        if SOURCE_SPECIFIC_NAME.search(relative):
            findings.append(relative)
            continue
        try:
            body = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if SOURCE_SPECIFIC_NAME.search(body):
            findings.append(relative)
    return sorted(findings)


class PublicationSourceTests(unittest.TestCase):
    # TEST-GATE-06: scan ALL tracked text, including policy scripts and docs.
    def test_TEST_GATE_06_current_repository_excludes_prohibited_names(self):
        self.assertEqual(
            [], tracked_source_identifiers(),
            "Prohibited organization name remains in current-tree file(s)"
        )


if __name__ == "__main__":
    unittest.main()
