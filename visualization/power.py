import ROOT
import os
from array import array
import ROOT
from twoD_histograms.D_histograms_library_new import get_histograms

def conversion(x, a, b):
    y = a*x + b
    return y

def stdv_conversion(x, a):
    y = abs(a)*x
    return y

def transform_histogram(hist, x_title, a, b, primary_type, primary_suffices, secondary_type):
    # Calculate the total number of bins
    total_num_bins = hist.GetNbinsX()
    
    # Creating a new histogram with transformed bin edges
    transformed_bin_edges = [conversion(hist.GetXaxis().GetBinLowEdge(i), a, b) for i in range(1, hist.GetNbinsX() + 2)]
    name = hist.GetName().replace(primary_suffices[primary_type], secondary_type)
    title = hist.GetTitle()
    transformed_hist = ROOT.TH1F(name, title, total_num_bins, array('d', transformed_bin_edges))

    y_title = hist.GetYaxis().GetTitle()
    transformed_hist.GetXaxis().SetTitle(x_title)
    transformed_hist.GetYaxis().SetTitle(y_title)
    
    # Fill in the values from the original histogram to the transformed histogram
    for bin in range(1, hist.GetNbinsX() + 1):
        original_bin_content = hist.GetBinContent(bin)
        original_bin_center = hist.GetBinCenter(bin)
        transformed_bin_center = conversion(original_bin_center, a, b)# Apply the transformation to the bin center
        transformed_bin_index = transformed_hist.FindBin(transformed_bin_center) # Find the bin index in the transformed histogram where this center would fall
        transformed_hist.AddBinContent(transformed_bin_index, original_bin_content) # Add the original bin content to the appropriate bin in the transformed histogram
        transformed_hist.SetBinError(transformed_bin_index, stdv_conversion(hist.GetBinError(bin), a)) # Propagate errors correctly
    transformed_hist.SetEntries(hist.GetEntries())

    return transformed_hist

def saving_histogram(histo_dir, canvas, type_name, type_dict, func_dir, system, function, secondary=False, stats_dict=None, secondary_dict=None, power_dict=None, power_list=None, data_dict=None, data_list=None, suffix_dict=None):
    """This function is minimally modified from write_histogram in oneD_histograms.histograms_library.py script."""
    if not func_dir.GetDirectory(type_name): # Check if the directory exists
        type_name_dir = func_dir.mkdir(type_name) # If the directory does not exist, create it
    else:
        type_name_dir = func_dir.GetDirectory(type_name) # If it exists, retrieve the existing directory
    if type_name_dir is None: print("Failed to create directory: {}".format(type_name))
    type_name_dir.cd()
    directory_type_name_dir = str(histo_dir) + "/" + system + "/" + function + "/" + type_name
    if not os.path.exists(directory_type_name_dir): os.makedirs(directory_type_name_dir)
    for z, hist in enumerate(type_dict[system][function]):
        if not secondary:
            hist.Draw("HIST")
            canvas.Update()  # Force canvas to update which should draw the stats box if it's set to display
        # Drawing the histogram
        print(hist.GetName())
        if secondary:
            hist.SetStats(0)  # Turn off the automatic stats box
            hist.Draw("HIST")

            stats = hist.GetListOfFunctions().FindObject("stats")
            if not stats:
                stats = ROOT.TPaveStats(0.78, 0.8, 0.98, 0.9, "brNDC")
                stats.SetName("stats")
                hist.GetListOfFunctions().Add(stats)
            else:
                stats.Clear()

            if stats:
                # Retrieve custom statistics
                statistics = stats_dict[system][function][secondary_dict[type_name]][z]
                
                # Adding new manually calculated statistics as text entries
                stats.AddText("Entries  {:.0f}".format(hist.GetEntries()))
                dicts_name = hist.GetName().replace(type_name, suffix_dict[secondary_dict[type_name]])
                if type_name in power_list:
                    stats.AddText("Mean  {:.4f}".format(conversion(statistics[0], power_dict[dicts_name][0], power_dict[dicts_name][1])))
                    stats.AddText("Std Dev  {:.2e}".format(stdv_conversion(statistics[1], power_dict[dicts_name][0])))
                elif type_name in data_list:
                    stats.AddText("Mean  {:.4f}".format(conversion(statistics[0], data_dict[dicts_name][0], data_dict[dicts_name][1])))
                    stats.AddText("Std Dev  {:.2e}".format(stdv_conversion(statistics[1], data_dict[dicts_name][0])))
                
                # Ensure the stats box is linked to the histogram and drawn
                stats.SetOptStat(1111)  # This line controls what statistics to display
                stats.Draw()
        canvas.Modified()
        canvas.Update()
        canvas.SaveAs(directory_type_name_dir + "/{}".format(hist.GetName()) + ".pdf")
        # Check if a histogram with the same name already exists in the ROOT file and delete it
        existing_hist = ROOT.gDirectory.Get(hist.GetName())
        if existing_hist:ROOT.gDirectory.Delete(hist.GetName() + ";*")  # Delete all versions
    
        # Write the histogram to the ROOT file
        hist.Write()
        hist.Delete()

def write_histogram(histo_dir, canvas, merged_histos, systemss, system_per_functions, type_names, stats_dict, secondary_dict, power_dict, power_list, data_dict, data_list, suffix_dict):
    """This function is minimally modified from oneD_histograms.histograms_library.py script."""
    ROOT.gStyle.SetOptStat(1111)  # Ensures the mean, RMS, entries, and underflow/overflow bins are displayed
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
                if type_name in secondary_dict.keys():
                    saving_histogram(histo_dir, canvas, type_name, type_dict, func_dir, system, function, True, stats_dict, secondary_dict, power_dict, power_list, data_dict, data_list, suffix_dict)
                else:
                    saving_histogram(histo_dir, canvas, type_name, type_dict, func_dir, system, function)
    myfile.Close()

if __name__ == "__main__":  

    root_file = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/merged_log/all.root"
    file = ROOT.TFile.Open(root_file)

    histogram_dictionary, stats_dictionary = get_histograms(file)

    system_functions = {}
    systems = histogram_dictionary.keys()
    systems = ["SiECALBarrel"]
    for system in systems:
        functions = histogram_dictionary[system].keys()
        system_functions[system] = functions

    type_namess = ["low_#Nhits", "high_#Nhits", "all_#Nhits"]
    suffices = {"low_#Nhits":"#hits", "high_#Nhits":"high_#hits", "all_#Nhits":"all_#hits"} 
    
    
    all_names = ["low_power", "high_power", "all_power", "low_data", "high_data", "all_data"]
    power_listo = ["low_power", "high_power", "all_power"]
    data_listo = ["low_data", "high_data", "all_data"]
    
    histogram_numbers = len(all_names)
    secondary_dict = {"low_power":"low_#Nhits", "high_power":"high_#Nhits", "all_power":"all_#Nhits", "low_data":"low_#Nhits", "high_data":"high_#Nhits", "all_data":"all_#Nhits"}

    secondary_parameters_power = {}
    secondary_parameters_data = {}
    parameters_power_list_b = [91.23137188, 85.35227891, 76.53362813]
    power_a = 0.000004546875
    data_a = 7
    
    merged_histograms = [{} for _ in range(histogram_numbers)]
    for j, histogram_type in enumerate(type_namess):
        for system in systems:
            merged_histograms[j][system], merged_histograms[len(type_namess)+j][system] = {}, {}
            functions = system_functions[system]
            for function in functions:
                merged_histograms[j][system][function], merged_histograms[j+len(type_namess)][system][function] = [], []
                iterable_histograms = histogram_dictionary[system][function][histogram_type]
                for i, hist in enumerate(iterable_histograms):
                    if i > 5 and i < 9:
                        secondary_parameters_power[hist.GetName()] = [power_a, parameters_power_list_b[i-6]]
                        secondary_parameters_data[hist.GetName()] = [data_a, 0]
                        
                        power_hist = transform_histogram(hist, "power [W]", power_a, parameters_power_list_b[i-6], histogram_type, suffices, all_names[j])
                        merged_histograms[j][system][function].append(power_hist)
                        data_hist = transform_histogram(hist, "data [Bytes]", data_a, 0, histogram_type, suffices, all_names[j+len(type_namess)])
                        merged_histograms[j+len(type_namess)][system][function].append(data_hist)
                    else: #dummy histograms to complete the structure
                        secondary_parameters_power[hist.GetName()] = [0, 0]
                        secondary_parameters_data[hist.GetName()] = [0, 0]
                        temp_power_hist = hist.Clone()
                        temp_data_hist = hist.Clone()
                        merged_histograms[j][system][function].append(temp_power_hist)
                        merged_histograms[j+len(type_namess)][system][function].append(temp_data_hist)

    # print(merged_histograms)
    output_dir = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/merged_log"
    canvas = ROOT.TCanvas('canvas', 'Histogram', 800, 600)
    canvas.SetLogy(1)

    write_histogram(output_dir, canvas, merged_histograms, systems, system_functions, all_names, stats_dictionary, secondary_dict, secondary_parameters_power, power_listo, secondary_parameters_data, data_listo, suffices)     