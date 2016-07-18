# Growth Profiler Image Analyser
This package contains functions for analysing the raw image outputs of the growth profiler.

## Installation

### Installing Python
Skip this if you already have a working installation of Python.</br>
To use this package you need to have Python.
Using the operating system's built-in Python interpreter is not recommended.
The easiest way to obtain Python is from https://www.continuum.io/downloads
- Select the relevant OS and download the Python 3.X installer (Python 2.7 will also work for now, but Python 3 is recommended).
- Run the installer and follow the instructions.
- Open a terminal in your operating system and type `python -V`. This should print the version of Python, and contain the word 'Anaconda'

### Installing requirements
Before installing this package you need some other Python packages that should be installed first. Luckily this is very easy if you're using Anaconda (see above)
- Go to your terminal
- run `conda install numpy, scipy, pandas, scikit-image`
- (if you're not using Anaconda you can install the packages by running `pip install numpy, scipy, pandas, scikit-image`, but on some OS's (windows in particular) this might not work)


### Installing the Growth Profiler Image Analyser (gp_align)
- Clone the package (http://github.com/biosustain/growth-profiler-align
- Open a terminal
- Go to the directory you cloned the package into
- run `pip install -e .`
- Go to your home directory and confirm that `python -c "import gp_align"` runs without error

## Usage

### Analysing the images
- Navigate to the directory where you want the output files to be placed
- Figure out which plate type was used for the run and use the number in the subsequent commands:
  - Black 96 well (PLATE_TYPE=1)
  - White 96 well (PLATE_TYPE=2)
  - White 24 well (PLATE_TYPE=3)
- To analyse the plates in scanner 1, run `python -m gp_align analyse --scanner 1 --plate_type PLATE_TYPE --out NAME_THAT_YOU_DECIDE "PATH/TO/YOUR/DATA/Scanner 1/*.Png"`
- To analyse the plates in scanner 2, run `python -m gp_align analyse --scanner 2 --plate_type PLATE_TYPE --out NAME_THAT_YOU_DECIDE "PATH/TO/YOUR/DATA/Scanner 2/*.Png"`
- The output files will be placed in your current working directory and will be named NAME_THAT_YOU_DECIDE_tray1 (_tray2 etc.). See below how the trays are organised in the scanners
- NOTE: You should place your plates such that A1 is in the upper right corner. Otherwise you should add the argument `--orientation bottom_left` to the above commands)


Tray layouts:

| Scanner 1  |   |
|---|---|
| 1 | 4 |
| 2 | 5 |
| 3 | 6 |
|   |   |


| Scanner 2  |   |
|---|---|
| 7 | 10 |
| 8 | 11 |
| 9 | 12 |
|   |   |


### Converting the G-values to OD
- Obtain a set of calibration parameters (A, B, C) from Kristian
- Run `python -m gp_align convert A B C file1 file2 file3 (etc)`
- (To convert all the G-value files in your current working directory run `python -m gp_align convert A B C *.G.tsv`
