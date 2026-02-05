"""Local responses handler for Yuki bot."""
import json
import random
import os


def load_responses():
    """Load responses from JSON file."""
    responses_path = os.path.join(os.path.dirname(__file__), "..", "responses.json")
    with open(responses_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_local_reply(text: str):
    """Get a local reply from responses.json based on keywords."""
    text = text.lower()
    responses = load_responses()
    
    # Support both old and new format
    triggers = responses.get("triggers", [])
    if not triggers:
        # Old format compatibility
        triggers = responses.values()

    for trigger in triggers:
        keywords = trigger.get("keywords", [])
        for keyword in keywords:
            if keyword.lower() in text:
                return random.choice(trigger.get("replies", []))

    return None


