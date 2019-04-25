import json
import math
import sys

def remove_unique_ingredients(vector, unique_ingredients):
    return [ingredient for ingredient in vector if ingredient not in unique_ingredients]

def get_weighted_vectors(filename):
    unweighted_vectors = get_unweighted_vectors(filename)

    ingredients = [ingredient for ingredient in unweighted_vectors.values()]
    ingredients = [ingredient[0] for recipe_ingredients in ingredients for ingredient in recipe_ingredients]
    
    unique_ingredients = {}
    for ingredient in ingredients:
        if ingredient in unique_ingredients:
            unique_ingredients[ingredient] += 1
        else:
            unique_ingredients[ingredient] = 1

    unique_ingredients = set(ingredient for ingredient in unique_ingredients if unique_ingredients[ingredient] == 1)

    unweighted_vectors = {food: remove_unique_ingredients(unweighted_vectors[food], unique_ingredients) for food in unweighted_vectors}

    weighted_vectors = {}

    for food in unweighted_vectors:
        vector = unweighted_vectors[food]

        ingredients = [ingredient[0] for ingredient in vector]
        weights = get_weights(ingredients)
        
        ingredients_and_weights = zip(ingredients, weights)
        
        weighted_vectors[food] = {ingredient: int(weight * 1000) for ingredient, weight in ingredients_and_weights}

    return weighted_vectors

def get_weights(ingredients):
    """ Returns a list containing the weight of the ingredients in order.
    """
    weights = []

    for i, _ in enumerate(ingredients):
        weights.append(1 / math.log((i + 1.1)))

    return weights

def normalize_term(term):
    return term.lower().strip()

def get_unweighted_vectors(filename):
    s = read_file(filename)
    j = get_json(s)

    # we want to preserve the order so we use a list
    for food in j:
        j[food] = [(normalize_term(ingredient), 1) for ingredient in j[food].split(',')]

    j = {normalize_term(food): j[food] for food in j}

    return j

def read_file(filename):
    f = open(filename, 'r')
    s = f.read()
    f.close()
    return s

def get_json(string):
    return json.loads(string)

def get_distance(vector1_name, vector1, vector2_name, vector2):
    distance = 0

    for term in vector1.keys() + vector2.keys(): 
        d = (vector1.get(term, 0) - vector2.get(term, 0)) ** 2
        distance += d ** 0.7

    if all(term not in vector2.keys() for term in vector1.keys()):
        distance *= 10000000

    food1_name = [normalize_term(term) for term in vector1_name.split()]
    food2_name = [normalize_term(term) for term in vector2_name.split()]

    for term in food1_name:
        if term in food2_name:
            distance ** 0.1

    return distance

def get_average_distance_from_centroids(vector_name, vector, centroids_vectors):
    total = 0.0

    for centroid_name in centroids_vectors:
        total += get_distance(vector_name, vector, centroid_name, centroids_vectors[centroid_name])

    return total / len(centroids_vectors)

def get_centroids(weighted_vectors, number_of_centroids):
    centroids = [weighted_vectors.keys()[0]]

    while len(centroids) != number_of_centroids:
        potential_centroids = {}

        for food in list(set(weighted_vectors.keys()) - set(centroids)):
            vector = weighted_vectors[food]
            centroids_vectors = {centroid_food: weighted_vectors[centroid_food] for centroid_food in centroids}
            average_distance_from_centroids = get_average_distance_from_centroids(food, vector, centroids_vectors)
            potential_centroids[average_distance_from_centroids] = food

        max_value = max(potential_centroids.keys())
        
        centroids.append(potential_centroids[max_value])

    return sorted(centroids)

def get_centroid_for_document(vector_name, vector, centroids_vectors):
    distances = {}

    for centroid_food in centroids_vectors:
        distance = get_distance(vector_name, vector, centroid_food, centroids_vectors[centroid_food])
        distances[distance] = centroid_food

    centroid = distances[min(distances.keys())]

    return centroid

def get_clusters_with_ingredients(centroids_to_clusters, filename):
    s = read_file(filename)
    j = get_json(s)

    for food in j:
        j[food] = [normalize_term(ingredient) for ingredient in j[food].split(',')]

    j = {normalize_term(food): j[food] for food in j}

    clusters_with_ingredients = []

    for centroid in centroids_to_clusters:
        c = []
        for item in centroids_to_clusters[centroid]:
            c.append('{:<50}: {}'.format(item, ', '.join(j[item])))
        clusters_with_ingredients.append({centroid: c})

    return clusters_with_ingredients

def main():
    cluster_size = 6

    weighted_vectors = get_weighted_vectors(sys.argv[1])

    centroids = get_centroids(weighted_vectors, len(weighted_vectors) / cluster_size)
    centroids_vectors = {centroid: weighted_vectors[centroid] for centroid in centroids}
    centroids_to_clusters = {centroid: [] for centroid in centroids}

    for food in weighted_vectors:
        centroid = get_centroid_for_document(food, weighted_vectors[food], centroids_vectors)
        centroids_to_clusters[centroid].append(food)

    # clusters = [centroids_to_clusters[centroid] for centroid in centroids_to_clusters]

    clusters_with_ingredients = get_clusters_with_ingredients(centroids_to_clusters, sys.argv[1])

    print json.dumps(clusters_with_ingredients, indent=4)

if __name__ == '__main__':
    main()