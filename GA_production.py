from template_params import *
from GA_params import *
from create_new_population import *
from create_initial_population import *
from utils import *

output_dir = "GA_run"

""" Create initial population"""
create_initial_population(bb_options, n_mof_per_generation, output_dir, tobacco_path, lhs_optimized='maximin', data_fname='data', create_MOF=True, template_info=template_info, tobacco_output=True, preconstruct_file=None)

### Your code to generate data fie###


# Create new generation
create_new_population(n_mof_per_generation, template_info, m_prob, r_prop, bb_options, output_dir, objective_fname, tobacco_path, data_fname='data', create_MOF=True, tobacco_output=True, preconstruct_file=None, restart=False)

