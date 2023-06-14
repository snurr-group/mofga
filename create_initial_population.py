from utils import read_preconstructed_data, read_database
import itertools
from skopt.sampler import Lhs
from skopt.space import Space
from generate_cif_from_chromosome import *
import random
import os
import subprocess

def create_initial_population(bb_options, size, output_dir, tobacco_path, lhs_optimized='maximin', data_fname='data', create_MOF=True, template_info=None, tobacco_output=True, preconstruct_file=None):
    """ Create initial population for GA using modified lhs sampling
    
    Parameters:
        bb_options:
        
    """

    #Todo: Only allow initial population for chromosomes with the same size

    def _create_a_random_chromosome(templates, bb_options):
        """ Create a random chromosome from building block options and a list of template """
        template = random.choice(templates)
        chromosome = [template]
        size = len(bb_options[template])

        for k in range(1, size):
            chromosome.append(random.choice(bb_options[template][k]))
        return chromosome


    def _lhs_sampling(dimensions, size, lhs_optimized=lhs_optimized):
        def _round_list(l0):
            rounded_l0 = []
            for k in l0:
                rounded_l0.append(round(k))
            return rounded_l0

        def _to_float(l0):
            float_l0 = []
            for k in l0:
                float_l0.append(float(k))
            return float_l0

        def _mapping_to_discrete_space(variables):
            size = len(variables)
            map_dict = {}

            for key, value in zip(range(0, size), variables):
                map_dict[key] = value

            return range(size), map_dict

        dimensions = [sorted(i) for i in dimensions]        
        dim = []
        
        all_mapping = []
        for bb in dimensions:
            if len(bb) == 1:
                dim.append(bb)
                all_mapping.append('X')
            else:
                map_bb, map_dict = _mapping_to_discrete_space(bb)
                all_mapping.append(map_dict)
                bb_float = _to_float(map_bb)
                tup = (min(bb_float), max(bb_float)+1)
                dim.append(tup)
        space = Space(dim)
        lhs = Lhs(criterion=lhs_optimized, iterations=1000)
        all_chromosomes = lhs.generate(space.dimensions, size)
        all_chromosomes = [_round_list(k) for k in all_chromosomes]

        # Ensure periodicity in sampling, so the start/end value in a range are sampled equally as other points
        for chromosome in all_chromosomes:
            for index in range(len(chromosome)):
                if all_mapping[index] == 'X':
                    continue
                else:
                    if chromosome[index] not in all_mapping[index]:
                        chromosome[index] = 0
        # Map values from our "discrete" space back to original space
        for index, value in enumerate(all_mapping):
            if value == 'X':
                continue
            else:
                for chromosome in all_chromosomes:
                    current_value = chromosome[index]
                    #print("chromosome: {} index: {} current: {} all_value {}".format(chromosome, index, chromosome[index], value))
                    chromosome[index] = value[current_value]

        for chromosome in all_chromosomes:
            for index in range(len(chromosome)):
                if chromosome[index] not in dimensions[index]:
                    chromosome[index] = dimensions[index][0]
        return all_chromosomes

    output_dir = output_dir + "/" + "generation_0"
    if os.path.isdir(output_dir):
        print("Output_dir_existed! Double check!")

    else:
        subprocess.call("mkdir -p {}".format(output_dir), shell=True)
    print("Creating initial population in {}".format(output_dir))
    # Generate Latin Hypercube Sampling for each template, then combine them together. Not the best, but can avoid situation when the chromosome order is different between topologies

    accept = []
    accept_names = []

    reject = []
    n_per_template =  int(size/len(bb_options))

    if n_per_template == 0:
        print("Initial population size is less than the total number of topologies. Increase the population size")
        return 1
    if create_MOF == True:
        temp_dict, node_dict, edge_dict = read_database(fname='data')
        for template in bb_options:
            accept_each_template = []
            dimensions = [[]]
            dimensions[0].append(template)
            for index, key in enumerate(bb_options[template]):
                if index == 0:
                    continue
                else:
                    dimensions.append(bb_options[template][key])
            all_chromosomes = _lhs_sampling(dimensions, n_per_template, lhs_optimized = lhs_optimized)
            
            for chromosome in all_chromosomes:
                if chromosome in accept or chromosome in reject:
                    continue
                else:
                    check, name = generate_cif_from_chromosome(chromosome, tobacco_path, template_info, temp_dict, node_dict, edge_dict, tobacco_output=tobacco_output, output_dir=output_dir)
                    if check == 0:
                        accept_each_template.append(chromosome)
                        accept.append(chromosome)
                        accept_names.append(name)
                        with open(output_dir+'/'+'mof_list_backup.txt', 'a') as f:
                            f.write("{}|{}\n".format(accept[-1], accept_names[-1]))

                        continue
                    else:
                        print("Cannot create {}. Searching for a neighbor".format(chromosome))
                        reject.append(chromosome)
                        neighbors = find_neighbors(chromosome, bb_options)

                        for index, neighbor in enumerate(neighbors):
                            """ Set a maximum number of iteration to search a neighbor to avoid long loop """
                            if neighbor in accept or neighbor in reject:
                                continue
                            else:
                                if index < 20:
                                    check, name = generate_cif_from_chromosome(neighbor, tobacco_path, template_info, temp_dict, node_dict, edge_dict, tobacco_output=tobacco_output, output_dir=output_dir)
                                    if check == 0:
                                        print("Neighbor found: {}".format(neighbor))
                                        accept_each_template.append(chromosome)
                                        accept.append(neighbor)
                                        accept_names.append(name)
                                        with open(output_dir+'/'+'mof_list_backup.txt', 'a') as f:
                                            f.write("{}|{}\n".format(accept[-1], accept_names[-1]))
                                        break
                                    else:
                                        reject.append(neighbor)
                                        continue
            while len(accept_each_template) < n_per_template:
                c = _create_a_random_chromosome([template], bb_options)
                if c in accept or c in reject:
                    continue
                else:
                    check, name = generate_cif_from_chromosome(c, tobacco_path, template_info, temp_dict, node_dict, edge_dict, tobacco_output=tobacco_output, output_dir=output_dir)
                    if check == 0:
                        accept_each_template.append(chromosome)
                        accept.append(c)
                        accept_names.append(name)
                    else:
                        reject.append(c)
                        continue
        while len(accept) < size:
            templates = [template for template in bb_options]
            c = _create_a_random_chromosome(templates, bb_options)
            if c in accept or c in reject:
                continue
            else:
                check, name = generate_cif_from_chromosome(c, tobacco_path, template_info, temp_dict, node_dict, edge_dict, tobacco_output=tobacco_output, output_dir=output_dir)
                if check == 0:
                    accept.append(c)
                    accept_names.append(name)
                else:
                    reject.append(c)
                    continue

    else:
        #Read preconstructed data file that contains (1) chromosomes, (2) names and possible (3) properties. This is used for testing GA with prior knowledge about the output space
        try:
            data = read_preconstructed_data(preconstruct_file)
        except:
            print("Error with reading preconstructed data file")
            return 1
        
        for template in bb_options:
            accept_each_template = []
            dimensions = [[]]
            dimensions[0].append(template)
            for index, key in enumerate(bb_options[template]):
                if index == 0:
                    continue
                else:
                    dimensions.append(bb_options[template][key])
            all_chromosomes = _lhs_sampling(dimensions, n_per_template, lhs_optimized = lhs_optimized)

            for chromosome in all_chromosomes:
                if chromosome in data[0]:
                    accept_each_template.append(chromosome)
                    accept.append(chromosome)
                    index = data[0].index(chromosome)
                    accept_names.append(data[1][index])
                else:
                    reject.append(chromosome)
                    neighbors = find_neighbors(chromosome, bb_options)
                    print("Cannot create {}. Searching for a neighbor".format(chromosome))
                    for index, neighbor in enumerate(neighbors):
                        if neighbor in accept or neighbor in reject:
                            continue
                        else:
                            if index < 20:
                                if neighbor in data[0]:
                                    print("Neighbor found: {}".format(neighbor))
                                    accept_each_template.append(neighbor)
                                    accept.append(neighbor)
                                    index = data[0].index(neighbor)
                                    accept_names.append(data[1][index])
                                    break
                            else:
                                reject.append(neighbor)
                                continue

            while len(accept_each_template) < n_per_template:
                c = _create_a_random_chromosome([template], bb_options)
                if c in accept or c in reject:
                    continue
                elif c in data[0]:
                    accept_each_template.append(c)
                    accept.append(c)
                    index = data[0].index(chromosome)
                    accept_names.append(data[1][index])
                else:
                    reject.append(c)
                    continue
             
        while len(accept) < size:
            templates = [template for template in bb_options]
            c = _create_a_random_chromosome(templates, bb_options)
            if c in accept or c in reject:
                continue
            elif c in data[0]:
                accept_each_template.append(c)
                accept.append(c)
                index = data[0].index(chromosome)
                accept_names.append(data[1][index])
            else:
                reject.append(c)
                continue
    with open(output_dir+'/'+'mof_list.txt', 'w') as f:
        if len(accept) != len(accept_names):
            print("Number of accepted chromosome and number of names are different!!!")
        for c, n in zip(accept, accept_names):
            f.write("{}|{}\n".format(c, n))

def find_neighbors(chromosome, bb_options):
    """ Find neighboring chromosome to replace chromosome that cannot be created """
    gene_list = [[chromosome[0]]]

    for k in range(1, len(chromosome)):
        bbs = bb_options[chromosome[0]][k]
        bb_index = bbs.index(chromosome[k])

        #print("k: {}; gene: {};  bbs: {}, bb_index: {}, length of bbs: {}".format(k, chromosome[k], bbs, bb_index, len(bbs)))
        if len(bbs) == 1:
            neighbors = [chromosome[k]]
        elif len(bbs) == 2:
            neighbors = bbs
        elif len(bbs) == 0:
            print("No option for building block {} of chromsome {}".format(k, chromosome))
        else:
            if bb_index == len(bbs)-1:
                neighbors = [bbs[bb_index-1], bbs[bb_index], bbs[0]]
            else:
                neighbors = [bbs[bb_index-1], bbs[bb_index], bbs[bb_index+1]]
        gene_list.append(neighbors)

    chromosomes = list(itertools.product(*gene_list))
    list_neighbor_chromosomes = [list(i) for i in chromosomes]
    list_neighbor_chromosomes.remove(chromosome)
    random.shuffle(list_neighbor_chromosomes)

    return list_neighbor_chromosomes

