from time import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from charles import Population, Individual
from sdp_data import data, min_nutrients, max_nutrients
from sdp_run import get_fitness

#operators
from selection import fps, ranking_selection, tournament_selection
from mutation import random_mutation
from crossover import single_point_co

results = pd.DataFrame(columns=['Selection Method', 'Time Elapsed', 'Final Fitness',
                                'Num Iterations', 'Final Num Ingredients', 'Num Requirements Met',
                                'Num Requirements Unmet'])

# Your list of selection methods
selection_methods = [fps, ranking_selection, tournament_selection]
method_names = ['FPS', 'Ranking', 'Tournament']

# Monkey Patching
Individual.get_fitness = get_fitness

for i in range(3): 
    print(method_names[i])
    for _ in range(50):  # run 50 times for each method
        pop = Population(size=50,
                         optim="min",
                         sol_size=len(data),
                         valid_set=range(len(data)),
                         replacement=True)
        start_time = time()
        best_individual, fitness_history= pop.evolve(pop=pop,
                   generations=500,
                   select=selection_methods[i],
                   mutate=random_mutation,
                   mutation_rate=0.5,
                   crossover=single_point_co,
                   elite_size=2,
                   no_improvement_threshold=50,
                   plot=None)
        end_time = time()

        # Initialize counts
        num_requirements_met = 0
        num_requirements_unmet = 0
        final_cost=0

        # Calculate nutritional values of the best individual
        nutritional_values = [0] * 14  # Initialize nutritional values list with 0s
        for index, quantity in enumerate(best_individual.representation):
            for j in range(14):
                nutritional_values[j] += data[index][j + 2] * quantity  # Accessing and accumulating nutritional values

                if quantity > 0:
                    final_cost += data[index][1] * quantity # Accessing the price of the ingredient at the given index

        # Check requirements
        for j, (nutrient, min_req) in enumerate(min_nutrients):
            if min_nutrients[j][1] <= nutritional_values[j] <= max_nutrients[j][1]:
                num_requirements_met += 1

        # Calculate other metrics here
        final_fitness = best_individual.get_fitness()
        num_iterations = len(fitness_history)
        final_qnt_ingredients = sum(best_individual.representation)

        # Append a row to the DataFrame
        row_data = {'Selection Method': method_names[i],
            'Time Elapsed': end_time - start_time,
            'Final Fitness': final_fitness,
            'Final Cost': final_cost,
            'Number of Iterations': num_iterations,
            'Final Quantity': final_qnt_ingredients,
            'Number of Requirements met': num_requirements_met}
        
        results = pd.concat([results, pd.DataFrame(row_data, index=[0])], ignore_index=True)

print(results.head(5))

results.to_csv('results.csv', index=False)

df = pd.read_csv('results.csv')

print(df.head(5))

# List of metrics you want to observe
metrics = ['Time Elapsed', 'Final Fitness', 'Final Cost', 'Number of Iterations', 'Final Quantity', 'Number of Requirements met']

# Create a figure and a grid of axes
fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(15, 15))

# Create a boxplot for each metric
for ax, metric in zip(axs.flatten(), metrics):
    sns.boxplot(x='Selection Method', y=metric, data=results, ax=ax)
    ax.set_xlabel('')  # Remove x-axis title

# To prevent overlapping of the labels and titles
plt.tight_layout()
plt.show()