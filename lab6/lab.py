#!/usr/bin/env python3
"""6.009 Lab 6 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def update(formula, var, value):
    # return 'falsifies' if formula contains a clause that is exactly (var, not value)
    # return 'truthifies' if at the end formula is empty
    # return simplified formula otherwise
    # basically, completely remove all clauses that contain (var = value), 
    #   and remove all literals of (var = not value) in clauses.
    new_formula = []
    for clause in formula:
        if clause == [(var, not value)]*len(clause):
            return 'falsifies'
        if not (var, value) in clause and clause:
            new_clause = [l for l in clause if l != (var, not value)]
            if new_clause:
                new_formula += [new_clause]
    if not new_formula:
        return 'truthifies'
    return new_formula


# try var = true, if it truthifies then return. if it falsifies then (try false, if it truthifies return, if it falsifies go back, if it intermediate then try next var), if it is intermediate then try next var

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    # if formula is empty or 'truthifies', return empty dict
    if formula == [] or formula == 'truthifies':
        return {}
    # if formula is 'falsifies', return None
    if formula == 'falsifies':
        return None
    # pick variable to test
    var = formula[0][0][0]
    for clause in formula:
        if len(clause) == 1:
            var = clause[0][0]
    # see if satisfying assignment exists with var=True. If so, return assgmt w/ {var:true}, if not, (try var=False. if not, return None)
    new_formula = update(formula, var, True)
    next_assgnmt = satisfying_assignment(new_formula)
    if next_assgnmt != None:
        next_assgnmt[var] = True
        return next_assgnmt
    else:
        new_formula = update(formula, var, False)
        next_assgnmt = satisfying_assignment(new_formula)
        if next_assgnmt != None:
            next_assgnmt[var] = False
            return next_assgnmt
        else:
            return None

def students_in_desired_sessions(student_preferences):
    """
    given a preference dictionary, returns a CNF formula that is the logical equivalent of making sure students are in desired rooms
    """
    formula = []
    for student in student_preferences:
        clause = []
        for room in student_preferences[student]:
            clause += [(student + '_' + room, True)]
        formula += [clause]
    return formula

def one_student_per_room(student_preferences, room_capacities):
    """
    given student prefs and room sizes, returns a CNF formula that is the logical equivalent of making sure each student is only in one room
    """
    formula = []
    rooms = list(room_capacities.keys())
    for student in student_preferences:
        for i in range(len(rooms)):
            for j in range(i+1, len(rooms)):
                clause = []
                r1, r2 = rooms[i], rooms[j]
                clause += [(student + '_' + r1, False), (student + '_' + r2, False)]
                formula += [clause]
    return formula

def student_combos(student_preferences, n):
    """
    given student pref dict and n, returns a list of all subsets (represented as lists) of students of size n
    """
    students = list(student_preferences.keys())
    s = len(students)
    returned = []
    for x in range(2**s):
        binary = bin(x)[2:]
        # if this subset has size n, pad it with leading zeros, make a subset list to populate
        if binary.count('1') == n:
            binary = '0'*(s-len(binary)) + binary
            subset = [students[i] for i in range(s) if binary[i] == '1']
            returned += [subset]
    return returned

def room_capacity_fits(student_preferences, room_capacities):
    """
    given student prefs and room sizes, return a CNF formula that is the logical equivalent of making sure no room is oversubscribed
    """
    s = len(list(student_preferences.keys()))
    formula = []
    for room in room_capacities:
        n = room_capacities[room]
        if n < s:
            student_subsets = student_combos(student_preferences, n+1)
            for group in student_subsets:
                clause = [(student + '_' + room, False) for student in group]
                formula += [clause]
    return formula


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    rule1 = students_in_desired_sessions(student_preferences)
    rule2 = one_student_per_room(student_preferences, room_capacities)
    rule3 = room_capacity_fits(student_preferences, room_capacities)
    return rule1 + rule2 + rule3


if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)

    # f = [
    #     [('a', True), ('b', True), ('c', True)],
    #     [('a', False), ('f', True)],
    #     [('d', False), ('e', True), ('a', True), ('g', True)],
    #     [('h', False), ('c', True), ('a', False), ('f', True)],
    #     ]
    # print(update(f, 'a', True))
    # print(update(update(f, 'a', True), 'f', True))
    # print(update(update(f, 'a', True), 'f', False))

    # cnf = [
    #     [('a', True), ('a', False)], 
    #     [('b', True), ('a', True)], 
    #     [('b', True)], 
    #     [('b', False), ('b', False), ('a', False)], 
    #     [('c', True), ('d', True)], 
    #     [('c', True), ('d', True)]
    #     ]
    # print(satisfying_assignment(cnf))

    # cnf = [
    #     [("a",True),("b",True)], 
    #     [("a",False),("b",False),("c",True)], 
    #     [("b",True),("c",True)], 
    #     [("b",True),("c",False)], 
    #     [("a",False),("b",False),("c",False)]
    #     ]

    # print(satisfying_assignment(cnf))

    # print(update(cnf, 'b', True))

    # print(update([[('a', False), ('a', False), ('a', False)]], 'a', True))

    # should be a false, b true, c true, d doesnt matter


    # print(one_student_per_room({'Alice': {'basement', 'penthouse'},
    #                         'Bob': {'kitchen'},
    #                         'Charles': {'basement', 'kitchen'},
    #                         'Dana': {'kitchen', 'penthouse', 'basement'}},
    #                        {'basement': 1,
    #                         'kitchen': 2,
    #                         'penthouse': 4}

    # ))


    # print(student_combos({'Alice': {'basement', 'penthouse'},
    #                         'Bob': {'kitchen'},
    #                         'Charles': {'basement', 'kitchen'},
    #                         'Dana': {'kitchen', 'penthouse', 'basement'}}, 3))

    # print(room_capacity_fits({'Alice': {'basement', 'penthouse'},
    #                         'Bob': {'kitchen'},
    #                         'Charles': {'basement', 'kitchen'},
    #                         'Dana': {'kitchen', 'penthouse', 'basement'}},
    #                        {'basement': 1,
    #                         'kitchen': 2,
    #                         'penthouse': 4}

    # ))