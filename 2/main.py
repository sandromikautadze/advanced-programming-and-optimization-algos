import numpy as np
import networkx as nx

pics = {} # dict to save each picture

files = [f"P{i}.txt" for i in range(16)] # list of all .txt files

# reading the files
for file in files:
    with open(file) as f:
        pics[file] = np.zeros((10, 80), dtype= int)
        for i, line in enumerate(f): # i corresponds to row number, so i = 0, ..., 9
            line = line.replace("", " ").split()
            for j in range(len(line)): # j corresponds to column number, so j = 0, ..., 79
                if int(line[j]) != 0:
                    pics[file][i, j] = int(line[j])

# Explanation of the above lines:
# For every file we create the corresponding key in pics, whose initial element is a 10x80 matrix filled with zeros.
# Then, after modifying a bit the lines in the file, we append the nonzero element of the file to the corresponding
# index in the matrix, hence mapping the txt file to its corresponding matrix (stored as a 2d numpy array)

def nonzero(file):
    """Returns nonzero coordinates and corresponding weight of a given file

    Args:
        file (np.array): 10x80 matrix of brightness of file

    Returns:
        list: list of tuples of 3 elements, first two elements are the coordinates, last one is the weight 
    """
    
    xyw_file = []
    assert file.shape[0] == 10 and file.shape[1] == 80 # check dimensions are correct
    
    for i in range(file.shape[0]): # rows (so y-coordinate)
        for j in range(file.shape[1]): # columns (so x-coordinate)
            if file[i, j] != 0:
                if file is pics["P10.txt"]:
                    xyw_file.append((i + 1, j + 1, file[i, j] * 80)) # normalize weight
                else:
                    xyw_file.append((i + 1, j + 1, file[i, j] * 39)) 
                        
    return xyw_file

def comp_dist(file1, file2):
    """Computes the EMD distance between file1 and file2

    Args:
        file1 (np.array): 10x80 matrix of brightness of file
        file2 (np.array): 10x80 matrix of brightness of file

    Returns:
        float: the EMD distance
    """
    # edge case with same file 
    if str(file1) == str(file2):
        return float(0)
    
    xyw_file1 = nonzero(file1) # note that xyw should be yxw based on nonzero's output, but the naming's not important
    xyw_file2 = nonzero(file2)
    
    # building the graphs
    G_file1 = nx.DiGraph()
    G_file2 = nx.DiGraph()
    
    # adding nodes
    G_file1.add_nodes_from(xyw_file1)
    for node in G_file1.nodes():
        #G.file1_nodes[node] returns a dict with the attributes of the node. So we're creating a new key with the weight demand
        G_file1.nodes[node]["demand"] = -node[2]
    G_file2.add_nodes_from(xyw_file2)
    for node in G_file2.nodes():
        G_file2.nodes[node]["demand"] = node[2]
    
    # graph to calculate the EMD
    G_flow = nx.compose(G_file1, G_file2)
    for node1 in G_file1.nodes():
        for node2 in G_file2.nodes():
            d1 = node1[1] # column
            d2 = node2[1]
            dist = (d2 - d1)%80 # by doing so we follow the jellyfish from left to right, so to speak
            G_flow.add_edge(node1, node2,
                            weight = dist)
            
    # solving the flow for the EMD
    emd = nx.min_cost_flow_cost(G_flow)
    
    return float(emd)

def sort_files():
    """It sorts the files in order, from left to right, starting from P1.txt

    Returns:
        list: the sorted list of files based on the EMD distance
    """
    
    files = ['P1.txt', 'P2.txt', 'P3.txt', 'P4.txt', 'P5.txt', 'P6.txt', 'P7.txt', 'P8.txt', 'P9.txt', 'P10.txt', 'P11.txt', 'P12.txt', 'P13.txt', 'P14.txt', 'P15.txt']
    
    # it's enough to compute dist from P1
    distances = {}
    for file in files[1:]:
        distances[file] = comp_dist(pics[files[0]], pics[file])    
    
    sorted_files = [k for k, v in sorted(distances.items(), key=lambda item: item[1])]
    sorted_files.insert(0, "P1.txt")
    
    # should return sorted list of file names
    return sorted_files
