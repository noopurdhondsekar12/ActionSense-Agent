# app.py
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

import streamlit as st

# Your core logic
from action_sense import decide_action, detect_urgency

st.set_page_config(
    page_title="ActionSense – Simulator",
    page_icon="⚡",
    layout="wide",
)

# ------------- Helpers -------------
SAMPLE_INPUT: Dict[str, Any] = {
    "user_id": "abc123",
    "summary": "User is asking if the pitch deck is finalized.",
    "type": "follow-up",
    "task_context": "project-checkin",
    "platform": "whatsapp",
    "timestamp": "2025-08-05T13:05:00Z"
}

SAMPLE_LIST: List[Dict[str, Any]] = [
    {
        "user_id": "u1",
        "summary": "Please send the report ASAP.",
        "type": "follow-up",
        "task_context": "project-checkin",
        "platform": "whatsapp",
        "timestamp": "2025-08-05T13:05:00Z"
    },
    {
        "user_id": "u2",
        "summary": "Confirm the meeting time for tomorrow.",
        "type": "meeting",
        "task_context": "client-call",
        "platform": "email",
        "timestamp": "2025-08-06T09:00:00Z"
    }
]

def parse_json_input(raw: str):
    """
    Accepts a JSON object or a JSON array string and returns a list of dicts.
    """
    payload = json.loads(raw)
    if isinstance(payload, dict):
        return [payload]
    elif isinstance(payload, list):
        # Ensure all items are dicts
        return [p for p in payload if isinstance(p, dict)]
    else:
        raise ValueError("JSON must be an object or an array of objects.")

def schedule_time_from_delay(delay_minutes: int) -> str:
    """
    Returns an ISO8601 string of now + delay_minutes (UTC).
    """
    now = datetime.now(timezone.utc)
    scheduled = now + timedelta(minutes=delay_minutes)
    return scheduled.isoformat(timespec="seconds")

def pretty_platform_chip(p: str):
    chips = {
        "whatsapp": "🟢 WhatsApp",
        "email": "✉️ Email",
        "slack": "💬 Slack",
        "instagram": "📸 Instagram",
        "telegram": "📨 Telegram"
    }
    return chips.get(p.lower(), f"🔧 {p}")

def run_pipeline(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    outputs = []
    for item in items:
        out = decide_action(item)
        # Enrich with computed scheduled time for convenience (not altering your core output)
        try:
            delay = int(out.get("response_format", {}).get("delay", "0"))
        except Exception:
            delay = 0
        out["_meta"] = {
            "scheduled_at_utc": schedule_time_from_delay(delay)
        }
        outputs.append(out)
    return outputs

# ------------- UI -------------
st.title("⚡ ActionSense – Context-Aware Response Generator & Scheduler")
st.caption("Simulate inputs, see decisions, and preview platform-ready messages.")

with st.sidebar:
    st.header("Quick Builder")
    summary = st.text_area(
        "Summary",
        value=SAMPLE_INPUT["summary"],
        height=120,
        placeholder="e.g., Please share the latest deck ASAP."
    )
    colA, colB = st.columns(2)
    with colA:
        task_type = st.selectbox(
            "Type",
            options=["follow-up", "meeting", "request", "other"],
            index=0
        )
    with colB:
        platform = st.selectbox(
            "Platform",
            options=["whatsapp", "email", "slack", "telegram"],
            index=0
        )
    task_context = st.text_input("Task Context", value=SAMPLE_INPUT["task_context"])
    user_id = st.text_input("User ID", value=SAMPLE_INPUT["user_id"])
    timestamp = st.text_input("Timestamp (ISO8601, UTC)", value=SAMPLE_INPUT["timestamp"])

    urgent = detect_urgency(summary)
    st.markdown("---")
    st.subheader("Urgency")
    if urgent:
        st.success("Detected: **URGENT** (delay will be 0)")
    else:
        st.info("No urgency detected")

    build_btn = st.button("Generate for this Input", use_container_width=True)

st.markdown("### Single Input")
st.write("Build a single input from the sidebar, or paste JSON below.")

# Single input card
single_input = {
    "user_id": user_id.strip() or "abc123",
    "summary": summary.strip(),
    "type": task_type,
    "task_context": task_context.strip() or "general",
    "platform": platform,
    "timestamp": timestamp.strip() or datetime.now(timezone.utc).isoformat(timespec="seconds")
}

col1, col2 = st.columns([1, 1])
with col1:
    st.code(json.dumps(single_input, indent=2), language="json")

if build_btn:
    result = run_pipeline([single_input])[0]
else:
    # auto-run once on load
    result = run_pipeline([single_input])[0]

with col2:
    st.subheader("Decision & Preview")
    # Badges
    platform_chip = pretty_platform_chip(result["response_format"]["platform"])
    action_type = result["action_type"]
    delay = result["response_format"]["delay"]
    scheduled_at = result.get("_meta", {}).get("scheduled_at_utc", "N/A")

    st.markdown(
        f"""
        **Action:** `{action_type}`  
        **Platform:** {platform_chip}  
        **Delay (min):** `{delay}`  
        **Scheduled @ (UTC):** `{scheduled_at}`
        """
    )

    # Preview Card
    st.markdown("**Platform Preview**")
    st.container(border=True)
    st.write(result["response_format"]["text"])

    st.markdown("**Raw Output**")
    st.code(json.dumps(result, indent=2), language="json")

st.markdown("---")

# ------------------- Batch Mode -------------------
st.markdown("### Batch: Upload or Paste JSON")
left, right = st.columns([1, 1])

with left:
    uploaded = st.file_uploader("Upload JSON file (object or array)", type=["json"])
    raw_text = st.text_area(
        "…or paste JSON here",
        height=200,
        placeholder="Paste a JSON object or array of objects matching your schema…"
    )
    sample_cols = st.columns(2)
    with sample_cols[0]:
        if st.button("Load Sample Object", type="secondary", use_container_width=True):
            st.session_state["raw_text"] = json.dumps(SAMPLE_INPUT, indent=2)
    with sample_cols[1]:
        if st.button("Load Sample Array", type="secondary", use_container_width=True):
            st.session_state["raw_text"] = json.dumps(SAMPLE_LIST, indent=2)

    if "raw_text" in st.session_state and not raw_text:
        raw_text = st.session_state["raw_text"]

process_clicked = st.button("Process Batch", use_container_width=True)

batch_results = []
with right:
    if process_clicked:
        try:
            items: List[Dict[str, Any]] = []
            if uploaded is not None:
                items = json.load(uploaded)
                if isinstance(items, dict):
                    items = [items]
            elif raw_text.strip():
                items = parse_json_input(raw_text)
            else:
                st.warning("Please upload a file or paste JSON.")
            if items:
                batch_results = run_pipeline(items)
        except Exception as e:
            st.error(f"Failed to process input: {e}")

    if batch_results:
        st.success(f"Processed {len(batch_results)} item(s).")
        st.code(json.dumps(batch_results, indent=2), language="json")

        # Download button
        st.download_button(
            label="⬇️ Download Results (JSON)",
            data=json.dumps(batch_results, indent=2),
            file_name="action_sense_outputs.json",
            mime="application/json",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.caption("ActionSense – Context-Aware Response Generator & Scheduler • Streamlit UI")
