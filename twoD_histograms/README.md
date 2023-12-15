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
The command would be:
```
python D_script.py /path/to/root/file/of/1D/histograms /path/to/output/directory <True or False>
```

Output
===============
