from datetime import datetime, timedelta

# Response templates stored as a dictionary
response_templates = {
    "follow-up": "We're on it and will update you shortly.",
    "meeting": "Confirming the call at {time}.",
    "request": "Yes, here’s the file you asked for.",
    "default": "Thanks for reaching out! We will get back to you soon."
}

def detect_urgency(summary):
    urgency_keywords = ["asap", "urgent", "waiting", "immediately", "important"]
    summary_lower = summary.lower()
    return any(word in summary_lower for word in urgency_keywords)

def decide_action(summary, task_type, task_context):
    if detect_urgency(summary):
        # Prioritize urgent messages
        if task_type == "schedule":
            return "schedule"
        else:
            return "respond"

    summary_lower = summary.lower()
    # Simple spam/ignore detection
    if any(word in summary_lower for word in ["spam", "ignore", "unsubscribe"]):
        return "ignore"

    # Normal action routing
    if task_type == "follow-up":
        return "respond"
    if task_type == "meeting":
        return "respond"
    if task_type == "request":
        return "respond"
    if task_type in ["reminder", "schedule"]:
        return "schedule"
    return "respond"  # default fallback

def generate_message(task_type, context_info=None):
    template = response_templates.get(task_type, response_templates["default"])
    if "{time}" in template and context_info and "time" in context_info:
        return template.format(time=context_info["time"])
    return template

def format_for_platform(platform, text):
    platform = platform.lower()
    if platform == "whatsapp":
        return text + " 😊"
    elif platform == "instagram":
        return text + " #action"
    elif platform == "email":
        return text
    else:
        return text

def get_scheduled_time(timestamp_str, delay_minutes=60):
    dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    scheduled_dt = dt + timedelta(minutes=delay_minutes)
    return scheduled_dt.isoformat()

def action_sense(input_json):
    user_id = input_json.get("user_id")
    summary = input_json.get("summary", "")
    task_type = input_json.get("type", "")
    task_context = input_json.get("task_context", "")
    platform = input_json.get("platform", "")
    timestamp = input_json.get("timestamp", "")

    action_type = decide_action(summary, task_type, task_context)

    if action_type == "ignore":
        return {
            "action_type": "ignore",
            "generated_text": "",
            "platform_ready": False,
            "response_format": {}
        }

    context_info = {}
    # Add dummy time info if meeting
    if task_type == "meeting":
        context_info["time"] = "3 PM"

    generated_text = generate_message(task_type, context_info)
    platform_text = format_for_platform(platform, generated_text)

    response = {
        "action_type": action_type,
        "generated_text": platform_text,
        "platform_ready": True,
        "response_format": {
            "platform": platform,
            "text": platform_text,
            "delay": "0"
        }
    }

    if action_type == "schedule":
        scheduled_time = get_scheduled_time(timestamp)
        response["response_format"]["delay"] = "60"  # delay in minutes
        response["response_format"]["scheduled_time"] = scheduled_time

    return response


# Example standalone test
if __name__ == "__main__":
    sample_input = {
        "user_id": "abc123",
        "summary": "This is urgent! Please send the file ASAP.",
        "type": "request",
        "task_context": "document",
        "platform": "whatsapp",
        "timestamp": "2025-08-05T13:05:00Z"
    }
    output = action_sense(sample_input)
    print("Output:\n", output)
