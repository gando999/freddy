import unittest

from query import ResultFilter
from test_basics import BaseQueryTestCase


ONE_LEVEL = {
    "contests": [
        {
            "name": "contest1",
            "entry_count": 23,
            "rosters": [
                "blah", "blah2"
            ]
        },
        {
            "name": "contest2",
            "entry_count": 24,
            "rosters": [
                "bleeb", "blop"
            ]
        },
        {
            "name": "contest4",
            "entry_count": 24,
            "rosters": [
                "bleeb", "blop"
            ]
        }
    ]
}


class OneItemFilterTestCase(BaseQueryTestCase):

    def setUp(self):
        self.testee = ResultFilter(ONE_LEVEL)

    def test_where_equals_name(self):
        result = self.testee.filter_on(
            filter_path='contests.name',
            target='contest1'
        )
        self._assert_type_str(result)
        expected = (
            '{"contests": [{"entry_count": 23, '
            '"name": "contest1", "rosters": ["blah", "blah2"]}]}'
        )
        self.assertEquals(expected, result)

    def test_where_equals_two_elements(self):
        result = self.testee.filter_on(
            filter_path='contests.entry_count',
            target=24
        )
        self._assert_type_str(result)
        expected = (
            '{"contests": [{"entry_count": 24, '
            '"name": "contest2", "rosters": ["bleeb", '
            '"blop"]}, {"entry_count": 24, "name": '
            '"contest4", "rosters": ["bleeb", "blop"]}]}'
        )
        self.assertEquals(expected, result)


TWO_LEVEL = {
    "contests": [
        {
            "name": "contest1",
            "entry_count": 23,
            "rosters": [
                "blah", "blah2"
            ],
            "bloopers": {
                "main_bloop": "256",
                "second_bloop": "blamo"
            }
        },
        {
            "name": "contest2",
            "entry_count": 24,
            "rosters": [
                "bleeb", "blop"
            ],
            "bloopers": {
                "main_bloop": "255",
                "second_bloop": "slamo"
            }
        },
        {
            "name": "contest4",
            "entry_count": 24,
            "rosters": [
                "bleeb", "blop"
            ],
            "bloopers": {
                "main_bloop": "254",
                "second_bloop": "rilamo"
            }
        }
    ]
}


class TwoItemFilterTestCase(BaseQueryTestCase):

    def setUp(self):
        self.testee = ResultFilter(TWO_LEVEL)

    def test_where_equals(self):
        result = self.testee.filter_on(
            filter_path='contests.bloopers.main_bloop',
            target="256"
        )
        self._assert_type_str(result)
        expected = (
            '{"contests": [{"bloopers": {"second_bloop":'
            ' "blamo", "main_bloop": "256"}, "entry_count":'
            ' 23, "name": "contest1", "rosters": ["blah", "blah2"]}]}'
        )
        self.assertEquals(expected, result)

    def test_where_equals_matches_two(self):
        result = self.testee.filter_on(
            filter_path='contests.entry_count',
            target=24
        )
        self._assert_type_str(result)
        expected = (
            '{"contests": [{"bloopers": {"second_bloop": '
            '"slamo", "main_bloop": "255"}, "entry_count": 24, '
            '"name": "contest2", "rosters": ["bleeb", "blop"]}, '
            '{"bloopers": {"second_bloop": "rilamo", "main_bloop": '
            '"254"}, "entry_count": 24, "name": "contest4", '
            '"rosters": ["bleeb", "blop"]}]}'
        )
        self.assertEquals(expected, result)

