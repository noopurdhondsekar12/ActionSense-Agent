import streamlit as st
import json
from action_sense import action_sense

st.title("ActionSense Agent Demo")

st.markdown("Enter the input JSON for the ActionSense agent below:")

default_input = {
    "user_id": "abc123",
    "summary": "User is asking if the pitch deck is finalized.",
    "type": "follow-up",
    "task_context": "project-checkin",
    "platform": "whatsapp",
    "timestamp": "2025-08-05T13:05:00Z"
}

input_text = st.text_area("Input JSON", value=json.dumps(default_input, indent=2), height=200)

if st.button("Generate Action"):
    try:
        input_json = json.loads(input_text)
        result = action_sense(input_json)
        st.subheader("Generated Output")
        st.json(result)

        st.subheader("Message Preview")
        platform = input_json.get("platform", "").lower()
        message = result.get("generated_text", "")
        if platform == "whatsapp":
            st.markdown(f"**WhatsApp:** {message} ")
        elif platform == "instagram":
            st.markdown(f"**Instagram:** {message} #action")
        elif platform == "email":
            st.markdown(f"**Email:** {message}")
        else:
            st.markdown(f"**Default:** {message}")

    except Exception as e:
        st.error(f"Invalid JSON input or processing error: {e}")
