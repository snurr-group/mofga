import os
from collections import OrderedDict
import glob
import subprocess

# List of vertices name used in tobacco template files
vertices = ('V' , 'Er', 'Ti', 'Ce', 'S',
            'H' , 'He', 'Li', 'Be', 'B',
            'C' , 'N' , 'O' , 'F' , 'Ne',
            'Na', 'Mg', 'Al', 'Si', 'P',
            'Cl', 'Ar', 'K' , 'Ca', 'Sc',
            'Cr', 'Mn', 'Fe', 'Co', 'Ni')

def generate_cif_from_chromosome(chromosome, tobacco_path, template_info, temp_dict, node_dict, edge_dict, avoid_BOND_CHECK=True, tobacco_output=True, output_dir=None):
    template_path = os.path.join(tobacco_path,"templates/")
    node_path = os.path.join(tobacco_path,"nodes/")
    edge_path = os.path.join(tobacco_path, "edges/")
    output_path = os.path.join(tobacco_path, "output_cifs/")
    pwd = os.getcwd()

    template = temp_dict.get(chromosome[0])
    t_info = template_info[chromosome[0]]

    n_node = 0
    n_edge = 0
    vertice_name = []
    for i, k in enumerate(t_info):
        if i == 0:
            continue
        else:
            k = k.split('-')
            if k[0] in vertices:
                n_node += 1
                vertice_name.append(k[0])
            if k[0] == 'edge':
                n_edge += 1

    v_set = [node_dict.get(chromosome[i]) for i in range(1,n_node+1)]
    e_set = list(OrderedDict.fromkeys([edge_dict.get(chromosome[i]) for i in range(n_node+1,len(chromosome))]))

    # Create vertex_assigment.txt file for tobacco
    with open(os.path.join(tobacco_path,"vertex_assignment.txt"),"w") as f:
        for vertex, node in zip(vertice_name, v_set):
            f.write("{} {}\n".format(vertex, node))
    # Remove existing templates, nodes, and output_cifs directory in tobacco. Then create empty ones
    if os.path.isdir(template_path):
        subprocess.run('rm -r {}'.format(template_path), shell=True)
    os.makedirs(template_path)
    if os.path.isdir(node_path):
        subprocess.run('rm -r {}'.format(node_path), shell=True)
    os.makedirs(node_path)
    if os.path.isdir(edge_path):
        subprocess.run('rm -r {}'.format(edge_path), shell=True)
    os.makedirs(edge_path)
    if os.path.isdir(output_path):
        subprocess.run('rm -r {}'.format(output_path), shell=True)
    os.makedirs(output_path)

    # Copy template and nodes to tobacco
    subprocess.run("cp templates/{} {}".format(template,template_path), shell=True)
    for v in v_set:
        subprocess.run("cp nodes/{} {}".format(v,node_path), shell=True)
    
    # Rename edge in specific order
    edge_rename = ['XYZ0.cif','XYZ1.cif','XYZ2.cif','XYZ3.cif','XYZ4.cif','XYZ5.cif','XYZ6.cif','XYZ7.cif','XYZ8.cif','XYZ9.cif','XYZ10.cif']
    new_edge_name = edge_rename[:len(e_set)]
    for old_name, new_name in zip(e_set,new_edge_name):
        subprocess.run("cp edges/{} {}/{}".format(old_name,edge_path,new_name), shell=True)
    os.chdir(tobacco_path)
    if tobacco_output == False:
        subprocess.run("python tobacco.py", shell=True, stdout=subprocess.DEVNULL)
    else:
        subprocess.run("python tobacco.py", shell=True)

    cifout = glob.glob(output_path+'/*')
    os.chdir(pwd)

    if len(cifout) == 1:
        current_name = glob.glob(output_path+'/*')[0]
        updated_name = str(current_name)
        for old_name, new_name in zip(e_set,new_edge_name):
            updated_name = updated_name.replace(new_name[0:-4],old_name[0:-4])
        subprocess.run("mv {} {}".format(current_name,updated_name), shell=True)

        if avoid_BOND_CHECK == True:
            """ Ignore structure with 'BOND_CHECK' in name """
            if 'BOND_CHECK' in updated_name:
                return 1, 'BOND_CHECK'
        if output_dir != None:
            mof_name = updated_name.split('/')[-1]
            subprocess.run("mv {} {}".format(updated_name, output_dir), shell=True)
            return 0, mof_name

    if len(cifout) == 0:
        print("Error in creating MOF with chromosome {}. No MOF was created".format(chromosome))
        return 1, 'Error'
    elif len(cifout) >= 2:
        print("Error in creating MOF with chromosome {}. More than 1 MOF created".format(chromosome))
        return 1, 'Error'

