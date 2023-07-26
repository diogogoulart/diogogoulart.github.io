from random import randint, choice, random

#changes the quantity of the food
def random_mutation(individual, elem_mute_rate=0.2):

    for i in range(len(individual)):

        if random() < elem_mute_rate:
            new_value = randint(0, 50)  # Randomly choose a new value between 0 and 50
            while new_value == individual[i]:
                new_value = randint(0, 50)
                
            individual[i] = new_value
    return individual

def geometric_mutation(individual, elem_mute_rate=0.2, scale_factor=4):
    mutated_individual = individual.copy()

    for i in range(len(mutated_individual)):
        if random() < elem_mute_rate:
            original_value = mutated_individual[i]
            mutated_value = original_value * randint(1 - scale_factor, 1 + scale_factor)
            mutated_individual[i] = mutated_value

    return mutated_individual

# equivalent to variable_size_mutation
def insert_delete_mutation(individual):

    mutated_individual = individual.copy()

    operation = choice(["insert", "delete"])

    if operation == "insert":
        zero_indices = [i for i, val in enumerate(mutated_individual) if val == 0]

        #if there is a food with 0 quanity, add it to the individual - put a quantity
        if zero_indices:
            index_to_add = choice(zero_indices)
            new_value = randint(1, 10)  #Assuming the range of random value is between 1 and 10
            mutated_individual[index_to_add] = new_value

    elif operation == "delete":
        nonzero_indices = [i for i, val in enumerate(mutated_individual) if val > 0]

        #if there is at least a food with quanitty bigger than 0, remove it (change to 0)
        if nonzero_indices:
            index_to_delete = choice(nonzero_indices)
            mutated_individual[index_to_delete] = 0

    return mutated_individual


