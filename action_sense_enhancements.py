# action_sense_enhancements.py
from datetime import datetime, timedelta

# ---------- URGENCY DETECTION ----------
def detect_urgency(summary: str) -> bool:
    """
    Detect if a message is urgent based on keywords.
    """
    keywords = ["urgent", "asap", "immediately", "priority", "waiting"]
    summary_lower = summary.lower()
    for word in keywords:
        if word in summary_lower:
            return True
    return False

# ---------- SCHEDULER / DELAY ----------
def compute_delay(task_type: str, summary: str) -> int:
    """
    Return delay in minutes based on task type and urgency.
    """
    if detect_urgency(summary):
        return 0  # send immediately
    elif task_type == "follow-up":
        return 60  # 1 hour
    elif task_type == "meeting":
        return 30  # 30 minutes
    else:
        return 0  # default: no delay

# ---------- PLATFORM FORMATTING ----------
def format_for_platform(text: str, platform: str) -> str:
    """
    Adjust message based on platform.
    """
    platform = platform.lower()
    if platform == "whatsapp":
        # Shorten text + emoji
        if len(text) > 80:
            text = text[:77] + "..."
        return text + " 😊"
    elif platform == "email":
        # Formal ending
        return text + "\n\nRegards,\nActionSense"
    elif platform == "slack":
        # Basic mention handling
        return text.replace("User", "<@user>")
    else:
        return text

# ---------- MAIN ENHANCED DECISION FUNCTION ----------
def enhanced_decide_action(input_data: dict) -> dict:
    """
    Input: JSON with summary, type, task_context, platform
    Output: structured action with delay and platform-ready text
    """
    # Example basic decision logic (replace with your real logic)
    task_type = input_data.get("type", "follow-up")
    summary = input_data.get("summary", "")
    platform = input_data.get("platform", "whatsapp")
    
    # Determine action_type (simplified, can extend)
    if "ignore" in summary.lower() or "done" in summary.lower():
        action_type = "ignore"
        generated_text = ""
    else:
        action_type = "respond"
        # Simple templated response
        if task_type == "follow-up":
            generated_text = "We’re on it and will update you soon."
        elif task_type == "meeting":
            generated_text = "Confirming the scheduled meeting. See you there!"
        elif task_type == "request":
            generated_text = "Yes, here’s the file you requested."
        else:
            generated_text = "Noted. We'll take action accordingly."

    # Compute delay based on urgency & type
    delay_minutes = compute_delay(task_type, summary)

    # Format message for platform
    platform_text = format_for_platform(generated_text, platform)

    # Construct output
    output = {
        "action_type": action_type,
        "generated_text": generated_text,
        "platform_ready": True,
        "response_format": {
            "platform": platform,
            "text": platform_text,
            "delay": str(delay_minutes)  # in minutes
        }
    }
    return output

# ---------- TEST EXAMPLE ----------
if __name__ == "__main__":
    sample_input = {
        "user_id": "abc123",
        "summary": "Please send the report ASAP.",
        "type": "follow-up",
        "task_context": "project-checkin",
        "platform": "whatsapp",
        "timestamp": "2025-08-05T13:05:00Z"
    }

    output = enhanced_decide_action(sample_input)
    print(output)
