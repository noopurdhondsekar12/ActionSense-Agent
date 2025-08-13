# unit_tests_action_sense.py
import json
import importlib
import types
import pathlib

import pytest

# Import the module under test
action_sense = importlib.import_module("action_sense")

# ---- Helpers ----
def _base_input(**overrides):
    base = {
        "user_id": "abc123",
        "summary": "User is asking if the pitch deck is finalized.",
        "type": "follow-up",
        "task_context": "project-checkin",
        "platform": "whatsapp",
        "timestamp": "2025-08-05T13:05:00Z"
    }
    base.update(overrides)
    return base

# ---------------------------
# Urgency Detection
# ---------------------------
@pytest.mark.parametrize("text", [
    "This is URGENT – please check now",
    "Can you send it ASAP?",
    "Need it immediately",
    "High PRIORITY item",
    "We are waiting for your response"
])
def test_detect_urgency_true(text):
    assert action_sense.detect_urgency(text) is True

@pytest.mark.parametrize("text", [
    "No rush, take your time.",
    "Just following up.",
    "Please confirm whenever convenient."
])
def test_detect_urgency_false(text):
    assert action_sense.detect_urgency(text) is False

# ---------------------------
# Scheduler / Delay
# ---------------------------
def test_compute_delay_urgent_zero():
    assert action_sense.compute_delay("follow-up", "ASAP please") == 0

def test_compute_delay_followup_60():
    assert action_sense.compute_delay("follow-up", "normal follow up") == 60

def test_compute_delay_meeting_30():
    assert action_sense.compute_delay("meeting", "confirm meeting time") == 30

def test_compute_delay_other_default_zero():
    assert action_sense.compute_delay("request", "send file later") == 0

# ---------------------------
# Platform Formatting
# ---------------------------
def test_format_for_platform_whatsapp_shortens_and_adds_emoji():
    long_text = "x" * 120  # force truncation
    out = action_sense.format_for_platform(long_text, "whatsapp")
    # should end with emoji and contain ellipsis due to truncation
    assert out.endswith(" 😊")
    assert "..." in out

def test_format_for_platform_email_formal():
    txt = "Hello team, confirming the meeting."
    out = action_sense.format_for_platform(txt, "email")
    assert txt in out
    assert out.endswith("\n\nRegards,\nActionSense")

def test_format_for_platform_slack_mentions():
    txt = "User please check the update"
    out = action_sense.format_for_platform(txt, "slack")
    assert "<@user>" in out

def test_format_for_platform_default_passthrough():
    txt = "Plain text"
    out = action_sense.format_for_platform(txt, "telegram")
    assert out == txt

# ---------------------------
# End-to-end decide_action
# ---------------------------
def test_decide_action_ignore_path():
    data = _base_input(summary="Thanks, done. You can ignore now.", type="follow-up")
    out = action_sense.decide_action(data)
    assert out["action_type"] == "ignore"
    assert out["generated_text"] == ""
    assert out["platform_ready"] is True
    assert out["response_format"]["delay"] == "0"

def test_decide_action_followup_whatsapp_with_delay():
    data = _base_input(summary="Please send the draft when ready.", type="follow-up", platform="whatsapp")
    out = action_sense.decide_action(data)
    assert out["action_type"] == "respond"
    assert isinstance(out["generated_text"], str) and out["generated_text"]
    assert out["response_format"]["platform"] == "whatsapp"
    assert out["response_format"]["delay"] == "60"  # follow-up default
    assert out["platform_ready"] is True

def test_decide_action_followup_urgent_overrides_delay():
    data = _base_input(summary="Please send the draft ASAP!", type="follow-up", platform="whatsapp")
    out = action_sense.decide_action(data)
    assert out["response_format"]["delay"] == "0"

def test_decide_action_meeting_email():
    data = _base_input(
        summary="Confirm the meeting for tomorrow.",
        type="meeting",
        platform="email"
    )
    out = action_sense.decide_action(data)
    assert out["action_type"] == "respond"
    assert out["response_format"]["platform"] == "email"
    # meeting default delay
    assert out["response_format"]["delay"] == "30"
    # email footer should be appended
    assert out["response_format"]["text"].endswith("\n\nRegards,\nActionSense")

def test_decide_action_request_slack():
    data = _base_input(
        summary="Can you send the file?",
        type="request",
        platform="slack"
    )
    out = action_sense.decide_action(data)
    assert out["action_type"] == "respond"
    assert out["response_format"]["platform"] == "slack"
    assert out["response_format"]["delay"] == "0"  # default for request
    assert "<@user>" in out["response_format"]["text"]

# ---------------------------
# Sample file smoke test
# ---------------------------
def test_test_data_json_smoke(tmp_path, monkeypatch):
    """
    Optional smoke test: ensures the pipeline can handle a list of inputs from test_data.json.
    """
    # Locate repo root (this file's parent)
    repo_root = pathlib.Path(__file__).resolve().parent
    test_data_path = repo_root / "test_data.json"
    assert test_data_path.exists(), "test_data.json not found. Please add it to the repo."

    with open(test_data_path, "r") as f:
        payload = json.load(f)

    # Allow either a dict or a list of dicts
    if isinstance(payload, dict):
        payload = [payload]

    for item in payload:
        out = action_sense.decide_action(item)
        assert "action_type" in out
        assert "generated_text" in out
        assert "platform_ready" in out
        assert "response_format" in out
        assert "platform" in out["response_format"]
        assert "text" in out["response_format"]
        assert "delay" in out["response_format"]
