from __future__ import absolute_import
from __future__ import print_function  # python3 style printing in python2.
import os
import sys
from pyLCIO.io import LcioReader
from pyLCIO import EVENT, UTIL
import ROOT
import multiprocessing
from copy import deepcopy
from collections import namedtuple
import traceback
from array import array

# Decoding 

#####################################################################################

cell_id_info = ["system", "stave", "module", "cellX", "cellY", "tower", "layer"]
endcap_replacements = dict(cellX="x", cellY="y")
def decoding(id_decoder, hit, is_ecal_endcap_ring=False):     
    cell_id = (hit.getCellID0() & 0xffffffff) | (hit.getCellID1() << 32)
    id_decoder.setValue(cell_id)
    hit_info = {}
    for cell_id_key in cell_id_info:
        encoded_key = cell_id_key
        if is_ecal_endcap_ring and cell_id_key in endcap_replacements:
            encoded_key = endcap_replacements[cell_id_key]
        hit_info[encoded_key + 's'] = int(id_decoder[encoded_key].value())
        hit_info["energy"] = hit.getEnergy()
        hit_info["pos_x"] = hit.getPosition()[0]
        hit_info["pos_y"] = hit.getPosition()[1]
        hit_info["pos_z"] = hit.getPosition()[2]    
    return hit_info

SubhitInfo = namedtuple("SubhitInfo", ["energy", "time", "pos_x", "pos_y", "pos_z"])
def subhit_decoding(hit):
    hit_subhits = []
    for i_subhit in range(hit.getNMCContributions()):
        subhit = SubhitInfo(energy=hit.getEnergyCont(i_subhit), time=hit.getTimeCont(i_subhit), pos_x=hit.getStepPosition(i_subhit)[0], pos_y=hit.getStepPosition(i_subhit)[1], pos_z=hit.getStepPosition(i_subhit)[2])
        hit_subhits.append(subhit)
    return hit_subhits

ring_collections = ["EcalEndcapRingCollection",
                        "HCalBarrelRPCHits",
                        "HCalECRingRPCHits",
                        "HCalEndcapRPCHits",
                        "HcalBarrelRegCollection",
                        "HcalEndcapRingCollection",
                        "HcalEndcapsCollection"]

###########################################################################################################

# Class to create complex functions of selections

###########################################################################################################

class ComplexFunction:
    def __init__(self, equation, name):
        self.equation = equation
        self.name = name

    def __call__(self, selection, is_endcap, decoded_hit):
        stave = decoded_hit["staves"]
        module = decoded_hit["modules"]
        tower = decoded_hit['towers']
        layer = decoded_hit['layers']
        if is_endcap:
            y_position = decoded_hit["ys"]
            x_position = decoded_hit["xs"]
        else:
            y_position = decoded_hit["cellYs"]
            x_position = decoded_hit["cellXs"]
        value = self.equation(stave, module, tower, layer, x_position, y_position)
        if isinstance(selection, list):
            if float(selection[0]) <= value <= float(selection[1]):
                return True
            else:
                return False
        else:
            if value == float(selection):
                return True
            else:
                return False

###########################################################################################################

# functions that create the dictionaries of histograms. 
# The functions follow the data sturcture of dictionary_of_system to be defined in the main steering script.

###########################################################################################################

def histograms_creation(histograms_to_select, histogram_name, time_args, lower_scale_args, upper_scale_args, all_scale_args, Nhits_args, high_Nhits_args, all_Nhit_args, threshold, mip, en_mip):
    created_histograms = {}
    mip_value = mip["_".join(histogram_name.split("_")[1:]) + '_lower_scale']
    if histograms_to_select["time"]:
        hist_time = ROOT.TH1F(histogram_name + '_time', 'Time histogram - {}'.format(histogram_name), time_args[0], 6, time_args[1])
        hist_time.GetXaxis().SetTitle("Weighted Time of Subhits [ns]")
        hist_time.GetYaxis().SetTitle("Number of hits times Energy [GeV]")
        created_histograms["time"] = hist_time

    if histograms_to_select["lower_scale_energy"]:
        hist_lower_scale = ROOT.TH1F(histogram_name + '_lower_scale', 'Lower-Scale Energy histogram - {}'.format(histogram_name), lower_scale_args[0], 0, lower_scale_args[1])
        hist_lower_scale.GetXaxis().SetTitle("Energy [GeV]")
        hist_lower_scale.GetYaxis().SetTitle("Number of hits")
        created_histograms["lower_scale_energy"] = hist_lower_scale
    
    if histograms_to_select["upper_scale_energy"]:
        hist_upper_scale = ROOT.TH1F(histogram_name + '_upper_scale', 'Upper-Scale Energy histogram - {}'.format(histogram_name), upper_scale_args[0], lower_scale_args[1], upper_scale_args[1])
        hist_upper_scale.GetXaxis().SetTitle("Energy [GeV]")
        hist_upper_scale.GetYaxis().SetTitle("Number of hits")
        hist_upper_scale.SetCanExtend(ROOT.TH1.kAllAxes)
        created_histograms["upper_scale_energy"] = hist_upper_scale

    if histograms_to_select["all_scale_energy"]:
        hist_all_energy = ROOT.TH1F(histogram_name + 'all_scale_energy', 'Energy histogram - {}'.format(histogram_name), all_scale_args[0], 0, all_scale_args[1])
        hist_all_energy.GetXaxis().SetTitle("Energy [GeV]")
        hist_all_energy.GetYaxis().SetTitle("Number of hits")
        hist_all_energy.SetCanExtend(ROOT.TH1.kAllAxes)
        created_histograms["all_scale_energy"] = hist_all_energy

    if histograms_to_select["scaled_upper_scale_energy"]:
        hist_scaled_upper_scale = ROOT.TH1F(histogram_name + '_scaled_upper_scale', 'Scaled Upper-Scale Energy histogram - {}'.format(histogram_name), upper_scale_args[0], (lower_scale_args[1]/mip_value), (upper_scale_args[1]/mip["_".join(histogram_name.split("_")[1:]) + '_lower_scale']))
        hist_scaled_upper_scale.GetXaxis().SetTitle("MIP")
        hist_scaled_upper_scale.GetYaxis().SetTitle("Number of hits")
        hist_scaled_upper_scale.SetCanExtend(ROOT.TH1.kAllAxes)
        created_histograms["scaled_upper_scale_energy"] = hist_scaled_upper_scale

    if histograms_to_select["scaled_all_scale_energy"]:
        hist_scaled_all_scale = ROOT.TH1F(histogram_name + '_scaled_all_scale', 'Scaled Energy histogram - {}'.format(histogram_name), all_scale_args[0], 0, (all_scale_args[1]/mip_value))
        hist_scaled_all_scale.GetXaxis().SetTitle("MIP")
        hist_scaled_all_scale.GetYaxis().SetTitle("Number of hits")
        hist_scaled_all_scale.SetCanExtend(ROOT.TH1.kAllAxes)
        created_histograms["scaled_all_scale_energy"] = hist_scaled_all_scale
    
    x_title_suffix_Nhits = str("{:.2e}".format(mip_value/4)) + " GeV  (MIP/4)" if en_mip else str(threshold[0]) + " GeV"
    if histograms_to_select["low_#Nhits"]:
        bin_width = Nhits_args[1] / Nhits_args[0] # Calculate the bin width
        bin_edges = [(i-0.5)*bin_width for i in range(Nhits_args[0] + 1)] # Define the bin edges

        hist_Nhits = ROOT.TH1F(histogram_name + '_#hits', 'Lower-Scale #hits histogram - {}'.format(histogram_name), Nhits_args[0], array('d', bin_edges))
        hist_Nhits.GetXaxis().SetTitle("Number of hits above " + x_title_suffix_Nhits)
        hist_Nhits.GetYaxis().SetTitle("Number of Events")
        created_histograms["low_#Nhits"] = hist_Nhits
    if histograms_to_select["high_#Nhits"]:
        hist_high_Nhits = ROOT.TH1F(histogram_name + '_high_#hits', 'Upper-Scale #hits histogram - {}'.format(histogram_name), high_Nhits_args[0], Nhits_args[1], high_Nhits_args[1])
        hist_high_Nhits.GetXaxis().SetTitle("Number of hits above " + x_title_suffix_Nhits)
        hist_high_Nhits.GetYaxis().SetTitle("Number of Events")
        hist_high_Nhits.SetCanExtend(ROOT.TH1.kAllAxes)
        created_histograms["high_#Nhits"] = hist_high_Nhits

    if histograms_to_select["all_#Nhits"]:
        hist_all_Nhits = ROOT.TH1F(histogram_name + '_all_#hits', '#hits histogram - {}'.format(histogram_name), all_Nhit_args[0], 0, all_Nhit_args[1])
        hist_all_Nhits.GetXaxis().SetTitle("Number of hits above " + x_title_suffix_Nhits)
        hist_all_Nhits.GetYaxis().SetTitle("Number of Events")
        hist_all_Nhits.SetCanExtend(ROOT.TH1.kAllAxes)
        created_histograms["all_#Nhits"] = hist_all_Nhits

    return created_histograms

type_names = ["time", "lower_scale_energy", "upper_scale_energy", "all_scale_energy", "scaled_upper_scale_energy", "scaled_all_scale_energy", "low_#Nhits", "high_#Nhits", "all_#Nhits"]
types_number = len(type_names)

def appending(dictionary_of_system, system, histograms_to_select, histogram_name, histograms_lists, mip, en_mip):
    histograms_args = dictionary_of_system[system][2]
    
    time_args, lower_scale_args, upper_scale_args, all_scale_args, Nhits_args, high_Nhits_args, all_Nhit_args, threshold = histograms_args
    
    histograms = histograms_creation(
        histograms_to_select, histogram_name,
        time_args, lower_scale_args, upper_scale_args, all_scale_args, Nhits_args, high_Nhits_args, all_Nhit_args, threshold, mip, en_mip)
    
    names_to_lists = zip(type_names, histograms_lists)
    
    for type_name, type_list in names_to_lists:
        if type_name in histograms:
            type_list.append(histograms[type_name])
        else:
            type_list.append(None)

def histograms_for_functions(dictionary_of_system, system, function, histograms_to_select, index, first_function, mip, en_mip):
    
    histograms_functions_lists = [[] for _ in range(types_number)]  
    function_dictionary_list = []
    Nhits_zeroes = []

    if first_function:
        staves, modules, towers, layers = dictionary_of_system[system][1]
        for stave in staves:
            for module in modules:
                for tower in towers:
                    for layer in layers:
                        parsed_func_selection = {}
                        my_dict = {'staves': stave, 'modules': module, 'towers': tower, 'layers': layer}
                        my_dict = {key: value for key, value in my_dict.items() if value != "*"}
                        for key, value in my_dict.items():
                            parsed_func_selection[key] = (map(int, value.split(':'))) if ':' in value else int(value)
                        function_dictionary_list.append(parsed_func_selection)
                        if histograms_to_select["low_#Nhits"] or histograms_to_select["high_#Nhits"] or histograms_to_select["all_#Nhits"]: 
                            Nhits_zeroes.append(0)
                        else: 
                            Nhits_zeroes.append(None)
                        histo_name = "{system}{stave}{module}{tower}{layer}".format(system=system, 
                                                                                                stave="_S" + stave if stave != "*" else "",
                                                                                                module="_M" + module if module != "*" else "", 
                                                                                                tower="_T" + tower if tower != "*" else "", 
                                                                                                layer="_L" + layer if layer != "*" else "")
                        appending(dictionary_of_system, system, histograms_to_select, "{}_".format(index) + histo_name, histograms_functions_lists, mip, en_mip)            
    else:
        function_limits = dictionary_of_system[system][3][function]
        for limit in function_limits:
            selection_string = (map(int, limit.split(':'))) if ':' in limit else int(limit)
            function_dictionary_list.append(selection_string)
            if histograms_to_select["low_#Nhits"] or histograms_to_select["high_#Nhits"] or histograms_to_select["all_#Nhits"]: 
                Nhits_zeroes.append(0)
            else: 
                Nhits_zeroes.append(None)

            histo_name = "{}_{}_{}".format(system, function, limit)
            appending(dictionary_of_system, system, histograms_to_select, "{}_".format(index) + histo_name, histograms_functions_lists, mip, en_mip)
    
    return histograms_functions_lists, function_dictionary_list, Nhits_zeroes

def histograms_for_systems(dictionary_of_system, system, histograms_to_select_function, system_functions, index, mip, en_mip):

    histograms_systems_dictionaries = [{} for _ in range(types_number)]
    parsing_function_dictionary = {}
    Nhits_dictionary={}
    
    functions = system_functions[system]
    first_function = True

    for function in functions:
        histograms_lists, parsing_function_dictionary[function], Nhits_dictionary[function] = histograms_for_functions(dictionary_of_system, system, function, histograms_to_select_function[function], index, first_function, mip, en_mip)
        for i in range(types_number): 
            histograms_systems_dictionaries[i][function] = histograms_lists[i]
        first_function = False
        
    return histograms_systems_dictionaries, Nhits_dictionary, parsing_function_dictionary

def name_histograms(dictionary_of_system, systems, histograms_to_select_system_function, system_functions, index, mip, en_mip):
    all_types_dictionaries = [{} for _ in range(types_number)]
    Nhits_dict = {}
    parsing_dict = {}

    for system in systems:
        system_hisotgrams, Nhits_dict[system], parsing_dict[system] = histograms_for_systems(dictionary_of_system, system, histograms_to_select_system_function[system], system_functions, index, mip, en_mip)
        for i in range(types_number):
            all_types_dictionaries[i][system] = system_hisotgrams[i]

    return all_types_dictionaries, Nhits_dict, parsing_dict

###########################################################################################################

# functions for filling the histograms. 

###########################################################################################################

def selecting(function_dict, funcion_name, func_selection, is_endcap, decoded_hit):
    values_same = True
    if funcion_name == "no_function":
        for key, value in func_selection.items():
            if isinstance(value, list):
                start, end = value
                if not (start <= decoded_hit[key] <= end):
                    values_same = False
                    break
            elif value != decoded_hit[key]:
                values_same = False
                break
    else:
        func = function_dict[funcion_name]
        values_same = func(func_selection, is_endcap, decoded_hit)
    return values_same

def fill_histogram(dictionary_of_system, systems, collections, function_dict, system_functions, mip, en_mip, histograms_to_select_dict, indexo, slcio_file,  ev_start, ev_stop):
    
    histograms_dicts, hits_dict, parsing_dicts = name_histograms(dictionary_of_system, systems, histograms_to_select_dict, system_functions, indexo, mip, en_mip)
    time_histograms, lower_scale_histograms, upper_scale_histograms, energy_histograms, scaled_upper_scale_histograms, scaled_energy_histograms,  Nhits_histograms, high_Nhits_histograms, all_Nhits_histograms = histograms_dicts
    reader = LcioReader.LcioReader(slcio_file)
    No_events = reader.getNumberOfEvents()
    print(No_events)
    if ev_stop < 0:
        ev_stop = No_events + ev_stop + 1
    
    for i, event in enumerate(reader):
        if i < ev_start:
            continue
        # Print out a progress update
        if i % 100 == 0:  # Adjust this condition to control how often updates are printed
            print('process : {} : processed {} out of {} items'.format(indexo, i, No_events))
        if i >= ev_stop:
            break
        
        Nhits = deepcopy(hits_dict)
        for collection_name in collections:
            is_endcap = (collection_name in ring_collections)
            try:
                calo_hits = event.getCollection(collection_name)
            except:
                continue
            cell_id_encoding = calo_hits.getParameters().getStringVal(EVENT.LCIO.CellIDEncoding)
            id_decoder = UTIL.BitField64(cell_id_encoding)
            for hit in calo_hits:
                decoded_hit = decoding(id_decoder, hit, is_endcap)
                energy = hit.getEnergy()
                subhit_information = subhit_decoding(hit)
                
                for system in systems:
                    system_material = dictionary_of_system[system]
                    if collection_name not in system_material[0]:
                        continue
                    functions = system_functions[system]
                    for function in functions:
                        histograms_to_select = histograms_to_select_dict[system][function]
                        iterable_histograms = zip(
                        time_histograms[system][function], 
                        lower_scale_histograms[system][function],
                        upper_scale_histograms[system][function],
                        energy_histograms[system][function],
                        scaled_upper_scale_histograms[system][function],
                        scaled_energy_histograms[system][function], 
                        parsing_dicts[system][function], 
                        enumerate(Nhits[system][function]))
                        for hist_time, hist_lower_scale, hist_upper_scale, hist_energy, scaled_hist_upper_scale, scaled_hist_energy, function_selection, (index, Nhit) in iterable_histograms:
                            if selecting(function_dict, function, function_selection, is_endcap, decoded_hit):
                                
                                #Number-of-cells-with-energy-above-threshold-per-cell histogram
                                threshold = (mip["_".join(hist_lower_scale.GetName().split("_")[1:])]/4) if en_mip else system_material[2][7][0]       #The energy threshold can be MIP/4 or given as a different input for every system in the dictionary of systems
                                if (histograms_to_select["low_#Nhits"] or histograms_to_select["high_#Nhits"] or histograms_to_select["all_#Nhits"]) and energy > threshold:
                                    Nhits[system][function][index] += 1
                                
                                #Lower-scale histogram
                                if histograms_to_select["lower_scale_energy"] and 0 <= energy < system_material[2][1][1]:
                                    hist_lower_scale.Fill(energy)
                                
                                #upper-scale histogram
                                if histograms_to_select["upper_scale_energy"] and energy > system_material[2][1][1]:
                                    hist_upper_scale.Fill(energy)
                                
                                #all energy histogram
                                if histograms_to_select["all_scale_energy"]:
                                    hist_energy.Fill(energy)

                                #scaled upper-scale histogram
                                if histograms_to_select["scaled_upper_scale_energy"] and energy > system_material[2][1][1]:
                                    scaled_hist_upper_scale.Fill(energy/(mip["_".join(hist_lower_scale.GetName().split("_")[1:])]))
                                
                                #scaled all energy histogram
                                if histograms_to_select["scaled_all_scale_energy"]:
                                    scaled_hist_energy.Fill(energy/(mip["_".join(hist_lower_scale.GetName().split("_")[1:])]))

                                #time histogram
                                if histograms_to_select["time"]:
                                    for subhit in subhit_information:
                                        hist_time.Fill(subhit.time, subhit.energy)
        for system in systems:
            system_material = dictionary_of_system[system]
            functions = system_functions[system]          
            for function in functions:
                histograms_to_select = histograms_to_select_dict[system][function]
                iterable_histograms = zip(Nhits[system][function], Nhits_histograms[system][function], high_Nhits_histograms[system][function], all_Nhits_histograms[system][function])
                for Nhit, hist_Nhits, hist_high_Nhits, hist_all_Nhits in iterable_histograms:
                    #Lower-scale histogram of #hits
                    if histograms_to_select["low_#Nhits"] and Nhit <= system_material[2][4][1]:
                        hist_Nhits.Fill(Nhit)
                    #Upper-scale histogram of #hits
                    if histograms_to_select["high_#Nhits"] and Nhit > system_material[2][4][1]:
                        hist_high_Nhits.Fill(Nhit)
                    #all-scale histogram of #hits
                    if histograms_to_select["all_#Nhits"]:
                        hist_all_Nhits.Fill(Nhit)
                    

    return [time_histograms, lower_scale_histograms, upper_scale_histograms, energy_histograms, scaled_upper_scale_histograms, scaled_energy_histograms,  Nhits_histograms, high_Nhits_histograms, all_Nhits_histograms]

###########################################################################################################

# functions for merging the histograms. 

###########################################################################################################

def find_max_range(histograms):
    max_range = 0
    for hist in histograms:
        maximum = hist.GetXaxis().GetXmax()
        if maximum > max_range:
            max_range = maximum
    return max_range

def merge_histograms(histograms, can_extend = True):
    """The histograms' properties are all similar. 
    That is why I retrieve the information from the first histogram (any other histogram would yield identical results).
    The only difference in the maximum range if the histogram can extend such as in the case of the upper-energy scale and number-of-hits-above-threshold histograms.
    For that difference, we apply find_max_range if the optional parameter can_extend is set True"""
    
    maximum = find_max_range(histograms) if can_extend else histograms[0].GetXaxis().GetXmax()
    minimum = histograms[0].GetXaxis().GetXmin()
    name = "_".join(histograms[0].GetName().split("_")[1:])
    title = "_".join(histograms[0].GetTitle().split("_")[1:])
    bins_number = histograms[0].GetXaxis().GetNbins()

    x_title = histograms[0].GetXaxis().GetTitle()
    y_title = histograms[0].GetYaxis().GetTitle()

    master_hist = ROOT.TH1F(name, title, bins_number, minimum, maximum)
    master_hist.GetXaxis().SetTitle(x_title)
    master_hist.GetYaxis().SetTitle(y_title)

    # Create a TList to hold the histograms
    hist_list = ROOT.TList()

    # Add each histogram to the TList
    for hist in histograms:
        hist_list.Add(hist)

    master_hist.Merge(hist_list)

    return master_hist  # This is the final merged histogram

def merging(number_of_processes, systems, system_functions, histograms_to_select_dict, list_of_all_histograms):
    
    # The histograms are retrieved in order according to the return of fill_histogram and parallel_processing functions.
    all_histograms = [[list_of_all_histograms[i][j] for i in range(number_of_processes)] for j in range(types_number)]    
    merged_all_histograms = [{} for _ in range(types_number)]
    
    for system in systems:
        
        for i in range(types_number): merged_all_histograms[i][system] = {}
        functions = system_functions[system]         
        
        for function in functions:
            merged_all_histos = [[] for _ in range(types_number)]

            system_function_selections = len(all_histograms[0][0][system][function]) # the 25 lists have the same length for having the same selections. Also, it is the same length for all the types for having the same set of selections.
            for selection_index in range(system_function_selections):
                histograms_to_merge = [[] for _ in range(types_number)]

                for proces_index in range(number_of_processes):
                    for j in range(types_number): histograms_to_merge[j].append(all_histograms[j][proces_index][system][function][selection_index])
                    
                for k, type_name in enumerate(type_names):
                    if histograms_to_select_dict[system][function][type_name]:
                        # can_extend = False if k in [0,1,2,6] else True
                        merged_type_histogram = merge_histograms(histograms_to_merge[k])   
                        merged_all_histos[k].append(merged_type_histogram)
                    else:
                        merged_all_histos[k].append(None)

            for z in range(types_number):
                merged_all_histograms[z][system][function] = merged_all_histos[z]

    return merged_all_histograms

###########################################################################################################

# functions for parallel processing. 

###########################################################################################################


def process_file(args):
    try:
        dictionary_of_system, systems, collections, function_dict, system_functions, mip, en_mip, histograms_to_select_dict, indexo, slcio_file, ev_start, ev_stop = args
        return fill_histogram(dictionary_of_system, systems, collections, function_dict, system_functions, mip, en_mip, histograms_to_select_dict, indexo, slcio_file, ev_start, ev_stop)
    except Exception as e:
        # print("Error processing {}: {}".format(args, e))
        traceback.print_exc() 
def execute_parallel_processing(dictionary_of_system, systems, collections, function_dict, system_functions, mip, histograms_to_select_dict, slcio_file_list, ev_start_list, ev_stop_list, en_mip=True):
    arguments = [(dictionary_of_system, systems, collections, function_dict, system_functions, mip, en_mip, histograms_to_select_dict, indexo, slcio_file, ev_start, ev_stop) 
             for indexo, (slcio_file, ev_start, ev_stop) in enumerate(zip(slcio_file_list, ev_start_list, ev_stop_list))]
    pool = multiprocessing.Pool()
    try:
        all_histograms_dicts = pool.map(process_file, arguments)
    finally:
        pool.close()
        pool.join()
    return all_histograms_dicts

###########################################################################################################

# functions for writing the histograms. 

###########################################################################################################

def saving_histogram(histo_dir, canvas, type_name, type_dict, func_dir, system, function):
    if not func_dir.GetDirectory(type_name): # Check if the directory exists
        type_name_dir = func_dir.mkdir(type_name) # If the directory does not exist, create it
    else:
        type_name_dir = func_dir.GetDirectory(type_name) # If it exists, retrieve the existing directory
    if type_name_dir is None: print("Failed to create directory: {}".format(type_name))
    type_name_dir.cd()
    directory_type_name_dir = str(histo_dir) + "/" + system + "/" + function + "/" + type_name
    
    if not os.path.exists(directory_type_name_dir): os.makedirs(directory_type_name_dir)
    
    for hist in type_dict[system][function]:
        canvas.SetLogy(1) if type_name in ["upper_scale_energy", "all_scale_energy", "scaled_upper_scale_energy", "scaled_all_scale_energy", "high_#Nhits", "all_#Nhits"] else canvas.SetLogy(0)
        hist.Draw("HIST")
        canvas.SaveAs(directory_type_name_dir + "/{}".format(hist.GetName()) + ".pdf")
        hist.Write()
        # Explicitly delete the histogram after writing to ROOT file and saving to PDF
        hist.Delete()

def write_histogram(histo_dir, canvas, number_of_processes, systems, system_functions, histograms_to_select_dict, all_histograms_dicts):
    merged_histograms = merging(number_of_processes, systems, system_functions, histograms_to_select_dict, all_histograms_dicts)
    myfile = ROOT.TFile(str(histo_dir) + '/all.root', 'UPDATE')
   
    for system in systems:
        if not myfile.GetDirectory(system): # Check if the directory exists
            sys_dir = myfile.mkdir(system) # If the directory does not exist, create it
        else:
            sys_dir = myfile.GetDirectory(system) # If it exists, retrieve the existing directory
        if sys_dir is None: print("Failed to create directory: {}".format(system))
        functions = system_functions[system]
        for function in functions:
            if not sys_dir.GetDirectory(function): # Check if the directory exists
                func_dir = sys_dir.mkdir(function) # If the directory does not exist, create it
            else:
                func_dir = sys_dir.GetDirectory(function) # If it exists, retrieve the existing directory
            if func_dir is None: print("Failed to create directory: {}:{}".format(system, function))
            iterable_histograms_and_names = zip(type_names, merged_histograms)
            for type_name, type_dict in iterable_histograms_and_names:
                if histograms_to_select_dict[system][function][type_name]:
                    saving_histogram(histo_dir, canvas, type_name, type_dict, func_dir, system, function)
    myfile.Close()

###########################################################################################################

# function to validate the cmd arguments. 

###########################################################################################################

def validate_command_line_args(help_string):
    
    """This just validates and returns the command line inputs."""
    if len(sys.argv) != 2 : raise Exception(help_string)
    histo_dir = os.path.abspath(sys.argv[1])
    hist_out_parent = os.path.dirname(histo_dir)
    if not os.path.isdir(hist_out_parent): raise Exception(help_string)
    if not os.path.exists(histo_dir): os.mkdir(histo_dir)

    return histo_dir