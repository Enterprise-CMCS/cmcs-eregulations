from django.test import TestCase
from django.urls import reverse from rest_framework.test import APIClient
from rest_framework import status
from file_manager.models import Subject, Location
from file_manager.serializers.groupings import SubjectSerializer

class TopSubjectsByLocationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Creating locations
        self.location_part_433 = Location.objects.create(name="42 CFR 433")
        self.location_section_436_110 = Location.objects.create(name="42 CFR 436.110")
        self.location_subpart_433_A = Location.objects.create(name="42 CFR 433 Subpart A")
        self.location_section_440_305 = Location.objects.create(name="42 CFR 440.305")
        self.location_subpart_95_A = Location.objects.create(name="45 CFR 95 Subpart A")

        # Create subjects and associate them with locations
        self.subjects = [
            Subject.objects.create(name="Medicaid Eligibility"),
            Subject.objects.create(name="Health Coverage"),
            Subject.objects.create(name="Provider Reimbursements"),
            Subject.objects.create(name="State Funding"),
            Subject.objects.create(name="Federal Support")
        ]
        for subject in self.subjects:
            subject.locations.add(self.location_part_433)

        self.url = reverse('top-subjects-by-location')  # Update with the actual URL name if necessary

    def test_top_subjects_default(self):
        """
        Test that the endpoint returns the default top 5 subjects when no specific count is provided.
        """
        response = self.client.get(f"{self.url}?locations={self.location_part_433.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_top_subjects_specific_count(self):
        """
        Test that the endpoint returns the correct number of subjects when a specific count is requested.
        """
        response = self.client.get(f"{self.url}?locations={self.location_part_433.id}&top_x=3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_top_subjects_exceeding_available(self):
        """
        Test that the endpoint returns all available subjects when the requested count exceeds the available number.
        """
        response = self.client.get(f"{self.url}?locations={self.location_part_433.id}&top_x=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.subjects))  # Assuming all subjects are linked to the location

    def test_top_subjects_no_subjects(self):
        """
        Test that the endpoint returns an empty list when there are no subjects associated with the location.
        """
        response = self.client.get(f"{self.url}?locations={self.location_subpart_95_A.id}&top_x=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, [])
