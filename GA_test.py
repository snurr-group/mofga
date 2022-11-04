from test_case.template_params import *
from test_case.GA_params import *
from create_new_population import *
from create_initial_population import *
from utils import *

output_dir = "test_case"
preconstruct_file = "objectives/alpha_ads_and_WC_CO2.csv"
objective_fname = "mof_objective.csv"

""" Create initial population"""
create_initial_population(bb_options, n_mof_per_generation, output_dir, tobacco_path, lhs_optimized='maximin', data_fname='test_case/data', create_MOF=False, template_info=template_info, tobacco_output=False, preconstruct_file=preconstruct_file)

""" Create data file """
get_mof_objective(output_dir,preconstruct_file=preconstruct_file, fname='mof_objective.csv')

for k in range(15):
    create_new_population(n_mof_per_generation, template_info, m_prob, r_prop, bb_options, output_dir, objective_fname, tobacco_path, data_fname='test_case/data', create_MOF=False, tobacco_output=False, preconstruct_file=preconstruct_file, restart=False)
    get_mof_objective(output_dir,preconstruct_file=preconstruct_file, fname='mof_objective.csv')
