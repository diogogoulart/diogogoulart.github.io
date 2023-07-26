from time import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import csv

from charles import Population, Individual
from sdp_data import data, min_nutrients, max_nutrients
from sdp_run import get_fitness

from selection import fps, ranking_selection, tournament_selection
from mutation import insert_delete_mutation, random_mutation
from crossover import arithmetic_co, geometric_co, single_point_co

results = pd.DataFrame(columns=['Selection Method', 'Time Elapsed', 'Final Fitness', 'Final Cost',
                                'Number of Iterations', 'Final Quantity', 'Number of Requirements met'])

selection_methods =[fps, ranking_selection, tournament_selection]
selection_names= ['Fitness Proportion', 'Ranking', 'Selection']

Individual.get_fitness = get_fitness

# Lists to store fitness values for each iteration
fps_fitness_values = []
ranking_fitness_values = []
tournament_fitness_values = []

for i in range(3):
    print(selection_names[i])
    for _ in range(50):
        pop = Population(size=50,
                         optim="min",
                         sol_size=len(data),
                         valid_set=range(len(data)),
                         replacement=True)
        start_time = time()
        best_individual, fitness_history = pop.evolve(pop=pop,
                                                     generations=500,
                                                     select=selection_methods[i],
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
        row_data = {'Selection Method': selection_names[i],
                    'Time Elapsed': end_time - start_time,
                    'Final Fitness': final_fitness,
                    'Final Cost': final_cost,
                    'Number of Iterations': num_iterations,
                    'Final Quantity': final_qnt_ingredients,
                    'Number of Requirements met': num_requirements_met}

        results = pd.concat([results, pd.DataFrame(row_data, index=[0])], ignore_index=True)

        # Save fitness values at each iteration
        if selection_methods[i] == fps:
            fps_fitness_values.append(fitness_history)
        elif selection_methods[i] == ranking_selection:
            ranking_fitness_values.append(fitness_history)
        elif selection_methods[i] == tournament_selection:
            tournament_fitness_values.append(fitness_history)

print(results.head(5))
results.to_csv('results.csv', index=False)

df = pd.read_csv('results.csv')
print(df.head(5))

# Combine fitness values
combined_fitness_values = [fps_fitness_values, ranking_fitness_values, tournament_fitness_values]

# List of metrics you want to observe
metrics = ['Time Elapsed', 'Final Fitness', 'Final Cost', 'Number of Iterations', 'Final Quantity', 'Number of Requirements met']

# Create a figure and an axis
fig, ax = plt.subplots(figsize=(10, 6))


# Calculate the mean fitness values
fps_mean_fitness = np.mean(fps_fitness_values, axis=0)
ranking_mean_fitness = np.mean(ranking_fitness_values, axis=0)
tournament_mean_fitness = np.mean(tournament_fitness_values, axis=0)

# Calculate the minimum and maximum fitness 
fps_min_fitness = np.min(fps_fitness_values, axis=0)
fps_max_fitness = np.max(fps_fitness_values, axis=0)
ranking_min_fitness = np.min(ranking_fitness_values, axis=0)
ranking_max_fitness = np.max(ranking_fitness_values, axis=0)
tournament_min_fitness = np.min(tournament_fitness_values, axis=0)
tournament_max_fitness = np.max(tournament_fitness_values, axis=0)

# Plot the line chart and fill the range for fps
ax.plot(range(len(fps_mean_fitness)), fps_mean_fitness, label='Fitness Proportionate')
ax.fill_between(range(len(fps_mean_fitness)), fps_min_fitness, fps_max_fitness, alpha=0.3)

# Plot the line chart for geometric crossover
ax.plot(range(len(ranking_mean_fitness)), ranking_mean_fitness, label='Ranking')
ax.fill_between(range(len(ranking_mean_fitness)), ranking_min_fitness, ranking_max_fitness, alpha=0.3)

# Plot the line chart for geometric crossover
ax.plot(range(len(tournament_mean_fitness)), tournament_mean_fitness, label='Tournment')
ax.fill_between(range(len(tournament_mean_fitness)), tournament_min_fitness, tournament_max_fitness, alpha=0.3)

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

