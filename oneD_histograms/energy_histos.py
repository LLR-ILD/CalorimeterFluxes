from cProfile import Profile
from itertools import chain
from ROOT import TCanvas
from glob import glob
from histograms_library import ComplexFunction, validate_command_line_args, execute_parallel_processing, write_histogram

help_string = """The script must be called with 2 arguments as:
$ python energy_histos.py  histograms_out_dir
- histograms_out_dir: Folder to write the histograms output to.
    Its parent must exist. The folder itself can exist, but must be empty then.
"""

# Define your equation functions here
def equation1(stave, module, tower, layer, x_position, y_position):
    return float((2 * y_position * (module - 1.5) + 117))

def equation2(stave, module, tower, layer, x_position, y_position):
    return float((2 * y_position * (module - 1.5) + 38))

# Create a version of the complex function for each equation
complex_sad = ComplexFunction(equation1, "complex_sad")
complex_happy = ComplexFunction(equation2, "complex_happy")
function_dict = {"complex_sad": complex_sad, "complex_happy": complex_happy}

# A dictionary that determines which histograms to produce. If the value is False, it means that this type of histograms wouldn't be produced for all systems. 
# histograms_to_select = {"time": True, "time peaks": True, "lower-scale energy": True, "upper-scale energy": True, "scaled_upper_scale_energy":True, "Nhits": True, "high_#Nhits":True}


mip = {'RPCHCalECRing_lower_scale': 7.499999999999999e-07, 'ScECALBarrel_M4_L0:9_lower_scale': 0.00026166666666666667, 'ScECalEndcap_T0_L10:19_lower_scale': 0.000235, 'ScHCalEndcap_T8:11_L0:15_lower_scale': 0.0005116666666666667, 'ScECalEndcap_T3:5_L10:19_lower_scale': 0.00025833333333333334, 'SiECalEndcap_T6:8_L0:9_lower_scale': 0.00019833333333333332, 'RPCHCalEndcap_T8:11_L16:31_lower_scale': 5.366666666666666e-07, 'ScECALBarrel_M5_L10:19_lower_scale': 0.00032833333333333336, 'RPCHCalBarrel_L16:31_lower_scale': 5.633333333333333e-07, 'RPCHCalEndcap_T12:15_L0:15_lower_scale': 6.633333333333333e-07, 'RPCHCalEndcap_T4:7_L32:48_lower_scale': 5.566666666666666e-07, 'ScHCalEndcap_T8:11_L16:31_lower_scale': 0.0005149999999999999, 'RPCHCalBarrel_complex_sad_80:159_lower_scale': 5.633333333333333e-07, 'ScECALBarrel_M1_L10:19_lower_scale': 0.00032500000000000004, 'RPCHCalBarrel_L32:48_lower_scale': 5.499999999999999e-07, 'RPCHCalEndcap_T8:11_L32:48_lower_scale': 5.833333333333333e-07, 'ScHCalEndcap_T0:3_L0:15_lower_scale': 0.0006283333333333333, 'ScHCalEndcap_T4:7_L0:15_lower_scale': 0.0005116666666666667, 'ScECALBarrel_M2_L10:19_lower_scale': 0.00025833333333333334, 'ScHcalBarrel_complex_happy_60:76_lower_scale': 0.0006183333333333333, 'SiECALBarrel_M2_L0:9_lower_scale': 0.00017833333333333332, 'SiECALBarrel_M1_L20:29_lower_scale': 0.00021833333333333332, 'SiECALBarrel_M2_L10:19_lower_scale': 0.00017833333333333332, 'ScECALBarrel_M3_L20:29_lower_scale': 0.00023166666666666667, 'SiECalEndcap_T1:2_L20:29_lower_scale': 0.00016833333333333332, 'RPCHCalEndcap_T0:3_L32:48_lower_scale': 5.966666666666666e-07, 'ScECALBarrel_M5_L0:9_lower_scale': 0.00032833333333333336, 'ScECalEndcap_T1:2_L20:29_lower_scale': 0.00024166666666666667, 'SiECALBarrel_M3_L20:29_lower_scale': 0.00015833333333333332, 'RPCHCalEndcap_T12:15_L32:48_lower_scale': 6.233333333333332e-07, 'SiECALBarrel_M1_L10:19_lower_scale': 0.00022166666666666667, 'ScECalEndcap_T6:8_L10:19_lower_scale': 0.00028166666666666666, 'ScECalEndcap_T3:5_L0:9_lower_scale': 0.00026166666666666667, 'SiECalEndcap_T3:5_L20:29_lower_scale': 0.00017833333333333332, 'RPCHCalEndcap_T8:11_L0:15_lower_scale': 5.366666666666666e-07, 'ScECALBarrel_M2_L0:9_lower_scale': 0.00026166666666666667, 'SiECalRing_L0:9_lower_scale': 0.000155, 'ScHCalEndcap_T4:7_L16:31_lower_scale': 0.0005083333333333333, 'SiECalEndcap_T0_L10:19_lower_scale': 0.00015833333333333332, 'ScECALBarrel_M4_L10:19_lower_scale': 0.00026166666666666667, 'RPCHCalEndcap_T0:3_L0:15_lower_scale': 6.433333333333332e-07, 'RPCHCalBarrel_L0:15_lower_scale': 5.833333333333333e-07, 'SiECALBarrel_M4_L10:19_lower_scale': 0.00017833333333333332, 'SiECalEndcap_T3:5_L10:19_lower_scale': 0.00017833333333333332, 'ScECalEndcap_T1:2_L0:9_lower_scale': 0.000245, 'ScECALBarrel_M3_L10:19_lower_scale': 0.000235, 'SiECalEndcap_T3:5_L0:9_lower_scale': 0.00017833333333333332, 'SiECALBarrel_M5_L10:19_lower_scale': 0.00022166666666666667, 'ScHCalEndcap_T0:3_L16:31_lower_scale': 0.0005983333333333333, 'SiECalEndcap_T1:2_L10:19_lower_scale': 0.00016833333333333332, 'ScHCalEndcap_T8:11_L32:48_lower_scale': 0.0005116666666666667, 'SiECalEndcap_T1:2_L0:9_lower_scale': 0.000165, 'ScHCalEndcap_T0:3_L32:48_lower_scale': 0.000575, 'ScHcalBarrel_L16:31_lower_scale': 0.0005316666666666666, 'SiECALBarrel_M5_L20:29_lower_scale': 0.00021833333333333332, 'ScECalEndcap_T0_L0:9_lower_scale': 0.000235, 'SiECALBarrel_M1_L0:9_lower_scale': 0.00022833333333333332, 'ScHCalECRing_lower_scale': 0.0006916666666666666, 'ScHcalBarrel_L32:48_lower_scale': 0.0005216666666666666, 'SiECALBarrel_M5_L0:9_lower_scale': 0.000225, 'RPCHCalBarrel_complex_sad_160:234_lower_scale': 6.366666666666666e-07, 'SiECalRing_L10:19_lower_scale': 0.00015833333333333332, 'ScECALBarrel_M1_L0:9_lower_scale': 0.0003316666666666667, 'ScHcalBarrel_complex_happy_0:29_lower_scale': 0.000495, 'ScECalEndcap_T1:2_L10:19_lower_scale': 0.000245, 'ScECALBarrel_M3_L0:9_lower_scale': 0.000235, 'ScHCalEndcap_T12:15_L32:48_lower_scale': 0.0005683333333333333, 'ScECALBarrel_M5_L20:29_lower_scale': 0.000315, 'SiECALBarrel_M4_L20:29_lower_scale': 0.00017166666666666667, 'ScECALBarrel_M4_L20:29_lower_scale': 0.00025833333333333334, 'ScECalEndcap_T0_L20:29_lower_scale': 0.00023833333333333332, 'ScECalEndcap_T6:8_L0:9_lower_scale': 0.00028166666666666666, 'SiECALBarrel_M3_L10:19_lower_scale': 0.00016166666666666665, 'ScHCalEndcap_T12:15_L16:31_lower_scale': 0.0005783333333333333, 'ScECALBarrel_M2_L20:29_lower_scale': 0.00026166666666666667, 'SiECalEndcap_T0_L20:29_lower_scale': 0.00016166666666666665, 'RPCHCalBarrel_complex_sad_0:79_lower_scale': 5.233333333333333e-07, 'ScHCalEndcap_T4:7_L32:48_lower_scale': 0.0005049999999999999, 'ScECalEndcap_T6:8_L20:29_lower_scale': 0.00027833333333333334, 'SiECALBarrel_M2_L20:29_lower_scale': 0.000175, 'SiECalEndcap_T6:8_L20:29_lower_scale': 0.00019166666666666667, 'RPCHCalEndcap_T4:7_L0:15_lower_scale': 6.1e-07, 'ScHcalBarrel_L0:15_lower_scale': 0.0005216666666666666, 'SiECalRing_L20:29_lower_scale': 0.000155, 'ScHCalEndcap_T12:15_L0:15_lower_scale': 0.0006216666666666666, 'ScECALBarrel_M1_L20:29_lower_scale': 0.00032166666666666666, 'RPCHCalEndcap_T4:7_L16:31_lower_scale': 5.699999999999999e-07, 'SiECalEndcap_T6:8_L10:19_lower_scale': 0.000195, 'ScHcalBarrel_complex_happy_30:59_lower_scale': 0.0005483333333333333, 'RPCHCalEndcap_T12:15_L16:31_lower_scale': 6.566666666666666e-07, 'SiECalEndcap_T0_L0:9_lower_scale': 0.00015833333333333332, 'ScECalEndcap_T3:5_L20:29_lower_scale': 0.00025833333333333334, 'SiECALBarrel_M4_L0:9_lower_scale': 0.00017833333333333332, 'SiECALBarrel_M3_L0:9_lower_scale': 0.00016166666666666665, 'RPCHCalEndcap_T0:3_L16:31_lower_scale': 6.166666666666667e-07}

# The dictionary that conatins all the systems and the required selections.
#selection format "S:M:T:L" conditions => "*:*:2:0-4,5-10" means no selection on M, S, 1 histo per 2 tower , 1 for layer 0 to 5, and one for layers in 5 to 10.
dictionary_of_system = {
#       System          collections                                         Stave  Modules                Towers                        Layers                      Time bins/max lowE bin/max highE bin/max low#-bin/max high#-bin/max EThr  Split Func:ranges         
        "SiECalEndcap": (["ECalEndcapSiHitsEven", "ECalEndcapSiHitsOdd"],   [["*"],["*"],                 ["0","1:2","3:5","6:8"],      ["0:9","10:19","20:29"]],   [[1000, 20], [300, 0.001], [100, 0.03], [100, 100], [100, 500]], [[0.0001]], {}),
        "SiECALBarrel": (["ECalBarrelSiHitsEven", "ECalBarrelSiHitsOdd"],   [["*"],["1","2","3","4","5"], ["*"],                        ["0:9","10:19","20:29"]],   [[1000, 20], [300, 0.001], [100, 0.03], [250, 250], [100, 500]], [[0.0001]], {}), 
        "SiECalRing": (["EcalEndcapRingCollection"],                        [["*"],["*"],                 ["*"],                        ["0:9","10:19","20:29"]],   [[1000, 20], [300, 0.001], [100, 0.03], [250, 250], [100, 500]], [[0.0001]], {}), 
        "ScECalEndcap": (["ECalEndcapScHitsEven", "ECalEndcapScHitsOdd"],   [["*"],["*"],                 ["0","1:2","3:5","6:8"],      ["0:9","10:19","20:29"]],   [[1000, 20], [300, 1e-7], [100, 3e-4], [250, 250], [100, 500]], [[3e-5]], {}),
        "ScECALBarrel": (["ECalBarrelScHitsEven", "ECalBarrelScHitsOdd"],   [["*"],["1","2","3","4","5"], ["*"],                        ["0:9","10:19","20:29"]],   [[1000, 20], [300, 1e-7], [100, 3e-4], [250, 250], [100, 500]], [[3e-5]], {}), 
        "RPCHCalEndcap": (["HCalEndcapRPCHits"],                            [["*"],["*"],                 ["0:3","4:7","8:11","12:15"], ["0:15","16:31","32:48"]],  [[1000, 20], [300, 2e-6],  [100, 3e-5], [250, 250], [100, 500]], [[3e-6]], {}),
        "RPCHCalBarrel": (["HCalBarrelRPCHits"],                            [["*"],["*"],                 ["*"],                        ["0:15","16:31","32:48"]],  [[1000, 20], [300, 2e-6],  [100, 3e-5], [250, 250], [100, 500]], [[3e-6]], {"complex_sad": ["0:79", "80:159", "160:234"]}), 
        "RPCHCalECRing": (["HCalECRingRPCHits"],                            [["*"],["*"],                 ["*"],                        ["*"]],                     [[1000, 20], [300, 2e-6], [100, 3e-4], [250, 250], [100, 500]], [[3e-5]], {}),         
        "ScHCalEndcap": (["HcalEndcapsCollection"],                         [["*"],["*"],                 ["0:3","4:7","8:11","12:15"], ["0:15","16:31","32:48"]],  [[1000, 20], [300, 1e-7], [100, 3e-3], [250, 250], [100, 500]], [[3e-4]], {}),
        "ScHcalBarrel": (["HcalBarrelRegCollection"],                       [["*"],["*"],                 ["*"],                        ["0:15","16:31","32:48"]],  [[1000, 20], [300, 1e-7], [100, 3e-3], [250, 250], [100, 500]], [[3e-4]], {"complex_happy" :["0:29", "30:59", "60:76"]}), 
        "ScHCalECRing": (["HcalEndcapRingCollection"],                      [["*"],["*"],                 ["*"],                        ["*"]],                     [[1000, 20], [300, 1e-7], [100, 3e-3], [250, 250], [100, 500]], [[3e-4]], {})                 
        }
systems = dictionary_of_system.keys()
collections = list(dict.fromkeys(list(chain(*[dictionary_of_system[system][0] for system in systems])))) #Retrieve all the collections
system_functions = {} #Retrieve all the functions per systems
histograms_to_select = {}
for system in systems:
    functions_list = dictionary_of_system[system][4].keys()
    functions_list.insert(0, "no_function")
    system_functions[system] = functions_list
    histograms_to_select[system] = {}
    for function in functions_list:
        histograms_to_select[system][function] = {"time":True, "time_peaks":False, "lower_scale_energy":True, "upper_scale_energy": True, "scaled_upper_scale_energy": True, "#Nhits": True, "high_#Nhits": True}
#Creating ROOT canvas to save the histograms
canvas = TCanvas('canvas', 'Histogram', 800, 600)


#Lists of slcio files along with the desired start and end events (ev_stop = -1 would mean that no upper limit as per the definition of fill_histograms function)
# partial_file_list = glob("/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/wzp6_ee_qq_ecm365/partial*.slcio")
# complementary_file_list = glob("/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/wzp6_ee_qq_ecm365/complementary*.slcio")
# slcio_file_list = partial_file_list + complementary_file_list
# number_of_processes = len(slcio_file_list)
number_of_processes = 100
slcio_file_list = ["/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/Machine/beamstrahlung_FCCee@91GeV/ILD_l5_v11gamma/pairs-{}_ZatIP_tpcTimeKeepMC_keep_microcurlers_10MeV_30mrad_ILD_l5_v11gamma.slcio".format(i+1) for i in range(number_of_processes)]

ev_start_list = [0 for _ in range(number_of_processes)] 
ev_stop_list = [-1 for _ in range(number_of_processes)]
    
# ev_start_list = [400*i for i in range(number_of_processes)] 
# ev_stop_list = [400*(i+1) for i in range(number_of_processes)

if __name__ == "__main__":
    profiler = Profile()
    profiler.enable()

    histo_dir = validate_command_line_args(help_string)   
    all_histograms_dicts = execute_parallel_processing(dictionary_of_system, systems, collections, function_dict, system_functions, mip, histograms_to_select, slcio_file_list, ev_start_list, ev_stop_list)
    write_histogram(histo_dir, canvas, number_of_processes, systems, system_functions, histograms_to_select, all_histograms_dicts)
    
    profiler.disable()
    profiler.print_stats(sort='cumtime')  # 'cumtime' will sort based on cumulative time spent on each function
    # profiler.dump_stats(os.path.expanduser("~/profile_results.prof"))