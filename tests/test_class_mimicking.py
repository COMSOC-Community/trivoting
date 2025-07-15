"""
Module testing class inheritance for basic Python classes (list, tuple, etc...).
"""

from copy import deepcopy

from unittest import TestCase

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile


def check_members_equality(obj1, obj2, verbose: bool = False, omitted_attributes: list = None):
    if omitted_attributes is None:
        omitted_attributes = []

    assert type(obj1) == type(obj2)
    obj1_attrs = [
        a
        for a in dir(obj1)
        if a[:2] + a[-2:] != "____" and not callable(getattr(obj1, a))
    ]
    obj2_attrs = [
        a
        for a in dir(obj2)
        if a[:2] + a[-2:] != "____" and not callable(getattr(obj2, a))
    ]
    if verbose:
        print(f"{obj1_attrs}     {obj2_attrs}")
    assert obj1_attrs == obj2_attrs
    for attr in obj1_attrs:
        if not attr in omitted_attributes:
            if verbose:
                print(
                    f"{attr} : {obj1.__getattribute__(attr)}    {obj2.__getattribute__(attr)}"
                )
            assert obj1.__getattribute__(attr) == obj2.__getattribute__(attr)


def check_set_members(set_class, initial_set, included_objects, additional_objects, omitted_attributes=None):
    new_set = deepcopy(initial_set)
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set.add(additional_objects[0])
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set.discard(included_objects[0])
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = deepcopy(initial_set)
    new_set.remove(included_objects[0])
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set.clear()
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = deepcopy(initial_set)
    new_set.pop()
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = initial_set.copy()
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = deepcopy(initial_set)
    new_set = new_set.difference(set_class(additional_objects))
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = deepcopy(initial_set)
    new_set.difference_update(set_class(additional_objects))
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = deepcopy(initial_set)
    new_set = new_set.intersection(
        set_class(additional_objects), set_class(additional_objects)
    )
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = deepcopy(initial_set)
    new_set = new_set.symmetric_difference(set_class(additional_objects))
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = deepcopy(initial_set)
    new_set.symmetric_difference_update(set_class(additional_objects))
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = deepcopy(initial_set)
    new_set = new_set.union(set_class(additional_objects))
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = deepcopy(initial_set)
    new_set.update(set_class(additional_objects))
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = deepcopy(initial_set)
    new_set = new_set.__ior__(initial_set)
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = deepcopy(initial_set)
    new_set = new_set | initial_set
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)

    new_set = deepcopy(initial_set)
    new_set |= initial_set
    check_members_equality(initial_set, new_set, omitted_attributes=omitted_attributes)


def check_dict_members(initial_dict, included_keys, additional_keys, omitted_attributes=None):
    new_dict = deepcopy(initial_dict)
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict.clear()
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = initial_dict.copy()
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = deepcopy(initial_dict)
    new_dict.get(included_keys[0])
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = deepcopy(initial_dict)
    new_dict.items()
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = deepcopy(initial_dict)
    new_dict.keys()
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = deepcopy(initial_dict)
    new_dict.pop(included_keys[0])
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = deepcopy(initial_dict)
    new_dict.popitem()
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = deepcopy(initial_dict)
    new_dict.setdefault(included_keys[0])
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = deepcopy(initial_dict)
    new_dict.setdefault(additional_keys[0])
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = deepcopy(initial_dict)
    new_dict.update({k: 10 for k in additional_keys})
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = deepcopy(initial_dict)
    new_dict.values()
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = deepcopy(initial_dict)
    new_dict = new_dict.__ior__(initial_dict)
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = deepcopy(initial_dict)
    new_dict = new_dict | initial_dict
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)

    new_dict = deepcopy(initial_dict)
    new_dict |= initial_dict
    check_members_equality(initial_dict, new_dict, omitted_attributes=omitted_attributes)


def check_list_members(initial_list, included_objects, additional_objects, omitted_attributes=None):
    new_list = deepcopy(initial_list)
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list.clear()
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = deepcopy(initial_list)
    new_list.append(additional_objects[0])
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = initial_list.copy()
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = deepcopy(initial_list)
    new_list.count(included_objects[0])
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = deepcopy(initial_list)
    new_list.extend(additional_objects)
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = deepcopy(initial_list)
    new_list.index(included_objects[0])
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = deepcopy(initial_list)
    new_list.insert(3, additional_objects[0])
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = deepcopy(initial_list)
    new_list.pop()
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = deepcopy(initial_list)
    new_list.remove(included_objects[0])
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = deepcopy(initial_list)
    new_list.reverse()
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    try:
        new_list = deepcopy(initial_list)
        new_list.sort()
        check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)
    except NotImplementedError:
        pass

    new_list = deepcopy(initial_list)
    new_list += new_list
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = deepcopy(initial_list)
    new_list *= 5
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = deepcopy(initial_list)
    new_list = new_list[1:5]
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = deepcopy(initial_list)
    new_list = new_list[:-1]
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)

    new_list = deepcopy(initial_list)
    new_list = new_list[0:5:2]
    check_members_equality(initial_list, new_list, omitted_attributes=omitted_attributes)


class TestClassMimicking(TestCase):
    ALTERNATIVES = [Alternative(i) for i in range(20)]
    BALLOTS = [
            TrichotomousBallot(approved=ALTERNATIVES[1:10], disapproved=ALTERNATIVES[11:14]),
            TrichotomousBallot(approved=ALTERNATIVES[15:18], disapproved=ALTERNATIVES[0:5]),
            TrichotomousBallot(approved=ALTERNATIVES[18:18], disapproved=ALTERNATIVES[4:9]),
        ]
    EXTRA_BALLOTS = [
            TrichotomousBallot(approved=ALTERNATIVES[1:3], disapproved=ALTERNATIVES[11:14]),
            TrichotomousBallot(approved=ALTERNATIVES[11:16], disapproved=ALTERNATIVES[0:5]),
            TrichotomousBallot(approved=ALTERNATIVES[18:20], disapproved=ALTERNATIVES[4:9]),
        ]

    def test_profile_members(self):
        profile = TrichotomousProfile(self.BALLOTS, alternatives=self.ALTERNATIVES)
        check_list_members(profile, self.BALLOTS, self.EXTRA_BALLOTS, omitted_attributes=["_ballots_list", "_ballot_container"])

    def test_multiprofile_members(self):
        profile = TrichotomousProfile(self.BALLOTS, alternatives=self.ALTERNATIVES)
        multiprofile = profile.as_multiprofile()
        check_dict_members(multiprofile, [b.freeze() for b in self.BALLOTS], [b.freeze() for b in self.EXTRA_BALLOTS], omitted_attributes=["_ballots_counter", "_ballot_container"])

