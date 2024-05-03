import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from file_manager.models import Subject
from resources.models import AbstractResource, Section, Subpart


@pytest.mark.django_db
def test_top_subjects_by_location():
    """
    Test the TopSubjectsByLocationViewSet's ability to return the top subjects based on location.
    """

    def create_resources():
        subject1 = Subject.objects.create(full_name="Medicaid Policies")
        subject2 = Subject.objects.create(full_name="Health Coverage")

        # Create locations
        subpart1 = Subpart.objects.create(title=42, part=433, subpart_id="A")
        section1 = Section.objects.create(title=42, part=433, section_id=110, parent=subpart1)
        section2 = Section.objects.create(title=42, part=433, section_id=120, parent=subpart1)
        section3 = Section.objects.create(title=42, part=434, section_id=130, parent=subpart1)

        # Create resources and associate subjects to sections
        resource1 = AbstractResource.objects.create()
        resource1.subjects.add(subject1, subject2)
        resource1.locations.add(section1)
        resource1.save()

        resource2 = AbstractResource.objects.create()
        resource2.subjects.add(subject1, subject2)
        resource2.locations.add(section2)
        resource2.save()

        resource3 = AbstractResource.objects.create()
        resource3.subjects.add(subject1)
        resource3.locations.add(section3)
        resource3.save()

        return {
            "subjects": [subject1, subject2],
            "sections": [section1, section2, section3],
        }

    def get_response(client, url, locations, top_x, min_count=1):
        locations_param = "&".join([f"locations={loc.title}.{loc.part}" for loc in locations])
        if top_x:
            locations_param += f"&top_x={top_x}"
        if min_count:
            locations_param += f"&min_count={min_count}"
        response = client.get(f"{url}?{locations_param}")
        return response

    # Set up resources
    resources = create_resources()
    sections = resources["sections"]

    # Initialize API client
    client = APIClient()
    url = reverse('top-subjects-by-location')

    # Test with all sections included
    response = get_response(client, url, sections, 5)
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    # Ensure specific number of subjects returned is correct
    assert len(results) == 2, "Should return 2 subjects"

    # Check counts and order
    top_subject = results[0]
    assert top_subject['full_name'] == "Medicaid Policies"
    assert top_subject['count'] == 3, "Medicaid Policies should appear three times"

    second_subject = results[1]
    assert second_subject['full_name'] == "Health Coverage"
    assert second_subject['count'] == 2, "Health Coverage should appear twice"

    # Test with a location by title only
    response = client.get(f"{url}?locations={sections[0].title}&top_x=5")
    assert response.status_code == status.HTTP_200_OK

    # check top_x parameter is working
    response = get_response(client, url, sections, 1, 2)
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert len(results) == 1, "Should return 1 subject"
    assert results[0]['full_name'] == "Medicaid Policies", "Should return Medicaid Policies"

    # Ensure the returned subjects have counts <= min_count
    response = get_response(client, url, sections, 5, 2)
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    for subject in results:
        assert subject['count'] >= 2, f"Subject {subject['full_name']} should have a count <= 2"

    # Ensure the returned subjects have counts <= 1 if none is specified
    response = get_response(client, url, sections, 5)
    assert response.status_code == status.HTTP_200_OK
    results = response.json()

    for subject in results:
        assert subject['count'] >= 1, f"Subject {subject['full_name']} should have a count <= 2"


    # Ensure the counts reflect distinct resources
    assert len(results) == 2, "Should return 2 subjects"

    subject_counts = {result['full_name']: result['count'] for result in results}
    assert subject_counts['Medicaid Policies'] == 3, "Medicaid Policies should be associated with 3 unique resources"
    assert subject_counts['Health Coverage'] == 2, "Health Coverage should be associated with 2 unique resources"
