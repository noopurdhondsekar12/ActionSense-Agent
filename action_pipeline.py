from datetime import datetime, timezone
from action_sense import action_sense  # Make sure action_sense.py is in the same folder

# --- Simulated Seeya Module ---
def seeya_process(raw_message):
    # For demo: return a simple summary (could be an NLP summary)
    summary = f"User said: {raw_message[:50]}"  # truncate for example
    return {"summary": summary}

# --- Simulated Sankalp Module ---
def sankalp_process(raw_message):
    # For demo: classify task type by keywords
    msg_lower = raw_message.lower()
    if "meeting" in msg_lower or "call" in msg_lower:
        return {"type": "meeting", "task_context": "calendar"}
    elif "please send" in msg_lower or "file" in msg_lower:
        return {"type": "request", "task_context": "document"}
    elif "remind" in msg_lower or "schedule" in msg_lower:
        return {"type": "schedule", "task_context": "reminder"}
    else:
        return {"type": "follow-up", "task_context": "general"}

# --- Merge Inputs Function ---
def merge_inputs(seeya_output, sankalp_output, user_id, platform):
    return {
        "user_id": user_id,
        "summary": seeya_output.get("summary", ""),
        "type": sankalp_output.get("type", ""),
        "task_context": sankalp_output.get("task_context", ""),
        "platform": platform,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# --- Main Pipeline Function ---
def run_pipeline(raw_message, user_id="user123", platform="whatsapp"):
    seeya_out = seeya_process(raw_message)
    sankalp_out = sankalp_process(raw_message)
    combined_input = merge_inputs(seeya_out, sankalp_out, user_id, platform)
    action_output = action_sense(combined_input)
    return action_output

# --- Example Run ---
if __name__ == "__main__":
    test_message = "Hi, please send me the latest project report."
    output = run_pipeline(test_message)
    print("Input message:", test_message)
    print("ActionSense output:", output)
