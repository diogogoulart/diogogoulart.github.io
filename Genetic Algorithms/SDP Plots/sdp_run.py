import matplotlib.pyplot as plt
from sdp_data import min_nutrients, max_nutrients, data
from charles import Population, Individual
from selection import tournament_selection, ranking_selection ,fps
from mutation import random_mutation, geometric_mutation, insert_delete_mutation
from crossover import single_point_co, uniform_co, multi_point_co, arithmetic_co, geometric_co
from utils import plot_c, print_nutrition
import numpy as np
from random import randrange, uniform

def get_fitness(self):
    """A fitness function that returns the
    price of the food if it meets the requirements, otherwise the fitness gets a penalty
    """
    total_cost = 0
    nutritional_values = [0] * 14  # Initialize nutritional values list with 0s

    for index, quantity in enumerate(self.representation):
        total_cost += quantity * data[index][1]  # Accessing the price of the ingredient at the given index
        for i in range(14):
            nutritional_values[i] +=quantity + data[index][i + 2]  # Accessing and accumulating nutritional values

    # Calculate penalty for not meeting the nutritional requirements

    penalty = 0

    #min nutrients
    for i in range(len(min_nutrients)):
        if nutritional_values[i] < min_nutrients[i][1]:
            nutrient_range = max_nutrients[i][1] - min_nutrients[i][1]
            nutrient_penalty = (min_nutrients[i][1] - nutritional_values[i]) / nutrient_range
            penalty += nutrient_penalty * 500000  # Apply a penalty for each nutrient bellow requirement

    #max nutrients
    for i in range(len(max_nutrients)):
        if nutritional_values[i] > max_nutrients[i][1]:
            nutrient_range = max_nutrients[i][1] - min_nutrients[i][1]
            nutrient_penalty = (nutritional_values[i] - max_nutrients[i][1]) / nutrient_range
            penalty += nutrient_penalty * 5  # Apply a penalty for each nutrient above requirement

    return total_cost + penalty


def random_initialization(self):
    return [randrange(201) for _ in range(58)] #expected quantity of food around 5kg per individual

def initialize_latin_hypercube(self,range_min=0, range_max=200):
    # Divide the range into equal-sized bins
    bin_size = (range_max - range_min) / 58

    # Initialize representation
    representation = []

    # Generate random values for each element using Latin Hypercube Sampling
    for i in range(58):
        # Calculate the range for the current bin
        bin_min = range_min + i * bin_size
        bin_max = range_min + (i + 1) * bin_size

        # Sample a random value from the current bin
        value = uniform(bin_min, bin_max)

        # Append the value to the representation
        representation.append(value)

    return representation

def initialize_goodfoods(self):
   first_good = [randrange(201) for _ in range(35)] #first 35 food are 'good'
   second_bad = [0] * 23 #last 28 foods are 'bad' so lets put them to 0

   return first_good + second_bad



# Monkey Patching
Individual.get_fitness = get_fitness
Individual.initialize = random_initialization


## -------- code to run alg one time ---------- ##

'''pop = Population(size=50,
                 optim="min",
                 sol_size=len(data),
                 valid_set=range(len(data)),
                 replacement=True)

pop.evolve(pop=pop,
           generations=100,
           select=fps,
           mutate= geometric_mutation,
           mutation_rate=0.5,
           crossover= multi_point_co,
           elite_size=2,
           no_improvement_threshold=50,
           plot= None)'''

## -------- code to run alg multipe times ---------- ##
best_fitness_values = []
best_individuals=[]

for _ in range(50):
    pop = Population(size=50,
                 optim="min",
                 sol_size=len(data),
                 valid_set=range(len(data)),
                 replacement=True)

    best_individual, fitness_history= pop.evolve(pop=pop,
                                        generations=300,
                                        select=fps,
                                        mutate= random_mutation,
                                        mutation_rate=0.5,
                                        crossover= multi_point_co,
                                        elite_size=6,
                                        no_improvement_threshold=1000,
                                        plot= None)
    
    # Store the best fitness value for each run
    best_individuals.append(best_individual)
    best_fitness_values.append(fitness_history)

#get best individual
best_individual_fit = [indiv.get_fitness() for indiv in best_individuals]
best_indiv_index = best_individual_fit.index(max(best_individual_fit))
best_indiv = best_individuals[best_indiv_index]

print_nutrition(best_indiv)

mean_fitness = np.mean(best_fitness_values, axis=0)
min_fitness = np.min(best_fitness_values, axis=0)
max_fitness = np.max(best_fitness_values, axis=0)

generations = range(1, len(mean_fitness) + 1)
plt.plot(generations, mean_fitness, label='Mean Best Fitness')
plt.fill_between(generations, min_fitness, max_fitness, alpha=0.3)
plt.xlabel('Generations')
plt.ylabel('Best Fitness')
plt.legend()
plt.show()

