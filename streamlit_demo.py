import streamlit as st
import json
from action_sense import decide_action

st.title("ActionSense: Context-Aware Response Generator")

# Input form
with st.form("input_form"):
    user_id = st.text_input("User ID", "abc123")
    summary = st.text_area("Summary", "User is asking if the pitch deck is finalized.")
    task_type = st.text_input("Task Type", "follow-up")
    task_context = st.text_input("Task Context", "follow-up")
    platform = st.selectbox("Platform", ["whatsapp", "instagram", "email"])
    timestamp = st.text_input("Timestamp (ISO)", "2025-08-05T13:05:00Z")
    submit = st.form_submit_button("Generate Action")

if submit:
    input_data = {
        "user_id": user_id,
        "summary": summary,
        "type": task_type,
        "task_context": task_context,
        "platform": platform,
        "timestamp": timestamp
    }

    output = decide_action(
        summary=input_data["summary"],
        task_type=input_data["type"],
        task_context=input_data["task_context"],
        platform=input_data["platform"]
    )

    st.subheader("Generated Action")
    st.json(output)
