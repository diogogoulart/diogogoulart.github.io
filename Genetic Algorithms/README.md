# CIFO group 21

This repository contains code related to the SDP Algorithm and Plots for comparing different approaches.

# SDP Algorithm Directory
The SDP Genetic Algorithm directory contains the implementation of a genetic algorithm for the SDP (Stigler's Diet Problem). The algorithm is designed to find optimal solutions that meet specific nutritional requirements while minimizing the cost of food items.

## File Structure
SDP Algorithm/<br>
- **charles.py**: Contains the implementation of the Individual and Population class and related functions for creating and evolving populations.<br>
- **selection.py**: Includes different selection methods used in the genetic algorithm (fitness proportionate selection, ranking selection and tournament selection).<br>
- **mutation.py**: Provides various mutation operators for introducing diversity into the population (random mutation, geometric mutation, insert-delete mutation).<br>
- **crossover.py**: Implements crossover operators for combining genetic material from two parent individuals (single point crossover, uniform crossover, multi point crossover, arithmetic crossover and geometric crossover).<br>
- **sdp_data.py**: Contains data related to food items, nutritional requirements, and other parameters used in the SDP problem.<br>
- **sdp_run.py**: Includes the initialization functions and the main function to run the genetic algorithm.<br>

# SDP Plots Directory
The SDP Plots directory contains the same files as SDP Algorithm plus py files for generating plots and performing comparisons between different approaches or variations of the genetic algorithm used in the SDP problem.

## File Structure
SDP Plots/<br>
- **boxplot_.py**: Generates boxplots to access the time elapse, final fitness, final cost, number of iterations, final quantity and number of requirements met.<br>
- **plot_.py**: Builds a line plot to acess the the mean best fitness and it's range (y axis) throughout the generations (x axis) when running the algorithm multiple times.<br>
