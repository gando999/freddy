import unittest

from query import ResultFilter


SIMPLE = {
    'level1': 'item_level1',
    'level2': {
        'level3': 'item_level3',
        'level35': 'item_level35'
    }
}


class BaseQueryTestCase(unittest.TestCase):

    def _assert_type_str(self, result):
        self.assertEquals(str, type(result))


class BadParametersTestCase(BaseQueryTestCase):

    def setUp(self):
        self.testee = ResultFilter(SIMPLE)

    def test_bad_key_one_level(self):
        self.assertEquals(
            'Unable to filter using level11',
            self.testee.apply('level11')
        )

    def test_bad_key_part(self):
        self.assertEquals(
            'Unable to filter using level2.level23',
            self.testee.apply('level2.level23')
        )


BAD_KEYS = {
    'level1': 'item_level1',
    'level2.5': {
        'level3': 'item_level3',
        'level35': 'item_level35'
    }
}


class JsonKeysClashWithCriteriaTestCase(BaseQueryTestCase):

    def setUp(self):
        self.testee = ResultFilter(BAD_KEYS)

    def test_clashing_key_with_period(self):
        result = self.testee.apply('level2.5.level35')
        self._assert_type_str(result)
        self.assertEquals(
            'Criteria delimiter [.] is a key in document',
            result
        )

    def test_ok_with_different_delimiter(self):
        testee = ResultFilter(
            BAD_KEYS, criteria_delim='^'
        )
        result = testee.apply('level2.5^level35')
        self._assert_type_str(result)
        self.assertEquals('item_level35', result)


class SimpleQueryTestCase(BaseQueryTestCase):

    def setUp(self):
        self.testee = ResultFilter(SIMPLE)

    def _assert_type_str(self, result):
        self.assertEquals(str, type(result))

    def test_query_level1(self):
        result = self.testee.apply('level1')
        self._assert_type_str(result)
        self.assertEquals('item_level1', result)

    def test_query_level2_first_key(self):
        result = self.testee.apply('level2.level3')
        self._assert_type_str(result)
        self.assertEquals('item_level3', result)

    def test_query_level2_all(self):
        result = self.testee.apply('level2')
        self._assert_type_str(result)
        self.assertEquals(
            '{"level3": "item_level3", "level35": "item_level35"}',
            self.testee.apply('level2')
        )


ONE_LEVEL = {
    'level1': 'item_level1',
    'level2': {
        'level25': {
            'level251': 'item_level251',
            'level252': 'item_level252'

        },
        'level26': {
            'level261': 'item_level261',
            'level262': 'item_level262'
        }
    }
}


class OneLevelNestedQueryTestCase(BaseQueryTestCase):

    def setUp(self):
        self.testee = ResultFilter(ONE_LEVEL)

    def test_two_subdicts(self):
        result = self.testee.apply('level2')
        self._assert_type_str(result)
        expected = ('{"level26": {"level262": "item_level262", "level261":'
                    ' "item_level261"}, "level25": {"level252": "item_level252",'
                    ' "level251": "item_level251"}}')
        self.assertEquals(expected, result)
        

ONE_LEVEL_REPEATS = {
    'level1': 'item_level1',
    'level2': {
        'level25': {
            'level251': 'item_level251',
            'level252': 'item_level252'

        },
        'level25': {
            'level261': 'item_level261',
            'level262': 'item_level262'
        }
    }
}


class OneLevelRepeatedKeysNoList(BaseQueryTestCase):

    def setUp(self):
        self.testee = ResultFilter(ONE_LEVEL_REPEATS)

    def test_same_keys_no_list(self):
        result = self.testee.apply('level2.level25')
        self._assert_type_str(result)
        expected = ''
        expected = ('{"level262": "item_level262", '
                    '"level261": "item_level261"}')
        self.assertEquals(expected, result)


ONE_LEVEL_REPEATS_WITH_LIST = {
    'level1': 'item_level1',
    'level2': [
        {
            'level25': {
                'level251': 'item_level251',
                'level252': 'item_level252'
            }
        },
        {
            'level25': {
                'level261': 'item_level261',
                'level262': 'item_level262'
            }
        }
    ]
}


class OneLevelRepeatedKeysTestCase(BaseQueryTestCase):

    def setUp(self):
        self.testee = ResultFilter(ONE_LEVEL_REPEATS_WITH_LIST)

    def test_same_keys(self):
        result = self.testee.apply('level2.level25')
        self._assert_type_str(result)
        expected = ('[{"level252": "item_level252", "level251": '
                    '"item_level251"}, {"level262": "item_level262", '
                    '"level261": "item_level261"}]')
        self.assertEquals(expected, result)

    def test_same_keys_root(self):
        result = self.testee.apply('level2')
        self._assert_type_str(result)
        expected = ('[{"level25": {"level252": "item_level252", "level251": '
                    '"item_level251"}}, {"level25": {"level262": "item_level262", '
                    '"level261": "item_level261"}}]')
        self.assertEquals(expected, result)
