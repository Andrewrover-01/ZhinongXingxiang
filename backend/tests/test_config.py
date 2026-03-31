"""
tests/test_config.py
Settings 配置验证测试。

覆盖:
  LOW-003 — 生产环境默认使用 SQLite 应被拒绝
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings


class TestProductionDatabaseValidation:
    """LOW-003 — SQLite must be rejected when APP_ENV=production."""

    def test_sqlite_in_production_raises(self):
        with pytest.raises(ValidationError, match="SQLite"):
            Settings(
                APP_ENV="production",
                DATABASE_URL="sqlite:///./zhinong.db",
                SECRET_KEY="a-very-strong-random-secret-key-32chars!!",
            )

    def test_sqlite_in_development_allowed(self):
        # SQLite is acceptable outside production
        s = Settings(
            APP_ENV="development",
            DATABASE_URL="sqlite:///./zhinong.db",
            SECRET_KEY="any-key-is-fine-in-dev",
        )
        assert s.DATABASE_URL.startswith("sqlite")

    def test_postgres_in_production_allowed(self):
        s = Settings(
            APP_ENV="production",
            DATABASE_URL="postgresql://user:pass@localhost/db",
            SECRET_KEY="a-very-strong-random-secret-key-32chars!!",
        )
        assert s.DATABASE_URL.startswith("postgresql")

    def test_weak_secret_in_production_still_raises(self):
        """Existing MED-001 check: weak SECRET_KEY in production must still fail."""
        with pytest.raises(ValidationError, match="SECRET_KEY"):
            Settings(
                APP_ENV="production",
                DATABASE_URL="postgresql://user:pass@localhost/db",
                SECRET_KEY="dev-secret-key-change-in-production",
            )
