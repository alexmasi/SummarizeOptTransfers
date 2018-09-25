#!/usr/bin/env python3

import os
import argparse
import ete3


# setup command line interface
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("MaxTiC_console", action="store", type=str,
                    help="specify MaxTiC_console_output file")

parser.add_argument("MaxTiC_consistent", action="store",
                    type=str, help="specify MaxTiC_consistent file")

parser.add_argument("SummarizeTransfers_output", action="store",
                    type=str, help="specify SummarizeTransfer_output file")

parser.add_argument("-o", action="store", default="SummarizeMaxTiC_output",
                    dest="output_file", type=str, help="specify output file")

arguments = parser.parse_args()

# initial setup
dir_addr = os.getcwd() + "/"
MaxTiC_console_addr = os.path.abspath(arguments.MaxTiC_console)
MaxTiC_consistent_addr = os.path.abspath(arguments.MaxTiC_consistent)
SummarizeTransfers_output_addr = os.path.abspath(
    arguments.SummarizeTransfers_output)
output_file_addr = os.path.abspath(arguments.output_file)
# consistent[pair] = [strength of constraint(int), donor depth,
#                     recipient depth,
#                     {set of long files that support constraint}]
consistent = {}
# transfers[pair] = [# occurences, {set of long files that support trans}]
transfers = {}
# create children dictionary, children["parent"] = ["child1", "child2"]
children = {}
# create depth dictionary, depth["node"] = depth of node
depth = {}


# scan transfers file
with open(SummarizeTransfers_output_addr) as infile:
    for line in infile:
        if "Species tree:" in line:
            species_tree = line.split("tree: ")[1]
        if "time(s), with confidence values:" in line:
            L = line.split(", ")
            pair = tuple(L[0].split(" --> "))
            num = L[1].split(" ")[0]
            next_line = next(infile)
            next_L = next_line.split(": ")
            support_str = next_L[1].strip()
            support_L = support_str.split(", ")
            transfers[pair] = [num, set()]
            for fn in support_L:
                transfers[pair][1].add(fn)
infile.close()


# create tree object from species tree
t = ete3.Tree(species_tree, format=8)
for node in t.traverse("preorder"):
    # get the children of this node:
    if not node.is_leaf():  # if it is not a leaf node
        children[node.name] = [child.name for child in node.children]
    if node.is_root():  # if it is the root node
        depth[node.name] = 0
    else:
        depth[node.name] = depth[node.up.name] + 1


# scan console file
with open(MaxTiC_console_addr) as infile:
    ranked_tree = infile.readlines()[-3]
infile.close()


# scan consistent file
with open(MaxTiC_consistent_addr) as infile:
    for line in infile:
        L = line.split(" ")
        pair = tuple(L[:2])
        consistent[pair] = [int(float(L[2])),
                            depth[pair[0]],
                            depth[pair[1]],
                            int(t.get_distance(pair[0], pair[1])), set()]
infile.close()


# combine transfer support sets
for pair in consistent.keys():
    donor = pair[0]
    rec = pair[1]
    try:
        support_set1 = transfers[tuple([children[donor][0], rec])][1]
    except KeyError:
        support_set1 = set()
    try:
        support_set2 = transfers[tuple([children[donor][1], rec])][1]
    except KeyError:
        support_set2 = set()
    final_set = support_set1 | support_set2
    consistent[pair][4] = final_set


# output transfer pairs
with open(SummarizeTransfers_output_addr) as infile, \
     open(output_file_addr, "w") as outfile:
    for line in infile.readlines()[:7]:
        outfile.write(line)
    outfile.write("Ranked species tree: " + ranked_tree + "\n")
    outfile.write("Optimal constraint pairs (older --> younger):\n\n")
    # for pair in consistent.keys():
    for pair in sorted(consistent.keys(),
                       key=consistent.get,
                       reverse=True):
        outfile.write(pair[0] + " --> " + pair[1] +
                      ", support strength: " + str(consistent[pair][0]) +
                      ", Donor depth: " + str(consistent[pair][1]) +
                      ", Recipient depth: " + str(consistent[pair][2]) +
                      ", Distance: " + str(consistent[pair][3]) +
                      ", support files: " +
                      ", ".join(fn for fn in consistent[pair][4]) + "\n")
    if consistent == {}:
        outfile.write("None found\n")
infile.close()
outfile.close()
