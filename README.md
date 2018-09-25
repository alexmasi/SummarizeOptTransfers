# SummarizeOptTransfers

An add-on to the phylogenetic [Ranger-DTL](http://compbio.engr.uconn.edu/software/RANGER-DTL/) framework that identifies likely **Horizontal Gene Transfers (HGTs)** to create a maximal consistent set of relative timing constraints.

**Summary**: Identifies transfers > Processes transfers > Removes contradictions > Creates constraints

## Getting Started

Before starting you will have to download the [Ranger-DTL](http://compbio.engr.uconn.edu/software/RANGER-DTL/) software.

### Prerequisites
To use `SummarizeOptTransfers` the following prerequisites will need to be installed:

1. **Python 2.7 or later** *and* **Python 3.6 or later**

2. python 2 scipy module
```
$ pip2 install scipy
```
3. python 3 six module
```
$ pip3 install six
```
4. python 3 numpy module
```
$ pip3 install numpy
```
5. python 3 ete3 module
```
$ pip3 install ete3
```


## Usage

### Main Programs
---
#### `SummarizeOptTransfers_gene.py`

**Description**: Python 3 script that uses `SummarizeOptRootings_recipient.py`, `SummarizeTransfers.py`, `MaxTiC.py`, and `SummarizeMaxTiC.py` to take a species tree and a directory of gene trees as input to return a directory of output data containing files with all of the most likely transfers (HGTs) and relative constraints along with their support values determined from the gene trees.

All input trees must be fully binary and expressed using the Newick format terminated by a semicolon.

The species tree must be rooted and species names in each tree must be unique. **Note: Internal nodes must not be labeled**.
```
ex. ((speciesA, speciesB), speciesC);
```
Each leaf in each gene tree must be labeled with the name of the species from which that gene was sampled.
```
ex. (((speciesA, speciesC), speciesB), speciesC);
```

**Input**: Species tree with unlabeled internal nodes, Directory of gene trees
```
$ python3 SummarizeOptTransfers_gene.py species_tree gene_tree_dir
```

**Output**: Directory of the following form:
```
|-- SummarizeOptTransfers_gene_output
    |-- MaxTiC_out
        |-- MaxTiC_conflicting
        |-- MaxTiC_consistent
        |-- MaxTiC_console_output
        |-- MaxTiC_informative
    |-- SummarizeOptRootings_out
        |-- long0001
        |-- ...
        |-- long9999
    |-- SummarizeTransfers_out
        |-- SummarizeTransfers_output
        |-- SummarizeTransfers_output_constraints
    |-- maximal_consistent_set_constraints
    |-- species_tree_label
```

**Optional parameters**:
```
-h, --help            show this help message and exit
-o OUTPUT_DIR         specify output name (default:
                      SummarizeOptTransfers_gene_output)
-D DUPLICATION_EVENT_COST
                      specify a list of comma delimited duplication event
                      costs (integers) (default: 2)
-T TRANSFER_EVENT_COST
                      specify a list of comma delimited transfer event costs
                      (integers) (default: 3)
-L LOSS_EVENT_COST    specify a list of comma delimited loss event costs
                      (integers) (default: 1)
-n SAMPLE_VALUE       set the number of sampled optimal reconciliations for
                      each rooting (default: 100)
--seed SEED_VALUE     set the seed value (integer) used in Ranger-DTL, if
                      false then random integer is chosen (default: False)
--dated               use dated version of Ranger-DTL (default: False)
-t TRANSFER_CONFIDENCE_PERCENTAGE
                      specify a transfer confidence percentage value
                      (default: 100)
-m MAPPING_CONFIDENCE_PERCENTAGE
                      specify a mapping confidence percentage value
                      (default: 100)
-r RECIPIENT_CONFIDENCE_PERCENTAGE
                      specify a recipient confidence percentage value
                      (default: 100)
-c CUTOFF_VALUE       specify a cutoff value to filter out transfers with
                      less confidence than cutoff (default: 1)
--internal            show internal nodes only (default: False)
--short               shorten runtime by not running MaxTiC or
                      SummarizeMaxTiC (default: False)
-s LOCAL_SEARCH_TIME  specify a local search time (in seconds) to improve
                      MaxTiC results (default: 180)
--quiet               suppress process output (default: False)
--version             show program's version number and exit
```

#### `SummarizeOptTransfers_long.py`

**Description**: Python 3 script that uses `SummarizeTransfers.py`, `MaxTiC.py`, and `SummarizeMaxTiC.py` to take a species tree and a directory of long files (output from `SummarizeOptRootings_recipient.py`) as input to return a directory of output data containing files with all of the most likely transfers (HGTs) and relative constraints along with their support values determined from the gene trees. **Note: This version of `SummarizeOptTransfers` has a much shorter runtime due to absence of calling Ranger-DTL many times**.

All input trees must be fully binary and expressed using the Newick format terminated by a semicolon.

The species tree must be rooted and species names in each tree must be unique. **Note: Internal nodes must be labeled using the same nomenclature as the long files**.
```
ex. ((speciesA, speciesB)n2, speciesC)n1;
```

**Input**: Species tree with labeled internal nodes, Directory of long files (output from `SummarizeOptRootings_recipient.py`)
```
$ python3 SummarizeOptTransfers_long.py species_tree long_dir
```

**Output**: Directory of output files of the following form:
```
|-- SummarizeOptTransfers_long_output
    |-- MaxTiC_out
        |-- MaxTiC_conflicting
        |-- MaxTiC_consistent
        |-- MaxTiC_console_output
        |-- MaxTiC_informative
    |-- SummarizeTransfers_out
        |-- SummarizeTransfers_output
        |-- SummarizeTransfers_output_constraints
    |-- maximal_consistent_set_constraints
    |-- species_tree_label
```


**Optional parameters**:
```
-h, --help            show this help message and exit
-o OUTPUT_DIR         specify output name (default:
                      SummarizeOptTransfers_long_output)
-t TRANSFER_CONFIDENCE_PERCENTAGE
                      specify a transfer confidence percentage value
                      (default: 100)
-m MAPPING_CONFIDENCE_PERCENTAGE
                      specify a mapping confidence percentage value
                      (default: 100)
-r RECIPIENT_CONFIDENCE_PERCENTAGE
                      specify a recipient confidence percentage value
                      (default: 100)
-c CUTOFF_VALUE       specify a cutoff value to filter out transfers with
                      less confidence than cutoff (default: 1)
--internal            show internal nodes only (default: False)
--short               shorten runtime by not running MaxTiC or
                      SummarizeMaxTiC (default: False)
-s LOCAL_SEARCH_TIME  specify a local search time (in seconds) to improve
                      MaxTiC results (default: 180)
--quiet               suppress process output (default: False)
--version             show program's version number and exit
```

### Sub Programs
---
#### `SummarizeOptRootings_recipient.py`
**Description**: Python 3 script that aggregates reconciliations across all optimal rootings of gene trees. Slightly modified `SummarizeOptRootings.py` script that has the same input/output with the option to supply a multiple event cost sets. See documentation in the [Ranger-DTL manual](http://compbio.engr.uconn.edu/software/RANGER-DTL/).

#### `SummarizeTransfers.py`

**Description**: Python 3 script that takes a species tree and a directory of long files as input to return a file of the most likely transfers (HGTs) with support values and file names. Also a file of constraints is generated from the transfers to be used as input for `MaxTiC.py`. This program parses all of the input long files to extract the transfer data. After normalizing and filtering the data it is written to output files for further use.

All input trees must be fully binary and expressed using the Newick format terminated by a semicolon.

The species tree must be rooted and species names in each tree must be unique. **Note: Internal nodes must be labeled using the same nomenclature as the long files**.
```
ex. ((speciesA, speciesB)n2, speciesC)n1;
```

**Input**: Species tree with labeled internal nodes, Directory of long files (output from `SummarizeOptRootings_recipient.py`)
```
$ python3 SummarizeTransfers.py species_tree long_dir
```
**Output**: File containing transfers, File containing constraints
```
|-- SummarizeTransfers_output
|-- SummarizeTransfers_output_constraints
```

**Optional parameters**:
```
-h, --help            show this help message and exit
-o OUTPUT_FILE        specify output file (default:
                      SummarizeTransfers_output)
-t TRANSFER_CONFIDENCE_PERCENTAGE
                      specify a transfer confidence percentage value
                      (default: 100)
-m MAPPING_CONFIDENCE_PERCENTAGE
                      specify a mapping confidence percentage value
                      (default: 100)
-r RECIPIENT_CONFIDENCE_PERCENTAGE
                      specify a recipient confidence percentage value
                      (default: 100)
-c CUTOFF_VALUE       specify a cutoff value to filter out transfers with
                      less confidence than cutoff (default: 1)
--internal            show internal nodes only (default: False)
--quiet               suppress process output (default: False)
--version             show program's version number and exit
```

#### `MaxTiC.py`
**Description**: Python 2 script that identifies and removes contradictions in timing constraints to produce a ranked species tree. See documentation in the [MaxTiC manual](https://github.com/ssolo/ALE/tree/master/misc). **Note: `MaxTiC.py` is a Python 2 script**.

#### `SummarizeMaxTiC.py`
**Description**: Python 3 script that combines the outputs of `MaxTiC.py` and `SummarizeTransfers.py` to produce a maximal consistent set of relative constraints with support values and file names.

**Input**: MaxTiC console output, MaxTiC list of constraints, SummarizeTransfers output file
```
$ python3 SummarizeMaxTiC.py MaxTiC_console MaxTiC_constraints SummarizeTransfers_output
```
**Output**: File of maximal consistent set of constraints

#### `CombineTransfers.py`
**Description**: Python 3 script that combines the outputs of `SummarizeTransfers.py` across mutliple runs using the same gene tree family inputs to produce a combined version of the outputs into one summary file.

**Input**: Directory of transfer files
```
$ python3 CombineTransfers.py transfer_dir
```
**Output**: File containing confident transfers across all input transfer files

**Optional parameters**:
```
-h, --help      show this help message and exit
-o OUTPUT_FILE  specify output file (default: CombineTransfers_output)
-c CONFIDENCE   specify confidence percentage value (default: 100)
--version       show program's version number and exit
```


---
###### Sample input files have been provided for the main programs.
---
## Authors

* **Alex Masi**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thank you:
  * Professor Mukul Bansal
  * Soumya Kundu
  * Eric Tannier
  * [Ranger-DTL](http://compbio.engr.uconn.edu/software/RANGER-DTL/)
  * [MaxTiC](https://github.com/ssolo/ALE/tree/master/misc)
  * [ETE Toolkit](http://etetoolkit.org/)
* Originally created at Professor Mukul Bansal's Computational Bio Lab at the University of Connecticut
