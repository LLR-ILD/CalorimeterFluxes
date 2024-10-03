Histograms
===========
This directory is repsonsible for creating 1D histograms of arbitrary coordinate selections of the simulated ILD calorimeter. The input is the ```.slcio``` files (of a given process like a decay channel or a machine background) obtained from the step of the full simulation and the output is a ROOT file with the selected histograms. The histograms are also printed in pdf files in nested folders following the same hierarchical structure of the ROOT file. 

Histograms hierarchy
============
Each histogram is determined by 2 selections: the geometric coordinate selection and the histogram type. 

__Geometric selections:__ The calorimeter is divided into systems which are subdivided into staves, modules, towers, and layers (Further classification can be implemented if desired). The user is set to select which part of the calormieter is desired for a histogram. 

__(1) Explicit selections:__ This can be {system =EcalBarrel, stave = 1, module = 2, tower = 5} for example or any selection of different parts of the calorimeter (ranges can be implemented as well). If no tower is selected, the histogram will include all the towers by default and the same applies to other coordinates. The selection here was explicit on the different coordinates.

__(2) Implicit selections:__ An example is {all modules and layers of the EcalBarrel system satisfying the equation: 2module + 2layer = 10}. The selection here was implicit. The right-hand side of the equation can be a range as well like instead of 10, it can be all the values between 9 and 12 for instance. As towers and staves weren't involved, all of them were considered like in the case of explicit selections. 
These selections are given through boolean functions that are true if and only if the involved coordinates satisify the given equation. 

__Histogram types:__ These are the different types of histograms of a given geometric selection such as the energy histograms and the time histograms for example.  

__Hierarchy:__ The ROOT file or the printed pdfs will have one directory for each system. Withing these directories, there are subdirectory for each function with "no_function" standing for the explicit geometric selections. Within these subdirectories, there are subsubdirectories for each histogram type. The histograms are then listed in those innermost directories.


How to use
===========
All the referred to variables are in the file ```energy_histos.py```. 

__Geometric selection of histograms:__ There is a dictionary called dictionary_of_system. This dictionary has keys of the desired systems of the calorimeter. The value of each of the keys (systems) is a n-tuple with the following arguments in order:

1. A list of the considered collections per system.
2. A list of 4 sublists. The 4 sublists are the selections made on staves, modules, towers, and layers in order. For example, let's take the value of the list to be this [["\*"],["\*"],["0","1:2","3:5","6:8"],["0:9","10:19","20:29"]]. This means that we have 4 selections on towers and 3 selections on layers producing a total of 3\*4=12 histogram selections.
The selections would be tower 0 and the first 10 layers, tower 0 and the second 10 layers, tower 0 and the third 10 layers, the towers 1 and 2 together with the same set of selections on layers...etc. As noted from the example, to set no selection on staves, modules, towers, or layers, put the corresponding sublits like this ["\*"]. For any selection, it is written as a numeric string and the range is given with a colon between the lower and upper limits as shown in the example.
3.  A list of 8 sublists with the following arguments in order for the histogram types (Histograms are 1D unless otherwise is specified. Also, some histograms are extendable if data points lie beyond the maximum value specified. They are mentioned):
    I. Low-scale energy-weighted time histogram: number of bins, max time in ns (time starts from 6 ns).
    
    II. High-scale energy-weighted time histogram (extendable): number of bins, max time in ns (Time starts from the max of the low scale histogram).
    
    III. Low-scale 2d hit-time histogram with the hit duration on the y-axis and the start time of the hit (time of the first subhit) on the x-axis: x-axis bins, min x value, max x value, y-axis bins, min y value, max y value.

    IV. High-scale 2d hit-time histogram with the hit duration on the y-axis and the start time of the hit (time of the first subhit) on the x-axis: x-axis bins,  max x value, y-axis bins, max y value (The minimum here is the maximum of the low-scale histogram).

    V. Low-scale energy histogram: number of bins, max energy (in GeV).

    VI. High-scale energy histogram (extendable): number of bins, max energy (in GeV).

    VII. Full-scale energy histogram (extendable): number of bins, max energy (in GeV).

    VIII. Low-scale number-of-hits-above-energy-threshold histogram: number of bins, max value.

    IX. High-scale number-of-hits-above-energy-threshold histogram (extendable): number of bins, max value.

    X. Full-scale number-of-hits-above-energy-threshold histogram (extendable): number of bins, max value.

    XI. The energy threshold used in the last 3 histograms. If this number is the one to be used, set the variable "energy_threshold" equal to True; otherwise, set the same variable to False and the energy threshold would be (MIP/4).
    
5. A list that contians a single sublist that contains the energy threshold used in #hits above threshold lower and upper scale histograms.
6. A dictionary that contians the complex boolean functions as keys with their selections listed in a list as their values.  These are the implicit selections. 

__Histogram types selection:__ There is a dictionary called histograms_to_select which has the systems as keys and the values are other subdictionaries having the values as dictionaries with the histogram types as keys and their values are boolean such that True means to be produced and False is not to be produced. By this, the user can choose which types are required for each system and each function. The explicit selections are denoted as "no_function".

__scaled_upper_scale_energy, scaled_all_scale_energy:__ These types of histogram are the same as upper_scale_energy and all_scale_energy histograms, respectively, but the x-axis is scaled by the MIP value obtained from getting the most probable value (MPV) from the energy distribution of the muons. There is a dictionary called mip that shows the MIP values of each selection compatible with the naming scheme. If the selections are modified by the user, the MIP values should be obtained for these selections from the muons energy distribution. To get this dictionary, run ```energy_histos.py``` on the muons first and then run the ```mpv.py``` script with 2 arguments which are the root file path of the muons histograms and directory in which the range bounds of finding the mpv are printed for the histograms to make sure that the MPV is really the MIP. The ranges can be controlled from ```mpv.py``` script.

__Input files:__ From the step of the full simulation, the data was divided into many ```.slcio``` files for parallel processing. The paths to these ```.slcio``` files is to be put into the list slcio_file_list. This list can be the combination of the initial simulation and their complementary counterparts. 
ev_start_list list is to give the initial event to start from out of each ```.slcio``` file in order. ev_stop_list list is to give the last event to process out of each ```.slcio``` file in order with -1 meaning the last event. Usually, ev_start is set to zeros (with the length of the slcio_file_list) and ev_stop is set to -1 for all elements with the length of (slcio_file_list) to process all the events.

__Parallel processing:__ The script is written to use multi processors to save the computational time. The number of parallel processes is set by the number of ```.slcio``` files. If all the data is included in a single file, it can still be parallel-processd. For instance, let's say that we have 1000 events and want to use 10 processors. We can write the slcio file path 10 times in the slcio_file_list and set ev_start list equal to [0,100,200.......,900] and ev_stop equal to [100, 200, .....1000]. This will make each process run 100 events. 

Running
==========
The code is to be run with a single argument which is the path to the directory in which the output ROOT file and the pdfs are to be saved. It is preferred to run the script in a screen and to save the output to a log file because technical problems can arise with large data sets and long computational time. The command is:
```
python energy_histos.py /path/to/output/directory
```
