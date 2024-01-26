Merge
===============
At this point, we have a collection of 1D histograms of separate processes and we want to scale each of them (typically by $\frac{\sigma L_{ins}}{N}$ for physics processes), and merge them to get the rates of the fluxes. 

How to use
===============
For a specific energy, save the directories of the individual processes in a one file and write the names of these subdirectories in the `processes` variable and the corresponding weights in the `weights` variable in the script `merging.py`. Get the path of the parent directory and modify the `root_file_list` variable accordingly. After that, specify the types of histograms, thay you want to get in `type_names` variable. The names of the types have to match those of the types of the individual processes.  <br>
The code is to be run with a single argument which is the name of the parent directory in which separate processes are saved. It is denoted as energy. 
The command would be:
```
python merging.py energy(name of the parent directory of the subdirectories of individual processes at a specific energy scale)
```
Output
===============
A folder with the same structure of the individual processes but for the merge of all of them. 
