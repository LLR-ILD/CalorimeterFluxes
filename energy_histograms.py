from __future__ import absolute_import
from __future__ import print_function  # python3 style printing in python2.
import logging
import os
import sys
import tarfile
import math
from pyLCIO.io import LcioReader
from pyLCIO import EVENT, IMPL, UTIL
import ROOT

# logging.DEBUG for debugging. Else logging.INFO.
format = "%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
logging.basicConfig(format=format, level=logging.DEBUG)

help_string = """The script must be called with 2 or 4 arguments as:
$ python pylcio_powered_2ascii.py slcio_file ascii_out_dir ev_start ev_stop
- slcio_file: File with the reconstructed information in LCIO format.
- ascii_out_dir: Folder to write the ASCII output to.
    Its parent must exist. The folder itself can exist, but must be empty then.
- ev_start ev_stop: Integers. Specify both or neither of them. Will process
    (ev_stop - ev_start) events. Use ev_stop=-1 to exhaust the file.
"""

def decoding(event, collection_name, hit, is_ecal_endcap_ring=False):
    cell_id_info = ["system", "stave", "module", "cellX", "cellY", "tower", "layer", "wafer", "slice"]
    endcap_replacements = dict(cellX="x", cellY="y")
    # Combine 32bits CellIDo and CellId1 in a 64 bits stream
    calo_hits = event.getCollection(collection_name)
    # is_endcap = (collection_name in ["EcalEndcapRingCollection"])
    cell_id_encoding = calo_hits.getParameters().getStringVal(EVENT.LCIO.CellIDEncoding)
    id_decoder = UTIL.BitField64(cell_id_encoding)
    cell_id = (hit.getCellID0() & 0xffffffff) | (hit.getCellID1() << 32)
    id_decoder.setValue(cell_id)
    hit_info = {}
    for cell_id_key in cell_id_info:
        encoded_key = cell_id_key
        if is_ecal_endcap_ring:
            if cell_id_key in endcap_replacements:
                encoded_key = endcap_replacements[cell_id_key]
            elif cell_id_key in ["wafer", "slice"]:
                hit_info[cell_id_key + 's'] = -1
                # Endcaps have no wafer information.
                continue
        hit_info[encoded_key + 's'] = int(id_decoder[encoded_key].value())
    return hit_info

def subhit_decoding(hit):
    hit_subhits = []
    for i_subhit in range(hit.getNMCContributions()):
            subhit_info = {}
            subhit_info["primary_pdg"] =  hit.getParticleCont(i_subhit).getPDG()
            subhit_info["energy"] =  hit.getEnergyCont(i_subhit)
            subhit_info["time"] =  hit.getTimeCont(i_subhit)
            subhit_info["length"] =  hit.getTimeCont(i_subhit)
            subhit_info["length"] = hit.getLengthCont(i_subhit)
            subhit_info["secondary_pdg"] = hit.getPDGCont(i_subhit)
            subhit_info["pos_x"] = hit.getStepPosition(i_subhit)[0]
            subhit_info["pos_y"] = hit.getStepPosition(i_subhit)[1]
            subhit_info["pos_z"] = hit.getStepPosition(i_subhit)[2]
            hit_subhits.append(subhit_info)
    return hit_subhits

ring_collections = ["EcalEndcapRingCollection",
                        "HCalBarrelRPCHits",
                        "HCalECRingRPCHits",
                        "HCalEndcapRPCHits",
                        "HcalBarrelRegCollection",
                        "HcalEndcapRingCollection",
                        "HcalEndcapsCollection"]

def make_complex(equation, name):
    def complex(range_str, event, collection_name, hit):
        is_endcap = (collection_name in ring_collections)
        decoded_hit = decoding(event, collection_name, hit, is_endcap)
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
        
        value = equation(stave, module, tower, layer, x_position, y_position)  # Call the equation function
        
        splitted_range = range_str.split(':')
        if len(splitted_range) != 1:
            if float(splitted_range[0]) <= value <= float(splitted_range[1]):
                return True
            else:
                return False
        else:
            if value == float(splitted_range[0]):
                return True
            else:
                return False
    complex.__name__ = name
    return complex

# Define your equation functions here
def equation1(stave, module, tower, layer, x_position, y_position):
    return float((2 * y_position * (module - 1.5) + 117))

def equation2(stave, module, tower, layer, x_position, y_position):
    return float((2 * y_position * (module - 1.5) + 38))

# Create a version of the complex function for each equation
complex_sad = make_complex(equation1, "complex_sad")
complex_happy = make_complex(equation2, "complex_happy")

#Creating ROOT canvas to save the histograms
canvas = ROOT.TCanvas('canvas', 'Histogram', 800, 600)

system_limits = {"ECALBarrel" : (8, 5, 5, 30) , "EndCaps" : (4, "0-6", 5, 30)}
#selection format "S:M:T:L" conditions => "*:*:2:0-4,5-10" means no selection on M, S, 1 histo per 2 tower , 1 for layer 0 to 5, and one for layers in 5 to 10.
#The keys of the dictionary are the system names. Each key has a value composed of 4 lists. 
# The first list has the collections' names. 
# The second one has the selections we impose on the histograms made in the order given above. 
# The third list has 4 lists each with 2 arguments. Each list has the bin number (the first argument) and the maximum of the range of the histogram (the second argument). The 4 lists are in this order: time, lower-scale energy, upper-scale energy, and number of hits above a specific threshold.
# The fourth list has the energy threshold that we use in the Nhits histogram. 
dictionary_of_system = {
#       System          Xollwctiona                                         Stave  MOdules                Towers                        Layers                      Time bins/max lowE bin/max highE bin/max  #hits bin/max  EThr  Split Func:ranges         
        "SiECalEndcap": (["ECalEndcapSiHitsEven", "ECalEndcapSiHitsOdd"],   [["*"],["*"],                 ["0","1:2","3:5","6:8"],      ["0:9","10:19","20:29"]],   [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0001]], {}),
        "SiECALBarrel": (["ECalBarrelSiHitsEven", "ECalBarrelSiHitsOdd"],   [["*"],["1","2","3","4","5"], ["*"],                        ["0:9","10:19","20:29"]],   [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0001]], {}), 
        "SiECalRing": (["EcalEndcapRingCollection"],                        [["*"],["*"],                 ["*"],                        ["0:9","10:19","20:29"]],   [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0001]], {}), 
        "ScECalEndcap": (["ECalEndcapScHitsEven", "ECalEndcapScHitsOdd"],   [["*"],["*"],                 ["0","1:2","3:5","6:8"],      ["0:9","10:19","20:29"]],   [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0003]], {}),
        "ScECALBarrel": (["ECalBarrelScHitsEven", "ECalBarrelScHitsOdd"],   [["*"],["1","2","3","4","5"], ["*"],                        ["0:9","10:19","20:29"]],   [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0002]], {}), 
        "RPCHCalEndcap": (["HCalEndcapRPCHits"],                            [["*"],["*"],                 ["0:3","4:7","8:11","12:15"], ["0:15","16:31","32:48"]],  [[100, 20], [100, 2e-6],  [100, 3e-5], [100, 35]], [[3e-7]], {}),
        "RPCHCalBarrel": (["HCalBarrelRPCHits"],                            [["*"],["*"],                 ["*"],                        ["0:15","16:31","32:48"]],  [[100, 20], [100, 2e-6],  [100, 3e-5], [100, 35]], [[3e-7]], {complex_sad:["0:79", "80:159", "160:234"]}), 
        "RPCHCalECRing": (["EcalEndcapRingCollection"],                     [["*"],["*"],                 ["*"],                        ["*"]],                     [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0001]], {}),         
        "ScHCalEndcap": (["HcalEndcapsCollection"],                         [["*"],["*"],                 ["0:3","4:7","8:11","12:15"], ["0:15","16:31","32:48"]],  [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0001]], {}),
        "ScHcalBarrel": (["HcalBarrelRegCollection"],                       [["*"],["*"],                 ["*"],                        ["0:15","16:31","32:48"]],  [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0003]], {complex_happy:["0:29", "30:59", "60:76"]}), 
        "ScHCalECRing": (["EcalEndcapRingCollection"],                      [["*"],["*"],                 ["*"],                        ["*"]],                     [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0001]], {})                 
        }

def histograms_for_systems(system):

    histograms_args = dictionary_of_system[system][2]
    time_args = histograms_args[0]
    lower_scale_args = histograms_args[1]
    upper_scale_args = histograms_args[2]
    Nhits_args = histograms_args[3]

    def histograms_creation(histogram_name):
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

    def appending(histogram_name, time_list, time_peaks_list, lower_scale_list, upper_scale_list, Nhits_list):
        histograms = histograms_creation(histogram_name)
        time_list.append(histograms[0])
        time_peaks_list.append(histograms[1])
        lower_scale_list.append(histograms[2])
        upper_scale_list.append(histograms[3])
        Nhits_list.append(histograms[4])

    dictionary_of_functions_histograms_time = {}
    dictionary_of_functions_histograms_time_peaks = {}
    dictionary_of_functions_histograms_lower_scale = {}
    dictionary_of_functions_histograms_upper_scale = {}
    dictionary_of_functions_histograms_Nhits = {}
    
    selection = dictionary_of_system[system][1] 
    staves = selection[0]
    modules = selection[1]
    towers = selection[2]
    layers = selection[3]
    system_dictionary_list = []
    for stave in staves:
            for module in modules:
                for tower in towers:
                    for layer in layers:
                        my_dict = {'staves': stave, 'modules': module, 'towers': tower, 'layers': layer}
                        my_dict = {key: value for key, value in my_dict.items() if value != "*"}
                        system_dictionary_list.append(my_dict)
    
    dictionary_of_functions = dictionary_of_system[system][4]    
    functions = dictionary_of_functions.keys()
    # functions = [func.__name__ for func in abstract_functions]
    functions.insert(0, "no_function")

    system_dictionary_dictionary = {}
    system_dictionary_dictionary["no_function"] = system_dictionary_list

    first_function = True

    for function in functions:

        system_histograms_time = []
        system_histograms_time_peaks = []
        system_histograms_lower_scale = []
        system_histograms_upper_scale = []
        system_histograms_Nhits = []
        
        function_dictionary_list = []
        
        if first_function:
            for limit in system_dictionary_list:
                histo_name = "{system}{stave}{module}{tower}{layer}".format(system=system, 
                                                                                        stave="_S" + limit["staves"] if "staves" in limit else "",
                                                                                        module="_M" + limit["modules"] if "modules" in limit else "", 
                                                                                        tower="_T" + limit["towers"] if "towers" in limit else "", 
                                                                                        layer="_L" + limit["layers"] if "layers" in limit else "")
                appending(histo_name, system_histograms_time, system_histograms_time_peaks, system_histograms_lower_scale, system_histograms_upper_scale, system_histograms_Nhits)            
        else:
            for limit in dictionary_of_functions[function]:
                histo_name = "{}_{}_{}".format(system, function.__name__, limit)
                appending(histo_name, system_histograms_time, system_histograms_time_peaks, system_histograms_lower_scale, system_histograms_upper_scale, system_histograms_Nhits)
                function_dictionary_list.append(limit)
            system_dictionary_dictionary[function] = function_dictionary_list
        
        dictionary_of_functions_histograms_time[function] = system_histograms_time
        dictionary_of_functions_histograms_time_peaks[function] = system_histograms_time_peaks
        dictionary_of_functions_histograms_lower_scale[function] = system_histograms_lower_scale
        dictionary_of_functions_histograms_upper_scale[function] = system_histograms_upper_scale    
        dictionary_of_functions_histograms_Nhits[function] = system_histograms_Nhits

        first_function = False

    return system_dictionary_dictionary, dictionary_of_functions_histograms_time, dictionary_of_functions_histograms_time_peaks, dictionary_of_functions_histograms_lower_scale, dictionary_of_functions_histograms_upper_scale, dictionary_of_functions_histograms_Nhits

def name_histograms():
    system_dictionary = {}
    all_histograms_time = {}
    all_histograms_time_peaks = {}
    all_histograms_lower_scale = {}
    all_histograms_upper_scale = {}
    all_histograms_Nhits = {}
    for system in dictionary_of_system.keys():
        system_dictionary[system] = histograms_for_systems(system)[0]
        all_histograms_time[system] = histograms_for_systems(system)[1]
        all_histograms_time_peaks[system] = histograms_for_systems(system)[2]
        all_histograms_lower_scale[system] = histograms_for_systems(system)[3]
        all_histograms_upper_scale[system] = histograms_for_systems(system)[4]
        all_histograms_Nhits[system] = histograms_for_systems(system)[5]

    return system_dictionary, all_histograms_time, all_histograms_time_peaks, all_histograms_lower_scale, all_histograms_upper_scale, all_histograms_Nhits

systems_dictionary, time_histograms, time_peaks_histograms, lower_scale_histograms, upper_scale_histograms, Nhits_histograms = name_histograms()
# print(systems_dictionary)
def fill_histogram(slcio_file, ev_start, ev_stop):
    
    def selecting(func, func_selection, event, collection_name, hit):
        is_endcap = (collection_name in ring_collections)
        decoded_hit = decoding(event, collection_name, hit, is_endcap)
        values_same = True
        if func == "no_function":
            for key in func_selection.keys():
                split = func_selection[key].split(':')
                integer_decoded_hit = decoded_hit[key]
                if len(split) != 1:
                    if int(split[0]) > integer_decoded_hit or integer_decoded_hit > int(split[1]):
                        values_same = False
                        break 
                elif int(func_selection[key]) != integer_decoded_hit:
                    values_same = False
                    break
        else:
            values_same = func(func_selection, event, collection_name, hit)
        return values_same

    # def histograms_looping(time_dict, time_peaks_dict, energy_lower_scale_dict, energy_upper_scale_dict, Nhits_dict, systems_dict, event):
    reader = LcioReader.LcioReader(slcio_file)
    if ev_stop < 0:
        ev_stop = reader.getNumberOfEvents() + ev_stop + 1
    
    for i, event in enumerate(reader):
        # Print out a progress update
        if i % 10 == 0:  # Adjust this condition to control how often updates are printed
            print('Processed {} out of {} items'.format(i, reader.getNumberOfEvents()))
        if i < ev_start:
            continue
        if i >= ev_stop:
            break
            
        for system in dictionary_of_system.keys():
            counter = 0
            threshold = 0.002
            
            dictionary_of_functions = dictionary_of_system[system][4]            
            functions = dictionary_of_functions.keys()
            functions.insert(0, "no_function")

            
            for function in functions:
                # print(function)
                for hist_time, hist_time_peaks, hist_lower_scale, hist_upper_scale, hist_Nhits, function_selection in zip(time_histograms[system][function], time_peaks_histograms[system][function], lower_scale_histograms[system][function], upper_scale_histograms[system][function], Nhits_histograms[system][function], systems_dictionary[system][function]):
                    Nhits = 0
                    for collection_name in dictionary_of_system[system][0]:
                        calo_hits = event.getCollection(collection_name)
                        for j, hit in enumerate(calo_hits, start=1):
                            energy = hit.getEnergy()
                            if selecting(function, function_selection, event, collection_name, hit):
                                #Number-of-cells-with-energy-above-threshold-per-cell histogram 
                                if energy > dictionary_of_system[system][3][0][0]:
                                    Nhits += 1
                                #Lower and upper scale histograms
                                if 0 <= energy < dictionary_of_system[system][2][1][1]:
                                    hist_lower_scale.Fill(energy)
                                else:
                                    hist_upper_scale.Fill(energy)
                                #time histogram
                                subhit_information = subhit_decoding(hit)
                                histo = ROOT.TH1F("histo for cell", "histo for cell", dictionary_of_system[system][2][0][0], 6, dictionary_of_system[system][2][0][1])
                                for subhit in subhit_information:
                                    histo.Fill(subhit["time"], subhit["energy"])
                                    hist_time.Fill(subhit["time"], subhit["energy"])
                                time = 0
                                in_peak = False
                                first_peak = True  # flag for the first peak
                                for bin in range(1, histo.GetNbinsX() + 1):  # bin indices start from 1
                                    bin_content = histo.GetBinContent(bin)
                                    if bin_content > threshold and not in_peak:
                                        # Entering a peak
                                        in_peak = True
                                        time = histo.GetBinCenter(bin) - time
                                        if not first_peak:  # if it's not the first peak
                                            hist_time_peaks.Fill(time)
                                        else:  # if it's the first peak, we skip filling the histogram and set the flag to False
                                            first_peak = False
                                    elif bin_content < threshold and in_peak:
                                        # Leaving a peak
                                        in_peak = False
                                if counter < 10:  # if we've processed fewer than 10 histograms
                                    histo.Draw("HIST")
                                    canvas.SaveAs(sys.argv[2]+ "/{}_{}".format(str(counter), system) + ".pdf")  # replace this with the actual command to print or display your histogram
                                counter += 1  # increment the counter

                                del histo 
                    hist_Nhits.Fill(Nhits)
    
def write_histogram(histo_dir):
    
    histograms = [time_histograms, time_peaks_histograms, lower_scale_histograms, upper_scale_histograms, Nhits_histograms]
    histograms_names = ["time", "time_peaks", "lower_scale_energy", "upper_scale_energy", "#Nhits"]
    myfile = ROOT.TFile(str(histo_dir) + '/all.root', 'RECREATE' )

    def saving_histogram(type_name, type_list, func_dir, system, function):
        type_name_dir = func_dir.mkdir(type_name)
        type_name_dir.cd()
        if callable(function):
            func_name = function.__name__
        else:  # Assume it's a string
            func_name = function
        directory_type_name_dir = str(histo_dir) + "/" + system + "/" + func_name + "/" + type_name
        if not os.path.exists(directory_type_name_dir):
                os.makedirs(directory_type_name_dir)
        for hist in type_list[system][function]:
            hist.Draw("HIST")
            canvas.SaveAs(directory_type_name_dir + "/{}".format(hist.GetName()) + ".pdf")
            hist.Write()
   
    for system in dictionary_of_system.keys():
        sys_dir = myfile.mkdir(system)
        
        dictionary_of_functions = dictionary_of_system[system][4]    
        functions = dictionary_of_functions.keys()
        functions.insert(0, "no_function")
                
        for function in functions:
            if function == "no_function":
                func_dir = sys_dir.mkdir(function)
            else:
                func_dir = sys_dir.mkdir(function.__name__)            
            for type_name, type_list in zip(histograms_names, histograms):
                saving_histogram(type_name, type_list, func_dir, system, function)
    
    myfile.Close()
            
def validate_command_line_args():
    """This just validates and returns the command line inputs."""
    if len(sys.argv) not in [3, 5]: raise Exception(help_string)

    slcio_file = sys.argv[1]
    if not os.path.isfile(slcio_file): raise Exception(help_string)
    histo_dir = os.path.abspath(sys.argv[2])
    hist_out_parent = os.path.dirname(histo_dir)
    if not os.path.isdir(hist_out_parent): raise Exception(help_string)
    if not os.path.exists(histo_dir):
        os.mkdir(histo_dir)
    #elif len(os.listdir(ascii_out_dir)) != 0: raise Exception(help_string)

    if len(sys.argv) == 3:
        ev_start = 0
        ev_stop = -1
    else:
        try:
            ev_start = int(sys.argv[3])
            ev_stop = int(sys.argv[4])
            ev_start = int(sys.argv[3])
            ev_stop = int(sys.argv[4])
        except (IndexError, ValueError): raise Exception(help_string)
    return slcio_file, histo_dir, ev_start, ev_stop

if __name__ == "__main__":
    slcio_file, histo_dir, ev_start, ev_stop = validate_command_line_args()
    fill_histogram(slcio_file, ev_start, ev_stop)
    write_histogram(histo_dir)