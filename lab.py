import pickle

def check_dic(dic, key, value):
    """
    Given a dictionary, mutates dictionary if value not at key.
    """
    if value not in dic[key]:
        dic[key].add(value)

def transform_data(raw_data):
    """
    Given raw data as a list of tuples in the form (actor_id_1, actor_id_2, film_id),
    returns a dictionary in the form:

    ex: {'actors': {parent_actor: {actor_1, actor_2, ...}, parent_actor:
    {actor_1]}..}, 'movies_and_who_with': {actor: {(film, actor),
    (film, actor), }}, 'movies': {movie: {actor, actor}}}
    """
    acted_with = {}
    movies_and_who_with = {}
    movies = {}
    for tup in raw_data:
        acted_with.setdefault(tup[0], {tup[0]})
        acted_with.setdefault(tup[1], {tup[1]})
        check_dic(acted_with, tup[0], tup[1])
        check_dic(acted_with, tup[1], tup[0])

        movies_and_who_with.setdefault(tup[0], {(tup[2], tup[0])})
        movies_and_who_with.setdefault(tup[1], {(tup[1], tup[0])})
        check_dic(movies_and_who_with, tup[0], (tup[2], tup[1]))
        check_dic(movies_and_who_with, tup[1], (tup[2], tup[0]))

        if tup[2] not in movies:
            movies[tup[2]] = {tup[0], tup[1]}
        elif tup[1] not in movies[tup[2]]:
            movies[tup[2]].add(tup[1])
        elif tup[0] not in movies[tup[2]]:
            movies[tup[2]].add(tup[0])

    return {"actors": acted_with,
            "movies_and_who_with": movies_and_who_with,
            "movies": movies}

def acted_together(transformed_data, actor_id_1, actor_id_2):
    """
    Given transformed_data in the format:
        ex: {'actors': {parent_actor: {actor_1, actor_2, ...}, parent_actor:
        {actor_1]}..}, 'movies_and_who_with': {actor: {(film, actor),
        (film, actor), }}, 'movies': {movie: {actor, actor}}}
    and two actor IDS, returns True if the two actors acted together, and
    False if not.

    """
    transformed_data = transformed_data["actors"]
    if actor_id_2 in transformed_data[actor_id_1]:
        return True
    return False

def actors_with_bacon_number(transformed_data, n):
    """
    Given transformed_data in the format:
        ex: {'actors': {parent_actor: {actor_1, actor_2, ...}, parent_actor:
        {actor_1]}..}, 'movies_and_who_with': {actor: {(film, actor),
        (film, actor), }}, 'movies': {movie: {actor, actor}}}
    and a Bacon number n >= 0, returns a set of all actors IDs with that
    Bacon number.
    """
    return actors_with_bacon_number_general(transformed_data, 4724, n)

def actors_with_bacon_number_general(transformed_data, actor_id, n):
    """
    Given transformed_data in the format:
        ex: {'actors': {parent_actor: {actor_1, actor_2, ...}, parent_actor:
        {actor_1]}..}, 'movies_and_who_with': {actor: {(film, actor),
        (film, actor), }}, 'movies': {movie: {actor, actor}}}
    a actor_id of the person who is "Bacon", and a Bacon number n >= 0,
    returns a set of all actors IDs with that Bacon number from actor_id.
    """
    transformed_data = transformed_data["actors"]
    if n>len(transformed_data):
        return set()
    if n == 0:
        return {actor_id}
    checked_actors = {actor_id}
    parent_actors = transformed_data[actor_id] #Set of actors with Bacon 1
    parent_actors = list(parent_actors)

    #Bacon number 1 list
    parent_actors = {parent for parent in parent_actors if parent != actor_id}
    while n>1:
        new_parents = set()
        for parent in parent_actors: #for all actors of previous Bacon number
            if parent not in checked_actors:
                for child in transformed_data[parent]:
                    if child not in checked_actors and child not in parent_actors:
                        new_parents.add(child)
        checked_actors = checked_actors.union(parent_actors)
        parent_actors = new_parents
        n -= 1
    return set(parent_actors)

def bacon_path(transformed_data, actor_id):
    """
    Given transformed_data in the format:
        ex: {'actors': {parent_actor: {actor_1, actor_2, ...}, parent_actor:
        {actor_1]}..}, 'movies_and_who_with': {actor: {(film, actor),
        (film, actor), }}, 'movies': {movie: {actor, actor}}}
    and an actor_id, returns a list detailing the shortest Bacon path from
    Bacon to the actor, or None if no path exists
    """

    return actor_to_actor_path(transformed_data, 4724, actor_id)

def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    """
    Given transformed_data in the format:
        ex: {'actors': {parent_actor: {actor_1, actor_2, ...}, parent_actor:
        {actor_1]}..}, 'movies_and_who_with': {actor: {(film, actor),
        (film, actor), }}, 'movies': {movie: {actor, actor}}}
    and two actor IDs, returns a list detailing the shortest path from the
    first actor to the second.
    """
    count = 0
    var = True
    bacons = {} # in the format {bacon number: {actors w/ bacon num}}
    while var:
        actors = actors_with_bacon_number_general(transformed_data,
                                                  actor_id_1,
                                                  count)
        bacons[count] = actors
        if actor_id_2 in actors:
            var = False
        if len(actors) == 0:
            return None
        count += 1
    cur_actor = actor_id_2
    path = [actor_id_2]
    transformed_data = transformed_data["actors"]
    #compare higher bacon number to actors actor_id worked with
    count -= 2
    while count >= 0:
        worked_with = transformed_data[cur_actor] #set of actors actor worked with
        bacon_actors = bacons[count]
        intersect = worked_with.intersection(bacon_actors)
        cur_actor = next(iter(intersect))
        path.insert(0, cur_actor)
        count -= 1

    return path

def movie_path(transformed_data, actor_id_1, actor_id_2):
    """
    Given transformed_data in the format:
        ex: {'actors': {parent_actor: {actor_1, actor_2, ...}, parent_actor:
        {actor_1]}..}, 'movies_and_who_with': {actor: {(film, actor),
        (film, actor), }}, 'movies': {movie: {actor, actor}}}
    and two actor IDs, returns a list detailing the shortest path of movies
    from the first actor to the second.
    """
    short_movie_path = []
    path = actor_to_actor_path(transformed_data, actor_id_1, actor_id_2)
    movie_data = transformed_data["movies_and_who_with"]
    for index in range(len(path)-1):
        actor_1 = path[index]
        actor_2 = path[index+1]
        movies = movie_data[actor_1]
        for tup in list(movies):
            if tup[1] == actor_2:
                short_movie_path.append(tup[0])
                break
    return short_movie_path

def actor_path(transformed_data, actor_id_1, goal_test_function):
    """
    Given transformed_data in the format:
        ex: {'actors': {parent_actor: {actor_1, actor_2, ...}, parent_actor:
        {actor_1]}..}, 'movies_and_who_with': {actor: {(film, actor),
        (film, actor), }}, 'movies': {movie: {actor, actor}}}
    and a starting point of actor_id_1, and a goal test function the ending
    actor should satisfy, returns the shortest path between these two actors
    as a list.
    """
    count = 0
    var = True
    while var:
        actors = actors_with_bacon_number_general(transformed_data,
                                                  actor_id_1,
                                                  count)
        if len(actors) == 0:
            var = False
        for actor in actors:
            if goal_test_function(actor):
                path = actor_to_actor_path(transformed_data, actor_id_1, actor)
                return path
        count += 1
    return None

def actors_connecting_films(transformed_data, film1, film2):
    """
    Given transformed_data in the format:
        ex: {'actors': {parent_actor: {actor_1, actor_2, ...}, parent_actor:
        {actor_1]}..}, 'movies_and_who_with': {actor: {(film, actor),
        (film, actor), }}, 'movies': {movie: {actor, actor}}}
    and two film IDs, returns the shortest path of actor IDs that connects
    the two films.
    """
    #returns True is actor_id is in film2, False if not
    def in_film2(actor_id):
        if actor_id in transformed_data["movies"][film2]:
            return True
        return False

    film1_actors = transformed_data["movies"][film1]
    path = actor_path(transformed_data, next(iter(film1_actors)), in_film2)
    for actor in film1_actors:
        new_path = actor_path(transformed_data, actor, in_film2)
        if (new_path is not None) and len(path) > len(new_path):
            path = new_path
    if len(path) == 0:
        return None
    return path

if __name__ == "__main__":
    with open("resources/small.pickle", "rb") as f:
        smalldb = pickle.load(f)
    with open("resources/names.pickle", "rb") as f:
        names = pickle.load(f)
    with open("resources/tiny.pickle", "rb") as f:
        tiny = pickle.load(f)
    with open("resources/large.pickle", "rb") as f:
        large = pickle.load(f)
    with open("resources/movies.pickle", "rb") as f:
        movies_list = pickle.load(f)

    #example usage
    data = transform_data(tiny)
    print(data)
    print(actors_connecting_films(data, 617, 74881))

    #MOVIE PATHS
    # largedb = transform_data(large)
    # print(movie_path(largedb, names["Richard Pierson"], names["Anton Radacic"]))
    # path = movie_path(largedb, names["Richard Pierson"], names["Anton Radacic"])
    # for i in path:
    #     index = list(movies_list.values()).index(i)
    #     print(list(movies_list.keys())[index])

    #BACON PATH
    # largedb = transform_data(large)
    # print(bacon_path(largedb, names["Jesus Castejon"]))
    # paths = bacon_path(largedb, names["Jesus Castejon"])
    # for i in paths:
    #     index = list(names.values()).index(i)
    #     print(list(names.keys())[index])

    #ARBITRARY PATHS
    # largedb = transform_data(large)
    # print(actor_to_actor_path(largedb, names["Louise Brooks"],
    # names["Matthew Macfadyen"]))
    # paths = actor_to_actor_path(largedb, names["Louise Brooks"],
    # names["Matthew Macfadyen"])
    # for i in paths:
    #     index = list(names.values()).index(i)
    #     print(list(names.keys())[index])
