# action_pipeline.py
from action_sense import decide_action
import json

def action_pipeline(input_data: dict) -> dict:
    """
    Full pipeline: take input JSON, decide action, return structured output.
    """
    output = decide_action(input_data)
    return output

# ---------- TEST PIPELINE ----------
if __name__ == "__main__":
    # Load sample input from test_data.json
    with open("test_data.json", "r") as f:
        inputs = json.load(f)

    for input_item in inputs:
        result = action_pipeline(input_item)
        print(json.dumps(result, indent=2))
