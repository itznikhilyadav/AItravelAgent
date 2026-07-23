from django.test import TestCase

from .views import get_rule_based_response


class RuleBasedResponseTests(TestCase):
    def test_rule_based_response_changes_for_different_travel_questions(self):
        flight_response = get_rule_based_response("Help me book a flight")
        hotel_response = get_rule_based_response("Find me a hotel")

        self.assertIn("flight", flight_response.lower())
        self.assertIn("hotel", hotel_response.lower())
        self.assertNotEqual(flight_response, hotel_response)
