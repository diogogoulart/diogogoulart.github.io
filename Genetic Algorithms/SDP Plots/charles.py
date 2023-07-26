from utils import print_nutrition
from random import randint,  uniform, randrange

class Individual:
    def __init__(self, representation=None):
    
        # Initialize the representation random
        if representation is None:
            self.representation = self.initialize()
        else:
            self.representation = representation
        self.fitness = self.get_fitness()

    def get_fitness(self):
        raise Exception("You need to monkey patch the fitness path.")

    def initialize():
        raise Exception("You need to monkey patch the fitness path.")

    def __len__(self):
        return len(self.representation)

    def __getitemvalue__(self, position):
        return self.representation[position]

    def __setitem__(self, position, value):
        self.representation[position] = value

    def __repr__(self):
        return f"Individual(size={len(self.representation)}); Fitness: {self.fitness}"


class Population:
    def __init__(self, size, optim, **kwargs):
        self.individuals = []
        self.size = size
        self.optim = optim
        for _ in range(size):
            self.individuals.append(
                Individual()
            )

    def evolve(self, pop, generations, select, mutate, mutation_rate, crossover, elite_size, no_improvement_threshold, plot):
        fitness_history = []
        generations_without_improvement = 0
        previous_best_fitness = float("inf")

        for _ in range(generations):
            new_population = []
            sorted_population = sorted(pop, key=lambda x: x.fitness)
            current_best_fitness = sorted_population[0].fitness
            fitness_history.append(current_best_fitness)
            
            # Check for improvements
            if current_best_fitness < previous_best_fitness:
                generations_without_improvement = 0
                previous_best_fitness = current_best_fitness
            else:
                generations_without_improvement += 1

            # Stopping criterion
            if generations_without_improvement >= no_improvement_threshold:
                break
            
            # Elitism: Preserve the best individuals
            new_population.extend(sorted_population[:elite_size])

            # Crossover and mutation
            while len(new_population) < len(pop):
                parent1 = select(pop)
                parent2 = select(pop)
                offspring1, offspring2 = crossover(parent1.representation, parent2.representation)
                
                if uniform(0, 1) < mutation_rate:
                    offspring1 = mutate(individual=offspring1)
                if uniform(0, 1) < mutation_rate:
                    offspring2 = mutate(individual=offspring2)
                

                new_population.append(Individual(representation=offspring1))
                new_population.append(Individual(representation=offspring2))
            
            # Update population
            pop.individuals = new_population

        # Get the best solution and its fitness
        best_solution = sorted(pop, key=lambda x: x.fitness)[0]
        
        if plot is not None:
            plot(fitness_history)
            print(best_solution)
            print_nutrition(best_solution)

        return best_solution, fitness_history

    def __len__(self):
        return len(self.individuals)

    def __getitem__(self, position):
        return self.individuals[position]
