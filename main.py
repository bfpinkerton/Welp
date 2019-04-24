import json
import random
import sys

def get_weighted_vectors(filename):
    unweighted_vectors = get_unweighted_vectors(filename)
    weighted_vectors = {}

    for food in unweighted_vectors:
        vector = unweighted_vectors[food]

        ingredients = [ingredient[0] for ingredient in vector]
        weights = get_weights(ingredients)
        
        ingredients_and_weights = zip(ingredients, weights)
        
        weighted_vectors[food] = {ingredient: int(weight * 1000) for ingredient, weight in ingredients_and_weights}

    return weighted_vectors

def get_weights(ingredients, dropoff_value=3.0):
    """ Returns a list containing the weight of the ingredients in order.
    """
    weights = []
    total = 100

    for _ in ingredients:
        weights.append(total)
        total /= float(dropoff_value)

    s = sum(weights)
    weights = [w / s for w in weights]

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

def get_distance(vector1, vector2):
    distance = 0

    for term in vector1.keys() + vector2.keys(): 
        distance += (vector1.get(term, 0) - vector2.get(term, 0)) ** 2

    return distance

def get_average_distance_from_centroids(vector, centroids_vectors):
    total = 0.0

    for centroid in centroids_vectors:
        total += get_distance(vector, centroid)

    return total / len(centroids_vectors)

def get_centroids(weighted_vectors, number_of_centroids):
    centroids = [weighted_vectors.keys()[0]]

    while len(centroids) != number_of_centroids:
        potential_centroids = {}

        for food in list(set(weighted_vectors.keys()) - set(centroids)):
            vector = weighted_vectors[food]
            centroids_vectors = [weighted_vectors[centroid_food] for centroid_food in centroids]
            average_distance_from_centroids = get_average_distance_from_centroids(vector, centroids_vectors)
            potential_centroids[average_distance_from_centroids] = food

        max_value = max(potential_centroids.keys())
        
        centroids.append(potential_centroids[max_value])

    return sorted(centroids)

def get_centroid_for_document(document_vector, centroids_vectors):
    distances = {}

    for centroid_food in centroids_vectors:
        distance = get_distance(document_vector, centroids_vectors[centroid_food])
        distances[distance] = centroid_food

    centroid = distances[min(distances.keys())]

    return centroid

def main():
    cluster_size = 10

    weighted_vectors = get_weighted_vectors(sys.argv[1])

    centroids = get_centroids(weighted_vectors, len(weighted_vectors) / cluster_size)
    centroids_vectors = {centroid: weighted_vectors[centroid] for centroid in centroids}
    centroids_to_clusters = {centroid: [] for centroid in centroids}

    for food in weighted_vectors:
        centroid = get_centroid_for_document(weighted_vectors[food], centroids_vectors)
        centroids_to_clusters[centroid].append(food)

    clusters = [centroids_to_clusters[centroid] for centroid in centroids_to_clusters]

    print json.dumps(clusters, indent=4)

if __name__ == '__main__':
    main()