#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

# NO IMPORTS ALLOWED!

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION

def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, False, False, False]
        [False, False, False, False]
    state: ongoing
    """
    return new_game_nd((num_rows, num_cols), bombs)

def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['mask'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['mask'][bomb_location] ==
    True), 'victory' when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, True, True, True]
        [False, False, True, True]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    mask:
        [True, True, False, False]
        [False, False, False, False]
    state: defeat
    """

    return dig_nd(game, (row, col))

def render_2d(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring bombs).
    game['mask'] indicates which squares should be visible.  If xray is True (the
    default is False), game['mask'] is ignored and all cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A 2D array (list of lists)

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, xray)

def render_ascii(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function 'render_2d(game)'.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A string-based representation of game

    >>> print(render_ascii({'dimensions': (2, 4),
    ...                     'state': 'ongoing',
    ...                     'board': [['.', 3, 1, 0],
    ...                               ['.', '.', 1, 0]],
    ...                     'mask':  [[True, True, True, False],
    ...                               [False, False, True, False]]}))
    .31_
    __1_
    """
    render = render_2d(game, xray)
    returned = ''
    for r in render:
        for c in r:
            returned += c
        returned += '\n'
    return returned[:-1]



# N-D IMPLEMENTATION

def get_at_loc(board, loc):
    """
    given an N-d array and a tuple/list of coordinates, returns the value at those coordinates in the array.
    """
    if len(loc) == 1:
        return board[loc[0]]
    return get_at_loc(board[loc[0]], loc[1:])

def set_at_loc(board, loc, value):
    """
    given an N-d array and a tuple/list of coordinates, sets the given value at those coordinates in the array. Returns a copy of the array, does not modify in-place.
    """
    if len(loc) == 1:
        board[loc[0]] = value
        return board
    return board[:loc[0]] + [set_at_loc(board[loc[0]], loc[1:], value)] + board[loc[0]+1:]

def create(dims, value):
    """
    given a list of dimensions and a value, creates an Nd array of given dims, populated with that value.
    """
    if len(dims) == 0:
        return value
    return [create(dims[1:], value) for x in range(dims[0])]

def get_neighbors(dims, coord, locs):
    """
    returns all the neighbors of a given list of coordinates in a game with a given dimension
    """
    if len(dims) == 0:
        return locs
    new_locs = [l + (coord[0]+x,) for x in range(-1, 2) for l in locs if 0 <= coord[0]+x < dims[0]]
    return get_neighbors(dims[1:], coord[1:], new_locs)

def get_all_coords(dims, coords):
    """
    returns all possible coordinates in a given dimensions of a board.
    """
    if len(dims) == 0:
        return coords
    new_coords = [c+(x,) for x in range(dims[0]) for c in coords]
    return get_all_coords(dims[1:], new_coords)

def check_for_victory(game):
    """
    return True if set of covered squares is exactly equal to set of bombs, else False
    """
    covered = []
    bombs = []
    mask = game['mask']
    board = game['board']
    for square in get_all_coords(game['dimensions'], [tuple()]):
        if get_at_loc(mask, square) == False:
            covered += [square]
        if get_at_loc(board, square) == '.':
            bombs += [square]
    return set(covered) == set(bombs)

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """
    # use create to make mask
    mask = create(dimensions, False)
    # use create to make board of 0s
    board = create(dimensions, 0)
    # iterate through bombs list and use set_at_loc to set bomb locs to '.' and increment values at neighboring squares
    for b in bombs:
        board = set_at_loc(board, b, '.')
        neighbors = [x for x in get_neighbors(dimensions, b, [tuple()]) if get_at_loc(board, x) != '.']
        for n in neighbors:
            board = set_at_loc(board, n, get_at_loc(board, n) + 1)
    # return game dict
    return {
        'dimensions': dimensions,
        'board' : board,
        'mask' : mask,
        'state': 'ongoing'
        }


def dig_nd(game, coordinates, firsttime=True):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """
    # if game state not 'ongoing' or square already revealed, return 0 and exit
    if game['state'] != 'ongoing' or get_at_loc(game['mask'], coordinates) == True:
        return 0
    # get value at dug loc and update mask
    dug_up = get_at_loc(game['board'], coordinates)
    game['mask'] = set_at_loc(game['mask'], coordinates, True)
    # if bomb, set to defeat
    if dug_up == '.':
        game['state'] = 'defeat'
        return 1
    # if non-0 number, done & return
    if dug_up != 0:
        if firsttime and check_for_victory(game):
            game['state'] = 'victory'
        return 1
    # if 0, 
    #   recursively dig to reveal as many contiguous 0s and their immediate neighbors as possible
    # check for victory
    if dug_up == 0:
        dig_more = [c for c in get_neighbors(game['dimensions'], coordinates, [tuple()]) if get_at_loc(game['mask'], c) == False]
        result = 1 + sum([dig_nd(game, coord, False) for coord in dig_more])
        if firsttime and check_for_victory(game):
            game['state'] = 'victory'
        return result


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares
    neighboring bombs).  The mask indicates which squares should be
    visible.  If xray is True (the default is False), the mask is ignored
    and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    the mask

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [True, True], [True, True]],
    ...               [[False, False], [False, False], [True, True], [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    display_board = create(game['dimensions'], '_')
    for square in get_all_coords(game['dimensions'], [tuple()]):
        uncovered = get_at_loc(game['mask'], square)
        if xray or uncovered:
            real_value = get_at_loc(game['board'], square)
            real_value = ' ' if real_value == 0 else str(real_value)
            display_board = set_at_loc(display_board, square, real_value)
    return display_board


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags) #runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  To do so, comment
    # out the above line, and uncomment the below line of code. This may be
    # useful as you write/debug individual doctests or functions.  Also, the
    # verbose flag can be set to True to see all test results, including those
    # that pass.
    #
    #doctest.run_docstring_examples(render_2d, globals(), optionflags=_doctest_flags, verbose=False)
    
    # print(make_2d_empty_board(2, 4, [(0, 0), (1, 0), (1, 1)]))


    # board1 = [
    #     [0, 0, 1, 1, 2, '.'],
    #     [0, 0, 2, '.', 3, 1],
    #     [1, 1, 2, '.', 2, 0],
    #     ['.', 1, 1, 1, 1, 0],
    #     [1, 1, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0]
    # ]
    # game1= {
    #     'board':
    #     [[3, '.'], [3, 3], [1, 1], [0, 0]],
    #     'dimensions': (2, 4),
    #     'mask':
    #         [[True, False], [False, False], [False, False], [True, True]],
    #     'state': 'ongoing'
    # }
    # print(render_2d(game1))
    # print(get_at_loc(board1, (4,5)))
    # board2 = [0,1,2,3]
    # print(get_at_loc(board2, (2,)))
    # print(set_at_loc(board1, (5,5), 6))

    # print(create((3,4), True))

    # print(get_all_coords((2,3), [tuple()]))

    # print(get_neighbors((10,20,3), (5,13,0), [tuple()]))

    # print(new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)]))

    # print(create((2,3), 0))


    # game = {'dimensions': (2, 4),
    #          'board': [['.', 3, 1, 0],
    #                    ['.', '.', 1, 0]],
    #          'mask': [[False, True, False, False],
    #                   [False, False, False, False]],
    #          'state': 'ongoing'}
    # print(dig_2d(game, 0, 3))
    # print(dump(game))
