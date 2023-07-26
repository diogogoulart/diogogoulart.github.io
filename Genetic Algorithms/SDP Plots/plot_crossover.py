from time import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from charles import Population, Individual
from sdp_data import data, min_nutrients, max_nutrients
from sdp_run import get_fitness

from selection import fps
from mutation import random_mutation
from crossover import single_point_co, uniform_co, multi_point_co, arithmetic_co, geometric_co

results = pd.DataFrame(columns=['Crossover Operator', 'Time Elapsed', 'Final Fitness', 'Final Cost',
                                'Number of Iterations', 'Final Quantity', 'Number of Requirements met'])

crossover_operators =[single_point_co, uniform_co, multi_point_co, arithmetic_co, geometric_co]
crossover_names= ['Single Point', 'Uniform', 'Multi Point', 'Arithmetic', 'Geometric']

Individual.get_fitness = get_fitness

# Lists to store fitness values for each iteration
single_fitness_values = []
uniform_fitness_values = []
multi_fitness_values = []
arithmetic_fitness_values = []
geometric_fitness_values = []

for i in range(5):
    print(crossover_names[i])
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
                                                     crossover=crossover_operators[i],
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
        row_data = {'Crossover Operator': crossover_names[i],
                    'Time Elapsed': end_time - start_time,
                    'Final Fitness': final_fitness,
                    'Final Cost': final_cost,
                    'Number of Iterations': num_iterations,
                    'Final Quantity': final_qnt_ingredients,
                    'Number of Requirements met': num_requirements_met}

        results = pd.concat([results, pd.DataFrame(row_data, index=[0])], ignore_index=True)

        # Save fitness values at each iteration
        if crossover_operators[i] == single_point_co:
            single_fitness_values.append(fitness_history)
        elif crossover_operators[i] == uniform_co:
            uniform_fitness_values.append(fitness_history)
        elif crossover_operators[i] == multi_point_co:
            multi_fitness_values.append(fitness_history)
        elif crossover_operators[i] == arithmetic_co:
            arithmetic_fitness_values.append(fitness_history)
        elif crossover_operators[i] == geometric_co:
            geometric_fitness_values.append(fitness_history)

print(results.head(5))
results.to_csv('results.csv', index=False)

df = pd.read_csv('results.csv')
print(df.head(5))

# Combine fitness values 
combined_fitness_values = [single_fitness_values, uniform_fitness_values, multi_fitness_values, arithmetic_fitness_values, geometric_fitness_values]

# List of metrics you want to observe
metrics = ['Time Elapsed', 'Final Fitness', 'Final Cost', 'Number of Iterations', 'Final Quantity', 'Number of Requirements met']

# Create a figure and an axis
fig, ax = plt.subplots(figsize=(10, 6))

# Calculate the mean fitness values 
single_mean_fitness = np.mean(single_fitness_values, axis=0)
uniform_mean_fitness = np.mean(uniform_fitness_values, axis=0)
multi_mean_fitness = np.mean(multi_fitness_values, axis=0)
arithmetic_mean_fitness = np.mean(arithmetic_fitness_values, axis=0)
geometric_mean_fitness = np.mean(geometric_fitness_values, axis=0)

# Calculate the minimum and maximum fitness values 
single_min_fitness = np.min(single_fitness_values, axis=0)
single_max_fitness = np.max(single_fitness_values, axis=0)
uniform_min_fitness = np.min(uniform_fitness_values, axis=0)
uniform_max_fitness = np.max(uniform_fitness_values, axis=0)
multi_min_fitness = np.min(multi_fitness_values, axis=0)
multi_max_fitness = np.max(multi_fitness_values, axis=0)
arithmetic_min_fitness = np.min(arithmetic_fitness_values, axis=0)
arithmetic_max_fitness = np.max(arithmetic_fitness_values, axis=0)
geometric_min_fitness = np.min(geometric_fitness_values, axis=0)
geometric_max_fitness = np.max(geometric_fitness_values, axis=0)

# Plot the line chart and fill the range for single point
ax.plot(range(len(single_mean_fitness)), single_mean_fitness, label='Single Point')
ax.fill_between(range(len(single_mean_fitness)), single_min_fitness, single_max_fitness, alpha=0.3)

# Plot the line chart for uniform crossover
ax.plot(range(len(uniform_mean_fitness)), uniform_mean_fitness, label='Uniform')
ax.fill_between(range(len(uniform_mean_fitness)), uniform_min_fitness, uniform_max_fitness, alpha=0.3)

# Plot the line chart for multi point crossover
ax.plot(range(len(multi_mean_fitness)), multi_mean_fitness, label='Multi Point')
ax.fill_between(range(len(multi_mean_fitness)), multi_min_fitness, multi_max_fitness, alpha=0.3)

# Plot the line chart for arithmetic crossover
ax.plot(range(len(arithmetic_mean_fitness)), arithmetic_mean_fitness, label='Arithmetic')
ax.fill_between(range(len(arithmetic_mean_fitness)), arithmetic_min_fitness, arithmetic_max_fitness, alpha=0.3)

# Plot the line chart for geometric crossover
ax.plot(range(len(geometric_mean_fitness)), geometric_mean_fitness, label='Geometric')
ax.fill_between(range(len(geometric_mean_fitness)), geometric_min_fitness, geometric_max_fitness, alpha=0.3)

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


# Create a figure and an axis
fig, ax = plt.subplots(figsize=(10, 6))
# Plot the line chart and fill the range for single point
ax.plot(range(len(single_mean_fitness)), single_mean_fitness, label='Single Point')

# Plot the line chart for uniform crossover
ax.plot(range(len(uniform_mean_fitness)), uniform_mean_fitness, label='Uniform')

# Plot the line chart for multipoint crossover
ax.plot(range(len(multi_mean_fitness)), multi_mean_fitness, label='Multi Point')

# Plot the line chart for arithmetic crossover
ax.plot(range(len(arithmetic_mean_fitness)), arithmetic_mean_fitness, label='Arithmetic')

# Plot the line chart for geometric crossover
ax.plot(range(len(geometric_mean_fitness)), geometric_mean_fitness, label='Geometric')

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