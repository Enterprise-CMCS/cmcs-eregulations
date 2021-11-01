from django.test import TestCase
from supplemental_content.views import _make_category_tree


class CategoryTreeTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_no_hierarchy(self):
        input = [
            {
                "id": 1,
                "parent": None,
                "title": "A",
                "description": "Category A",
                "supplemental_content": [
                    {"content_id": 1},
                    {"content_id": 2},
                ],
            },
            {
                "id": 2,
                "parent": None,
                "title": "B",
                "description": "Category B",
                "supplemental_content": [
                    {"content_id": 3},
                    {"content_id": 4},
                ],
            },
            {
                "id": 3,
                "parent": None,
                "title": "C",
                "description": "Category C",
                "supplemental_content": [
                    {"content_id": 5},
                    {"content_id": 6},
                ],
            },
        ]

        output = [
            {
                "id": 1,
                "title": "A",
                "description": "Category A",
                "supplemental_content": [
                    {"content_id": 1},
                    {"content_id": 2},
                ],
                "sub_categories": [],
            },
            {
                "id": 2,
                "title": "B",
                "description": "Category B",
                "supplemental_content": [
                    {"content_id": 3},
                    {"content_id": 4},
                ],
                "sub_categories": [],
            },
            {
                "id": 3,
                "title": "C",
                "description": "Category C",
                "supplemental_content": [
                    {"content_id": 5},
                    {"content_id": 6},
                ],
                "sub_categories": [],
            },
        ]

        self.assertListEqual(_make_category_tree(input), output)

    def test_basic_hierarchy(self):
        input = [
            {
                "id": 1,
                "parent": None,
                "title": "A",
                "description": "Category A",
                "supplemental_content": [
                    {"content_id": 1},
                    {"content_id": 2},
                ],
            },
            {
                "id": 2,
                "parent": None,
                "title": "B",
                "description": "Category B",
                "supplemental_content": [
                    {"content_id": 3},
                    {"content_id": 4},
                ],
            },
            {
                "id": 3,
                "parent": {
                    "id": 1,
                    "parent": None,
                    "title": "A",
                    "description": "Category A",
                },
                "title": "A-A",
                "description": "Category A Sub-category A",
                "supplemental_content": [
                    {"content_id": 5},
                    {"content_id": 6},
                ],
            },
            {
                "id": 4,
                "parent": {
                    "id": 2,
                    "parent": None,
                    "title": "B",
                    "description": "Category B",
                },
                "title": "B-A",
                "description": "Category B Sub-category A",
                "supplemental_content": [
                    {"content_id": 7},
                    {"content_id": 8},
                ],
            },
        ]

        output = [
            {
                "id": 1,
                "title": "A",
                "description": "Category A",
                "supplemental_content": [
                    {"content_id": 1},
                    {"content_id": 2},
                ],
                "sub_categories": [
                    {
                        "id": 3,
                        "title": "A-A",
                        "description": "Category A Sub-category A",
                        "supplemental_content": [
                            {"content_id": 5},
                            {"content_id": 6},
                        ],
                        "sub_categories": [],
                    },
                ],
            },
            {
                "id": 2,
                "title": "B",
                "description": "Category B",
                "supplemental_content": [
                    {"content_id": 3},
                    {"content_id": 4},
                ],
                "sub_categories": [
                    {
                        "id": 4,
                        "title": "B-A",
                        "description": "Category B Sub-category A",
                        "supplemental_content": [
                            {"content_id": 7},
                            {"content_id": 8},
                        ],
                        "sub_categories": [],
                    },
                ],
            },
        ]

        self.assertListEqual(_make_category_tree(input), output)

    def test_advanced_hierarchy(self):
        input = [
            {
                "id": 1,
                "parent": {
                    "id": 2,
                    "parent": None,
                    "title": "B",
                    "description": "Category B",
                },
                "title": "A",
                "description": "Category A",
                "supplemental_content": [
                    {"content_id": 1},
                    {"content_id": 2},
                ],
            },
            {
                "id": 2,
                "parent": None,
                "title": "B",
                "description": "Category B",
                "supplemental_content": [
                    {"content_id": 3},
                    {"content_id": 4},
                ],
            },
            {
                "id": 3,
                "parent": {
                    "id": 1,
                    "parent": {
                        "id": 2,
                        "parent": None,
                        "title": "B",
                        "description": "Category B",
                    },
                    "title": "A",
                    "description": "Category A",
                },
                "title": "A-A",
                "description": "Category A Sub-category A",
                "supplemental_content": [
                    {"content_id": 5},
                    {"content_id": 6},
                ],
            },
            {
                "id": 4,
                "parent": {
                    "id": 2,
                    "parent": None,
                    "title": "B",
                    "description": "Category B",
                },
                "title": "B-A",
                "description": "Category B Sub-category A",
                "supplemental_content": [
                    {"content_id": 7},
                    {"content_id": 8},
                ],
            },
        ]

        output = [
            {
                "id": 2,
                "title": "B",
                "description": "Category B",
                "supplemental_content": [
                    {"content_id": 3},
                    {"content_id": 4},
                ],
                "sub_categories": [
                    {
                        "id": 1,
                        "title": "A",
                        "description": "Category A",
                        "supplemental_content": [
                            {"content_id": 1},
                            {"content_id": 2},
                        ],
                        "sub_categories": [
                            {
                                "id": 3,
                                "title": "A-A",
                                "description": "Category A Sub-category A",
                                "supplemental_content": [
                                    {"content_id": 5},
                                    {"content_id": 6},
                                ],
                                "sub_categories": [],
                            }
                        ]
                    },
                    {
                        "id": 4,
                        "title": "B-A",
                        "description": "Category B Sub-category A",
                        "supplemental_content": [
                            {"content_id": 7},
                            {"content_id": 8},
                        ],
                        "sub_categories": [],
                    },
                ],
            },
        ]

        self.assertListEqual(_make_category_tree(input), output)
