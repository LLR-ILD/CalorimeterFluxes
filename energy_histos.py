from cProfile import Profile
from itertools import chain
from ROOT import TCanvas
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

# The dictionary that conatins all the systems and the required selections.
#selection format "S:M:T:L" conditions => "*:*:2:0-4,5-10" means no selection on M, S, 1 histo per 2 tower , 1 for layer 0 to 5, and one for layers in 5 to 10.
dictionary_of_system = {
#       System          collections                                         Stave  Modules                Towers                        Layers                      Time bins/max lowE bin/max highE bin/max  #hits bin/max  EThr  Split Func:ranges         
        "SiECalEndcap": (["ECalEndcapSiHitsEven", "ECalEndcapSiHitsOdd"],   [["*"],["*"],                 ["0","1:2","3:5","6:8"],      ["0:9","10:19","20:29"]],   [[1000, 20], [1000, 0.001], [1000, 0.03], [100, 35]], [[0.0001]], {}),
        "SiECALBarrel": (["ECalBarrelSiHitsEven", "ECalBarrelSiHitsOdd"],   [["*"],["1","2","3","4","5"], ["*"],                        ["0:9","10:19","20:29"]],   [[1000, 20], [1000, 0.001], [1000, 0.03], [100, 35]], [[0.0001]], {}), 
        "SiECalRing": (["EcalEndcapRingCollection"],                        [["*"],["*"],                 ["*"],                        ["0:9","10:19","20:29"]],   [[1000, 20], [1000, 0.001], [1000, 0.03], [100, 35]], [[0.0001]], {}), 
        "ScECalEndcap": (["ECalEndcapScHitsEven", "ECalEndcapScHitsOdd"],   [["*"],["*"],                 ["0","1:2","3:5","6:8"],      ["0:9","10:19","20:29"]],   [[1000, 20], [1000, 0.001], [1000, 0.03], [100, 35]], [[0.0003]], {}),
        "ScECALBarrel": (["ECalBarrelScHitsEven", "ECalBarrelScHitsOdd"],   [["*"],["1","2","3","4","5"], ["*"],                        ["0:9","10:19","20:29"]],   [[1000, 20], [1000, 0.001], [1000, 0.03], [100, 35]], [[0.0002]], {}), 
        "RPCHCalEndcap": (["HCalEndcapRPCHits"],                            [["*"],["*"],                 ["0:3","4:7","8:11","12:15"], ["0:15","16:31","32:48"]],  [[1000, 20], [1000, 2e-6],  [1000, 3e-5], [100, 35]], [[3e-7]], {}),
        "RPCHCalBarrel": (["HCalBarrelRPCHits"],                            [["*"],["*"],                 ["*"],                        ["0:15","16:31","32:48"]],  [[1000, 20], [1000, 2e-6],  [1000, 3e-5], [100, 35]], [[3e-7]], {"complex_sad": ["0:79", "80:159", "160:234"]}), 
        "RPCHCalECRing": (["HCalECRingRPCHits"],                            [["*"],["*"],                 ["*"],                        ["*"]],                     [[1000, 20], [1000, 0.001], [1000, 0.03], [100, 35]], [[0.0001]], {}),         
        "ScHCalEndcap": (["HcalEndcapsCollection"],                         [["*"],["*"],                 ["0:3","4:7","8:11","12:15"], ["0:15","16:31","32:48"]],  [[1000, 20], [1000, 0.001], [1000, 0.03], [100, 35]], [[0.0001]], {}),
        "ScHcalBarrel": (["HcalBarrelRegCollection"],                       [["*"],["*"],                 ["*"],                        ["0:15","16:31","32:48"]],  [[1000, 20], [1000, 0.001], [1000, 0.03], [100, 35]], [[0.0003]], {"complex_happy" :["0:29", "30:59", "60:76"]}), 
        "ScHCalECRing": (["HcalEndcapRingCollection"],                      [["*"],["*"],                 ["*"],                        ["*"]],                     [[1000, 20], [1000, 0.001], [1000, 0.03], [100, 35]], [[0.0001]], {})                 
        }
systems = dictionary_of_system.keys() #Retrieve all the systems
collections = list(dict.fromkeys(list(chain(*[dictionary_of_system[system][0] for system in dictionary_of_system.keys()])))) #Retrieve all the collections
system_functions = {} #Retrieve all the functions per systems
for system in systems:
    functions_list = dictionary_of_system[system][4].keys()
    functions_list.insert(0, "no_function")
    system_functions[system] = functions_list


#Creating ROOT canvas to save the histograms
canvas = TCanvas('canvas', 'Histogram', 800, 600)

number_of_processes = 25
#Lists of slcio files along with the desired start and end events (ev_stop = -1 would mean that no upper limit as per the definition of fill_histograms function)
slcio_file_list = ["/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/wzp6_ee_qq_ecm90/partial_{}_fullSim_wzp6_ee_qq_ecm90_0+10000.slcio".format(str(i)) for i in range(number_of_processes)]
ev_start_list = [0 for i in range(number_of_processes)] 
ev_stop_list = [-1 for i in range(number_of_processes)]

if __name__ == "__main__":
    profiler = Profile()
    profiler.enable()

    histo_dir = validate_command_line_args(help_string)   
    all_histograms_dicts = execute_parallel_processing(dictionary_of_system, systems, collections, function_dict, system_functions, slcio_file_list, ev_start_list, ev_stop_list)
    write_histogram(histo_dir, canvas, number_of_processes, systems, system_functions, all_histograms_dicts)
    
    profiler.disable()
    profiler.print_stats(sort='cumtime')  # 'cumtime' will sort based on cumulative time spent on each function
    # profiler.dump_stats(os.path.expanduser("~/profile_results.prof"))