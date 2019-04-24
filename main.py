import json

def get_weighted_vectors():
    unweighted_vectors = get_unweighted_vectors()
    weighted_vectors = {}

    for food in unweighted_vectors:
        vector = unweighted_vectors[food]

        ingredients = [ingredient[0] for ingredient in vector]
        weights = get_weights(ingredients)
        
        ingredients_and_weights = zip(ingredients, weights)
        
        weighted_vectors[food] = {ingredient: int(weight * 1000) for ingredient, weight in ingredients_and_weights}

    return weighted_vectors

def get_weights(ingredients, dropoff_value=1.2):
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

def get_unweighted_vectors():
    s = read_file('food.json')
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

def main():
    print get_weighted_vectors()

if __name__ == '__main__':
    main()