from app.providers.triage.rules import RuleBasedTriage
from app.providers.triage.base import Category, Priority


def test_water_keyword_detected():
    provider = RuleBasedTriage()
    result = provider.triage("There is a water leak on the street", "Test")
    assert result.category == Category.water


def test_electricity_keyword_detected():
    provider = RuleBasedTriage()
    result = provider.triage("Power outage in our area", "Test")
    assert result.category == Category.electricity


def test_urgent_keyword_sets_high_priority():
    provider = RuleBasedTriage()
    result = provider.triage("Emergency flooding happening now", "Test")
    assert result.priority == Priority.high


def test_no_keyword_defaults_to_other():
    provider = RuleBasedTriage()
    result = provider.triage("Something unusual happened today", "Test")
    assert result.category == Category.other


def test_summary_is_truncated_when_too_long():
    provider = RuleBasedTriage()
    long_text = "word " * 100
    result = provider.triage(long_text, "Test")
    assert len(result.summary) <= 140
