from time import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from charles import Population, Individual
from sdp_data import data, min_nutrients, max_nutrients
from sdp_run import get_fitness

from selection import fps
from mutation import random_mutation
from crossover import multi_point_co

results = pd.DataFrame(columns=['Population Size', 'Time Elapsed', 'Final Fitness', 'Final Cost',
                                'Number of Iterations', 'Final Quantity', 'Number of Requirements met'])

population_sizes = [50, 100, 150, 200, 250]

Individual.get_fitness = get_fitness

fitness_values = []

for pop_size in population_sizes:
    print("Population Size:", pop_size)
    pop_fitness_values = []  # Store fitness values for each run
    for _ in range(50):
        pop = Population(size=pop_size,
                         optim="min",
                         sol_size=len(data),
                         valid_set=range(len(data)),
                         replacement=True)
        start_time = time()
        best_individual, fitness_history = pop.evolve(pop=pop,
                                                     generations=300,
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
        nutritional_values = [0] * 15

        # Calculate nutritional values and other metrics
        for index, quantity in enumerate(best_individual.representation):
            for j in range(15):
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
        row_data = {'Population Size': pop_size,
                    'Time Elapsed': end_time - start_time,
                    'Final Fitness': final_fitness,
                    'Final Cost': final_cost,
                    'Number of Iterations': num_iterations,
                    'Final Quantity': final_qnt_ingredients,
                    'Number of Requirements met': num_requirements_met}

        results = pd.concat([results, pd.DataFrame(row_data, index=[0])], ignore_index=True)

        # Save fitness values at each iteration
        pop_fitness_values.append(fitness_history)

    fitness_values.append(pop_fitness_values)

print(results.head(5))
results.to_csv('results.csv', index=False)

# Calculate the mean fitness values for each population size
mean_fitness_values = [np.mean(fitness, axis=0) for fitness in fitness_values]
min_fitness_values = [np.min(fitness, axis=0) for fitness in fitness_values]
max_fitness_values = [np.max(fitness, axis=0) for fitness in fitness_values]

# Create a figure and an axis
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the line chart for each population size
for i, pop_size in enumerate(population_sizes):
    ax.plot(range(len(mean_fitness_values[i])), mean_fitness_values[i], label=f'Population Size {pop_size}')
    ax.fill_between(range(len(mean_fitness_values[i])), min_fitness_values[i], max_fitness_values[i], alpha=0.1)

# Set the x-axis label
ax.set_xlabel('Generations')

# Set the y-axis label
ax.set_ylabel('Mean Best Fitness')

# Set the title
ax.set_title('Mean Best Fitness Progression for Different Population Sizes')

# Add a legend
ax.legend()

# Show the plot
plt.show()





