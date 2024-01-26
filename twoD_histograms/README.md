2D Histograms
===============
The main function of this is to display a group of 1D histograms in a single histogram. For example, let's say we have produced the 1D low-scale energy distribution of some system with a selection on module 0 for the first 10 layers, second 10 layers and third 10 layers. These are 3 1D histograms. 
They can be gathered in one 2D histogram with 3 x-axis bins in which each of the 1D histogram represents an x-axis bin with the y-values are now represented by the color bar of the z-axis. 

How to use
===============
Run the script ```D_script.py``` with 3 arguments:  <br>
1. The path to the ROOT file of the 1D histograms.
2. The path to the directory in which the output 2D histograms are to be saved. The output is a ROOT file along with printed histograms in pdfs following the hierarchcal structure of the ROOT file.
3. This is a boolean value. If True, the printed histograms would be in logarithmic scale; otherwise (False), they would be in a normal linear scale.
4. This is a boolean value. If True, each bin will have a box printed below it with the statsistics of it (mean, standard deviation, and the integration); otherwise (False), the statistics wouldn't be printed out. 
The command would be:
```
python D_script.py /path/to/root/file/of/1D/histograms /path/to/output/directory <True or False> <True or False>
```

Output
===============
__Implicit selections:__ For a function in a system, the selections are grouped in one 2D histogram with each bin representing a 1D histogram.  <br>

__Explicit selections:__ This is better explained with an example. Let's say that we have 1D histograms of low-scale energy of some system of each module from 1 to 5 with the first 10 layers, second 10 layers, and third 10 layers. This is a total of 15 1D histograms. The different selections of the layers would be grouped in one histogram for the first module, second module,....etc. This produces 5 2D histograms with each one with a fixed selection of the module and all the selections of the layers grouped in bins. The same applies to the layers, we would have a one 2D histogram with the first 10 layers but with each module representing a bin (5 bins for 5 modules), another 2D hisotgram for the second 10 layers and another one for the third 10 layers. This produces 3 2D histograms. Thus, instead of having 3\*5 = 15 histograms like in the case of 1D histograms, we would have 3+5 = 8 histograms. 

Hierarchy
===============
First, there are directories of the different systems with subdirectories for the functions. These subdirectories have subsubdirectories for the histograms types. These innermost directories either have a histogram as in the case of the implicit selections or having other subsubsubdirectories with the names: staves, modules, towers,or layers. The directory staves would have the 2D histograms in which the staves are fixed and the bins representing the selections on the other coordinates. The same applies to modules, towers, and layers. 
