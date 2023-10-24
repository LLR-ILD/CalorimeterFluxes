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
    return hit_info

SubhitInfo = namedtuple("SubhitInfo", ["energy", "time"])
def subhit_decoding(hit):
    hit_subhits = []
    for i_subhit in range(hit.getNMCContributions()):
        subhit = SubhitInfo(energy=hit.getEnergyCont(i_subhit), time=hit.getTimeCont(i_subhit))
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

def histograms_creation(dictionary_of_system, system, histogram_name, time_args, lower_scale_args, upper_scale_args, Nhits_args):
    hist_time = ROOT.TH1F(histogram_name + '_time', 'Time histogram - {}'.format(histogram_name), time_args[0], 6, time_args[1])
    hist_time.GetXaxis().SetTitle("Weighted Time of Subhits [ns]")
    hist_time.GetYaxis().SetTitle("Number of Events times Energy [GeV]")
    
    hist_time_peaks = ROOT.TH1F(histogram_name + '_time_peaks', 'Time peaks histogram - {}'.format(histogram_name), 10, 0, 10)
    hist_time_peaks.GetXaxis().SetTitle("Time between peaks [ns]")
    hist_time_peaks.GetYaxis().SetTitle("frequency")
    
    hist_lower_scale = ROOT.TH1F(histogram_name + '_lower_scale', 'Energy histogram - {}'.format(histogram_name), lower_scale_args[0], 0, lower_scale_args[1])
    hist_lower_scale.GetXaxis().SetTitle("Energy [GeV]")
    hist_lower_scale.GetYaxis().SetTitle("Number of Events")
    
    hist_upper_scale = ROOT.TH1F(histogram_name + '_upper_scale', 'Upper-Scale Energy histogram - {}'.format(histogram_name), upper_scale_args[0], lower_scale_args[1], upper_scale_args[1])
    hist_upper_scale.GetXaxis().SetTitle("Energy [GeV]")
    hist_upper_scale.GetYaxis().SetTitle("Number of Events")
    hist_upper_scale.SetCanExtend(ROOT.TH1.kAllAxes)
    
    hist_Nhits = ROOT.TH1F(histogram_name + '_#hits', 'Number-of-hits histogram - {}'.format(histogram_name), Nhits_args[0], 0, Nhits_args[1])
    hist_Nhits.GetXaxis().SetTitle("Number of hits above " + str(dictionary_of_system[system][3][0]) + " GeV")
    hist_Nhits.GetYaxis().SetTitle("Number of Events")
    hist_Nhits.SetCanExtend(ROOT.TH1.kAllAxes)
    
    return hist_time, hist_time_peaks, hist_lower_scale, hist_upper_scale, hist_Nhits

def appending(dictionary_of_system, system, histogram_name, time_list, time_peaks_list, lower_scale_list, upper_scale_list, Nhits_list):
    histograms_args = dictionary_of_system[system][2]
    time_args = histograms_args[0]
    lower_scale_args = histograms_args[1]
    upper_scale_args = histograms_args[2]
    Nhits_args = histograms_args[3]
    histograms = histograms_creation(dictionary_of_system, system, histogram_name, time_args, lower_scale_args, upper_scale_args, Nhits_args)
    time_list.append(histograms[0])
    time_peaks_list.append(histograms[1])
    lower_scale_list.append(histograms[2])
    upper_scale_list.append(histograms[3])
    Nhits_list.append(histograms[4])

def histograms_for_systems(dictionary_of_system, system, system_functions, index):

    dictionary_of_functions_histograms_time = {}
    dictionary_of_functions_histograms_time_peaks = {}
    dictionary_of_functions_histograms_lower_scale = {}
    dictionary_of_functions_histograms_upper_scale = {}
    dictionary_of_functions_histograms_Nhits = {}
    
    parsing_dictionary = {}
    Nhits_dictionary = {}

    dictionary_of_function = dictionary_of_system[system][4]    
    functions = system_functions[system]
     
    first_function = True

    for function in functions:

        system_histograms_time = []
        system_histograms_time_peaks = []
        system_histograms_lower_scale = []
        system_histograms_upper_scale = []
        system_histograms_Nhits = []
        
        function_dictionary_list = []
        Nhits_zeroes = []

        if first_function:
            selection = dictionary_of_system[system][1] 
            staves = selection[0]
            modules = selection[1]
            towers = selection[2]
            layers = selection[3]
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
                            Nhits_zeroes.append(0)
                            
                            histo_name = "{system}{stave}{module}{tower}{layer}".format(system=system, 
                                                                                                    stave="_S" + stave if stave != "*" else "",
                                                                                                    module="_M" + module if module != "*" else "", 
                                                                                                    tower="_T" + tower if tower != "*" else "", 
                                                                                                    layer="_L" + layer if layer != "*" else "")
                            appending(dictionary_of_system, system, histo_name + "_{}".format(index), system_histograms_time, system_histograms_time_peaks, system_histograms_lower_scale, system_histograms_upper_scale, system_histograms_Nhits)            
        else:
            for limit in dictionary_of_function[function]:
                selection_string = (map(int, limit.split(':'))) if ':' in limit else int(limit)
                function_dictionary_list.append(selection_string)
                Nhits_zeroes.append(0)

                histo_name = "{}_{}_{}".format(system, function, limit)
                appending(dictionary_of_system, system, histo_name + "_{}".format(index), system_histograms_time, system_histograms_time_peaks, system_histograms_lower_scale, system_histograms_upper_scale, system_histograms_Nhits)
                 
        parsing_dictionary[function] = function_dictionary_list
        Nhits_dictionary[function] = Nhits_zeroes

        dictionary_of_functions_histograms_time[function] = system_histograms_time
        dictionary_of_functions_histograms_time_peaks[function] = system_histograms_time_peaks
        dictionary_of_functions_histograms_lower_scale[function] = system_histograms_lower_scale
        dictionary_of_functions_histograms_upper_scale[function] = system_histograms_upper_scale    
        dictionary_of_functions_histograms_Nhits[function] = system_histograms_Nhits

        first_function = False
        
    return Nhits_dictionary, parsing_dictionary, dictionary_of_functions_histograms_time, dictionary_of_functions_histograms_time_peaks, dictionary_of_functions_histograms_lower_scale, dictionary_of_functions_histograms_upper_scale, dictionary_of_functions_histograms_Nhits

def name_histograms(dictionary_of_system, systems, system_functions, index):
    Nhits_dict = {}
    parsing_dict = {}
    all_histograms_time = {}
    all_histograms_time_peaks = {}
    all_histograms_lower_scale = {}
    all_histograms_upper_scale = {}
    all_histograms_Nhits = {}
    for system in systems:
        system_res = histograms_for_systems(dictionary_of_system, system, system_functions, index)
        Nhits_dict[system] = system_res[0]
        parsing_dict[system] = system_res[1]
        all_histograms_time[system] = system_res[2]
        all_histograms_time_peaks[system] = system_res[3]
        all_histograms_lower_scale[system] = system_res[4]
        all_histograms_upper_scale[system] = system_res[5]
        all_histograms_Nhits[system] = system_res[6]

    return Nhits_dict, parsing_dict, all_histograms_time, all_histograms_time_peaks, all_histograms_lower_scale, all_histograms_upper_scale, all_histograms_Nhits

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

def fill_histogram(dictionary_of_system, systems, collections, function_dict, system_functions, indexo, slcio_file,  ev_start, ev_stop):
    
    hits_dict, parsing_dicts, time_histograms, time_peaks_histograms, lower_scale_histograms, upper_scale_histograms, Nhits_histograms = name_histograms(dictionary_of_system, systems, system_functions, indexo)
    
    reader = LcioReader.LcioReader(slcio_file)
    No_events = reader.getNumberOfEvents()
    if ev_stop < 0:
        ev_stop = No_events + ev_stop + 1
    
    for i, event in enumerate(reader):
        # Print out a progress update
        if i % 50 == 0:  # Adjust this condition to control how often updates are printed
            print('process : {} : processed {} out of {} items'.format(indexo, i, No_events))
        if i < ev_start:
            continue
        if i >= ev_stop:
            break
        
        Nhits = deepcopy(hits_dict)
        for collection_name in collections:
            is_endcap = (collection_name in ring_collections)
            calo_hits = event.getCollection(collection_name)
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
                        iterable_histograms = zip(
                        time_histograms[system][function], 
                        lower_scale_histograms[system][function],
                        upper_scale_histograms[system][function], 
                        parsing_dicts[system][function], 
                        enumerate(Nhits[system][function]))
                        for hist_time, hist_lower_scale, hist_upper_scale, function_selection, (index, Nhit) in iterable_histograms:
                            if selecting(function_dict, function, function_selection, is_endcap, decoded_hit):
                                #Number-of-cells-with-energy-above-threshold-per-cell histogram
                                if energy > system_material[3][0][0]:
                                    Nhits[system][function][index] += 1
                                #Lower-scale histogram
                                if 0 <= energy < system_material[2][1][1]:
                                    hist_lower_scale.Fill(energy)
                                #Upper-scale histogram
                                else:
                                    hist_upper_scale.Fill(energy)
                                #time histogram
                                for subhit in subhit_information:
                                    hist_time.Fill(subhit.time, subhit.energy)
        for system in systems:
            system_material = dictionary_of_system[system]
            functions = system_functions[system]          
            for function in functions:
                iterable_histograms = zip(Nhits[system][function], Nhits_histograms[system][function])
                for Nhit, hist_Nhits in iterable_histograms:
                    hist_Nhits.Fill(Nhit)
    
    return [time_histograms, time_peaks_histograms, lower_scale_histograms, upper_scale_histograms, Nhits_histograms]

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
    name = "_".join(histograms[0].GetName().split("_")[:-1])
    title = "_".join(histograms[0].GetTitle().split("_")[:-1])
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

def merging(number_of_processes, systems, system_functions, list_of_all_histograms):
    
    # The histograms are retrieved in order according to the return of fill_histogram and parallel_processing functions.
    time_histograms = [list_of_all_histograms[i][0] for i in range(number_of_processes)]
    time_peaks_histograms = [list_of_all_histograms[i][1] for i in range(number_of_processes)]
    lower_scale_histograms = [list_of_all_histograms[i][2] for i in range(number_of_processes)]
    upper_scale_histograms = [list_of_all_histograms[i][3] for i in range(number_of_processes)]
    Nhits_histograms = [list_of_all_histograms[i][4] for i in range(number_of_processes)]
    
    merged_time_histograms = {}
    merged_time_peaks_histograms = {}
    merged_lower_scale_histograms = {}
    merged_upper_scale_histograms = {}
    merged_Nhits_histograms = {}

    for system in systems:
        merged_time_histograms[system] = {}
        merged_time_peaks_histograms[system] = {}
        merged_lower_scale_histograms[system] = {}
        merged_upper_scale_histograms[system] = {}
        merged_Nhits_histograms[system] = {}

        functions = system_functions[system]         
        for function in functions:
            merged_time_histos = []
            merged_time_peaks_histos = []
            merged_lowE_histos = []
            merged_UpE_histos = []
            merged_Nhits_histos = []

            system_function_selections = len(time_histograms[0][system][function]) # the 25 lists have the same length for having the same selections. Also, it is the same length for all the types for having the same set of selections.
            for selection_index in range(system_function_selections):
                time_histograms_to_merge = []
                time_peaks_histograms_to_merge = []
                lowE_histograms_to_merge = []
                UpE_histograms_to_merge = []
                Nhits_histograms_to_merge = []

                for proces_index in range(number_of_processes):
                    time_histograms_to_merge.append(time_histograms[proces_index][system][function][selection_index])
                    time_peaks_histograms_to_merge.append(time_peaks_histograms[proces_index][system][function][selection_index])
                    lowE_histograms_to_merge.append(lower_scale_histograms[proces_index][system][function][selection_index])
                    UpE_histograms_to_merge.append(upper_scale_histograms[proces_index][system][function][selection_index])
                    Nhits_histograms_to_merge.append(Nhits_histograms[proces_index][system][function][selection_index])

                merged_time_histogram = merge_histograms(time_histograms_to_merge, can_extend = False)
                merged_time_histos.append(merged_time_histogram)
                merged_time_peak_histogram = merge_histograms(time_peaks_histograms_to_merge, can_extend = False)
                merged_time_peaks_histos.append(merged_time_peak_histogram)
                merged_lowE_histogram = merge_histograms(lowE_histograms_to_merge, can_extend = False)
                merged_lowE_histos.append(merged_lowE_histogram)
                merged_UpE_histogram = merge_histograms(UpE_histograms_to_merge)
                merged_UpE_histos.append(merged_UpE_histogram)
                merged_Nhit_histogram = merge_histograms(Nhits_histograms_to_merge)
                merged_Nhits_histos.append(merged_Nhit_histogram)

            merged_time_histograms[system][function] = merged_time_histos
            merged_time_peaks_histograms[system][function] = merged_time_peaks_histos
            merged_lower_scale_histograms[system][function] = merged_lowE_histos
            merged_upper_scale_histograms[system][function] = merged_UpE_histos
            merged_Nhits_histograms[system][function] = merged_Nhits_histos

    return [merged_time_histograms, merged_time_peaks_histograms, merged_lower_scale_histograms, merged_upper_scale_histograms, merged_Nhits_histograms]

###########################################################################################################

# functions for parallel processing. 

###########################################################################################################


def process_file(args):
    try:
        dictionary_of_system, systems, collections, function_dict, system_functions, indexo, slcio_file, ev_start, ev_stop = args
        return fill_histogram(dictionary_of_system, systems, collections, function_dict, system_functions, indexo, slcio_file, ev_start, ev_stop)
    except Exception as e:
        print("Error processing {}: {}".format(args, e))
        traceback.print_exc() 
def execute_parallel_processing(dictionary_of_system, systems, collections, function_dict, system_functions, slcio_file_list, ev_start_list, ev_stop_list):
    arguments = [(dictionary_of_system, systems, collections, function_dict, system_functions, indexo, slcio_file, ev_start, ev_stop) 
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
    type_name_dir = func_dir.mkdir(type_name)
    type_name_dir.cd()
    directory_type_name_dir = str(histo_dir) + "/" + system + "/" + function + "/" + type_name
    
    if not os.path.exists(directory_type_name_dir): os.makedirs(directory_type_name_dir)
    
    for hist in type_dict[system][function]:
        canvas.SetLogy(1) if type_name == "upper_scale_energy" else canvas.SetLogy(0)
        hist.Draw("HIST")
        canvas.SaveAs(directory_type_name_dir + "/{}".format(hist.GetName()) + ".pdf")
        hist.Write()
        # Explicitly delete the histogram after writing to ROOT file and saving to PDF
        hist.Delete()


def write_histogram(histo_dir, canvas, number_of_processes, systems, system_functions, all_histograms_dicts):
    merged_histograms = merging(number_of_processes, systems, system_functions, all_histograms_dicts)
    histograms_names = ["time", "time_peaks", "lower_scale_energy", "upper_scale_energy", "#Nhits"]
    myfile = ROOT.TFile(str(histo_dir) + '/all.root', 'RECREATE' )
   
    for system in systems:
        sys_dir = myfile.mkdir(system)
        functions = system_functions[system]
        for function in functions:
            func_dir = sys_dir.mkdir(function)
            iterable_histograms_and_names = zip(histograms_names, merged_histograms)
            for type_name, type_dict in iterable_histograms_and_names:
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