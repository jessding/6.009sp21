import os
import doctest
import time
import traceback

import importlib, importlib.util
from copy import deepcopy
from collections import OrderedDict

# programmatically import buggy implementations

import lab
importlib.reload(lab)

# list different implementations
# called by ui
def list_impls(d):
    return ["lab"]

TESTDOC_FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
def testdoc(target):
    if target == "lab":
        results = doctest.testmod(lab, optionflags=TESTDOC_FLAGS, report=False)
    elif target == "readme":
        results = doctest.testfile("readme.md", optionflags=TESTDOC_FLAGS, report=False)
    return results[0] == 0

def checkdoc(kind):
    tests = doctest.DocTestFinder(exclude_empty=False).find(lab)
    for test in tests:
        if test.name == "lab":
            continue
        if kind == "docstrings" and not test.docstring:
            return "Oh no, '{}' has no docstring!".format(test.name)
        if kind == "doctests" and not test.examples:
            return "Oh no, '{}' has no doctests!".format(test.name)
    return {"docstrings": "All functions are documented; great!",
            "doctests": "All functions have tests; great!"}[kind]

def ui_new_game_2d(d):
    return lab.new_game_2d(d['num_rows'], d['num_cols'], [tuple(i) for i in d['bombs']])

def ui_dig_2d(d):
    game, row, col = d["game"], d["row"], d["col"]
    nb_dug = lab.dig_2d(game, row, col)
    status = game['state']
    return [game, status, nb_dug]

def ui_render_2d(d):
    g = d['game']
    x = d['xray']
    b = g['board']
    m = g['mask']
    r = d['our_renderer']
    if r:
        return [[ '_' if (not x) and (not m[r][c]) else ' ' if b[r][c] == 0 else str(b[r][c]) for c in range(d['num_cols'])] for r in range(d['num_rows'])]
    else:
        try:
            game = d['game']
            r = lab.render_2d(game, x)
        except:
            r = [['ERROR' for i in range(d['num_cols'])] for j in range(d['num_rows'])]
        return r

current_game_nd = None

def ui_new_game_nd(d):
    global current_game_nd
    current_game_nd = lab.new_game_nd(d["dimensions"], [tuple(i) for i in d["bombs"]])
    return

def ui_dig_nd(d):
    coordinates = d["coordinates"]
    nd_dug = lab.dig_nd(current_game_nd, tuple(coordinates))
    status = current_game_nd['state']
    return [status, nd_dug]

def ui_render_nd(d):
    return lab.render_nd(current_game_nd, d['xray'])

