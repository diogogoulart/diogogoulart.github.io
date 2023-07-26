from time import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from charles import Population, Individual
from sdp_data import data, min_nutrients, max_nutrients
from sdp_run import random_initialization

from selection import fps
from mutation import random_mutation
from crossover import multi_point_co

results = pd.DataFrame(columns=['Penalty Size', 'Time Elapsed', 'Final Fitness', 'Final Cost',
                                'Number of Iterations', 'Final Quantity', 'Number of Requirements met'])

penalty_sizes = [0.001, 0.1, 10, 10000, 50000, 100000, 500000]

fitness_values = []

Individual.initialize = random_initialization

for penalty_size in penalty_sizes:
    print("Penalty Size:", penalty_size)

    elite_fitness_values = []  # Store fitness values for each run

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
                penalty += nutrient_penalty * penalty_size  # Apply a penalty for each nutrient bellow requirement

        #max nutrients
        for i in range(len(max_nutrients)):
            if nutritional_values[i] > max_nutrients[i][1]:
                nutrient_range = max_nutrients[i][1] - min_nutrients[i][1]
                nutrient_penalty = (nutritional_values[i] - max_nutrients[i][1]) / nutrient_range
                penalty += nutrient_penalty * 5  # Apply a penalty for each nutrient above requirement

        return total_cost + penalty

    Individual.get_fitness = get_fitness  # Monkey patch the get_fitness method

    for _ in range(3):
        pop = Population(size=10,
                         optim="min",
                         sol_size=len(data),
                         valid_set=range(len(data)),
                         replacement=True)
        start_time = time()
        best_individual, fitness_history = pop.evolve(pop=pop,
                                                     generations=100,
                                                     select=fps,
                                                     mutate=random_mutation,
                                                     mutation_rate=0.5,
                                                     crossover=multi_point_co,
                                                     elite_size=2,
                                                     no_improvement_threshold=1000,
                                                     plot=None)
        end_time = time()

        # Initialize counts and metrics
        num_requirements_met = 0
        final_cost = 0
        nutritional_values = [0] * 14

        # Calculate nutritional values and other metrics
        for index, quantity in enumerate(best_individual.representation):
            for j in range(14):
                nutritional_values[j] += data[index][j + 2] * quantity

                if quantity > 0:
                    final_cost += data[index][1] * quantity

        for j, (nutrient, min_req) in enumerate(min_nutrients):
            if min_nutrients[j][1] <= nutritional_values[j] <= max_nutrients[j][1]:
                num_requirements_met += 1

        final_fitness = best_individual.get_fitness()  
        num_iterations = len(fitness_history)
        final_qnt_ingredients = sum(best_individual.representation)

        # Append a row to the DataFrame
        row_data = {'Penalty Size': penalty_size,
                    'Time Elapsed': end_time - start_time,
                    'Final Fitness': final_fitness,
                    'Final Cost': final_cost,
                    'Number of Iterations': num_iterations,
                    'Final Quantity': final_qnt_ingredients,
                    'Number of Requirements met': num_requirements_met}

        results = pd.concat([results, pd.DataFrame(row_data, index=[0])], ignore_index=True)

        # Save fitness values at each iteration
        elite_fitness_values.append(fitness_history)

    fitness_values.append(elite_fitness_values)

print(results.head(5))
results.to_csv('results.csv', index=False)

# List of metrics you want to observe
metrics = ['Time Elapsed', 'Final Fitness', 'Final Cost', 'Number of Iterations', 'Final Quantity', 'Number of Requirements met']

# Create a figure and a grid of axes
fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(15, 15))

# Create a boxplot for each metric
for ax, metric in zip(axs.flatten(), metrics):
    sns.boxplot(x='Penalty Size', y=metric, data=results, ax=ax)
    ax.set_xlabel('')  # Remove x-axis title


# To prevent overlapping of the labels and titles
plt.tight_layout()
plt.show()
