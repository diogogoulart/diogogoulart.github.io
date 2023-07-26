from random import uniform, choices, sample

def fps(population):
    '''Fitness Proportional selection Implementation'''
    total_fitness = sum([i.fitness for i in population])
    spin = uniform(0, total_fitness)
    position = 0
    for individual in population:
        position += individual.fitness
        if position > spin:
            return individual

def ranking_selection(population):
    sorted_pop = sorted(population, key=lambda x: x.fitness)
    fitness_sum = sum(i for i in range(1, len(population) + 1))
    probabilities = [i/fitness_sum for i in range(1, len(population) + 1)]
    winner = choices(sorted_pop, weights=probabilities,k=1)
    return winner[0]


def tournament_selection(population, tournament_size=2):
    participants = sample(list(population), tournament_size)
    winner = min(participants, key=lambda x: x.fitness)
    return winner


