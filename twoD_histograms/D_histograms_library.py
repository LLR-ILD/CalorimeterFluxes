from collections import OrderedDict
import copy 
import re
import ROOT
import os

#Sorting functions
##################################################################################################################################################

"""This function takes the selection string that can occur in two formats (either a range in the form (x:y) where both x and y are integers or just an integer value). 
   The output would be an ordered pair having the range minimum as the first element and the range maximum as the second one in case we have a range or a repeated value
   if we get an integer. This function acts to transform the selection string into a numerical tuple that can be used easier in sorting later. 
"""
def parse_selection_string(selection_string):
    # Parse a selection string and return a tuple (start, end)
    if ':' in selection_string:
        return tuple(map(int, selection_string.split(':')))
    else:
        return (int(selection_string), int(selection_string))

"""This function acts to sort the bin labels in the same way the histograms are sorted. According to histograms_selections and create_histograms functions, the bin labels would
   take the format: "Staves:(x:y if range or x if just an integer) (new line) Modules: (the same as staves) and then Towers and Layers in the same way as Staves". If we don't have selections
   on an element, its string wouldn't appear. Thus, we search for the patterns and if found we put the value in an ordered tuple and if not, we put infinity. The ordering is ascending.
   (\d+(:\d+)?): \d+ searches for a number (+ allows for a number greater than 9), (:\d+)? searches for a colon followed by another number (? guarantees that this one is not necessary if we
   don't have a range) and the parentheses group all of this as a whole. 
"""
def extract_ranges(string):
    # Find all numbers or number ranges following the category names
    staves_match = re.search(r"Staves:(\d+(:\d+)?)", string)
    modules_match = re.search(r"Modules:(\d+(:\d+)?)", string)
    towers_match = re.search(r"Towers:(\d+(:\d+)?)", string)
    layers_match = re.search(r"Layers:(\d+(:\d+)?)", string)

    # Parse the found ranges, or use infinity if not found
    staves = parse_selection_string(staves_match.group(1)) if staves_match else (float('inf'),)
    modules = parse_selection_string(modules_match.group(1)) if modules_match else (float('inf'),)
    towers = parse_selection_string(towers_match.group(1)) if towers_match else (float('inf'),)
    layers = parse_selection_string(layers_match.group(1)) if layers_match else (float('inf'),)

    return (staves, modules, towers, layers)

"""This function is exactly as the one above but this one is designed for the complex functions where the bin labels take the form Selection:(x:y or x). The logic is the same.
"""
def extract_ranges_functions(string):
    selection_match = re.search(r"Selection:(\d+(:\d+)?)", string)
    selection = parse_selection_string(selection_match.group(1)) if selection_match else (float('inf'),)
    return selection 

"""This function is designed for the sorting of the histograms. It takes the names of histograms and split them by _ to read off the selections on Staves, Modules, Towers and Layers. 
   If a selection on element is found, the selection string is saved in a dictionary but after being parsed by parse_selection_string defined above. 
"""
def extract_values(histogram):
    # Extract values from the name and return a dictionary with parsed numbers
    values = {'S': (float('inf'),), 'M': (float('inf'),), 'T': (float('inf'),), 'L': (float('inf'),)}
    parts = histogram.GetName().split("_")
    for part in parts:
        if re.match(r'[SMTL]\d', part):
            values[part[0]] = parse_selection_string(part[1:])
    return values

"""This function acts to order the dictionary values of the decoded selections into an ordered tuple to sort the histigrams later. 
"""
def histogram_sort_key(name):
    values = extract_values(name)
    # Flatten the dictionary values into a single tuple to represent the sort key
    return (values['S'], values['M'], values['T'], values['L'])

"""This function is designed for the decoding of the histograms. It takes the names of histograms and split them by _ to read off the selections on Staves, Modules, Towers and Layers. 
   If a selection on element is found, the selection string is saved in a dictionary. 
"""
def decoding(histogram):
    # Define a mapping from single letters to full category names
    category_mapping = {'S': 'Staves', 'M': 'Modules', 'T': 'Towers', 'L': 'Layers'}
    
    # Extract values from the name and return a dictionary with selection strings
    values = OrderedDict()
    parts = histogram.GetName().split("_")
    for part in parts:
        if re.match(r'[SMTL]\d', part):
            # Use the category_mapping to get the full category name
            category = category_mapping[part[0]]
            values[category] = part[1:]
    return values
##################################################################################################################################################

# Functions to read the 1D histograms from the ROOT file and retrieve their information.

##################################################################################################################################################

"""A function to read off the histograms structure from the root file and build the very same hierarchical structure. 
""" 
def get_histograms(file):

    histogram_dictionary = OrderedDict()
    stats_dict = OrderedDict()
    systems = file.GetListOfKeys()
    
    for system in systems:
        system_name = system.GetName()
        histogram_dictionary[system_name]= OrderedDict()  # Create a new dictionary for this system
        stats_dict[system_name] = OrderedDict()
        functions = system.ReadObj().GetListOfKeys()

        for function in functions:
            function_name = function.GetName()
            histogram_dictionary[system_name][function_name] = OrderedDict()  # Create a new dictionary for this function
            stats_dict[system_name][function_name] = OrderedDict()  # Create a new dictionary for this function
            histogram_sets = function.ReadObj().GetListOfKeys()
            
            for histogram_type in histogram_sets:
                histogram_type_name = histogram_type.GetName()
                histograms = histogram_type.ReadObj().GetListOfKeys()
                histograms_list = []
                
                for histogram in histograms:
                    histogram_obj = histogram.ReadObj()
                    if histogram_obj and histogram_obj.InheritsFrom("TH1F"):
                        histogram_obj.SetDirectory(0)  # Make ROOT retain ownership of the object
                        histograms_list.append(histogram_obj)
                if function == "no_function":
                    histograms_list = sorted(histograms_list, key=histogram_sort_key)
                histogram_dictionary[system_name][function_name][histogram_type_name] = histograms_list
                stats_dict[system_name][function_name][histogram_type_name] = []
                for hist in histograms_list:
                    stats_list=[hist.GetMean(), hist.GetStdDev(), hist.Integral()]
                    stats_dict[system_name][function_name][histogram_type_name].append(stats_list)
    file.Close()
    return histogram_dictionary, stats_dict

""" A function that reads off the x-axis titles from the histograms.
"""
def get_x_titles(histogram_dictionary, systems, excluded_types):
    histograms_x_titles = OrderedDict()
    histogram_types_unfiltered = histogram_dictionary[systems[0]]["no_function"].keys()
    histogram_type_names = [item for item in histogram_types_unfiltered if item not in excluded_types]
    for type_name in histogram_type_names:
        x_title = histogram_dictionary[systems[0]]["no_function"][type_name][0].GetXaxis().GetTitle()
        histograms_x_titles[type_name] = x_title
    return histograms_x_titles

""" A function that reads off the y-axis titles from the histograms.
"""
def get_y_titles(histogram_dictionary, systems, excluded_types):
    histograms_y_titles = OrderedDict()
    histogram_types_unfiltered = histogram_dictionary[systems[0]]["no_function"].keys()
    histogram_type_names = [item for item in histogram_types_unfiltered if item not in excluded_types]
    for type_name in histogram_type_names:
        y_title = histogram_dictionary[systems[0]]["no_function"][type_name][0].GetYaxis().GetTitle() # The y-axis titles are the same for all the selections, all the systems and all the functions. 
        histograms_y_titles[type_name] = y_title
    return histograms_y_titles

""" A function to decode the histograms selections from their names.
    The decoding depends on how the histograms are  named according to histograms_for_functions and merge_histograms in histograms_library.py.
"""
def histograms_selections(histogram_dictionary, systems, system_functions):
    histogram_selection_dictionary = OrderedDict()
    Bin_labels = OrderedDict()

    for system in systems:
        histogram_selection_dictionary[system] = OrderedDict()
        functions = system_functions[system]
        Bin_labels[system] = []
        
        for function in functions:
            
            if function == "no_function":
                histogram_selection_dictionary[system][function] = OrderedDict()
                histogram_selection_dictionary[system][function]['Staves'] = []
                histogram_selection_dictionary[system][function]['Modules'] = []
                histogram_selection_dictionary[system][function]['Towers'] = []
                histogram_selection_dictionary[system][function]['Layers'] = []
                
                for histogram in histogram_dictionary[system][function]["time"]: #Related to how the time hisotgrams are the easiest to decode their names depending on the aforementioned functions.
                    
                    dict_labels = decoding(histogram)
                    for key, value in dict_labels.items():
                        if value not in histogram_selection_dictionary[system][function][key]:histogram_selection_dictionary[system][function][key].append(value)
                    Bin_labels[system].append(dict_labels)
                
                histogram_selection_dictionary_keys = histogram_selection_dictionary[system][function].keys()
                for key in histogram_selection_dictionary_keys:
                    if len(histogram_selection_dictionary[system][function][key]) == 0:
                        histogram_selection_dictionary[system][function].pop(key)        
            else:
                histogram_selection_dictionary[system][function] = []
                
                for histogram in histogram_dictionary[system][function]["time"]:
                    key = histogram.GetName().split("_")
                    selection = key[-2]
                    histogram_selection_dictionary[system][function].append(selection)
    return histogram_selection_dictionary, Bin_labels

##################################################################################################################################################

# Functions for 2D histograms        

##################################################################################################################################################

def get_min_max(histograms_list):
    overall_min = float('inf') # Start with a very large number
    overall_max = float('-inf')  # Start with a very small number
    for hist in histograms_list:
        for bin in range(1, hist.GetNbinsX() + 1):
            bin_content = hist.GetBinContent(bin)            
            # Update overall_min for non-zero values
            if 0 < bin_content < overall_min:
                overall_min = bin_content
            # Update overall_max
            if bin_content > overall_max:
                overall_max = bin_content
    # If overall_min wasn't updated, set it to a default small value
    if overall_min == float('inf'):
        overall_min = 1e-6
    # If overall_max wasn't updated (very unlikely), set it to a default larger value
    if overall_max == float('-inf'):
        overall_max = 1e3  # Example default value
    return overall_min, overall_max

def get_secondary_stat(hist, secondary):
    
    if not secondary:
        stats = [hist.GetMean(), hist.GetStdDev(), hist.Integral()]
    else:
        stats_box = hist.GetListOfFunctions().FindObject("stats")
        text_list = stats_box.GetListOfLines()
        iterator = text_list.MakeIterator()
        item = iterator.Next()
        while item:
            text_content = item.GetTitle()
            if "Mean" in text_content:
                mean_value = float(text_content.split()[1])
            elif "Std Dev" in text_content:
                std_dev_value = float(text_content.split()[2])
            elif "Entries" in text_content:
                entries = float(text_content.split()[1])
            item = iterator.Next()
        stats = [mean_value, std_dev_value, entries]
        
    return stats

def make_histogram(histogram_dictionary, histogram_selection_dictionary, histograms_x_titles, selected_histogram_list_type_for_element,  histos_names, system, function, histogram_type, secondary_types=[], element=None, element_selection = None):
    min_bin_value = min([hist.GetXaxis().GetXmin() for hist in selected_histogram_list_type_for_element])
    max_bin_value = max([hist.GetXaxis().GetXmax() for hist in selected_histogram_list_type_for_element])
    max_bins_type = max([hist.GetNbinsX() for hist in selected_histogram_list_type_for_element])
    oneD_histos_stats = []
    if function == "no_function" and len(histogram_selection_dictionary[system][function].keys()) != 0 and len(histogram_selection_dictionary[system][function].keys()) != 1:
        hist_2d_type = ROOT.TH2F("{}_{}_{}_{}_{}".format(system, function, histogram_type, element, element_selection), "{} {} {} {}".format(system, histogram_type, element, element_selection), len(selected_histogram_list_type_for_element), 0, len(selected_histogram_list_type_for_element), max_bins_type, min_bin_value, max_bin_value)
    else:
        hist_2d_type = ROOT.TH2F("{}_{}_{}".format(system, function, histogram_type), "{}_{}_{}".format(system, function, histogram_type), len(histogram_dictionary[system][function][histogram_type]), 0, len(histogram_dictionary[system][function][histogram_type]), max_bins_type, min_bin_value, max_bin_value)
    hist_2d_type.GetYaxis().SetTitle(histograms_x_titles[histogram_type])
    secondary = histogram_type in secondary_types
    for i, hist in enumerate(selected_histogram_list_type_for_element):
        hist_2d_type.GetXaxis().SetBinLabel(i+1, histos_names[i])
        oneD_histos_stats.append(get_secondary_stat(hist, secondary))
        for bin in range(1, hist.GetNbinsX() + 1):
            hist_2d_type.Fill(i, hist.GetBinCenter(bin), hist.GetBinContent(bin))
    hist_2d_type.SetMinimum(get_min_max(selected_histogram_list_type_for_element)[0])
    hist_2d_type.SetMaximum(get_min_max(selected_histogram_list_type_for_element)[1])
    return hist_2d_type, oneD_histos_stats

def product_of_keys_lengths(keys_element, dictionary):
    for key in keys_element:
        dictionary.pop(key)
    lengths_element = [len(v) for v in dictionary.values()]
    product_of_lengths_element = 1
    for i in range(len(lengths_element)):
        product_of_lengths_element = product_of_lengths_element*lengths_element[i]
    return product_of_lengths_element

def create_histogram(twoDD_histograms, oneDD_stats, histogram_dictionary, histograms_x_titles, histogram_selection_dictionary, Bin_labelss, system, function, histogram_type, secondary_types=[], element=None):
    names = []
    hist_2d_list = []
    oneD_stats_list = []
    
    if function == "no_function" and len(histogram_selection_dictionary[system][function].keys()) != 0 and len(histogram_selection_dictionary[system][function].keys()) != 1:

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
            name = ""
            for key, value in selection_dict.items(): name = name + "{}:{}".format(key, value) + " "
            if name not in names: names.append(name) # preemptive line to make sure that there is no duplication; however, the code is structured that this is avoided by default. It is a way to avoid human mistakes.
        names = sorted(names, key=extract_ranges)    
        for k, element_selection in enumerate(element_selections):                            
            new_list = [histogram_dictionary[system][function][histogram_type][(product_of_lengths_after_element*n) + ((k*product_of_lengths_after_element)/element_length):(product_of_lengths_after_element*n) + ((k*product_of_lengths_after_element)/element_length) + product_of_lengths_after_element/element_length] for n in range(product_of_lengths_before_element)]
            selected_histogram_list_type_per_element = [item for sublist in new_list for item in sublist]
            hist_twoD, one_Dstat = make_histogram(histogram_dictionary, histogram_selection_dictionary, histograms_x_titles, selected_histogram_list_type_per_element,  names, system, function, histogram_type, secondary_types, element, element_selection)
            hist_2d_list.append(hist_twoD)
            oneD_stats_list.append(one_Dstat)
            twoDD_histograms[system][function][histogram_type][element] = hist_2d_list
            oneDD_stats[system][function][histogram_type][element] = oneD_stats_list
    else:
        if function == "no_function" and len(histogram_selection_dictionary[system][function].keys()) == 1:
            for selecto in Bin_labelss[system]:
                for key, value in selecto.items(): name = "{}:{}".format(key, value) + "\n"
                if name not in names: names.append(name)
            names = sorted(names, key=extract_ranges)
        elif function == "no_function" and len(histogram_selection_dictionary[system][function].keys()) == 0:
            names.append("Nothing")
        else:
            for selection in histogram_selection_dictionary[system][function]:
                name = "Selection:{}".format(selection)
                names.append(name)
            names = sorted(names, key=extract_ranges_functions)
        selected_histogram_list_type_per_element = histogram_dictionary[system][function][histogram_type]
        hist_twoD, one_Dstat = make_histogram(histogram_dictionary, histogram_selection_dictionary, histograms_x_titles, selected_histogram_list_type_per_element, names, system, function, histogram_type, secondary_types)
        hist_2d_list.append(hist_twoD)
        oneD_stats_list.append(one_Dstat)
        twoDD_histograms[system][function][histogram_type] = hist_2d_list
        oneDD_stats[system][function][histogram_type] = oneD_stats_list 

def all_histograms(histogram_dictionary, histograms_x_titles, histogram_selection_dictionary, Bin_labels, systems, system_functions, excluded_types, secondary_types=[]):
    twoD_histograms, oneD_stats = {}, {}

    for system in systems:
        twoD_histograms[system], oneD_stats[system] = {}, {}
        functions = system_functions[system]  
        for function in functions:
            twoD_histograms[system][function], oneD_stats[system][function]= {}, {}
            histogram_types_unfiltered = histogram_dictionary[system][function].keys()
            histogram_types = [item for item in histogram_types_unfiltered if item not in excluded_types]
            for histogram_type in histogram_types:
                if function == "no_function" and len(histogram_selection_dictionary[system][function].keys()) != 0 and len(histogram_selection_dictionary[system][function].keys()) != 1:
                    twoD_histograms[system][function][histogram_type], oneD_stats[system][function][histogram_type]= {}, {}
                    for element in histogram_selection_dictionary[system][function].keys():
                        create_histogram(twoD_histograms, oneD_stats, histogram_dictionary, histograms_x_titles, histogram_selection_dictionary, Bin_labels, system, function, histogram_type, secondary_types, element)
                else:
                    twoD_histograms[system][function][histogram_type], oneD_stats[system][function][histogram_type] = [], []
                    create_histogram(twoD_histograms, oneD_stats, histogram_dictionary, histograms_x_titles, histogram_selection_dictionary, Bin_labels, system, function, histogram_type, secondary_types)
    return twoD_histograms, oneD_stats

##################################################################################################################################################

# Functions for writing the histograms        

##################################################################################################################################################

def saving_histogram(histogram_list, stats_list, save_dir, histograms_y_titles, histo_type, canvas, entries, units, log, stats):
    if log: 
        canvas.SetLogz(1) # A flag that changes the scale to logarithmic if needed
    else:
        canvas.SetLogz(0)
    for n, histogram in enumerate(histogram_list):
        histogram.SetStats(0)  # Remove the statistics box
        histogram.Draw("COLZ")
        canvas.Update()  # Update the canvas to ensure the palette is created
        
        stats_boxes = []  # List to hold TPaveText objects
        
        if stats:
            xbins_number = histogram.GetNbinsX()
            xmin, xmax = histogram.GetXaxis().GetXmin(), histogram.GetXaxis().GetXmax()  # Get X-axis range
            xrange = xmax - xmin  # Calculate the X-axis range
            ymin, ymax = histogram.GetYaxis().GetXmin(), histogram.GetYaxis().GetXmax()  # Get Y-axis range
            yrange = ymax - ymin  # Calculate the Y-axis range
            
            stats_per_2Dhistogram = stats_list[n]
            for m, oneD_stat in enumerate(stats_per_2Dhistogram):
                # Create a TPaveText to display the stats
                x1NDC = ((((m+1)*xrange)/xbins_number) - 1) + xmin
                x2NDC = ((((m+1)*xrange)/xbins_number)) + xmin
                y1NDC = -0.3*yrange + ymin
                y2NDC = -0.1*yrange + ymin
                stats_box = ROOT.TPaveText(x1NDC, y1NDC, x2NDC, y2NDC)
                
                # Calculate statistics for this projection
                mean, stddev, sum_bin_contents = oneD_stat[0], oneD_stat[1], oneD_stat[2]
                stats_box.AddText("Mean: {:.2e} {}".format(mean,units[histo_type]))
                stats_box.AddText("Std Dev: {:.2e} {}".format(stddev,units[histo_type]))
                stats_box.AddText("{}: {:.2e}".format(entries[histo_type],sum_bin_contents))
                stats_box.SetTextSize(0.03)  # Adjust font size as needed                
                stats_boxes.append(stats_box)  # Add to list to maintain scope
                 
        # Draw the stats boxes after histogram
        for box in stats_boxes:
            box.Draw()
        # Update canvas to reflect the drawn stats boxes
        canvas.Modified()
        canvas.Update()    
        
        palette = histogram.GetListOfFunctions().FindObject("palette")
        if palette:
            x1 = palette.GetX1NDC()
            y1 = palette.GetY1NDC()
            x2 = palette.GetX2NDC()
            y2 = palette.GetY2NDC()

            # Create a TLatex object for the title
            latex = ROOT.TLatex()
            latex.SetTextSize(0.03)
            latex.SetTextAlign(33)  # Horizontal center and vertical top
            latex.SetTextFont(42)

            # Position the title above or to the right of the color palette
            title_x = x2 + 0.02  # Adjust as needed
            title_y = y2 + 0.05  # Centered vertically on the palette
            latex.DrawLatexNDC(title_x, title_y, histograms_y_titles[histo_type])

        canvas.Modified()  # Apply the modifications
        canvas.Update()  # Update the canvas again to reflect the changes
        canvas.SaveAs("{}/{}{}".format(save_dir, histogram.GetName(), ".pdf"))
        existing_hist = ROOT.gDirectory.Get(histogram.GetName())
        if existing_hist:ROOT.gDirectory.Delete(histogram.GetName() + ";*")  # Delete all versions
        histogram.Write()
        histogram.Delete()

def write_histograms(twoD_histograms, stats_dict, histogram_selection_dictionary, histograms_y_titles, dir, canvas, entries, units, log=False, stats=False):
    if not os.path.exists(dir):os.makedirs(dir)
    myfile = ROOT.TFile(dir + '/all.root', 'UPDATE')
    for system in twoD_histograms.keys():
        if not myfile.GetDirectory(system): # Check if the directory exists
            sys_dir_root = myfile.mkdir(system) # If the directory does not exist, create it
        else:
            sys_dir_root = myfile.GetDirectory(system) # If it exists, retrieve the existing directory
        if sys_dir_root is None: print("Failed to create directory: {}".format(system))
        sys_dir = "{}/{}".format(dir, system)
        if not os.path.exists(sys_dir): os.makedirs(sys_dir)
        for function in twoD_histograms[system].keys():
            if not sys_dir_root.GetDirectory(function): # Check if the directory exists
                func_dir_root = sys_dir_root.mkdir(function) # If the directory does not exist, create it
            else:
                func_dir_root = sys_dir_root.GetDirectory(function) # If it exists, retrieve the existing directory
            if func_dir_root is None: print("Failed to create directory: {}:{}".format(system, function))
            func_dir = "{}/{}".format(sys_dir, function)
            if not os.path.exists(func_dir): os.makedirs(func_dir)
            if function == "no_function" and len(histogram_selection_dictionary[system][function].keys()) != 0 and len(histogram_selection_dictionary[system][function].keys()) != 1:
                for histo_type in twoD_histograms[system][function].keys():
                    if not func_dir_root.GetDirectory(histo_type): # Check if the directory exists
                        histo_type_dir_root = func_dir_root.mkdir(histo_type) # If the directory does not exist, create it
                    else:
                        histo_type_dir_root = func_dir_root.GetDirectory(histo_type) # If it exists, retrieve the existing directory
                    histo_type_dir = "{}/{}".format(func_dir, histo_type)
                    if not os.path.exists(histo_type_dir): os.makedirs(histo_type_dir)
                    for element in twoD_histograms[system][function][histo_type]:
                        if not histo_type_dir_root.GetDirectory(element): # Check if the directory exists
                            element_dir_root = histo_type_dir_root.mkdir(element) # If the directory does not exist, create it
                        else:
                            element_dir_root = histo_type_dir_root.GetDirectory(element) # If it exists, retrieve the existing directory
                        element_dir_root.cd()
                        element_dir = "{}/{}".format(histo_type_dir, element)
                        if not os.path.exists(element_dir): os.makedirs(element_dir)
                        histogram_list = twoD_histograms[system][function][histo_type][element]
                        stats_list = stats_dict[system][function][histo_type][element]
                        saving_histogram(histogram_list, stats_list, element_dir, histograms_y_titles, histo_type, canvas, entries, units, log, stats)
            else:
                for histo_type in twoD_histograms[system][function].keys():
                    if not func_dir_root.GetDirectory(histo_type): # Check if the directory exists
                        histo_type_dir_root = func_dir_root.mkdir(histo_type) # If the directory does not exist, create it
                    else:
                        histo_type_dir_root = func_dir_root.GetDirectory(histo_type) # If it exists, retrieve the existing directory                    
                    histo_type_dir_root.cd()
                    histo_type_dir = "{}/{}".format(func_dir, histo_type)
                    if not os.path.exists(histo_type_dir): os.makedirs(histo_type_dir)
                    histogram_list = twoD_histograms[system][function][histo_type]
                    stats_list = stats_dict[system][function][histo_type] 
                    saving_histogram(histogram_list, stats_list, histo_type_dir, histograms_y_titles, histo_type, canvas, entries, units, log, stats)
    myfile.Close()