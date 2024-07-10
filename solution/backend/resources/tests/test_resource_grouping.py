# The tests in this file are comprehensive of expected grouping behavior when post-save hooks are invoked
# on model save. The structure is like this:
#
#   0   1  <-- group parents (item 0 is parent to groups 0 and 1, item 1 is parent to group 2)
#   | \ |
#   2   3  <-- item 2 belongs to group 0 only, item 3 belongs to both groups 1 and 2
#   |   |
#   4   5  <-- item 4 belongs to group 0 only, item 5 belongs to group 1 only
#
# Categories are assigned based on pk ascending (item 1 belongs to category 1, etc).
# Subjects are assigned in the same way as categories.
# Citations are assigned such that item 0 has citations 0 and 1, item 1 has citations 1 and 2, etc.
#
# This structure permits testing of parent item computation as well as related_X field assignment for many
# different group configurations.


from datetime import datetime, timedelta

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, Value
from django.test import TestCase

from resources.models import (
    FederalRegisterLink,
    PublicCategory,
    ResourceGroup,
    Section,
    Subject,
)


def distinct_array_agg(field):
    return ArrayAgg(
        field,
        distinct=True,
        filter=Q(**{f"{field}__isnull": False}),
        default=Value([]),
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

        # Create a link with no group
        link = FederalRegisterLink.objects.create(id=6, category=categories[0])
        link.cfr_citations.set([citations[0], citations[1]])
        link.subjects.set([subjects[0], subjects[1]])
        link.save()

    # Ensure only items 0 and 1 are computed to be group parents
    def test_group_parents(self):
        links = FederalRegisterLink.objects.filter(resource_groups__isnull=False).order_by("id").distinct()
        for i in links[0:2]:
            self.assertEqual(i.group_parent, True)
        for i in links[2:]:
            self.assertEqual(i.group_parent, False)

    # Test to be sure related_resources, related_categories, and related_subjects are being
    # computed properly in a multigroup scenario.
    def test_related_fields(self):
        links = FederalRegisterLink.objects.filter(resource_groups__isnull=False).order_by("id").annotate(
            related_resources_set=distinct_array_agg("related_resources"),
            related_categories_set=distinct_array_agg("related_categories"),
            related_subjects_set=distinct_array_agg("related_subjects"),
        ).distinct()

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
        links = FederalRegisterLink.objects.filter(resource_groups__isnull=False).order_by("id").annotate(
            related_citations_set=distinct_array_agg("related_citations"),
        ).distinct()

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

    # Test that related_X fields are set correctly when a resource is not part of a group
    def test_no_group_related_fields(self):
        query = FederalRegisterLink.objects.filter(resource_groups__isnull=True).annotate(
            related_resources_set=distinct_array_agg("related_resources"),
            related_categories_set=distinct_array_agg("related_categories"),
            related_subjects_set=distinct_array_agg("related_subjects"),
            related_citations_set=distinct_array_agg("related_citations"),
        ).distinct()
        self.assertEqual(len(query), 1)
        link = query.first()

        self.assertEqual(len(link.related_resources_set), 0)
        self.assertCountEqual(link.related_categories_set, [0])
        self.assertCountEqual(link.related_subjects_set, [0, 1])
        self.assertCountEqual(link.related_citations_set, [0, 1])
