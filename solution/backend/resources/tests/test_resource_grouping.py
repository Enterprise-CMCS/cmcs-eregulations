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
        # As part of initial migrations, an FR Link category is created which will
        # cause duplicate key errors if the following line is not run.
        PublicCategory.objects.all().delete()
        groups = [ResourceGroup.objects.create(id=i) for i in range(3)]
        categories = [PublicCategory.objects.create(id=i, name=f"{i}") for i in range(7)]
        subjects = [Subject.objects.create(id=i) for i in range(7)]
        citations = [Section.objects.create(id=i, title=i, part=i, section_id=i) for i in range(8)]
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
        link = FederalRegisterLink.objects.create(id=6, category=categories[6])
        link.cfr_citations.set([citations[6], citations[7]])
        link.subjects.set([subjects[6]])
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
        self.assertCountEqual(link.related_categories_set, [6])
        self.assertCountEqual(link.related_subjects_set, [6])
        self.assertCountEqual(link.related_citations_set, [6, 7])

    def test_update_group(self):
        group = ResourceGroup.objects.get(id=0)
        group.resources.set([2, 4])
        group.save()

        links = FederalRegisterLink.objects.filter(resource_groups__isnull=False).order_by("id").annotate(
            related_resources_set=distinct_array_agg("related_resources"),
            related_categories_set=distinct_array_agg("related_categories"),
            related_subjects_set=distinct_array_agg("related_subjects"),
            related_citations_set=distinct_array_agg("related_citations"),
        ).distinct()

        [self.assertEqual(links[i].group_parent, True) for i in [0, 2, 1]]
        [self.assertEqual(links[i].group_parent, False) for i in [3, 4, 5]]

        expected = [
            [3, 5],
            [3],
            [4],
            [0, 5, 1],
            [2],
            [0, 3],
        ]

        for i in range(len(links)):
            self.assertCountEqual(
                links[i].related_resources_set,
                expected[i],
                msg=f"related_resources for resource {i} is incorrect!",
            )
            self.assertCountEqual(
                links[i].related_categories_set,
                expected[i] + [i],
                msg=f"related_categories for resource {i} is incorrect!",
            )
            self.assertCountEqual(
                links[i].related_subjects_set,
                expected[i] + [i],
                msg=f"related_subjects for resource {i} is incorrect!",
            )

    # Test that a resource's related_X fields are cleared when removed from a group
    #
    # Test config looks like:
    # {
    #   "to_update": items_pk,
    #   "new_groups": [new_group_pks],
    #   "updated_related_fields": {
    #     "related_resources": [expected_related_resource_pks],
    #     "related_categories": [expected_related_category_pks],
    #     "related_subjects": [expected_related_subject_pks],
    #     "related_citations": [expected_related_citation_pks],
    #   },
    #   "parents_true": [expected_pks_where_parent_is_true],
    #   "parents_false": [expected_pks_where_parent_is_false],
    #   "grouped_related_fields": [
    #     [expected_related_resource_pks_item_0],
    #     .....
    #     [expected_related_resource_pks_item_5],
    #   ],
    # }
    #
    # See examples below.
    def perform_group_reset_test(self, config):
        # Update the configured link's group assignments
        to_update = FederalRegisterLink.objects.get(id=config["to_update"])
        to_update.resource_groups.set(config["new_groups"])
        to_update.save()

        # Get the configured link again
        updated = FederalRegisterLink.objects.annotate(
            related_resources_set=distinct_array_agg("related_resources"),
            related_categories_set=distinct_array_agg("related_categories"),
            related_subjects_set=distinct_array_agg("related_subjects"),
            related_citations_set=distinct_array_agg("related_citations"),
        ).distinct().get(id=config["to_update"])

        # Verify that its related_X fields are reset
        updated_related_fields = config["updated_related_fields"]
        self.assertCountEqual(updated.related_resources_set, updated_related_fields["related_resources"])
        self.assertCountEqual(updated.related_categories_set, updated_related_fields["related_categories"])
        self.assertCountEqual(updated.related_subjects_set, updated_related_fields["related_subjects"])
        self.assertCountEqual(updated.related_citations_set, updated_related_fields["related_citations"])

        # Get the other (still grouped) links
        links = FederalRegisterLink.objects.filter(resource_groups__isnull=False).order_by("id").annotate(
            related_resources_set=distinct_array_agg("related_resources"),
            related_categories_set=distinct_array_agg("related_categories"),
            related_subjects_set=distinct_array_agg("related_subjects"),
            related_citations_set=distinct_array_agg("related_citations"),
        ).distinct()

        # To simplify the following code, get link by pk instead of array index
        def get_link(i): return [link for link in links if link.id == i][0]

        # Verify group_parent field is set correctly
        for i in config["parents_true"]:
            self.assertEqual(get_link(i).group_parent, True, msg=f"resource {i} should be a group parent now, but isn't!")
        for i in config["parents_false"]:
            self.assertEqual(get_link(i).group_parent, False, msg=f"resource {i} should not be a group parent now, but is!")

        # Verify related fields are set correctly
        expected = config["grouped_related_fields"]
        for i in [link.pk for link in links]:
            self.assertCountEqual(
                get_link(i).related_resources_set,
                expected[i],
                msg=f"related_resources for resource {i} is incorrect!",
            )
            self.assertCountEqual(
                get_link(i).related_categories_set,
                expected[i] + [i],
                msg=f"related_categories for resource {i} is incorrect!",
            )
            self.assertCountEqual(
                get_link(i).related_subjects_set,
                expected[i] + [i],
                msg=f"related_subjects for resource {i} is incorrect!",
            )

    def test_group_removal_item_0(self):
        config = {
            "to_update": 0,
            "new_groups": [],
            "updated_related_fields": {
                "related_resources": [],
                "related_categories": [0],
                "related_subjects": [0],
                "related_citations": [0, 1],
            },
            "parents_true": [1, 2, 3],
            "parents_false": [4, 5],
            "grouped_related_fields": {
                1: [3],
                2: [4],
                3: [1, 5],
                4: [2],
                5: [3],
            },
        }
        self.perform_group_reset_test(config)

    def test_group_removal_item_1(self):
        config = {
            "to_update": 1,
            "new_groups": [],
            "updated_related_fields": {
                "related_resources": [],
                "related_categories": [1],
                "related_subjects": [1],
                "related_citations": [1, 2],
            },
            "parents_true": [0, 3],
            "parents_false": [2, 4, 5],
            "grouped_related_fields": {
                0: [2, 4, 3, 5],
                2: [0, 4],
                3: [0, 5],
                4: [0, 2],
                5: [0, 3],
            },
        }
        self.perform_group_reset_test(config)

    def test_group_update_item_3(self):
        config = {
            "to_update": 3,
            "new_groups": [0, 1],
            "updated_related_fields": {
                "related_resources": [0, 2, 4, 5],
                "related_categories": [0, 2, 3, 4, 5],
                "related_subjects": [0, 2, 3, 4, 5],
                "related_citations": [0, 1, 2, 3, 4, 5, 6],
            },
            "parents_true": [0, 1],
            "parents_false": [2, 3, 4, 5],
            "grouped_related_fields": {
                0: [2, 4, 3, 5],
                1: [],
                2: [0, 3, 4],
                3: [0, 2, 4, 5],
                4: [0, 2, 3],
                5: [0, 3],
            },
        }
        self.perform_group_reset_test(config)

    def test_group_add_item_5(self):
        config = {
            "to_update": 5,
            "new_groups": [1, 2],
            "updated_related_fields": {
                "related_resources": [0, 3, 1],
                "related_categories": [0, 3, 1, 5],
                "related_subjects": [0, 3, 1, 5],
                "related_citations": [0, 1, 2, 3, 4, 5, 6],
            },
            "parents_true": [0, 1],
            "parents_false": [2, 3, 4, 5],
            "grouped_related_fields": {
                0: [2, 3, 4, 5],
                1: [3, 5],
                2: [0, 4],
                3: [0, 1, 5],
                4: [0, 2],
                5: [0, 3, 1],
            },
        }
        self.perform_group_reset_test(config)

    def test_group_add_item_6(self):
        config = {
            "to_update": 6,
            "new_groups": [1, 2],
            "updated_related_fields": {
                "related_resources": [0, 3, 1, 5],
                "related_categories": [0, 3, 1, 5, 6],
                "related_subjects": [0, 3, 1, 5, 6],
                "related_citations": [0, 1, 2, 3, 4, 5, 6, 7],
            },
            "parents_true": [0, 1],
            "parents_false": [2, 3, 4, 5],
            "grouped_related_fields": {
                0: [2, 3, 4, 5, 6],
                1: [3, 6],
                2: [0, 4],
                3: [0, 1, 5, 6],
                4: [0, 2],
                5: [0, 3, 6],
                6: [0, 1, 3, 5],
            },
        }
        self.perform_group_reset_test(config)
