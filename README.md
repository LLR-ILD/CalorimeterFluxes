CalorimeterFluxes
=============

This package is used mainly to take slcio files of fully simulated physics processes or machine background in the ILD calorimeter as input to produce histograms of any chosen selection of the calorimeter components and coordinates.
Further utilities can be made using this package as well such as taking generator-level simulation and running a full simulation, producing 2D histograms of grouped 1D histograms, and producing geometry plots of the calorimeter. 

A description and use case of the package has been published in JINST:
[10.1088/1748-0221/19/10/T10009](10.1088/1748-0221/19/10/T10009)
please cite as:

K. Hassouna and V. Boudry, CaloFlux: a tool to estimate fluxes in calorimeters at colliders, JINST 19, (2024) T10009.


Table of contents
=================
  * [CalorimeterFluxes](#CalorimeterFluxes)
  * [Table of contents](#table-of-contents)
  * [Clone and initialisation](#clone-and-initilisation)
  * [Using Hierarchy](#using-hierarchy)

Clone and initialisation
=================
Start by cloning the repository:
```
git clone https://github.com/LLR-ILD/CalorimeterFluxes.git
```
Navigate to the repository directory:
```
cd /path/to/CalorimterFluxes
```
Initialize:
```
source ./init.sh
```
Using Hierarchy
=================
The details of every step are explained in the Read.md files in each designated directory.
1. Prepare the generator-level simulation files in STDHEP format. Examples of simulated data are given in the ```CalorimeterFluxes/generator_level_simulation``` directory which can be edited depending on the desired analysis.
2. The full simulation in ILD is done using  the ```CalorimeterFluxes/full_simulation``` directory.
3. 1D histograms are obtained using the ```CalorimeterFluxes/oneD_histograms``` directory.
4. Step 4 depends on what the user wants. It can be obtaining 2D histograms from grouped 1D histograms using the ```CalorimeterFluxes/twoD_histograms``` directory. It also can be merging different processes in one unified 1D histograms (1 histogram per coordinate selection); then, getting the 2D histograms.

Produced Results
==================
1D and 2D histograms of multiple processes are produced at 4 different energy scales. The Results are shown in the Histograms directory. Also, some random geometric plots of the calorimeter can be found in the geometry directory along with a brief description of how the can be produced in the ```README.md``` file in the visualization directory. 
