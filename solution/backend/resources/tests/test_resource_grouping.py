from datetime import datetime, timedelta

from django.contrib.postgres.aggregates import ArrayAgg
from django.test import TestCase

from resources.models import (
    FederalRegisterLink,
    PublicCategory,
    ResourceGroup,
    Section,
    Subject,
)


class TestResourceGrouping(TestCase):
    def setUp(self):
        groups = [ResourceGroup.objects.create(id=i) for i in range(3)]
        categories = [PublicCategory.objects.create(id=i, name=f"{i}") for i in range(6)]
        subjects = [Subject.objects.create(id=i) for i in range(6)]
        citations = [Section.objects.create(id=i, title=i, part=i, section_id=i) for i in range(7)]
        links = [FederalRegisterLink.objects.create(
                    id=i,
                    date=(datetime.now() - timedelta(i)).strftime('%Y-%m-%d'),
                    category=categories[i],
                ) for i in range(6)]
        groupings = [
            [groups[0], groups[1]],
            [groups[2]],
            [groups[0]],
            [groups[1], groups[2]],
            [groups[0]],
            [groups[1]],
        ]

        for i in range(len(links)):
            links[i].resource_groups.set(groupings[i])
            links[i].subjects.set([subjects[i]])
            links[i].cfr_citations.set([citations[i], citations[i + 1]])

        for i in links:
            i.save()

    # Ensure only items 0 and 1 are computed to be group parents
    def test_group_parents(self):
        links = FederalRegisterLink.objects.order_by("id")
        for i in links[0:2]:
            self.assertEqual(i.group_parent, True)
        for i in links[2:]:
            self.assertEqual(i.group_parent, False)

    # Test to be sure related_resources, related_categories, and related_subjects are being
    # computed properly in a multigroup scenario.
    def test_related_resources(self):
        links = FederalRegisterLink.objects.order_by("id").annotate(
            related_resources_set=ArrayAgg("related_resources", distinct=True),
            related_categories_set=ArrayAgg("related_categories", distinct=True),
            related_subjects_set=ArrayAgg("related_subjects", distinct=True),
        )

        # Expected related_X pks for all newly created links
        # For related_resources, we exclude the first item in each list (because related_resources does not include itself)
        expected = [
            [0, 2, 4, 3, 5],
            [1, 3],
            [2, 0, 4],
            [3, 0, 1, 5],
            [4, 0, 2],
            [5, 0, 3],
        ]

        for i in range(len(links)):
            self.assertCountEqual(
                links[i].related_resources_set,
                expected[i][1:],
                msg=f"related_resources for resource {i} is incorrect!",
            )
            self.assertCountEqual(
                links[i].related_categories_set,
                expected[i],
                msg=f"related_categories for resource {i} is incorrect!",
            )
            self.assertCountEqual(
                links[i].related_subjects_set,
                expected[i],
                msg=f"related_subjects for resource {i} is incorrect!",
            )

    # Test that related_citations are being computed properly in a multigroup scenario
    def test_related_citations(self):
        links = FederalRegisterLink.objects.order_by("id").annotate(
            related_citations_set=ArrayAgg("related_citations", distinct=True),
        )

        expected = [
            [0, 1, 2, 3, 4, 5, 6],
            [1, 2, 3, 4],
            [0, 1, 2, 3, 4, 5],
            [0, 1, 3, 4, 2, 5, 6],
            [0, 1, 2, 3, 4, 5],
            [0, 1, 3, 4, 5, 6],
        ]

        for i in range(len(links)):
            self.assertCountEqual(
                links[i].related_citations_set,
                expected[i],
                msg=f"related_citations for resource {i} is incorrect!",
            )
