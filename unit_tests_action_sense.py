import unittest
from action_sense import action_sense

class TestActionSense(unittest.TestCase):

    def test_follow_up_respond(self):
        input_data = {
            "user_id": "user1",
            "summary": "Please update me on the report.",
            "type": "follow-up",
            "task_context": "project-checkin",
            "platform": "whatsapp",
            "timestamp": "2025-08-05T10:00:00Z"
        }
        result = action_sense(input_data)
        self.assertEqual(result["action_type"], "respond")
        self.assertIn("😊", result["generated_text"])

    def test_ignore_spam(self):
        input_data = {
            "user_id": "user2",
            "summary": "This is spam, ignore please.",
            "type": "follow-up",
            "task_context": "random",
            "platform": "email",
            "timestamp": "2025-08-05T10:00:00Z"
        }
        result = action_sense(input_data)
        self.assertEqual(result["action_type"], "ignore")
        self.assertFalse(result["platform_ready"])

    def test_schedule_reminder(self):
        input_data = {
            "user_id": "user3",
            "summary": "Remind me about the meeting.",
            "type": "schedule",
            "task_context": "calendar",
            "platform": "email",
            "timestamp": "2025-08-05T10:00:00Z"
        }
        result = action_sense(input_data)
        self.assertEqual(result["action_type"], "schedule")
        self.assertIn("scheduled_time", result["response_format"])
        self.assertEqual(result["response_format"]["delay"], "60")

    def test_meeting_response_with_time(self):
        input_data = {
            "user_id": "user4",
            "summary": "Confirm the meeting time.",
            "type": "meeting",
            "task_context": "project-checkin",
            "platform": "instagram",
            "timestamp": "2025-08-05T10:00:00Z"
        }
        result = action_sense(input_data)
        self.assertEqual(result["action_type"], "respond")
        self.assertIn("3 PM", result["generated_text"])
        self.assertIn("#action", result["generated_text"])

    def test_urgency_detection(self):
        input_data = {
            "user_id": "user5",
            "summary": "This is urgent! Please send the file ASAP.",
            "type": "request",
            "task_context": "document",
            "platform": "email",
            "timestamp": "2025-08-05T10:00:00Z"
        }
        result = action_sense(input_data)
        self.assertEqual(result["action_type"], "respond")
        self.assertIn("Yes, here’s the file", result["generated_text"])

if __name__ == "__main__":
    unittest.main()
