#!/usr/bin/env python3

import pickle

# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for this lab will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).


def transform_data(raw_data):
    """
    transforms data of type [(aid_1, aid_2, film_id)] to 
    actors-indexed dictionary of type {aid1: {(aid2, film_id), }, aid2: {(aid1, film_id), }}
    and film-indexed dictionary of type {film1: {(aid1, aid2), (aid2, aid1)}, film2: }
    """
    db = {}
    filmdb = {}
    for tup in raw_data:
        aid_1, aid_2, film_id = tup
        # add to actor-indexed db
        if aid_1 in db.keys():
            db[aid_1] |= set([(aid_2, film_id)])
        else:
            db[aid_1] = set([(aid_2, film_id)])
        if aid_2 in db.keys():
            db[aid_2] |= set([(aid_1, film_id)])
        # add to film-indexed db
        else:
            db[aid_2] = set([(aid_1, film_id)])
        if film_id in filmdb.keys():
            filmdb[film_id] |= set([(aid_1, aid_2), (aid_2, aid_1)])
        else:
            filmdb[film_id] = set([(aid_1, aid_2), (aid_2, aid_1)])
    return (db, filmdb)


def acted_together(data, actor_id_1, actor_id_2):
    """
    returns if the given two actors have acted together in a film before.
    """
    data = data[0]
    if actor_id_1 == actor_id_2:
        return True
    if actor_id_1 in data.keys() and [x for x in data[actor_id_1] if x[0] == actor_id_2]:
        return True
    if actor_id_2 in data.keys() and [x for x in data[actor_id_2] if x[0] == actor_id_1]:
        return True
    return False


def actors_with_bacon_number(data, n):
    """
    performs BFS, but doesn't include actors we've encountered before in the subsequent level sets.
    Also, returns early if level set is already empty at a smaller bacon number.
    """
    data = data[0]
    bacon = 4724
    level = {bacon}
    seen = {bacon}
    for i in range(n):
        new_level = set()
        for x in level:
            new_level |= set([y[0] for y in data[x] if not y[0] in seen])
        level = new_level
        seen |= new_level
        if not new_level:
            return set()
    return level

def bacon_path(data, actor_id):
    # use actor_to_actor_path since it's more general
    return actor_to_actor_path(data, 4724, actor_id)


def actor_to_actor_path(data, actor_id_1, actor_id_2):
    '''
    essentially implements BFS, WLOG from id1 to id2
    '''
    data = data[0]
    if actor_id_1 not in data.keys() or actor_id_2 not in data.keys():
        return None
    if actor_id_1 == actor_id_2:
        return [actor_id_1]
    bacon = actor_id_1
    level = {(bacon,)}
    seen = set()
    while True:
        next_level = set()
        for path in level:
            latest_id = path[-1]
            next_actors = [x[0] for x in data[latest_id]]
            if actor_id_2 in next_actors:
                return list( path + (actor_id_2,) )
            for x in next_actors:
                if x not in seen:
                    next_level |= set([ path + (x,) ])
                seen |= {x}
        if not next_level:
            return None
        level = next_level

def actors_with_bfs_number(data, n, actor_id):
    """
    performs BFS, but doesn't include actors we've encountered before in the subsequent level sets.
    Also, returns early if level set is already empty at a smaller bacon number.
    """
    data = data[0]
    bacon = actor_id
    level = {bacon}
    seen = {bacon}
    for i in range(n):
        new_level = set()
        for x in level:
            new_level |= set([y[0] for y in data[x] if not y[0] in seen])
        level = new_level
        seen |= new_level
        if not new_level:
            return set()
    return level

def actor_path(data, actor_id_1, goal_test_function):
    '''
    does BFS in steps of level sets, and returns the path of the shortest length 
    for the first actor that satisfies goal test function.
    '''
    for n in range(len(data[0])):
        dist_set = actors_with_bfs_number(data, n, actor_id_1)
        if not dist_set:
            return None
        for actor in dist_set:
            if goal_test_function(actor):
                return actor_to_actor_path(data, actor_id_1, actor)
    return None


def actors_connecting_films(data, film1, film2):
    actordb, filmdb = data
    if film1 not in filmdb.keys() or film2 not in filmdb.keys():
        return None
    #level is {(a1,), (a2,), (a3,), }, is a set of actor paths
    # wlog, go from film1 to film2
    level = set([(x[0],) for x in filmdb[film1]])
    # actors_seen is set of actors we have come across already
    actors_seen = set()
    # implement BFS, consider every node as 'split' with two parts - related movie and actors
    while True:
        next_level = set()
        for path in level:
            aid = path[-1]
            next_actors = set()
            for x in actordb[aid]:
                if film2 == x[1]:
                    return path
                if x[0] not in actors_seen:
                    next_actors |= set([x[0]])
                actors_seen |= next_actors
            next_level |= set([ path + (x,) for x in next_actors ])            
        if not next_level:
            return None
        level = next_level


if __name__ == '__main__':
    with open('resources/small.pickle', 'rb') as f:
        smalldb = pickle.load(f)

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.


    # with open('resources/names.pickle', 'rb') as f:
    #     namesdb = pickle.load(f)
    #     for name, id in namesdb.items():
    #         if id == 107939:
    #             print(name)

    # with open('resources/tiny.pickle', 'rb') as f:
    #     tinydb = transform_data(pickle.load(f))
    #     ids = actors_with_bacon_number(tinydb, 3)


    # with open('resources/large.pickle', 'rb') as f:
    #     largedb = transform_data(pickle.load(f))
    #     ids = actors_with_bacon_number(largedb, 6)
    #     names = set()
    #     with open('resources/names.pickle', 'rb') as f:
    #         namesdb = pickle.load(f)
    #         for id in ids:
    #             names |= {list(namesdb.keys())[list(namesdb.values()).index(id)]}
    # print(names)

    # with open('resources/tiny.pickle', 'rb') as f:
    #     tinydb = transform_data(pickle.load(f))
    #     print(bacon_path(tinydb, 1640))


    # with open('resources/names.pickle', 'rb') as f:
    #     namesdb = pickle.load(f)
    #     with open('resources/large.pickle', 'rb') as f:
    #         largedb = transform_data(pickle.load(f))
    #         a_id = namesdb['Jack Hoxie']
    #         ids = bacon_path(largedb, a_id)
    #         names = []
    #         for id in ids:
    #             names += [list(namesdb.keys())[list(namesdb.values()).index(id)]]
    # print(names)

    # with open('resources/names.pickle', 'rb') as f:
    #     namesdb = pickle.load(f)
    #     with open('resources/large.pickle', 'rb') as f:
    #         largedb = transform_data(pickle.load(f))
    #         a_id_1 = namesdb['Lionel Belmore']
    #         a_id_2 = namesdb['Wilmer Valderrama']
    #         print(a_id_1, a_id_2)
    #         ids = actor_to_actor_path(largedb, a_id_1, a_id_2)
    #         print(ids)
    #         names = []
    #         for id in ids:
    #             names += [list(namesdb.keys())[list(namesdb.values()).index(id)]]
    # print(names)


    # with open('resources/movies.pickle', 'rb') as f:
    #     moviesdb = pickle.load(f)
    #     with open('resources/names.pickle', 'rb') as f:
    #         namesdb = pickle.load(f)
    #         with open('resources/large.pickle', 'rb') as f:
    #             largedb = transform_data(pickle.load(f))
    #             a_id_1 = namesdb['Curtis Hanson']
    #             a_id_2 = namesdb['Vjeran Tin Turk']
    #             print(a_id_1, a_id_2)
    #             ids = actor_to_actor_path(largedb, a_id_1, a_id_2)
    #             movies = []
    #             for i in range(1, len(ids)):
    #                 for d in largedb[ids[i-1]]:
    #                     if d[0] == ids[i]:
    #                         movies += [d[1]]
    #             print(ids)
    #             movie_names = []
    #             for m in movies:
    #                 movie_names += [list(moviesdb.keys())[list(moviesdb.values()).index(m)]]
    # print(movie_names)

    
