import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from file_manager.models import Subject
from resources.models import AbstractResource, Section, Subpart


@pytest.mark.django_db
class TestTopSubjectsByLocation:
    def setup_method(self, method):
        """Setup resources and client before each test."""
        self.client = APIClient()
        self.url = reverse('top-subjects-by-location')

        subject1 = Subject.objects.create(full_name="Medicaid Policies")
        subject2 = Subject.objects.create(full_name="Health Coverage")

        subpart1 = Subpart.objects.create(title=42, part=433, subpart_id="A")
        section1 = Section.objects.create(title=42, part=433, section_id=110, parent=subpart1)
        section2 = Section.objects.create(title=42, part=433, section_id=120, parent=subpart1)

        resource1 = AbstractResource.objects.create()
        resource1.subjects.add(subject1, subject2)
        resource1.locations.add(section1, section2)
        resource1.save()

        resource2 = AbstractResource.objects.create()
        resource2.subjects.add(subject1, subject2)
        resource2.locations.add(section2)
        resource2.save()

        resource3 = AbstractResource.objects.create()
        resource3.subjects.add(subject2)
        resource3.locations.add(subpart1)
        resource3.save()

        self.sections = [section1, section2]
        self.subparts = [subpart1]

    def get_response(self, locations, top_x, min_count=1):
        """Helper function to send a request to the API."""
        locations_param = "&".join([f"locations={loc.title}.{loc.part}" for loc in locations])
        if top_x:
            locations_param += f"&top_x={top_x}"
        if min_count:
            locations_param += f"&min_count={min_count}"
        return self.client.get(f"{self.url}?{locations_param}")

    def test_subject_counts_reflect_distinct_resources_only(self):
        """ Ensure that the count of subjects returned only reflects counts from distinct resources.
        This test checks that subjects linked to multiple resources are counted once per unique resource,
        ensuring that duplicate resources for a subject do not inflate their count.
        """
        response = self.get_response(self.subparts, 5)
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        assert len(results) == 2, "Should return 2 subjects"
        # results count should be 4 and 3
        assert results[0]['full_name'] == "Health Coverage"
        assert results[0]['count'] == 3, "Medicaid Policies should appear three times"
        assert results[1]['full_name'] == "Medicaid Policies"
        assert results[1]['count'] == 2, "Health Coverage should appear two times"

    def test_all_sections_included(self):
        """Test with all sections included."""
        response = self.get_response(self.sections, 5)
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        assert len(results) == 2, "Should return 2 subjects"
        assert results[0]['full_name'] == "Health Coverage"
        assert results[0]['count'] == 3, "Medicaid Policies should appear three times"
        assert results[1]['full_name'] == "Medicaid Policies"
        assert results[1]['count'] == 2, "Health Coverage should appear two times"

    def test_location_by_title(self):
        """Test with a location by title only."""
        response = self.client.get(f"{self.url}?locations={self.sections[0].title}&top_x=5")
        assert response.status_code == status.HTTP_200_OK

    def test_top_x_parameter(self):
        """Check top_x parameter is working."""
        response = self.get_response(self.sections, 1, 2)
        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        assert len(results) == 1, "Should return 1 subject"
        assert results[0]['full_name'] == "Health Coverage", "Should return Health Coverage"

    def test_min_count_parameter(self):
        """Ensure the returned subjects have counts >= min_count."""
        response = self.get_response(self.sections, 5, 2)
        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        for subject in results:
            assert subject['count'] >= 2, f"Subject {subject['full_name']} should have a count >= 2"

    def test_min_count_unspecified(self):
        """Ensure subjects have counts >= 1 if min_count isn't specified."""
        response = self.get_response(self.sections, 5)
        assert response.status_code == status.HTTP_200_OK
        results = response.json()
        for subject in results:
            assert subject['count'] >= 1, f"Subject {subject['full_name']} should have a count >= 1"
