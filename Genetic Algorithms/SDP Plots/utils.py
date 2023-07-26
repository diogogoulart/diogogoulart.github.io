import matplotlib.pyplot as plt
from sdp_data import min_nutrients, data

def plot_c(fitness_history_ga):
    plt.plot(fitness_history_ga)
    plt.title("Genetic Algorithm Fitness over Time")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.show()

def print_nutrition(individual):
    print('Fitness:', individual.get_fitness())
    total_cost = 0
    nutritional_values = [0] * 14  # Initialize nutritional values list with 0s
    ingredients = []
    requirements_met = 0

    for index, quantity in enumerate(individual.representation):
        if quantity > 0:
            ingredients.append([data[index][0], quantity])  # Accessing the name of the ingredient at the given index
            total_cost += data[index][1] * quantity  # Accessing the price of the ingredient at the given index
            for i in range(14):
                nutritional_values[i] += data[index][i + 2] * quantity  # Accessing and accumulating nutritional values

    print(f"Total cost: {total_cost}")
    print(f"Number of ingredients chosen: {len(ingredients)}\n")


    for i, (nutrient, min_req) in enumerate(min_nutrients):
        nutrient_percentage = (nutritional_values[i] / min_req) * 100
        if min_nutrients[i][1] <= nutritional_values[i]:
            requirements_met += 1
        print(f"{nutrient}: {nutritional_values[i]:.2f} ({min_req}) - {nutrient_percentage:.2f}% of minimum requirement met")

    requirements_unmet = len(min_nutrients) - requirements_met
    print(f"\nNumber of requirements met: {requirements_met}/{len(min_nutrients)}")
    print(f"Number of requirements unmet: {requirements_unmet}/{len(min_nutrients)}")

    # Print the ingredients and their counts in descending order
    print("\nIngredients chosen:")
    for ingredient, quantity in ingredients:
        print(f"{ingredient}: {quantity}")



