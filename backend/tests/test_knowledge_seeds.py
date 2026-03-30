"""Tests for backend/data/knowledge_seeds.py"""
import sys
import pathlib

# Ensure the backend package root is importable when run via pytest from /backend
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from data.knowledge_seeds import get_seeds  # noqa: E402


def test_get_seeds_default_count():
    seeds = get_seeds()
    assert len(seeds) >= 500


def test_get_seeds_custom_count():
    seeds = get_seeds(min_count=10)
    assert len(seeds) >= 10


def test_seed_schema():
    seeds = get_seeds(min_count=1)
    for seed in seeds[:20]:  # spot-check first 20
        assert isinstance(seed["id"], int)
        assert isinstance(seed["title"], str) and seed["title"]
        assert isinstance(seed["content"], str) and seed["content"]
        assert isinstance(seed["tags"], list) and len(seed["tags"]) >= 1


def test_seed_ids_are_sequential():
    seeds = get_seeds(min_count=50)
    ids = [s["id"] for s in seeds]
    assert ids == list(range(1, len(seeds) + 1))


def test_seed_categories_present():
    seeds = get_seeds()
    all_tags = {tag for s in seeds for tag in s["tags"]}
    for expected in ("病害", "虫害", "栽培技术", "农业政策", "气象灾害"):
        assert expected in all_tags, f"类别标签 '{expected}' 未出现在种子数据中"
