import random
import numpy as np

def tournament_selection(chromosomes, properties, r_prop, n_chromosomes=16):
    def _compare_objectives(l0, l1):
        """Compare two lists of objectives. Return the better list. If they are equal, return a random one of the two lists
        Params: chromosomes: list of all chromosomes
                properties: list of all properties, correspond to the order in list of all chromosomes - format: [[prop1]] (single objective) or [[prop1], [prop2], [prop3]] (multiple objecitves)
                r_prop: ranking probability - if random number >= r_prop, return the worst chromosome. Else return the worst chromosome
                n_chromosomes: number of chromosomes selected for tournament selection - exponent of 2
        """
        l0_count = 0
        l1_count = 0
        rn = random.uniform(0,1)

        for k in range(len(l1)):
            if l0[k] > l1[k]:
                l0_count = l0_count + 1
            elif l0[k] == l1[k]:
                pass
            else:
                l1_count = l1_count + 1

        if l0_count > l1_count:
            if rn <= r_prop:
                return 0
            else:
                return 1

        if l0_count < l1_count:
            if rn <= r_prop:
                return 1
            else:
                return 0

        if l0_count == l1_count:
            rn = random.uniform(0,1)
            if rn >= 0.5:
                return 0
            else:
                return 1

    def _rank_objectives(c0, c1, c0_prop, c1_prop):
        winner = _compare_objectives(c0_prop, c1_prop)
        if winner == 0:
            return c0, c0_prop
        elif winner == 1:
            return c1, c1_prop
            

    def _random_sample():
        return random.sample(list(range(0, len(chromosomes))), n_chromosomes)

    """ Main function """
    # Shuffle lists of chromosomes and properties

    # Maybe move this to main function
    indice = _random_sample()
    lc = []
    lp = [[] for i in range(n_chromosomes)]

    for i, j in zip(indice, range(n_chromosomes)):
        lc.append(chromosomes[i])
        for k in range(len(properties)):
            lp[j].append(properties[k][i])

    while len(lc) > 2:
        lc_winners = []
        lp_winners = []
        for k in range(0, len(lc), 2):
            w, w_prop = _rank_objectives(lc[k], lc[k+1], lp[k], lp[k+1])
            lc_winners.append(w)
            lp_winners.append(w_prop)

        lc = lc_winners
        lp = lp_winners
    return lc[0], lc[1]


def elitism(chromosomes, properties):
    """Return the best MOF for each objective function and each template. """

    distinct_templates = []
    indice_to_return = []
    for c in chromosomes:
        if c[0] not in distinct_templates:
            distinct_templates.append(c[0])
    
    for dt in distinct_templates:
        dt_list = []
        dt_indice = []
        dt_prop = [[] for k in range(len(properties))]

        for index, chromosome in enumerate(chromosomes):
            if chromosome[0] == dt:
                dt_list.append(chromosome)
                dt_indice.append(index)
                for i, k in enumerate(properties):
                    dt_prop[i].append(properties[i][index])
        
        for prop in dt_prop:
            indice_to_return.append(dt_indice[np.argmax(prop)])
    return list(set(indice_to_return))

