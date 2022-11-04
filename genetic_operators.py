import random

vertices = ('V' , 'Er', 'Ti', 'Ce', 'S',
            'H' , 'He', 'Li', 'Be', 'B',
            'C' , 'N' , 'O' , 'F' , 'Ne',
            'Na', 'Mg', 'Al', 'Si', 'P',
            'Cl', 'Ar', 'K' , 'Ca', 'Sc',
            'Cr', 'Mn', 'Fe', 'Co', 'Ni')

# Compare two template info of 2 templates. Return instructions for (1) crossover and (2) mutation. For mutation, t1 and t2 orders are not important.
# For mutation, t1 is the initial template, and t2 is the mutated template

def compare_template_info(template_info, t1, t2, check=None):
    def _get_vertice_edges(t, template_info):
        v_type = []
        e_type = []
        t_info = template_info[t]
        for i in range(1, len(t_info)):
            ty = t_info[i].split("-")
            if ty[0] in vertices:
                v_type.append(ty[1])
            else:
                e_type.append(t_info[i])

        return v_type, e_type
    
    v1, e1 = _get_vertice_edges(t1, template_info)
    v2, e2 = _get_vertice_edges(t2, template_info)

    if check == 'crossover':
        c1_order = list(range(len(template_info[t1])))
        c2_order = [0]

        for i2, k2 in enumerate(v2):
            indices = [i1 for i1, k1 in enumerate(v1) if k2 == k1]
            if len(indices) == 1:
                c2_order.append(indices[0] + 1)
            if len(indices) < 1:
                c2_order.append('X')
        for i2, k2 in enumerate(e2):
            indices = [i1 for i1, k1 in enumerate(e1) if k2 == k1]
            if len(indices) == 1:
                c2_order.append(indices[0] + 1 + len(v2))
            if len(indices) < 1:
                c2_order.append('X')
        return c1_order, c2_order                    
        
    if check == 'mutation':
        if sorted(v1) == sorted(v2) and sorted(e1) == sorted(e2):
            return True
        else:
            return False
def crossover(chromosome_1, chromosome_2, template_info):
    c1_order, c2_order = compare_template_info(template_info, chromosome_1[0], chromosome_2[0], check='crossover')
    check_similarity = False

    # Return True if 2 topologies share at least 1 common gene
    for i in c2_order[1:]:
        if i != 'X':
            check_similarity = True
            
    if check_similarity == True:
        rn = random.uniform(0,1)
        # If rn >= 0.5, then create child with template of chromosome_1. Else, create chilkd with template of chromosome_2 
        if rn >= 0.5:
            child = [chromosome_1[0]]
            for index in range(1, len(chromosome_1)):
                # If crossover order is 'X' for the gene, then add the parent's gene instead of doing crossover 
                if c1_order[index] == 'X':
                    child.append(chromosome_1[index])
                else:
                    c1_pool = [chromosome_1[i] for i, k in enumerate(c1_order) if k==c1_order[index]]
                    c2_pool = [chromosome_2[i] for i, k in enumerate(c2_order) if k==c1_order[index]]
                    pool = c1_pool + c2_pool
                    child.append(random.choice(pool))
        else:
            child = [chromosome_2[0]]
            for index in range(1, len(chromosome_2)):
                # If crossover order is 'X' for the gene, then add the parent's gene instead of doing crossover 
                if c2_order[index] == 'X':
                    child.append(chromosome_2[index])
                else:
                    c1_pool = [chromosome_1[i] for i, k in enumerate(c1_order) if k==c2_order[index]]
                    c2_pool = [chromosome_2[i] for i, k in enumerate(c2_order) if k==c2_order[index]]
                    pool = c1_pool + c2_pool
                    child.append(random.choice(pool))
        return 0, child
    else:
        return 1, None

# Only mutate MOFs with same composition, maybe different order.
def mutate(chromosome, template_info, m_prob, bb_options, m_type='uniform'):
    """ Mutate a chromosome."""
    """ Params:
    chromosome: list, list of integers
    m_prob: float, mutation probability
    m_type: string, mutation type. Options: 'uniform', 'one_point'
    m_options: mutation options for each building block of each template
        """

    def _diff_list(list1, list2):
        """ Return a list of members that are not shared by 2 lists. """
        if len(list1) >= len(list2):
            return list(set(list1)-set(list2))
        else:
            return list(set(list2)-set(list1))
            
    org_chromosome = chromosome[:]

    if m_type == "uniform":
        if bb_options[chromosome[0]][0] != 'X':
            rn = random.uniform(0,1)
            # Mutation between different templates
            if rn < m_prob:
                t1 = chromosome[0]
                t2 = random.choice(_diff_list(bb_options[t1][0], [t1]))
                if compare_template_info(template_info, t1, t2, check='mutation'):
                    chromosome[0] = t2
                    c1_order, c2_order = compare_template_info(template_info, t1, t2, check='crossover')

                    if c1_order != c2_order:
                        # If the chromosome reprensetations (or crossover order) are different, then switch the chromosome order before mutating the node and edge building blocks
                        new_chromosome = list([chromosome[0]])

                        for i, v in enumerate(c1_order):
                            if i == 0:
                                continue
                            else:
                                pos = c2_order.index(v)
                                new_chromosome.insert(pos, chromosome[i])
                        chromosome = new_chromosome[:]
                else:
                    chromosome = org_chromosome
        for index in range(1, len(chromosome)):
            rn = random.uniform(0,1)
            if rn < m_prob:
                options = bb_options[chromosome[0]][index]
                chromosome[index] = random.choice(_diff_list(options, [chromosome[index]]))

        #if org_chromosome[0] != chromosome[0]:
        print("Original chromosome: {}, Mutated Chromosome: {}".format(org_chromosome, chromosome))
    elif m_type == "one_point":
        m_points = []
        for index in range(len(chromosome)):
            options = m_data[index]
            if options == 'X':
                continue
            else:
                m_points.append(index)
        index = random.choice(m_points)
        chromosome[index] = random.choice(_diff_list(options, [chromosome[index]]))
    
    return 0, chromosome
