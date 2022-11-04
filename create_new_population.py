import os
import glob
from ranking_selection import *
from genetic_operators import *
import subprocess
from generate_cif_from_chromosome import *
from utils import read_preconstructed_data, read_database

def create_new_population(n_mof_per_generation, template_info, m_prob, r_prop, bb_options, output_dir, objective_fname, tobacco_path, data_fname='data', create_MOF=True, tobacco_output=True, preconstruct_file=None, restart=False):
    N_generation = glob.glob(os.path.join(output_dir,"generation_*/"))
    if restart == False:
        new_generation = output_dir + '/' + 'generation_' + str(len(N_generation)) + '/'
        pre_generation = output_dir + '/' + 'generation_' + str(len(N_generation)-1) + '/'
        accept = []
        accept_names = []
        print("Found details of generation {}".format(len(N_generation)-1))
        print("Starting GA -  Creating generation {}".format(len(N_generation)))
        subprocess.call("mkdir -p {}".format(new_generation), shell=True)
     
    else:
        new_generation = output_dir + '/' + 'generation_' + str(len(N_generation)-1) + '/'
        pre_generation = output_dir + '/' + 'generation_' + str(len(N_generation)-2) + '/'
        known = read_preconstructed_data(new_generation + objective_fname)
        accept = known[0]
        accept_names = known[1]
        print("Restarting GA - generation {}".format(len(N_generation) - 1))

    try:
        data = read_preconstructed_data(os.path.join(pre_generation, objective_fname))
    except:
        print("Missing output file of generation_{}".format(len(N_generation)-1))
        return 1
    
    # Start from elitism. MOFs are used from previous generations
    if restart == False:
        b = elitism(data[0], data[2:])
        for k in b:
            accept.append(data[0][k])
            accept_names.append(data[1][k])

            print("MOFs added from elitism: ", data[0][k])
   
    if create_MOF == True:
        while len(accept) < n_mof_per_generation:
            p1, p2 = tournament_selection(data[0], data[2:], r_prop)
            checkc, c = crossover(p1, p2, template_info)
            if checkc == 1:
                continue

            check, c = mutate(c, template_info, m_prob, bb_options)

            if c in accept:
                continue

            if create_MOF ==  True:
                temp_dict, node_dict, edge_dict = read_database(fname=data_fname)
                check, name = generate_cif_from_chromosome(c, tobacco_path, template_info, temp_dict, node_dict, edge_dict, tobacco_output=tobacco_output, output_dir=new_generation)
                if check == 0:
                    accept.append(c)
                    accept_names.append(name)

    # For testing purpose. Read data from a dataset file instead of creating new MOFs.
    else:
        try:
            dataset = read_preconstructed_data(preconstruct_file)
        except:
            print("Error with reading preconstructed data file")
            return 1

        while len(accept) < n_mof_per_generation:
            p1, p2 = tournament_selection(data[0], data[2:], r_prop)
            checkc, c = crossover(p1, p2, template_info)
            if checkc == 1:
                continue
            check, c = mutate(c, template_info, m_prob, bb_options)

            if c in accept:
                continue

            if c in dataset[0]:
                c_index = dataset[0].index(c)
                name = dataset[1][c_index]
                accept.append(c)
                accept_names.append(name)

    with open(os.path.join(new_generation, "mof_list.txt"), "w") as f:
        for c, n in zip(accept, accept_names):
            f.write("{}|{}\n".format(c, n))

