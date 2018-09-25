#!/usr/bin/env python3

import os
import argparse


# setup command line interface
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("transfer_dir", action="store", type=str,
                    help="specify input transfer directory")

parser.add_argument("-o", action="store", default="CombineTransfers_output",
                    dest="output_file", type=str, help="specify output file")

parser.add_argument("-c", action="store", default=100, dest="confidence",
                    type=int, help="specify confidence percentage value")

parser.add_argument("--version", action="version", version="%(prog)s 1.0")

arguments = parser.parse_args()

# initial setup
dir_addr = os.getcwd() + "/"
transfer_dir_addr = os.path.abspath(arguments.transfer_dir) + "/"
output_file_addr = os.path.abspath(arguments.output_file)
transfers_combined = {}
transfers_support = {}
transfers_data = {}
num_transfer_files = len(os.listdir(transfer_dir_addr))

# scan each input file one at a time
for transfer_file in os.listdir(transfer_dir_addr):
    with open(transfer_dir_addr + transfer_file) as infile:
        for line in infile:
            if "Species tree:" in line:
                species_tree_line = line
            if "with confidence values:" in line:
                line_list = line.split(", ")
                pair = line_list[0].split(" --> ")
                donor = pair[0]
                rec = pair[1]
                tcon = line_list[2].split(": ")[2].split(" %")[0]
                dcon = line_list[3].split(": ")[1].split(" %")[0]
                rcon = line_list[4].split(": ")[1].split(" %")[0]
                donor_depth = line_list[5].split(": ")[1]
                rec_depth = line_list[6].split(": ")[1]
                dist = line_list[7].split(": ")[1].split(".")[0]
                next_line = next(infile)
                support = next_line.strip().split(", ")
                support[0] = support[0].split(": ")[1]
                k = tuple([donor, rec])
                if k not in list(transfers_data.keys()):
                    transfers_data[k] = [tcon, dcon, rcon,
                                         donor_depth, rec_depth, dist]
                for f in support:
                    k = tuple([donor, rec, f])
                    try:
                        transfers_support[k] += 1
                    except KeyError:
                        transfers_support[k] = 1
    infile.close()

# filter supports
cutoff = round((arguments.confidence / 100) * num_transfer_files)
for k in list(transfers_support.keys()):
    if transfers_support[k] >= cutoff:
        try:
            transfers_combined[k[:2]][1].add(k[2])
        except KeyError:
            transfers_combined[k[:2]] = [transfers_data[k[:2]], {k[2]}]

for k in list(transfers_combined.keys()):
    num_files = len(transfers_combined[k][1])
    transfers_combined[k].append(num_files)

# output transfer pairs
with open(output_file_addr, "w") as outfile:
    outfile.write(species_tree_line)
    outfile.write("Input directory: " + transfer_dir_addr + "\n")
    outfile.write("Number of files in directory: " + str(num_transfer_files) + "\n")
    outfile.write("Confidence percentage: " + str(arguments.confidence) + "\n\n")
    outfile.write("Optimal transfer pairs (mapping --> recipient):\n\n")
    for pair in sorted(transfers_combined.keys(),
                       key=transfers_combined.get,
                       reverse=True):
        outfile.write(pair[0] + " --> " + pair[1] + ", " +
                      str(transfers_combined[pair][2]) +
                      " time(s), with confidence values: Transfer: " +
                      transfers_combined[pair][0][0] + " %, Mapping: " +
                      transfers_combined[pair][0][1] + " %, Recipient: " +
                      transfers_combined[pair][0][2] + " %, Donor depth: " +
                      transfers_combined[pair][0][3] + ", Recipient depth: " +
                      transfers_combined[pair][0][4] + ", Distance: " +
                      transfers_combined[pair][0][5] + ".\n")
        outfile.write("Files supporting transfer: " +
                      ", ".join(tree for tree in transfers_combined[pair][1])
                      + "\n")
    if transfers_combined == {}:
        outfile.write("None found\n")
outfile.close()
