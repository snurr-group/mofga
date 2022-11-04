# MOFGA

Genetic Algorithms Implementation in Metal-Organic Frameworks

# Overview
mofga is a python module to perform genetic algorithms to optimize metal-organic framework (MOF)'s building blocks (including topology, organic linker and metal node). mofga was tested on optimizing MOFs for CO<sub>2</sub> capture. mofga can perform GA search usingr a single objective function or multiple objective functions. MOFGA uses a chromosome representation format based on ToBaCCo 3.0's definition of a template. A MOF chromosome is consisted of (1) a topology, (2) node(s) (both inorganic and organic node) and (3) edge(s). 

# General Workflow
Initial solutions are created using Latin Hypercube sampling, modified from skopt library. MOF crystal structures are created using ToBaCCo 3.0. Through ranking selection methods, top-performing MOFs are kept, or used as parents for new solutions. To create new solutions, genetic operators, including crossover and mutation, are used. 

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

# Components
- GA_params.py: contains GA parameters, such as the number of MOFs per generation, number of MOFs in tournament selection, ranking probability and the mutation probability
- template_params.py: contains the chromosome representation and building block compatibility for each topology
- data: contains the labels of the templates, nodes and edges.

# Usage
To test your GA installation, run following command:
```
python GA_test.py
```
This will run GA using the parameters in test_case/. GA will be performed with 15 GA generations, 96 MOFs per generation, 10% mutation probability and 95% ranking probability to optimize the selectivity of CO2/N2 at adsorption conditions. GA will be performed using a preconstructed objective file (objectives/alpha_ads_and_WC_CO2_data.csv) which contains (in order) (1) MOF chromosomes of MOFs with fof topology, (2) MOF names as created by ToBaCCo 3.0, (3) the CO2/N2 selectivity and (4) the CO2 working capacity. More details about this data file can be found in our publication. thus no MOF crystal structure will be created.

To run mofga:
1. Include your libraries of templates, nodes and edges in the templates, nodes and edges directory.
2. Run the script "read_vertex_info.py" to automatically create a data file and template_params.py for your libraries of templates, nodes and edges.
3. (Optional) Modify GA_params.py to set GA parameters.
4. Run GA_production.py to create an initial population using the following method
```
create_initial_population(bb_options, n_mof_per_generation, output_dir, tobacco_path, lhs_optimized='maximin', data_fname='data', create_MOF=True, template_info=template_info, tobacco_output=True, preconstruct_file=None)
```
This will create the initial MOF population in the specified > output_dir

5. Calculate the objective function(s), then create a file with the mof chromosome, mof name and objective(s).
6. Once the mof_objective.txt is create, create new population using
```
create_new_population(n_mof_per_generation, template_info, m_prob, r_prop, bb_options, output_dir, objective_fname, tobacco_path, data_fname='data', create_MOF=True, tobacco_output=True, preconstruct_file=None, restart=False)
```


