from time import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from charles import Population, Individual
from sdp_data import data, min_nutrients, max_nutrients
from sdp_run import get_fitness, random_initialization, initialize_latin_hypercube, initialize_goodfoods

from selection import fps
from mutation import random_mutation
from crossover import single_point_co

results = pd.DataFrame(columns=['Initialization Method', 'Time Elapsed', 'Final Fitness', 'Final Cost',
                                'Number of Iterations', 'Final Quantity', 'Number of Requirements met'])

init_methods =[random_initialization, initialize_latin_hypercube, initialize_goodfoods]
init_names= ['Random', 'Latin Hypercube Sampling', 'Good Foods']

Individual.get_fitness = get_fitness

# Lists to store fitness values for each iteration
random_fitness_values = []
latin_fitness_values = []
goodfoods_fitness_values = []

for i in range(3):
    print(init_names[i])
    Individual.initialize = init_methods[i]
    for _ in range(50):
        pop = Population(size=50,
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
                                                     crossover=single_point_co,
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
        row_data = {'Initialization Method': init_names[i],
                    'Time Elapsed': end_time - start_time,
                    'Final Fitness': final_fitness,
                    'Final Cost': final_cost,
                    'Number of Iterations': num_iterations,
                    'Final Quantity': final_qnt_ingredients,
                    'Number of Requirements met': num_requirements_met}

        results = pd.concat([results, pd.DataFrame(row_data, index=[0])], ignore_index=True)

        # Save fitness values at each iteration
        if init_methods[i] == random_initialization:
            random_fitness_values.append(fitness_history)
        elif init_methods[i] == initialize_latin_hypercube:
            latin_fitness_values.append(fitness_history)
        elif init_methods[i] == initialize_goodfoods:
            goodfoods_fitness_values.append(fitness_history)

print(results.head(5))
results.to_csv('results.csv', index=False)

df = pd.read_csv('results.csv')
print(df.head(5))

# List of metrics you want to observe
metrics = ['Time Elapsed', 'Final Fitness', 'Final Cost', 'Number of Iterations', 'Final Quantity', 'Number of Requirements met']

# Create a figure and an axis
fig, ax = plt.subplots(figsize=(10, 6))


# Calculate the mean fitness values 
random_mean_fitness = np.mean(random_fitness_values, axis=0)
latin_mean_fitness = np.mean(latin_fitness_values, axis=0)
goodfoods_mean_fitness = np.mean(goodfoods_fitness_values, axis=0)

# Calculate the minimum and maximum fitness values 
random_min_fitness = np.min(random_fitness_values, axis=0)
random_max_fitness = np.max(random_fitness_values, axis=0)
latin_min_fitness = np.min(latin_fitness_values, axis=0)
latin_max_fitness = np.max(latin_fitness_values, axis=0)
goodfoods_min_fitness = np.min(goodfoods_fitness_values, axis=0)
goodfoods_max_fitness = np.max(goodfoods_fitness_values, axis=0)

# Plot the line chart and fill the range for random
ax.plot(range(len(random_mean_fitness)), random_mean_fitness, label='Random')
ax.fill_between(range(len(random_mean_fitness)), random_min_fitness, random_max_fitness, alpha=0.3)

# Plot the line chart for geometric crossover
ax.plot(range(len(latin_mean_fitness)), latin_mean_fitness, label='Latin Hypercube Sampling')
ax.fill_between(range(len(latin_mean_fitness)), latin_min_fitness, latin_max_fitness, alpha=0.3)

# Plot the line chart for geometric crossover
ax.plot(range(len(goodfoods_mean_fitness)), goodfoods_mean_fitness, label='Good Foods')
ax.fill_between(range(len(goodfoods_mean_fitness)), latin_min_fitness, latin_max_fitness, alpha=0.3)

# Set the x-axis label
ax.set_xlabel('Generations')

# Set the y-axis label
ax.set_ylabel('Mean Best Fitness')

# Set the title
ax.set_title('Mean Best Fitness Progression')

# Add a legend
ax.legend()

# Show the plot
plt.show()