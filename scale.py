import ROOT


GeV240 = {"qq":53476, "WW":16667}

def scale_histograms_in_file(input_filename, output_filename, scale_factor=1.0):
    # Open the input ROOT file in read mode
    input_file = ROOT.TFile(input_filename, "READ")
    
    # Open the output ROOT file in recreate mode
    output_file = ROOT.TFile(output_filename, "RECREATE")

    systems = input_file.GetListOfKeys()
    for system in systems:
        sys_dir = output_file.mkdir(system)
        functions = system.ReadObj().GetListOfKeys()
        for function in functions:
            func_dir = sys_dir.mkdir(function)
            histogram_sets = function.ReadObj().GetListOfKeys()
            for histogram_type in histogram_sets:
                type_name_dir = func_dir.mkdir(histogram_type)
                histograms = histogram_type.ReadObj().GetListOfKeys()
                for histogram in histograms:
                    histogram_obj = histogram.ReadObj()
                    if histogram_obj and histogram_obj.InheritsFrom("TH1F"):
                        histogram_obj.SetDirectory(0)  # Make ROOT retain ownership of the object 
                        obj_clone = histogram_obj.Clone()  # Clone the histogram to avoid modifying the original
                        obj_clone.Scale(scale_factor)
                        type_name_dir.cd()
                        obj_clone.Write()

    # Close the ROOT files
    input_file.Close()
    output_file.Close()
    
# Use the function on multiple ROOT files
root_files = [("input1.root", "output1.root"), ("input2.root", "output2.root"), ...]
for i, (input_file, output_file) in enumerate(root_files):
    scale_histograms_in_file(input_file, output_file, scale_factor=GeV240[i])  # Adjust scale_factor as needed