"""Isolate V5 receipts while reusing the proven native validation harnesses."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Docs/WorldExpansion/V5'
LEGACY = ROOT / 'Scripts/WorldExpansion'


def assert_baseline_copy():
    original = ROOT / 'Docs/WorldExpansion/original-baseline.json'
    copy = OUT / 'original-baseline.json'
    assert copy.exists(), 'Run validation_v5/prepare.py before editor validation'
    assert hashlib.sha256(copy.read_bytes()).digest() == hashlib.sha256(original.read_bytes()).digest(), 'Original baseline copy differs'


def legacy_source(name):
    source = (LEGACY / name).read_text(encoding='utf-8-sig')
    marker = "OUT = ROOT / 'Docs/WorldExpansion'"
    assert source.count(marker) == 1, 'Legacy output contract changed; review wrapper before executing'
    return source.replace(marker, "OUT = ROOT / 'Docs/WorldExpansion/V5'")


def execute_source(source, name):
    exec(compile(source, str(LEGACY / name), 'exec'), {'__name__': '__main__', '__file__': str(LEGACY / name)})
