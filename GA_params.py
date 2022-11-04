""" Parameters for GA """

tobacco_path = '#ABS/PATH/TO/tobacco'
n_mof_per_generation = 200
""" Ranking Selection parameters"""
n_mof_selection = 8 # number of MOFs selected for tournament selection. Must be a power of 2
r_prop = 0.95 # ranking probability

""" Mutation parameters"""
m_prob = 0.10 # mutation probability
m_type = 'uniform' # mutation types: uniform, one_point
