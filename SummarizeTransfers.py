#!/usr/bin/env python3

import argparse
import ete3
import os
import shutil


# setup command line interface
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("species_tree_file", action="store",
                    type=str, help="specify labeled species_tree file")

parser.add_argument("long_dir", action="store", type=str,
                    help="specify input directory of long files")

parser.add_argument("-o", action="store", default="SummarizeTransfers_output",
                    dest="output_file", type=str, help="specify output file")

parser.add_argument("-t", action="store", default=100,
                    dest="transfer_confidence_percentage", type=int,
                    help="specify a transfer confidence percentage value")

parser.add_argument("-m", action="store", default=100,
                    dest="mapping_confidence_percentage", type=int,
                    help="specify a mapping confidence percentage value")

parser.add_argument("-r", action="store", default=100,
                    dest="recipient_confidence_percentage", type=int,
                    help="specify a recipient confidence percentage value")

parser.add_argument("-c", action="store", default=1, dest="cutoff_value",
                    type=int, help="specify a cutoff value to filter out " +
                    "transfers with less confidence than cutoff")

parser.add_argument("--internal", action="store_true", default=False,
                    dest="internal", help="show internal nodes only")

parser.add_argument("--quiet", action="store_true", default=False,
                    dest="quiet", help="suppress process output")

parser.add_argument("--version", action="version", version="%(prog)s 1.0")

arguments = parser.parse_args()

# initial setup
dir_addr = os.getcwd() + "/"
species_tree_addr = os.path.abspath(arguments.species_tree_file)
long_dir_addr = os.path.abspath(arguments.long_dir) + "/"
output_file_addr = os.path.abspath(arguments.output_file)
# transfers_raw[pair] = [# occurences, transfer_confidence,
#                        mapping_confidence, recipient_confidence]
transfers_raw = {}
# transfers_norm[pair] = [# occurences, transfer_confidence,
#                         mapping_confidence, recipient_confidence]
transfers_norm = {}
# transfer_trees[pair] = {set of long file names that support transfer pair}
transfers_tree = {}
# create parent dictionary, parent["child"] = "parent of child"
parent = {}
# create depth dictionary, depth["node"] = depth from root
depth = {}
# create leaf set
leaves = set()
# read labeled species tree from file
with open(species_tree_addr) as infile:
    species_tree = infile.read().strip()
infile.close()

# scan each input file one at a time
for long_file in os.listdir(long_dir_addr):
    # initial parse for extra paramters
    with open(long_dir_addr + long_file) as infile:
        if not arguments.quiet:
            print("Parsing " + long_file + " ...")
        for line in infile:
            # get num optimal rootings
            if "The total number of optimal rootings is:" in line:
                num_rootings = int(line.split(": ")[1].split("\n")[0])
            # get sample size
            elif "Sample Size for each Optimal Rooting:" in line:
                sample_size = int(line.split(": ")[1].split("\n")[0])
            # get event costs
            elif "Duplication cost:" in line:
                event_costs = line
    infile.close()

    # change percentage to number of events
    transfer_confidence = (arguments.transfer_confidence_percentage
                           / 100 * sample_size)
    mapping_confidence = (arguments.mapping_confidence_percentage
                          / 100 * sample_size)
    recipient_confidence = (arguments.recipient_confidence_percentage
                            / 100 * sample_size)

    with open(long_dir_addr + long_file) as infile:
        for line in infile:
            # consider only lines with recipient data
            if "[Most Frequent recipient -->" in line:
                line_list = line.split("]")
                # get the confidence values
                lca = line_list[0] + "]"
                t_confidence = int(line_list[1].split("Transfers = ")[1])
                m_confidence = int(line_list[2].split(", ")[2].split(" ")[0])
                r_confidence = int(line_list[3].split(", ")[2].split(" ")[0])
                # compare the confidence values
                if t_confidence >= transfer_confidence:
                    t_confidence_percentage = (t_confidence
                                               / sample_size * 100)
                    if m_confidence >= mapping_confidence:
                        mapping = line_list[2].split("--> ")[1].split(",")[0]
                        m_confidence_percentage = (m_confidence
                                                   / sample_size * 100)
                        if r_confidence >= recipient_confidence:
                            recipient = line_list[3].split(
                                "--> ")[1].split(",")[0]
                            r_confidence_percentage = (r_confidence
                                                       / sample_size * 100)
                            # if everything is high confidence then add to dict
                            pair = tuple([mapping, recipient, lca])
                            confidence_list = [1, t_confidence_percentage,
                                               m_confidence_percentage,
                                               r_confidence_percentage]
                            # pair already in trans dict
                            try:
                                transfers_raw[pair] = [x + y for x, y in
                                                       zip(transfers_raw[pair],
                                                           confidence_list)]
                            # pair not yet in trans dict
                            except KeyError:
                                transfers_raw[pair] = confidence_list
                          #  # pair already in tree dict
                          #  try:
                          #      transfers_tree[pair[:2]].add(long_file)
                          #  # pair not yet in tree dict
                          #  except KeyError:
                          #      transfers_tree[pair[:2]] = {long_file}
    infile.close()

    # process pairs using number of rootings
    for pair in transfers_raw.keys():
        # check if consistent across all optimal rootings
        if transfers_raw[pair][0] == num_rootings:
            # normalize if more than 1 optimal rootings
            transfers_raw[pair] = [x /
                                   num_rootings for x in transfers_raw[pair]]
            # pair already in final dict
            try:
                transfers_norm[pair[:2]] = [x + y for x, y in
                                            zip(transfers_norm[pair[:2]],
                                                transfers_raw[pair])]
            # pair not yet in final dict
            except KeyError:
                transfers_norm[pair[:2]] = transfers_raw[pair]
            # pair already in tree dict
            try:
                transfers_tree[pair[:2]].add(long_file)
            # pair not yet in tree dict
            except KeyError:
                transfers_tree[pair[:2]] = {long_file}
    # init dict for next file
    transfers_raw = {}

# normalize across multiple occurences found
if not arguments.quiet:
    print("Normalizing identified transfers...")
for pair in transfers_norm.keys():
    occurences = transfers_norm[pair][0]
    if occurences != 1:
        transfers_norm[pair] = [x / occurences for x in transfers_norm[pair]]
        transfers_norm[pair][0] = occurences
    # round final numbers
    transfers_norm[pair] = [round(x) for x in transfers_norm[pair]]

# create tree object from species tree
t = ete3.Tree(species_tree, format=8)
for node in t.traverse("preorder"):
    # get the parent of this node:
    if node.is_root():  # if it is the root node
        parent[node.name] = "None"
        depth[node.name] = 0
    else:
        parent[node.name] = node.up.name
        depth[node.name] = depth[node.up.name] + 1
    if node.is_leaf():
        leaves.add(node.name)

if not arguments.quiet:
    print("Filtering transfers...")

# cutoff filtering
for pair in list(transfers_norm.keys()):
    if transfers_norm[pair][0] < arguments.cutoff_value:
        del transfers_norm[pair]

# internal filtering
if arguments.internal:
    for pair in list(transfers_norm.keys()):
        if pair[0] in leaves or pair[1] in leaves:
            del transfers_norm[pair]

# write constraints (family, older, younger, support) to file
with open(output_file_addr + "_constraints", "w") as outfile:
    for pair in transfers_norm.keys():
        outfile.write("none," + parent[pair[0]] + "," +
                      pair[1] + "," + str(transfers_norm[pair][0]) + "\n")
    if transfers_norm == {}:
        outfile.write("None found\n")
outfile.close()

# output transfer pairs
with open(output_file_addr, "w") as outfile:
    outfile.write("Species tree: " + species_tree + "\n")
    outfile.write("Long directory: " + arguments.long_dir + "\n")
    outfile.write("Number of long files: " +
                  str(len([name for name in
                           os.listdir(long_dir_addr)])) + "\n")
    outfile.write(event_costs)
    outfile.write("Confidence thresholds: Transfer: " +
                  str(arguments.transfer_confidence_percentage) +
                  " %, Mapping: " +
                  str(arguments.mapping_confidence_percentage) +
                  " %, Recipient: " +
                  str(arguments.recipient_confidence_percentage) + " %.\n")
    outfile.write("Cutoff value: " + str(arguments.cutoff_value) + "\n")
    outfile.write("Internal nodes only: " + str(arguments.internal) + "\n\n")
    outfile.write("Optimal transfer pairs (mapping --> recipient):\n\n")
    for pair in sorted(transfers_norm.keys(),
                       key=transfers_norm.get,
                       reverse=True):
        try:
            outfile.write(pair[0] + " --> " + pair[1] + ", " +
                        str(transfers_norm[pair][0]) +
                        " time(s), with confidence values: Transfer: " +
                        str(transfers_norm[pair][1]) + " %, Mapping: " +
                        str(transfers_norm[pair][2]) + " %, Recipient: " +
                        str(transfers_norm[pair][3]) + " %, Donor depth: " +
                        str(depth[pair[0]]) + ", Recipient depth: " +
                        str(depth[pair[1]]) + ", Distance: " +
                        str(int(t.get_distance(pair[0], pair[1]))) + ".\n")
        except ValueError:
            outfile.write(pair[0] + " --> " + pair[1] + ", " +
                        str(transfers_norm[pair][0]) +
                        " time(s), with confidence values: Transfer: " +
                        str(transfers_norm[pair][1]) + " %, Mapping: " +
                        str(transfers_norm[pair][2]) + " %, Recipient: " +
                        str(transfers_norm[pair][3]) + " %, Donor depth: " +
                        str(depth[pair[0]]) + ", Recipient depth: " +
                        str(depth[pair[1]]) + ", Distance: n/a.\n")
        outfile.write("Files supporting transfer: " +
                      ", ".join(tree for tree in transfers_tree[pair]) + "\n")
    if transfers_norm == {}:
        outfile.write("None found\n")
outfile.close()
