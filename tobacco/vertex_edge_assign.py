from __future__ import print_function
import os
import itertools
import numpy as np
from numpy.linalg import norm
from bbcif_properties import X_vecs
from place_bbs import superimpose, mag_superimpose
from ciftemplate2graph import node_vecs
import warnings

def vertex_assign(TG, TVT, node_cns, unit_cell, USNA, SYM_TOL, ALL_NODE_COMBINATIONS):
    node_dict = dict((k,[]) for k in TVT)

    for node in node_cns:
        for k in TVT:
            if node[0] == k[0]:
                node_dict[k].append(node[1])

    if USNA:

        va = []
        va_append = va.append

        choice_dict = dict((k,'') for k in TVT)
        if not os.path.isfile('vertex_assignment.txt'):
            raise ValueError('User specificed node assignment is on, but there is not vertex_assignment.txt')
        else:
            with open('vertex_assignment.txt','r') as va_key:
                va_key = va_key.read()
                va_key = va_key.split('\n')
                choices = [(l.split()[0],l.split()[1]) for l in va_key if len(l.split())==2]
            for k in node_dict:
                for c in choices:
                    if c[0] == k[1] and c[1] in node_dict[k]:
                        choice_dict[k] = c[1]
                        break
                    else:
                        continue

        for k in choice_dict:

            if len(choice_dict[k]) == 0:
                raise ValueError('Node type ' + k[0] + ' has not assigned cif.')

            for n in TG.nodes(data=True):
                name,ndict = n
                if ndict['type'] == k[1]:
                    va_append((name, choice_dict[k]))

        va = [va]

    else:

        print('*****************************************************************')
        print('RMSD of the compatible node BBs with assigned vertices:          ')
        print('*****************************************************************')
        print()
        
        sym_assign = []
        sym_assign_append = sym_assign.append

        for k in node_dict:

            print('vertex', k[1], '('+str(k[0]) + ' connected)')

            matched = 0
            unmatched = 0
            
            if len(node_dict[k]) == 0:
                continue
            coord_num = k[0]
    
            for n in TG.nodes(data=True):
                name,ndict = n
                distances = []
                distances_append = distances.append
                cptb = []
                if ndict['type'] == k[1]:
                    for cif in node_dict[k]:

                        nvec = np.array([v/np.linalg.norm(v) for v in node_vecs(name, TG, unit_cell, False)])
                        bbxvec = np.array([v/np.linalg.norm(v) for v in X_vecs(cif, 'nodes', False)])
                        rmsd,rot,tran = superimpose(bbxvec,nvec)
                        distances_append((rmsd,cif))

                    for d in distances:
                        disp,cif = d
                        if d[0] < SYM_TOL[coord_num]:
                            matched += 1
                            matches = '(within tolerance)'
                            cptb.append(cif)
                        else:
                            unmatched += 1
                            matches = '(outside tolerance)'
                        print('    ', cif, 'deviation =', np.round(disp,5), matches)

                    for d in distances:
                        if d[0] < SYM_TOL[coord_num]:
                            sym_assign_append((k[1],d[1],d[0]))
                    break
            print('*', matched, 'compatible building blocks out of', len(node_dict[k]), 'available for node', k[1], '*')
            with open('vertex_info.txt', 'a') as f:
                f.write("{}|{}\n".format(k, cptb))
        print()
        
        rearrange = dict((k[1],[]) for k in TVT)
        for a in sym_assign:
            rearrange[a[0]].append((a[0],a[1],a[2]))

        va_uncomb = [rearrange[a] for a in rearrange]
        
        for i in range(len(va_uncomb)):
            va_uncomb[i] = sorted(va_uncomb[i], key=lambda x:x[-1])

        va = []
        va_append = va.append
        used = []
        used_append = used.append
        for l in itertools.product(*va_uncomb):

            cifs = sorted(tuple([c[1] for c in l]))
            if cifs in used and not ALL_NODE_COMBINATIONS:
                continue

            choice_dict = dict((i[0],i[1]) for i in l)
            va_temp = []
            va_temp_append = va_temp.append

            for n in TG.nodes(data=True):
                name,ndict = n
                va_temp_append((name, choice_dict[ndict['type']]))

            va_append(va_temp)
            used_append(cifs)
                    
    return va

def assign_node_vecs2edges(TG, unit_cell, SYM_TOL, template_name):
    
    edge_assign_dict = dict((k,{}) for k in TG.nodes())

    for n in TG.nodes(data=True):

        name,ndict = n
        cif = ndict['cifname']

        bbxlabels = np.array([l[0] for l in X_vecs(cif, 'nodes', True)])
        nodlabels = np.array([l[0] for l in node_vecs(n[0], TG, unit_cell, True)])

        bbxvec = X_vecs(cif, 'nodes', False)
        nodvec = node_vecs(n[0], TG, unit_cell, False)
        
        rmsd,rot,tran = mag_superimpose(bbxvec, nodvec)
        aff_b = np.dot(bbxvec,rot) + tran
        laff_b = np.c_[bbxlabels,aff_b]
        lnodvec = np.c_[nodlabels,nodvec]
        
        asd = []
        asd_append = asd.append

        distance_matrix = np.zeros((len(laff_b),len(laff_b)))
        nrow = ncol = len(laff_b)
        
        for i in range(nrow):
            for j in range(ncol):
        
                v1 = laff_b[i]
                v1vec = np.array([float(q) for q in v1[1:]])
                v1vec /= norm(v1vec)
        
                v2 = lnodvec[j]
                v2vec = np.array([float(q) for q in v2[1:]])
                v2vec /= norm(v2vec)
        
                dist = np.linalg.norm(v1vec - v2vec)
                distance_matrix[i,j] += dist
        
        distances = []
        for i in range(nrow):
            for j in range(ncol):
                distances.append((distance_matrix[i,j],i,j))
        distances = sorted(distances, key=lambda x:x[0])
        
        used_edges = []
        
        for dist in distances:
        
            v1 = laff_b[dist[1]]
            v1vec = np.array([float(q) for q in v1[1:]])
            mag = np.linalg.norm(v1vec)
        
            v2 = lnodvec[dist[2]]
            ind = int(v2[0])
        
            edge_assign = ind
        
            if edge_assign not in used_edges:

                used_edges.append(edge_assign)
                asd_append([ind, v1[0], mag, v1vec, dist[0]])
                
                if dist[0] > 0.60:
                    message = "There is a nodular building block vector that deviates from its assigned edge by more large\nthis may be fixed during scaling, but don't count on it!\n"
                    message = message + "the deviation is for " + cif + " assigned to " + name + " for template " + template_name
                    warnings.warn(message)
            
            if len(used_edges) == ncol:
                break

        elad = dict((k[0], (k[1],k[2],k[3])) for k in asd)
        edge_assign_dict[name] = elad
    return edge_assign_dict
