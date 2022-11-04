import glob
import ast
import os
import re
import numpy as np

def nn(string):
    return re.sub('[^a-zA-Z]','', string)

def nl(string):
    return re.sub('[^0-9]','', string)

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Write data file
def write_data(fname='data'):
    if (os.path.isdir("templates") and os.path.isdir("nodes") and os.path.isdir("edges")):
        templates = sorted(os.listdir("templates"))
        nodes = sorted(os.listdir("nodes"))
        edges = sorted(os.listdir("edges"))
    else:
        print("Missing templates/nodes/edges directory")
        return 1
    if (len(templates) == 0) or (len(nodes)==0) or (len(edges)==0):
        print("templates/nodes/edges directory is empty")
        return 1
    else:
        # Create dictionary for templates, nodes and edges
        temp_dict = {int(key): value for (key,value) in enumerate(templates)}
        node_dict = {int(key): value for (key,value) in enumerate(nodes)}
        edge_dict = {int(key): value for (key,value) in enumerate(edges)}

        # Write the dictionary to a file
        data = open(fname,"w")
        data.write("TEMPLATES\n")
        for key, item in temp_dict.items():
            data.write("%d %s\n"%(key,item))
        data.write("NODES\n")
        for key, item in node_dict.items():
            data.write("%d %s\n"%(key,item))
        data.write("EDGES\n")
        for key, item in edge_dict.items():
            data.write("%d %s\n"%(key,item))
        data.close()

# Read data file
def read_database(fname='data'):
    if os.path.isfile(fname):
        f = open(fname, 'r')
        data = f.read()
        data = list(filter(None, data.split('\n')))

        # Get the index of templates, nodes and edges
        t_index = data.index('TEMPLATES')
        n_index = data.index('NODES')
        e_index = data.index('EDGES')
        
        # Get all templates, nodes and edges
        templates = data[t_index+1 : n_index]
        nodes = data[n_index+1: e_index]
        edges = data[e_index+1:] 
        
        # Get all templates
        gene_t = []
        name_t = []

        for template in templates:
            t = template.split()
            gene_t.append(t[0])
            name_t.append(t[1])

        gene_n = []
        name_n = []
        for node in nodes:
            n = node.split()
            gene_n.append(n[0])
            name_n.append(n[1])
        
        gene_e = []
        name_e = []

        for edge in edges:
            e = edge.split()
            gene_e.append(e[0])
            name_e.append(e[1])
        # Create dictionaries for template, node and edge
        temp_dict = {int(key): value for (key,value) in zip(gene_t, name_t)}
        node_dict = {int(key): value for (key,value) in zip(gene_n, name_n)}
        edge_dict = {int(key): value for (key,value) in zip(gene_e, name_e)}
        return temp_dict, node_dict, edge_dict
    else:
        print("Error with read_database")

def read_preconstructed_data(fname):
    import ast
    data = []

    # Read first line to know how many columns
    with open(fname, "r") as f:
        first_line = f.readline()
        n_column = len(list(filter(None, first_line.strip().split("|"))))

    # Read data file
    with open(fname, "r") as f:
        data = [[] for k in range(n_column)]
        
        for line in f:
            try:
                d = list(filter(None, line.strip().split("|")))
                for index, value in enumerate(d):
                    if index == 0:
                        data[index].append(ast.literal_eval(d[0]))
                    if index == 1:
                        data[index].append(d[1])
                    if index >= 2:
                        data[index].append(float(value))
            except ValueError:
                print("Error reading data file at line {}".format(line))
                return 1
    return data
# Todo: Automatically recognize size of the constructed_data
def read_constructed_data(fname='fixed_data.txt'):
    mof_name_list = []
    mof_chromosome_list = []
    mof_prop_list = []
    mof_prop_list2 = []
    with open(fname, "r") as f:
        for line in f:
            data = line.strip().split("|")
            mof_chromosome_list.append(ast.literal_eval(data[0]))
            mof_name_list.append(data[1])
            mof_prop_list.append(data[2])

            if len(data) == 4:
                mof_prop_list2.append(data[3])
    if len(mof_prop_list2) == 0:
        return mof_chromosome_list, mof_name_list, mof_prop_list
    else:
        return mof_chromosome_list, mof_name_list, mof_prop_list, mof_prop_list2

# Read template cif files. Return the number of nodes, number of connection points for each node, and number of edges

# 3 functins isfloat(), isvert() and isedge() are adopted from ToBaCCo 3.0 code
def nn(string):
    return re.sub('[^a-zA-Z]','', string)

def get_mof_objective(output_dir, preconstruct_file=None, fname="mof_analyze.txt"):
    import pandas as pd
    N_generation = glob.glob(os.path.join(output_dir,"generation_*/"))
    pre_generation = output_dir + '/' + 'generation_' + str(len(N_generation)-1) + '/'
    data_all = read_preconstructed_data(preconstruct_file)

    # Single objective
    if len(data_all) == 3:
        kc = data_all[0]
        kn = data_all[1]
        kp = data_all[2]

        data_current = read_preconstructed_data(pre_generation +"/" + "mof_list.txt")
        cc = data_current[0]
        cn = data_current[1]
        cp = []
        for k in cc:
            index = kc.index(k)
            cp.append(kp[index])

        output = list(zip(cc, cn, cp))
        df = pd.DataFrame(output)
        df.to_csv(pre_generation + "/" + fname, index=False, header=False, sep='|')
    # Two objectives
    elif len(data_all) == 4:
        kc = data_all[0]
        kn = data_all[1]
        kp1 = data_all[2]
        kp2 = data_all[3]

        data_current = read_preconstructed_data(pre_generation +"/" + "mof_list.txt")
        cc = data_current[0]
        cn = data_current[1]
        cp1 = []
        cp2 = []
        for k in cc:
            index = kc.index(k)
            cp1.append(kp1[index])
            cp2.append(kp2[index])

        output = list(zip(cc, cn, cp1, cp2))
        df = pd.DataFrame(output)
        df.to_csv(pre_generation + "/" + fname, index=False, header=False, sep='|')

    elif len(data_all) == 5:
        kc = data_all[0]
        kn = data_all[1]
        kp1 = data_all[2]
        kp2 = data_all[3]
        kp3 = data_all[4]

        data_current = read_preconstructed_data(pre_generation +"/" + "mof_list.txt")
        cc = data_current[0]
        cn = data_current[1]
        cp1 = []
        cp2 = []
        cp3 = []
        for k in cc:
            index = kc.index(k)
            cp1.append(kp1[index])
            cp2.append(kp2[index])
            cp3.append(kp3[index])
        output = list(zip(cc, cn, cp1, cp2, cp3))
        df = pd.DataFrame(output)
        df.to_csv(pre_generation + "/" + fname, index=False, header=False, sep='|')

def get_mof_objective2(output_dir, fname="mof_analyze.txt"):
    N_generation = glob.glob(os.path.join(output_dir,"generation_*/"))
    pre_generation = output_dir + '/' + 'generation_' + str(len(N_generation)-1) + '/'
    
    with open(pre_generation + '/' + 'mof_list.txt', 'r') as f:
        data = f.readlines()
        data = [i.strip().split('|') for i in data]
    chromosomes = [ast.literal_eval(i[0]) for i in data]
    names = [i[1] for i in data]
    objectives = [46 - i[0] -i[1] - i[2] - i[3] for i in chromosomes]
    with open(pre_generation + '/' + fname, 'w') as f:
        for c, n, o in zip(chromosomes, names, objectives):
            f.write("{}|{}|{}\n".format(c, n, o))
    
