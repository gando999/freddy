import json
from functools import partial
from collections import namedtuple


DEFAULT_CRITERIA_DELIM = '.'

FilterMask = namedtuple('FilterMask', ['path', 'truths'])


class BadCriteriaError(Exception):
    """
    Failed to find results with given criteria
    """
    pass


class CriteriaDelimiterClash(Exception):
    """
    The delimiter for criteria is also contained
    on one of the keys in the document
    """
    pass


def byteify(input):
    '''Take care of unicode formatting'''
    if isinstance(input, dict):
        return {
            byteify(key):byteify(value)
            for key,value in input.iteritems()
        }
    elif isinstance(input, list):
        return [
            byteify(element) for element in input
        ]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def pretty_json(json_doc):
    """
    Takes a JSON doc as string and
    returns as formatted string.
    Returns input untouched if not valid JSON.
    """
    try:
        return json.dumps(
            json.loads(json_doc), sort_keys=True,
            indent=2, separators=(',', ': ')
        )
    except ValueError:
        return json_doc


def apply_criteria(supplied_criteria, criteria_delim, doc):
    """
    Takes a JSON string as input and returns
    JSON string as output
    """
    json_doc = json.loads(doc)
    criteria = (
        supplied_criteria.split(criteria_delim)
        if not supplied_criteria == '*' else []
    )
    
    def find(k, jv):
        if isinstance(jv, dict):
            try:
                for level_key in jv.keys():
                    if criteria_delim in level_key:
                        raise CriteriaDelimiterClash()
                return jv[k]
            except KeyError:
                raise BadCriteriaError()
        if isinstance(jv, list):
            results = []
            for i in jv:
                results.append(find(k, i))
            return results
        raise BadCriteriaError()
    last = json_doc
    criteria.reverse()
    while criteria:
        last = find(criteria.pop(), last)

    if isinstance(last, list):
        last_formatted = map(lambda x: byteify(x), last)
        return json.dumps(last_formatted)
    if isinstance(last, dict):
        return json.dumps(byteify(last))
    return byteify(last)


def apply_filter(filter_mask, doc):
    """
    Takes a JSON string as input and returns
    JSON string as output
    """
    json_doc = json.loads(doc)

    list_elements = []
    def root_list(k, jv):
        if isinstance(jv, dict):
            try:
                return jv[k]
            except KeyError:
                raise BadCriteriaError()
        if isinstance(jv, list):
            list_elements.append(jv)
            return jv    

    mask_path = filter_mask.path
    mask_path.reverse()
    last = json_doc
    while mask_path:
        last = root_list(mask_path.pop(), last)

    last_list = list_elements.pop()
    assert len(filter_mask.truths) == len(last_list)
    for item, truth in zip(last_list, filter_mask.truths):
        if not truth:
            last_list.remove(item)

    return json.dumps(byteify(json_doc))


def create_filter(filter_path, target, doc):
    """
    Takes a JSON string as input and returns
    truth mapping to be used 
    """
    json_doc = json.loads(doc)
    criteria = filter_path.split('.') #mutated!

    def lfunc(target_param, x, y):
        if isinstance(x, list):
            criteria.pop(0)
            results = []
            for item in x:
                results.append(
                    reduce(partial(lfunc, target_param), criteria, item)
                )
            return results
        if isinstance(x, dict):
            try:
                result = x[y]
                if (not isinstance(result, dict) and
                    not isinstance(result, list)):
                    return True if result == target_param else False
                return x[y]
            except KeyError:
                return False
        if isinstance(x, bool):
            return x
    
    pfunc = partial(lfunc, target)
    context = filter_path.split('.')
    return FilterMask(
        path=context, truths=reduce(pfunc, criteria, json_doc)
    )


class ResultFilter(object):

    def __init__(
            self, json_in,
            criteria_delim=DEFAULT_CRITERIA_DELIM
        ):
        if not isinstance(json_in, str):
            self.json_in = json.dumps(json_in)
        else:
            self.json_in = json_in
        self.criteria_delim = criteria_delim

    def apply(self, criteria):
        '''Apply a criteria to the json document'''
        try:
            return apply_criteria(
                criteria,
                self.criteria_delim,
                self.json_in
            )
        except BadCriteriaError:
            return 'Unable to filter using {}'.format(
                criteria
            )
        except CriteriaDelimiterClash:
            info_string = 'Criteria delimiter [{}] is a key in document'
            return info_string.format(
                self.criteria_delim
            )

    def filter_on(self, filter_path, target):
        try:
            filter_mask = create_filter(
                filter_path, target, self.json_in
            )
            return apply_filter(
                filter_mask, self.json_in
            )
        except BadCriteriaError:
            return 'Unable to filter using {}'.format(
                filter_path
            )
        except CriteriaDelimiterClash:
            info_string = 'Criteria delimiter [{}] is a key in document'
            return info_string.format(
                self.criteria_delim
            )
            
                
