from template_params import *
from GA_params import *
from create_new_population import *
from create_initial_population import *
from utils import *

output_dir = "GA_run"

""" Create initial population"""
create_initial_population(bb_options, n_mof_per_generation, output_dir, tobacco_path, lhs_optimized='maximin', data_fname='data', create_MOF=True, template_info=template_info, tobacco_output=True, preconstruct_file=None)

""" Create data file
get_mof_objective(output_dir,preconstruct_file=preconstruct_file)

for k in range(15):
    create_new_population(n_mof_per_generation, m_prob, r_prop, c_orders, bb_options, output_dir, "mof_analyze.txt", n_mof_per_generation, create_MOF=False, preconstruct_file=preconstruct_file)
    get_mof_objective(output_dir,preconstruct_file=preconstruct_file)

"""    
