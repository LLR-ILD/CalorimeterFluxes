import ROOT
import sys
import os
from collections import OrderedDict
# import numpy as np
import copy

dir = sys.argv[1]

file = ROOT.TFile.Open("data/ILD/FullSim/histograms2/all.root")

systems = file.GetListOfKeys()
histogram_dictionary = OrderedDict()

for system in systems:
    system_name = system.GetName()
    functions = system.ReadObj().GetListOfKeys()
    histogram_dictionary[system_name] = OrderedDict()  # Create a new dictionary for this system

    for function in functions:
        function_name = function.GetName()
        histogram_sets = function.ReadObj().GetListOfKeys()
        histogram_dictionary[system_name][function_name] = OrderedDict()  # Create a new dictionary for this function
        
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


histograms_x_titles = OrderedDict()
for system in histogram_dictionary.keys():
    x_titles = []
    histogram_type_names = histogram_dictionary[system]["no_function"].keys()
    for type_name in histogram_type_names:
        x_titles.append(histogram_dictionary[system]["no_function"][type_name][0].GetXaxis().GetTitle())
    histograms_x_titles[system] = x_titles
    
histogram_selection_dictionary = OrderedDict()
Bin_labelss = OrderedDict()

for system in histogram_dictionary.keys():
    histogram_selection_dictionary[system] = OrderedDict()
    functions = histogram_dictionary[system].keys()
    
    Bin_labelss[system] = []
    
    for function in functions:
        
        if function == "no_function":
            histogram_selection_dictionary[system][function] = OrderedDict()
            histogram_selection_dictionary[system][function]['Staves'] = []
            histogram_selection_dictionary[system][function]['Modules'] = []
            histogram_selection_dictionary[system][function]['Towers'] = []
            histogram_selection_dictionary[system][function]['Layers'] = []
            
            for histogram in histogram_dictionary[system][function]["time"]:
                dict_labels = {}
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
                    dict_labels[name] = selection[1:]

                    if selection[1:] not in histogram_selection_dictionary[system][function][name]:
                       histogram_selection_dictionary[system][function][name].append(selection[1:])
                Bin_labelss[system].append(dict_labels)

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

def craete_histogram(twoDD_histograms, system, function, histogram_type, element=None):
    # print(system)
    def make_histogram(selected_histogram_list_type_for_element, histos_names, element_selection = None):
        min_bin_value = min([hist.GetXaxis().GetXmin() for hist in selected_histogram_list_type_for_element])
        max_bin_value = max([hist.GetXaxis().GetXmax() for hist in selected_histogram_list_type_for_element])
        max_bins_type = max([hist.GetNbinsX() for hist in selected_histogram_list_type_for_element])
        if function == "no_function" and len(histogram_selection_dictionary[system][function].keys()) != 0:
            hist_2d_type = ROOT.TH2F("{}_{}_{}_{}_{}".format(system, function, histogram_type, element, element_selection), "{} {} {} {}".format(system, histogram_type, element, element_selection), len(selected_histogram_list_type_for_element), 0, len(selected_histogram_list_type_for_element), max_bins_type, min_bin_value, max_bin_value)
        else:
            hist_2d_type = ROOT.TH2F("{}_{}_{}".format(system, function, histogram_type), "{}_{}_{}".format(system, function, histogram_type), len(histogram_dictionary[system][function][histogram_type]), 0, len(histogram_dictionary[system][function][histogram_type]), max_bins_type, min_bin_value, max_bin_value)
        hist_2d_type.GetYaxis().SetTitle(histograms_x_titles[system][histogram_dictionary[system][function].keys().index(histogram_type)])
        for i, hist in enumerate(selected_histogram_list_type_for_element):
            hist_2d_type.GetXaxis().SetBinLabel(i+1, histos_names[i])
            for bin in range(1, hist.GetNbinsX() + 1):
                hist_2d_type.Fill(i, hist.GetBinCenter(bin), hist.GetBinContent(bin))
        return hist_2d_type

    names = []
    hist_2d_list = []

    if function == "no_function" and len(histogram_selection_dictionary[system][function].keys()) != 0:
        def product_of_keys_lengths(keys_element, dictionary):
            for key in keys_element:
                dictionary.pop(key)
            lengths_element = [len(v) for v in dictionary.values()]
            product_of_lengths_element = 1
            for i in range(len(lengths_element)):
                product_of_lengths_element = product_of_lengths_element*lengths_element[i]
            return product_of_lengths_element

        selection_dict_for_length_before = copy.deepcopy(histogram_selection_dictionary[system][function])
        keys_after_element = list(selection_dict_for_length_before.keys())[list(selection_dict_for_length_before.keys()).index(element):]
        product_of_lengths_before_element = product_of_keys_lengths(keys_after_element, selection_dict_for_length_before)
        
        selection_dict_for_length_after = copy.deepcopy(histogram_selection_dictionary[system][function])
        keys_before_element = list(selection_dict_for_length_after.keys())[:list(selection_dict_for_length_after.keys()).index(element)]
        product_of_lengths_after_element = product_of_keys_lengths(keys_before_element, selection_dict_for_length_after)

        element_selections = histogram_selection_dictionary[system][function][element]
        element_length = len(element_selections)
        
        for selecto in Bin_labelss[system]:
            selection_dict = copy.deepcopy(selecto)
            selection_dict.pop(element)
            for key, value in selection_dict.items():
                name = "{}:{}".format(key, value) + "\n"
                names.append(name)
        
        for k, element_selection in enumerate(element_selections):                            
            new_list = [histogram_dictionary[system][function][histogram_type][(product_of_lengths_after_element*n) + ((k*product_of_lengths_after_element)/element_length):(product_of_lengths_after_element*n) + ((k*product_of_lengths_after_element)/element_length) + product_of_lengths_after_element/element_length] for n in range(product_of_lengths_before_element)]
            selected_histogram_list_type_per_element = [item for sublist in new_list for item in sublist]
            hist_2d_list.append(make_histogram(selected_histogram_list_type_per_element, names, element_selection))
        twoDD_histograms[system][function][histogram_type][element] = hist_2d_list        
    else:
        if function == "no_function":
            names.append("Nothing")
        else:
            for selection in histogram_selection_dictionary[system][function]:
                name = "selection : {}".format(selection)
                names.append(name)
        
        selected_histogram_list_type_per_element = histogram_dictionary[system][function][histogram_type]
        hist_2d_list.append(make_histogram(selected_histogram_list_type_per_element, names))
        twoDD_histograms[system][function][histogram_type] = hist_2d_list

twoD_histograms = {}

for system in histogram_dictionary.keys():
    twoD_histograms[system] = {}
    functions = histogram_dictionary[system].keys()  
    for function in functions:
        twoD_histograms[system][function]= {}
        histogram_types = histogram_dictionary[system][function].keys()
        for histogram_type in histogram_types:
            if function == "no_function" and len(histogram_selection_dictionary[system][function].keys()) != 0:
                twoD_histograms[system][function][histogram_type]= {}
                for element in histogram_selection_dictionary[system][function].keys():
                    craete_histogram(twoD_histograms, system, function, histogram_type, element)
            else:
                twoD_histograms[system][function][histogram_type] = []
                craete_histogram(twoD_histograms, system, function, histogram_type) 

canvas = ROOT.TCanvas("canvas", "Canvas", 1000, 600)

for system in twoD_histograms.keys():
    sys_dir = "{}/{}".format(dir, system)
    if not os.path.exists(sys_dir):
        os.makedirs(sys_dir)
    for function in twoD_histograms[system].keys():
        func_dir = "{}/{}".format(sys_dir, function)
        if not os.path.exists(func_dir):
            os.makedirs(func_dir)
        if function == "no_function" and len(histogram_selection_dictionary[system][function].keys()) != 0:
            for histo_type in twoD_histograms[system][function].keys():
                histo_type_dir = "{}/{}".format(func_dir, histo_type)
                if not os.path.exists(histo_type_dir):
                    os.makedirs(histo_type_dir)
                for element in twoD_histograms[system][function][histo_type]:
                    element_dir = "{}/{}".format(histo_type_dir, element)
                    if not os.path.exists(element_dir):
                        os.makedirs(element_dir)
                    for histogram in twoD_histograms[system][function][histo_type][element]:
                        histogram.Draw("COLZ")
                        canvas.SaveAs("{}/{}{}".format(element_dir, histogram.GetName(), ".pdf"))
        else:
            for histo_type in twoD_histograms[system][function].keys():
                histo_type_dir = "{}/{}".format(func_dir, histo_type)
                if not os.path.exists(histo_type_dir):
                    os.makedirs(histo_type_dir)                
                for histogram in twoD_histograms[system][function][histo_type]:
                    histogram.Draw("COLZ")
                    canvas.SaveAs("{}/{}{}".format(histo_type_dir, histogram.GetName(), ".pdf"))