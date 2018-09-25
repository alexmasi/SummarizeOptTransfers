#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import random


# setup command line interface
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("species_tree_file", action="store",
                    type=str, help="specify input species_tree file")

parser.add_argument("gene_tree_dir", action="store", type=str,
                    help="specify input gene_tree directory")

parser.add_argument("-o", action="store",
                    default="SummarizeOptTransfers_gene_output",
                    dest="output_dir", type=str, help="specify output name")

parser.add_argument("-D", action="store", default="2",
                    dest="duplication_event_cost", type=str,
                    help="specify a list of comma delimited " +
                    "duplication event costs (integers)")

parser.add_argument("-T", action="store", default="3",
                    dest="transfer_event_cost", type=str,
                    help="specify a list of comma delimited " +
                    "transfer event costs (integers)")

parser.add_argument("-L", action="store", default="1", dest="loss_event_cost",
                    type=str, help="specify a list of comma delimited " +
                    "loss event costs (integers)")

parser.add_argument("--family_seed", action="store", default=False, dest="family_seed",
                    type=int, help="set the seed value (integer) used to " +
                    "select gene tree from family, if False then random integer is chosen")

parser.add_argument("-n", action="store", default=100, dest="sample_value",
                    type=int, help="set the number of sampled optimal " +
                    "reconciliations for each rooting")

parser.add_argument("--ranger_seed", action="store", default=False, dest="ranger_seed",
                    type=int, help="set the seed value (integer) used in " +
                    "Ranger-DTL, if False then random integer is chosen")

parser.add_argument("--dated", action="store_true", default=False,
                    dest="dated", help="use dated version of Ranger-DTL")

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

parser.add_argument("--short", action="store_true", default=False,
                    dest="short", help="shorten runtime by not " +
                    "running MaxTiC or SummarizeMaxTiC")

parser.add_argument("-s", action="store", default=180,
                    dest="local_search_time", type=int,
                    help="specify a local search time (in seconds) " +
                    "to improve MaxTiC results")

parser.add_argument("--quiet", action="store_true", default=False,
                    dest="quiet", help="suppress process output")

parser.add_argument("--version", action="version", version="%(prog)s 1.0")

arguments = parser.parse_args()

# initial setup
project_addr = os.getcwd() + "/"
species_tree_file_addr = os.path.abspath(arguments.species_tree_file)
gene_trees_dir_addr = os.path.abspath(arguments.gene_tree_dir) + "/"
output_dir_addr = os.path.abspath(arguments.output_dir) + "/"
output_dir_addr_root = output_dir_addr + "SummarizeOptRootings_out/"
output_dir_addr_trans = output_dir_addr + "SummarizeTransfers_out/"
output_dir_addr_max = output_dir_addr + "MaxTiC_out/"
if os.path.exists(output_dir_addr):
    raise OSError("Directory with the given output name already exists: " +
                  "use ' - o' to change output name to one that does " +
                  "not conflict with an existing directory.")
os.mkdir(output_dir_addr)
os.mkdir(output_dir_addr_root)
os.mkdir(output_dir_addr_trans)
os.mkdir(output_dir_addr_max)


def run_SummarizeOptRootings_recipient(gene_tree_file, gene_tree_name):
    # create input file from species tree and gene tree
    cmd = ("cat " + species_tree_file_addr + " " + gene_tree_file +
           " > " + output_dir_addr_root + "tempOptRootIn")
    subprocess.check_call(cmd, shell=True)
    # call SummarizeOptRootings_recipient with correct parameters
    cmd = ["python3", "SummarizeOptRootings_recipient.py", "-i",
           output_dir_addr_root + "tempOptRootIn", "-o",
           output_dir_addr_root + gene_tree_name,
           "-D", arguments.duplication_event_cost, "-T",
           arguments.transfer_event_cost, "-L", arguments.loss_event_cost,
           "-n", str(arguments.sample_value)]
    if arguments.quiet:
        cmd.append("--quiet")
    if arguments.dated:
        cmd.append("--dated")
    if arguments.ranger_seed is not False:
        cmd.append("--seed")
        cmd.append(str(arguments.ranger_seed))
    subprocess.check_call(cmd)


def run_SummarizeTransfers():
    # call SummarizeTransfers with long folder input
    cmd = ["python3", "SummarizeTransfers.py",
           output_dir_addr + "species_tree_label", output_dir_addr_root,
           "-o", output_dir_addr_trans + "SummarizeTransfers_output",
           "-t", str(arguments.transfer_confidence_percentage),
           "-m", str(arguments.mapping_confidence_percentage),
           "-r", str(arguments.recipient_confidence_percentage),
           "-c", str(arguments.cutoff_value)]
    if arguments.quiet:
        cmd.append("--quiet")
    if arguments.internal:
        cmd.append("--internal")
    subprocess.check_call(cmd)


def run_MaxTiC():
    # call MaxTiC with constraints
    cmd = ["python", "MaxTiC.py", output_dir_addr + "species_tree_label",
           output_dir_addr_trans + "SummarizeTransfers_output_constraints",
           "ls=" + str(arguments.local_search_time)]
    with open(output_dir_addr_max + "MaxTiC_console_output", "w") as outfile:
        subprocess.check_call(cmd, stdout=outfile)
    outfile.close()


def run_SummarizeMaxTiC():
    # call SummarizeMaxTiC
    cmd = ["python3", "SummarizeMaxTiC.py",
           output_dir_addr_max + "MaxTiC_console_output",
           output_dir_addr_max + "MaxTiC_consistent",
           output_dir_addr_trans + "SummarizeTransfers_output",
           "-o", output_dir_addr + "maximal_consistent_set_constraints"]
    subprocess.check_call(cmd)


def main():
    # run SummarizeOptRootings_recipient on gene trees
    if not arguments.quiet:
        print("Running SummarizeOptRootings_recipient...")
    if arguments.family_seed is not False:
        random.seed(arguments.family_seed)
    for gene_tree in os.listdir(gene_trees_dir_addr):
        # choose a random gene tree from file
        with open(gene_trees_dir_addr + gene_tree) as infile, \
                open(output_dir_addr_root + "temp_gene_tree", "w") as outfile:
            num_trees = len(infile.readlines())
            rand_gene_tree = "\n"
            while rand_gene_tree == "\n":  # make sure selected line is not \n
                infile.seek(0)
                rand_num = random.randrange(num_trees)
                rand_gene_tree = infile.readlines()[rand_num]
            outfile.write(rand_gene_tree)
        print("Gene tree " + str(rand_num + 1) + " out of " + str(num_trees) +
              ": " + rand_gene_tree)
        infile.close()
        outfile.close()
        run_SummarizeOptRootings_recipient(output_dir_addr_root +
                                           "temp_gene_tree", gene_tree)
    # handle SummarizeOptRootings_recipient output
    os.remove(output_dir_addr_root + "tempOptRootIn")
    os.remove(output_dir_addr_root + "temp_gene_tree")
    shutil.move(project_addr + "tempOptRootOut_species_tree_label",
                output_dir_addr + "species_tree_label")
    # run SummarizeTransfers on long output folder
    if not arguments.quiet:
        print("Running SummarizeTransfers...")
    run_SummarizeTransfers()
    # check if no transfers were found
    with open(output_dir_addr_trans +
              "SummarizeTransfers_output_constraints") as infile:
        none_check = infile.read().strip()
    infile.close()
    # skip MaxTiC if desired
    if not arguments.short:
        if not (none_check == "None found"):
            # run MaxTiC on constraints
            if not arguments.quiet:
                print("Running MaxTiC...")
            run_MaxTiC()
            # handle MaxTiC output
            shutil.move(output_dir_addr_trans +
                        "SummarizeTransfers_output_constraints_MT_output" +
                        "_filtered_list_of_weighted_informative_constraints",
                        output_dir_addr_max + "MaxTiC_informative")
            shutil.move(output_dir_addr_trans +
                        "SummarizeTransfers_output_constraints_MT_output" +
                        "_list_of_constraints_conflicting_with_best_order",
                        output_dir_addr_max + "MaxTiC_conflicting")
            shutil.move(output_dir_addr_trans +
                        "SummarizeTransfers_output_constraints_MT_output" +
                        "_partial_order",
                        output_dir_addr_max + "MaxTiC_consistent")
            # run SummarizeMaxTiC
            if not arguments.quiet:
                print("Running SummarizeMaxTiC...")
            run_SummarizeMaxTiC()
    if not arguments.quiet:
        print("Complete")


if __name__ == "__main__":
    main()
