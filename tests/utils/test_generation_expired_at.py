from datetime import datetime, timedelta, timezone

import pytest

from app.adapters.db.utils.expire import (
    calculate_expires_at_by_severity,
    get_ttl_days_by_severity,
)
from app.settings import config

LOW = config.mongo.expire_at_ttl_days_low
MEDIUM = config.mongo.expire_at_ttl_days_medium
CRITICAL = config.mongo.expire_at_ttl_days_critical


class TestTTL:
    @pytest.mark.parametrize(
        "severity",
        ["jjjj", None],
    )
    def test_get_ttl_days_is_LOW_incorrect_data(self, severity):
        """Если не int, то LOW"""
        result = get_ttl_days_by_severity(severity)
        assert result == LOW

    @pytest.mark.parametrize(
        "severity",
        [8, "8", 9, 10, 100000],
    )
    def test_get_ttl_days_is_CRITICAL(self, severity):
        """Если >= 8, то CRITICAL"""
        result1 = get_ttl_days_by_severity(severity)
        assert result1 == CRITICAL

    @pytest.mark.parametrize(
        "severity",
        [5, 6, 7],
    )
    def test_get_ttl_days_is_MEDIUM(self, severity):
        """Если from 5 to 7, то MEDIUM"""
        result1 = get_ttl_days_by_severity(severity)
        assert result1 == MEDIUM

    @pytest.mark.parametrize(
        "severity",
        [1, 2, 3, 4, "2"],
    )
    def test_get_ttl_days_is_LOW(self, severity):
        """Если from 1 to 4, то MEDIUM"""
        result1 = get_ttl_days_by_severity(severity)
        assert result1 == LOW


class TestExpiredAt:
    @pytest.mark.parametrize(
        "severity",
        ["jjjj", None],
    )
    def test_calculate_severity_is_LOW_incorrect_data(self, severity):
        """Если None или не int, то LOW"""
        data = {
            "severity": severity,
            "type": "test",
        }
        result = calculate_expires_at_by_severity(data.get("severity"))
        to_be = datetime.now(timezone.utc) + timedelta(days=LOW)

        assert result.strftime("%Y-%m-%d %H:%M:%S") == to_be.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    @pytest.mark.parametrize(
        "severity",
        [8, "8", 9, 10, 100000],
    )
    def test_calculate_severity_is_CRITICAL(self, severity):
        """Если severity >= 8, то CRITICAL"""
        data = {
            "severity": severity,
            "type": "test",
        }
        result = calculate_expires_at_by_severity(data.get("severity"))
        to_be = datetime.now(timezone.utc) + timedelta(days=CRITICAL)

        assert result.strftime("%Y-%m-%d %H:%M:%S") == to_be.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    @pytest.mark.parametrize(
        "severity",
        [5, "5", 6, 7],
    )
    def test_calculate_severity_is_MEDIUM(self, severity):
        """Если severity = 5-7, то MEDIUM"""
        data = {
            "severity": severity,
            "type": "test",
        }
        result = calculate_expires_at_by_severity(data.get("severity"))
        to_be = datetime.now(timezone.utc) + timedelta(days=MEDIUM)

        assert result.strftime("%Y-%m-%d %H:%M:%S") == to_be.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    @pytest.mark.parametrize(
        "severity",
        [1, 2, 3, 4, "2"],
    )
    def test_calculate_severity_is_LOW(self, severity):
        """Если severity = 1-4, то LOW"""
        data = {
            "severity": severity,
            "type": "test",
        }
        result = calculate_expires_at_by_severity(data.get("severity"))
        to_be = datetime.now(timezone.utc) + timedelta(days=LOW)

        assert result.strftime("%Y-%m-%d %H:%M:%S") == to_be.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
