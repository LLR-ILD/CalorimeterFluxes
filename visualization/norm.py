import ROOT
import os
from array import array
from twoD_histograms.D_histograms_library import get_histograms

import ROOT

def modify_and_normalize_histogram(hist, y_title):
    # Calculate the total number of bins (excluding the first bin)
    total_num_bins = hist.GetNbinsX() - 1

    # Calculate the adjusted number of entries (excluding the first bin's content)
    adjusted_entries = sum(hist.GetBinContent(bin) for bin in range(1, hist.GetNbinsX() + 1))

    # Creating a new histogram with the same bin widths, but skipping the first bin
    merged_bin_edges = [hist.GetXaxis().GetBinLowEdge(i) + 0.5 for i in range(1, hist.GetNbinsX() + 2)]

    name = hist.GetName()
    title = hist.GetTitle()
    merged_hist = ROOT.TH1F("modified_" + name, title, total_num_bins, array('d', merged_bin_edges))

    x_title = hist.GetXaxis().GetTitle()
    merged_hist.GetXaxis().SetTitle(x_title)
    merged_hist.GetYaxis().SetTitle(y_title)

    # Fill in the values (starting from bin 2 in the original histogram)
    for bin in range(2, hist.GetNbinsX() + 1):
        merged_hist.SetBinContent(bin - 1, hist.GetBinContent(bin))
        # Set error using Wald approximation (sqrt(n))
        merged_hist.SetBinError(bin - 1, ROOT.TMath.Sqrt(hist.GetBinContent(bin)))

    # Manually set the adjusted number of entries
    merged_hist.SetEntries(adjusted_entries)

    # Normalize the modified histogram
    if adjusted_entries != 0:
        merged_hist.Scale(1.0 / adjusted_entries)

    return merged_hist

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

def write_histogram(histo_dir, canvas, merged_histos, systemss, system_per_functions):
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
                saving_histogram(histo_dir, canvas, type_name, type_dict, func_dir, system, function)
    myfile.Close()
    
root_file = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/Energy_histos/GeV240/merged_log/all.root"
file = ROOT.TFile.Open(root_file)
histogram_dictionary = get_histograms(file)

system_functions = {}
systems = histogram_dictionary.keys()
for system in systems:
    functions = histogram_dictionary[system].keys()
    system_functions[system] = functions

type_names = ["#Nhits"]
histogram_numbers = len(type_names)

merged_histograms = [{} for _ in range(histogram_numbers)]
for j, histogram_type in enumerate(type_names):
    for system in systems:
        merged_histograms[j][system] = {}
        functions = system_functions[system]
        for function in functions:
            merged_histograms[j][system][function] = []
            iterable_histograms = histogram_dictionary[system][function]["#Nhits"]
            for hist in iterable_histograms:
                merged_hist = modify_and_normalize_histogram(hist, "probability of events")
                merged_histograms[j][system][function].append(merged_hist)

# print(merged_histograms)
output_dir = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/energy_histograms/GeV240/normalized_240_all"
canvas = ROOT.TCanvas('canvas', 'Histogram', 800, 600)
# canvas.SetLogy(1)

write_histogram(output_dir, canvas, merged_histograms, systems, system_functions)     