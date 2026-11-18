"""Regression tests for the quality gate and the memory.

The gate is the only thing between the model's draft and the reader, so it is tested
against real editions: it must accept every edition published since it was introduced,
reject the three that were written before it, and catch each failure mode when it is
injected into an otherwise valid edition.
"""
import glob
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "check_edition.py"
EDITIONS = sorted(glob.glob(str(ROOT / "editions" / "2*.md")))
PRE_GATE = {"2026-09-13.md", "2026-09-14.md", "2026-09-15.md"}


def gate(path):
    return subprocess.run([sys.executable, str(GATE), str(path)],
                          cwd=ROOT, capture_output=True, text=True)


@pytest.mark.parametrize("edition", [e for e in EDITIONS if Path(e).name not in PRE_GATE],
                         ids=lambda e: Path(e).stem)
def test_published_editions_pass(edition):
    result = gate(edition)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize("name", sorted(PRE_GATE))
def test_pre_gate_editions_are_rejected(name):
    assert gate(ROOT / "editions" / name).returncode == 1


@pytest.fixture
def valid_edition():
    latest = [e for e in EDITIONS if Path(e).name not in PRE_GATE][-1]
    return Path(latest).read_text(encoding="utf-8")


def run_on(text, tmp_path):
    path = tmp_path / "edition.md"
    path.write_text(text, encoding="utf-8")
    return gate(path)


def test_duplicated_url_is_blocking(valid_edition, tmp_path):
    url = re.search(r"\]\((https?://[^)]+)\)", valid_edition).group(1)
    text = valid_edition + f"\n\n**Extra item.** Duplicate source. [Source]({url})\n"
    result = run_on(text, tmp_path)
    assert result.returncode == 1
    assert "deux fois" in result.stdout


def test_item_without_source_is_blocking(valid_edition, tmp_path):
    first_link = re.search(r"\[[^\]]+\]\(https?://[^)]+\)", valid_edition).group(0)
    text = valid_edition.replace(first_link, "", 1)
    assert run_on(text, tmp_path).returncode == 1


def test_missing_front_matter_is_blocking(valid_edition, tmp_path):
    text = re.sub(r"(?m)^accroche:.*\n", "", valid_edition, count=1)
    result = run_on(text, tmp_path)
    assert result.returncode == 1
    assert "accroche" in result.stdout


def test_memory_rebuilds_from_archive():
    result = subprocess.run([sys.executable, "scripts/registry.py"],
                            cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0
    assert f"{len(EDITIONS)} éditions" in result.stdout
