# MOFGA

Genetic Algorithms Implementation in Metal-Organic Frameworks

# Overview
mofga is a python module to perform genetic algorithms to optimize metal-organic framework (MOF)'s building blocks (including topology, organic linker and metal node). mofga was tested on optimizing MOFs for CO<sub>2</sub> capture

Initial solutions are created using Latin Hypercube sampling, modified from skopt library. Through ranking selection methods, top-performing MOFs are kept, or used as parents for new solutions. To create new solutions, genetic operators, including crossover and mutation, are used. 

# Installation and Dependencies

MOFGA is tested for Python 3.7. MOFGA requires the following packages (and their dependencies):
- [ToBaCCo 3.0](https://github.com/tobacco-mofs/tobacco_3.0) - used to create a MOF crystal structure from a chromosome
- [Skopt](https://scikit-optimize.github.io/stable/install.html) - used to create initial population using Latin Hypercube Sampling

To set up MOFGA, we recommend to install Anaconda. If you already have a conda environment for ToBaCCo, you can continue to use that environment, and only need to install Skopt using
```
conda install -c conda-forge scikit-optimize
```

For a new environment, run the following commands:
```
conda create -n MOFGA python=3.7
conda activate MOFGA
conda install -c conda-forge scikit-optimize networkx=2.2
```
Note: networkx is the prerequisite of ToBaCCo. We tested ToBaCCo 3.0 using networkx version 2.2. Other versions of networkx maybe compatible with ToBaCCo (see [ToBaCCo 3.0](https://github.com/tobacco-mofs/tobacco_3.0) for more details)

# What is in MOFGA?
Important components of MOFGA are listed here. For more details, please read the included manual.pdf
- configuration.py: contains important GA parameters.
- data: contains the labels of the templates, nodes and edges.
- GA.py: contains the commands needed to run GA. (1) create_initial_population: Create an initial population of GA using a modified version of Latin Hypercube, (2) get_mof_objective: Get the objective of the MOFs from a preconstructed data file (mainly used for testing purposes) and (3) create_new_population: Create a new population of GA using the chromosomes and MOF properties from previous generations

# Usage
To test GA, run following command:
```
python GA_test.py
```
This will run GA using the parameters in test_configurations.py. GA will be performed with 15 GA generations, 96 MOFs per generation, 10% mutation probability and 95% ranking probability to optimize the selectivity of CO2/N2 at adsorption conditions. GA will be performed using a preconstructed objective file (objectives/alpha_ads_and_WC_CO2_data.csv) which contains (in order) (1) MOF chromosomes of MOFs with fof topology, (2) MOF names as created by ToBaCCo 3.0, (3) the CO2/N2 selectivity and (4) the CO2 working capacity. More details about this data file can be found in our publication. thus no MOF crystal structure will be created.

To run GA in a production enviroment, the steps above (create initial population, get objective functions and create new population) will be decoupled. Detailed steps are listed in GA_production.py (and also the manual). First, an initial population of GA can be created by:

```
create_initial_population(bb_options, n_mof_per_generation, output_dir, create_MOF=True, template_info=template_info, preconstruct_file=preconstruct_file
```
This will create a MOF population in the specified > output_dir


MOFGA can perform Genetic Algorithms search to optimize metal-organic frameworks for a single objective function and multiple objective functions. MOFGA uses a chromosome representation format based on ToBaCCo 3.0's definition of a template. A MOF chromosome is consisted of (1) a topology, (2) node(s) (both inorganic and organic node) and (3) edge(s). MOFGA was developed to (1) provide proof of concept that GA can reduce the number of molecular simulations involved when search for MOFs and (2) perform GA on-the-fly to search for top-performing MOFs for CO$_2$ and N$_2$ separation.

