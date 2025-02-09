Geometry Plots
================
```geometry_plots.py``` script can be used to obtain geometry plots of various components of the calorimeter. The specification of the geometric component to be plotted is controlled from the if condition in the ```plotting``` function. Also, control the ntuple to choose what to be plotted on the x-axis and y-axis and what to be represented by the color bar. Additionally, the user has to specify the ROOT file of 1D histograms directory (The ROOT file has to be compatible with the structure followed in this package. Also, for geometric plots, it is advised to use muons because they have low probability of producing showers giving clean geometric plots.), the output directory of the produced pdf and the system (The ```plotting``` function is written such that there is a condition on the system but this condition can be released if wanted) along with its numeric code and its collections. For the syntax of the decoding function, refer to this script: ```oneD_histograms/histograms_library.py```.  

Normaliztion
=================
The ```norm.py``` script can be used as a template for normalizing 1D histograms. There are many parameters to control such as the y-axis title after normalization, the ew binning, the systems, functions, and types to be considered...etc. The ROOT file directory has to be specified and the ROOT file must follow the structure in this package and the type names have to follow those in ```oneD_histograms/histograms_library.py```. This is just a template to be modified by the user.  

Power
=================
The ```power.py``` script can be used as a template for generating secondary histograms out of primary 1D histograms. Modify the conversion and stdv_conversion functions to adapt the relation between the primary and secondary histograms. Then, modify secondary_dict where the keys are the primary histograms and the values are the secondary ones. In the loop in the main function, determine carefully which primary histograms are to be used and sepcify the scaling parameters. Finally, sepcify the output_directory. This script is just a template and a modification is required from the user depending on the needs.
