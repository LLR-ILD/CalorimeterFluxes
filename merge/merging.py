import ROOT
import sys
import os
from twoD_histograms.D_histograms_library import get_histograms
from oneD_histograms.histograms_library import find_max_range
from oneD_histograms.energy_histos import systems, system_functions, histograms_to_select

energy = sys.argv[1]

def merge_histograms(histogram_list, histogram_weights, can_extend = True):
    """This function is a modification of merge_histograms in CalorimeterFluxes.oneD_histograms.histograms_library.py script. 
    The only modification is regarding the name and the title."""

    """The histograms' properties are all similar. 
    That is why I retrieve the information from the first histogram (any other histogram would yield identical results).
    The only difference in the maximum range if the histogram can extend such as in the case of the upper-energy scale and number-of-hits-above-threshold histograms.
    For that difference, we apply find_max_range if the optional parameter can_extend is set True"""
    
    maximum = find_max_range(histogram_list) if can_extend else histogram_list[0].GetXaxis().GetXmax()
    minimum = histogram_list[0].GetXaxis().GetXmin()
    name =histogram_list[0].GetName()
    title = histogram_list[0].GetTitle()
    bins_number = histogram_list[0].GetXaxis().GetNbins()

    x_title = histogram_list[0].GetXaxis().GetTitle()
    y_title = histogram_list[0].GetYaxis().GetTitle()

    master_hist = ROOT.TH1F(name, title, bins_number, minimum, maximum)
    master_hist.GetXaxis().SetTitle(x_title)
    master_hist.GetYaxis().SetTitle(y_title + " per second")

    # Create a TList to hold the histograms
    hist_list = ROOT.TList()

    # Add each histogram to the TList
    for hist, weight in zip(histogram_list, histogram_weights):
        temp_hist = hist.Clone()
        temp_hist.Scale(weight)
        hist_list.Add(temp_hist)

    master_hist.Merge(hist_list)

    return master_hist  # This is the final merged histogram

def saving_histogram(histo_dir, canvas, type_name, type_dict, func_dir, system, function):
    """This function is minimally modified from write_histogram in oneD_histograms.histograms_library.py script."""
    if not func_dir.GetDirectory(type_name): # Check if the directory exists
        type_name_dir = func_dir.mkdir(type_name) # If the directory does not exist, create it
    else:
        type_name_dir = func_dir.GetDirectory(type_name) # If it exists, retrieve the existing directory
    if type_name_dir is None: print("Failed to create directory: {}".format(type_name))
    type_name_dir.cd()
    directory_type_name_dir = str(histo_dir) + "/" + system + "/" + function + "/" + type_name
    if not os.path.exists(directory_type_name_dir): os.makedirs(directory_type_name_dir)
        
    for hist in type_dict[system][function]:
        hist.Draw("HIST")
        canvas.SaveAs(directory_type_name_dir + "/{}".format(hist.GetName()) + ".pdf")
        hist.Write()
        # Explicitly delete the histogram after writing to ROOT file and saving to PDF
        hist.Delete()

def write_histogram(histo_dir, canvas, merged_histos, systemss, system_per_functions, histos_to_select_dict):
    """This function is minimally modified from oneD_histograms.histograms_library.py script."""
    directory_type_name_dir = str(histo_dir)
    if not os.path.exists(directory_type_name_dir): os.makedirs(directory_type_name_dir)
    myfile = ROOT.TFile(str(histo_dir) + '/all.root', 'UPDATE')
   
    for system in systemss:
        if not myfile.GetDirectory(system): # Check if the directory exists
            sys_dir = myfile.mkdir(system) # If the directory does not exist, create it
        else:
            sys_dir = myfile.GetDirectory(system) # If it exists, retrieve the existing directory
        if sys_dir is None: print("Failed to create directory: {}".format(system))
        functions = system_per_functions[system]
        for function in functions:
            if not sys_dir.GetDirectory(function): # Check if the directory exists
                func_dir = sys_dir.mkdir(function) # If the directory does not exist, create it
            else:
                func_dir = sys_dir.GetDirectory(function) # If it exists, retrieve the existing directory
            if func_dir is None: print("Failed to create directory: {}:{}".format(system, function))
            iterable_histograms_and_names = zip(type_names, merged_histos)
            for type_name, type_dict in iterable_histograms_and_names:
                if histos_to_select_dict[system][function][type_name]:
                    saving_histogram(histo_dir, canvas, type_name, type_dict, func_dir, system, function)
    myfile.Close()          

# The weights are in the same order as the processes.
processes = ["qq365", "ll365", "ww365", "ZH365", "tt365", "030ee365", "above30ee365"]
weights = [2.74e-5, 5.16e-6, 1.33e-5, 1.47e-7, 4.46e-7, 5.99e-6, 4.65e-6]

root_file_list = ["/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/Energy_histos/{}/{}/all.root".format(energy, process) for process in processes]
type_names = ["time", "lower_scale_energy", "upper_scale_energy", "all_scale_energy", "scaled_upper_scale_energy", "scaled_all_scale_energy", "low_#Nhits", "high_#Nhits", "all_#Nhits"]
histogram_numbers = len(type_names)

histograms_dict = {}
for i, process in enumerate(processes):
    process_file = ROOT.TFile.Open(root_file_list[i])
    histograms_dict[process] = get_histograms(process_file)

"""The systems and functions and histogram types are all the same. Thus, I read them from just one dictionary of histograms."""
merged_histograms = [{} for _ in range(histogram_numbers)]
for j, histogram_type in enumerate(type_names):
    for system in systems:
        merged_histograms[j][system] = {}
        functions = system_functions[system]
        for function in functions:
            merged_histograms[j][system][function] = []
            number_histograms = len(histograms_dict[processes[0]][system][function][histogram_type])
            for i in range(number_histograms):
                histograms_to_merge = []
                for process in processes:
                    histograms_to_merge.append(histograms_dict[process][system][function][histogram_type][i])
                merged_histograms[j][system][function].append(merge_histograms(histograms_to_merge, weights))
                  
output_dir = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/Energy_histos/{}/merged_log_no_machine".format(energy)
canvas = ROOT.TCanvas('canvas', 'Histogram', 800, 600)
canvas.SetLogy(1)

write_histogram(output_dir, canvas, merged_histograms, systems, system_functions, histograms_to_select)     