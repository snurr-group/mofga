import os
import ast
from utils import read_database, write_data

write_data()

def get_key(my_dict, val):
    for key, value in my_dict.items():
        if val == value:
            return key

v_info = "tobacco/vertex_info.txt"
data = []
t_indices = []
templates_dict = {}
with open(v_info, 'r') as f:
    for index, line in enumerate(f):
        data.append(line.strip('\n'))
        if 'TEMPLATE' in line:
            t_indices.append(index)
for index, k in enumerate(t_indices):
    if index < len(t_indices) - 1:
        templates_dict[data[k][9:]] = {}
        templates_dict[data[k][9:]]['edge'] = ast.literal_eval(data[k+1])
        for i in range(t_indices[index]+2, t_indices[index+1]):
            line = data[i].split('|')
            line[0] = eval(line[0])
            templates_dict[data[k][9:]][line[0]] = ast.literal_eval(line[1])
    else:
        templates_dict[data[k][9:]] = {}
        templates_dict[data[k][9:]]['edge'] = ast.literal_eval(data[k+1])
        for i in range(t_indices[index]+2, len(data)):
            line = data[i].split('|')
            line[0] = eval(line[0])
            templates_dict[data[k][9:]][line[0]] = ast.literal_eval(line[1])

# Remove template with at least one node with no cif compatibility
template_empty_node = []
for i in templates_dict:
    for j in templates_dict[i]:
        if len(templates_dict[i][j]) == 0:
            template_empty_node.append(i)
            continue
for i in template_empty_node:
    templates_dict.pop(i, None)

chromosome_representations = []
template_list = []
template_label, node_label, edge_label = read_database()

# Generate chromosome representation
for template in templates_dict:
    template_list.append(template)
    chr_rep = ['template']
    edges = templates_dict[template]['edge']
    vertices = {}
    for item in templates_dict[template]:
        if item != 'edge':
            vertices[item[1]] = item[0]
            chr_rep.append(item[1] + '-' + str(item[0]) + 'c')
    for edge in edges:
        c1 = edge[0]
        c2 = edge[1]
        v1 = str(vertices[c1]) + 'c'
        v2 = str(vertices[c2]) + 'c'
        edge_ = sorted([v1, v2], reverse=True)
        chr_rep.append('-'.join(edge_))
    chromosome_representations.append(chr_rep)
final = []    
for t, chr_ in zip(template_list, chromosome_representations):
    final.append([t, chr_])
for i, t in enumerate(final):
    label = get_key(template_label, t[0])
    final[i][0] = label
with open('template_params.py', 'w') as f:
    f.write("template_info = {\n")
    for i, t in enumerate(final):
        f.write("{}:{},\n".format(str(t[0]),t[1]))
    f.write('}\n')
    f.write("bb_options = {\n")
# Generate template compatibility    

for i, k in enumerate(templates_dict):
    vertices = []
    compatible = []
    labels = []
    chromosome_count = 0
    t_label = get_key(template_label, k)
    edge =[]
    for ii, kk in enumerate(templates_dict[k]):
        if kk == 'edge':
            #edge.append(range(len(edge_label)))
            continue
        else:
            vertices.append(chromosome_count + 1)
            compatible.append(templates_dict[k][kk])
            labels.append([])
            for cif in compatible[chromosome_count]:
                labels[chromosome_count].append(get_key(node_label, cif))
            labels[chromosome_count] = sorted(labels[chromosome_count])
            chromosome_count += 1            
    n_edge = len(templates_dict[k]['edge'])            
    node_info= [str(vertices[i_]) + ':' + str(labels[i_]) for i_ in range(len(labels))]
    edge_info = [str(len(labels)+i+1) + ':' + "list(range({}))".format(len(edge_label)) for i in range(n_edge)]
    with open('template_params.py', 'a') as f:
        f.write("{}: {{0:list(range({})), {}, {} }},\n".format(t_label, len(template_label), ','.join(node_info), ','.join(edge_info)))
with open('template_params.py', 'a') as f:
    f.write('}')
