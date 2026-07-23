from django.test import TestCase
from django.urls import reverse


class RecommendationUrlTests(TestCase):
    def test_recommendation_urls_are_reverse_resolved(self):
        self.assertEqual(reverse('recommendation:recommendation'), '/recommendation/')
        self.assertEqual(reverse('recommendation:preference_setup'), '/recommendation/preferences/')
