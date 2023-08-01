import ROOT
import sys
import os
from collections import OrderedDict
import numpy as np
import copy

dir = sys.argv[1]

file = ROOT.TFile.Open("data/ILD/FullSim/histograms2/all.root")

systems = file.GetListOfKeys()
histogram_dictionary = {}

for system in systems:
    system_name = system.GetName()
    functions = system.ReadObj().GetListOfKeys()
    histogram_dictionary[system_name] = {}  # Create a new dictionary for this system

    for function in functions:
        function_name = function.GetName()
        histogram_sets = function.ReadObj().GetListOfKeys()
        histogram_dictionary[system_name][function_name] = {}  # Create a new dictionary for this function
        
        for histogram_type in histogram_sets:
            histogram_type_name = histogram_type.GetName()
            histograms = histogram_type.ReadObj().GetListOfKeys()
            histograms_list = []
            
            for histogram in histograms:
                histogram_obj = histogram.ReadObj()
                if histogram_obj and histogram_obj.InheritsFrom("TH1F"):
                    histogram_obj.SetDirectory(0)  # Make ROOT retain ownership of the object
                    histograms_list.append(histogram_obj)
            
            histogram_dictionary[system_name][function_name][histogram_type_name] = histograms_list


histograms_x_titles = {}
for system in histogram_dictionary.keys():
    x_titles = []
    histogram_type_names = histogram_dictionary[system]["no_function"].keys()
    for type_name in histogram_type_names:
        x_titles.append(histogram_dictionary[system]["no_function"][type_name][0].GetXaxis().GetTitle())
    histograms_x_titles[system] = x_titles
    
print(histograms_x_titles)

histogram_selection_dictionary = {}

for system in histogram_dictionary.keys():
    histogram_selection_dictionary[system] = {}
    functions = histogram_dictionary[system].keys()
    
    for function in functions:
        
        if function == "no_function":
            histogram_selection_dictionary[system][function] = OrderedDict()
            histogram_selection_dictionary[system][function]['Staves'] = []
            histogram_selection_dictionary[system][function]['Modules'] = []
            histogram_selection_dictionary[system][function]['Towers'] = []
            histogram_selection_dictionary[system][function]['Layers'] = []
            
            for histogram in histogram_dictionary[system][function]["time"]:
                key = histogram.GetName().split("_")
                
                for selection in key[1:-1]:
                    if selection[0] == "S":
                        name = "Staves"
                    elif selection[0] == "M":
                        name = "Modules"
                    elif selection[0] == "T":
                        name = "Towers"
                    elif selection[0] == "L":
                        name = "Layers"
                    if selection[1:] not in histogram_selection_dictionary[system][function][name]:
                       histogram_selection_dictionary[system][function][name].append(selection[1:])

            for key in histogram_selection_dictionary[system][function].keys():
                if len(histogram_selection_dictionary[system][function][key]) == 0:
                    histogram_selection_dictionary[system][function].pop(key)
                    # histogram_selection_dictionary[system][function][key].append("*")
       
        else:
            histogram_selection_dictionary[system][function] = []
            
            for histogram in histogram_dictionary[system][function]["time"]:
                key = histogram.GetName().split("_")
                selection = key[-2]
                histogram_selection_dictionary[system][function].append(selection)

# print(histogram_selection_dictionary)

def craete_histogram(twoDD_histograms, system, function, histogram_types, element):
    
    def nested_loops(dict, keys, values=[]):
        if keys:
            current_key = keys[0]
            remaining_keys = keys[1:]
            for value in dict.get(current_key, []):
                nested_loops(dict, remaining_keys, values + [value])
        else:
            # Replace the following line with your own code
            print(values)


    element_selections = histogram_selection_dictionary[system][function][element]
    element_length = len(element_selections)
    
    selection_dict_for_length = copy.deepcopy(histogram_selection_dictionary[system][function])
    keys_before_specific = list(selection_dict_for_length.keys())[:list(selection_dict_for_length.keys()).index(element)+1]
    for key in keys_before_specific:
        selection_dict_for_length.pop(key)
    lengths = [len(v) for v in selection_dict_for_length.values()]
    product_of_lengths = np.prod(lengths)

    selection_dict = copy.deepcopy(histogram_selection_dictionary[system][function])
    selection_dict.pop(element)

        
    for k, histogram_type in enumerate(histogram_types):
        
        hist_2d_type = [None] * element_length
        
        for j, element_selection in enumerate(element_selections):
            selected_histogram_list_type_per_element = histogram_dictionary[system][function][histogram_type][j::L]
            min_bin_value = min([hist.GetXaxis().GetXmin() for hist in selected_histogram_list_type_per_element])
            max_bin_value = max([hist.GetXaxis().GetXmax() for hist in selected_histogram_list_type_per_element])
            max_bins_type = max([hist.GetNbinsX() for hist in selected_histogram_list_type_per_element])
            if histogram_selection_dictionary[system][function]["M"] != ["*"]: 
                X_title = "Modules"
            elif histogram_selection_dictionary[system][function]["T"] != ["*"]:
                X_title = "Towers"
            else:
                X_title = "no selections"
            hist_2d_type[j] = ROOT.TH2F("{}_{}_{}_{}_layers_{}".format(system, function, histogram_type, X_title, element_selection), "{}_{}_{}_{}_layers_{}".format(system, function, histogram_type, X_title, layer_selection), len(selected_histogram_list_type_per_layer), 0, len(selected_histogram_list_type_per_layer), max_bins_type, min_bin_value, max_bin_value)
            hist_2d_type[j].GetXaxis().SetTitle(X_title) 
            hist_2d_type[j].GetYaxis().SetTitle(histograms_x_titles[system][k])
            if X_title == "Modules":
                sele = "M"
            elif X_title == "Towers":
                sele = "T"
            else:
                sele = "None"
            for i, hist in enumerate(selected_histogram_list_type_per_layer):
                hist_2d_type[j].GetXaxis().SetBinLabel(i+1, "{} : {}".format(X_title, histogram_selection_dictionary[system][function][sele][i]) if sele != "None" else "No selection")
                for bin in range(1, hist.GetNbinsX() + 1):
                    hist_2d_type[j].Fill(i, hist.GetBinCenter(bin), hist.GetBinContent(bin))
        twoD_histograms[system][function][histogram_type] = hist_2d_type

twoD_histograms = {}

for system in histogram_dictionary.keys():
    twoD_histograms[system] = {}
    functions = histogram_dictionary[system].keys()
    
    for function in functions:
        twoD_histograms[system][function]= {}
        histogram_types = histogram_dictionary[system][function].keys()
        if function == "no_function":
            layer_selections = histogram_selection_dictionary[system][function]["Layers"]
            L = len(layer_selections)
            
            for k, histogram_type in enumerate(histogram_types):
                
                hist_2d_type = [None] * L
                
                for j, layer_selection in enumerate(layer_selections):
                    selected_histogram_list_type_per_layer = histogram_dictionary[system][function][histogram_type][j::L]
                    min_bin_value = min([hist.GetXaxis().GetXmin() for hist in selected_histogram_list_type_per_layer])
                    max_bin_value = max([hist.GetXaxis().GetXmax() for hist in selected_histogram_list_type_per_layer])
                    max_bins_type = max([hist.GetNbinsX() for hist in selected_histogram_list_type_per_layer])
                    if histogram_selection_dictionary[system][function]["M"] != ["*"]: 
                        X_title = "Modules"
                    elif histogram_selection_dictionary[system][function]["T"] != ["*"]:
                        X_title = "Towers"
                    else:
                        X_title = "no selections"
                    hist_2d_type[j] = ROOT.TH2F("{}_{}_{}_{}_layers_{}".format(system, function, histogram_type, X_title, layer_selection), "{}_{}_{}_{}_layers_{}".format(system, function, histogram_type, X_title, layer_selection), len(selected_histogram_list_type_per_layer), 0, len(selected_histogram_list_type_per_layer), max_bins_type, min_bin_value, max_bin_value)
                    hist_2d_type[j].GetXaxis().SetTitle(X_title) 
                    hist_2d_type[j].GetYaxis().SetTitle(histograms_x_titles[system][k])
                    if X_title == "Modules":
                        sele = "M"
                    elif X_title == "Towers":
                        sele = "T"
                    else:
                        sele = "None"
                    for i, hist in enumerate(selected_histogram_list_type_per_layer):
                        hist_2d_type[j].GetXaxis().SetBinLabel(i+1, "{} : {}".format(X_title, histogram_selection_dictionary[system][function][sele][i]) if sele != "None" else "No selection")
                        for bin in range(1, hist.GetNbinsX() + 1):
                            hist_2d_type[j].Fill(i, hist.GetBinCenter(bin), hist.GetBinContent(bin))
                twoD_histograms[system][function][histogram_type] = hist_2d_type
        else:
            for m, histogram_type in enumerate(histogram_types):
                twoD_histograms[system][function][histogram_type] = [] 
                selected_histogram_list_type_per_selection = histogram_dictionary[system][function][histogram_type]
                min_bin_value = min([hist.GetXaxis().GetXmin() for hist in selected_histogram_list_type_per_selection])
                max_bin_value = max([hist.GetXaxis().GetXmax() for hist in selected_histogram_list_type_per_selection])
                max_bins_type = max([hist.GetNbinsX() for hist in selected_histogram_list_type_per_selection])
                hist_2d_type = ROOT.TH2F("{}_{}_{}".format(system, function, histogram_type), "{}_{}_{}".format(system, function, histogram_type), len(selected_histogram_list_type_per_selection), 0, len(selected_histogram_list_type_per_selection), max_bins_type, min_bin_value, max_bin_value)
                hist_2d_type.GetXaxis().SetTitle("selections")
                hist_2d_type.GetYaxis().SetTitle(histograms_x_titles[system][k])
                
                for i, hist in enumerate(selected_histogram_list_type_per_selection):
                    hist_2d_type.GetXaxis().SetBinLabel(i+1, "selection : {}".format(histogram_selection_dictionary[system][function][i]))
                    for bin in range(1, hist.GetNbinsX() + 1):
                        hist_2d_type.Fill(i, hist.GetBinCenter(bin), hist.GetBinContent(bin))
                twoD_histograms[system][function][histogram_type].append(hist_2d_type)
# print(twoD_histograms)


canvas = ROOT.TCanvas("canvas", "Canvas", 1000, 600)

for system in twoD_histograms.keys():
    sys_dir = "{}/{}".format(dir, system)
    if not os.path.exists(sys_dir):
        os.makedirs(sys_dir)
    for function in twoD_histograms[system].keys():
        func_dir = "{}/{}".format(sys_dir, function)
        if not os.path.exists(func_dir):
            os.makedirs(func_dir)
        for histo_type in twoD_histograms[system][function].keys():
            histo_type_dir = "{}/{}".format(func_dir, histo_type)
            if not os.path.exists(histo_type_dir):
                os.makedirs(histo_type_dir)
            for histogram in twoD_histograms[system][function][histo_type]:
                histogram.Draw("COLZ")
                canvas.SaveAs("{}/{}{}".format(histo_type_dir, histogram.GetName(), ".pdf"))