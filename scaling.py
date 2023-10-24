import ROOT
import sys
import os

file_dir = sys.argv[1]

#decay channel : [beam energy, instantaneous luminosity, number of events]
scale_dictionary = {"FCC_Z2":[45.6, 180], "FCC_Z4": [45.6, 140], "FCC_W":[80, 21.4], "FCC_ZH":[120, 6.9], "FCC_tt":[182.5, 1.2]}

file = ROOT.TFile.Open(file_dir)
systems = file.GetListOfKeys()
for system in systems:
    
    functions = system.ReadObj().GetListOfKeys()
    for function in functions:
        histogram_sets = function.ReadObj().GetListOfKeys()
        for histogram_type in histogram_sets:
            histograms = histogram_type.ReadObj().GetListOfKeys()
            for histogram in histograms:
                histogram_obj = histogram.ReadObj()
                if histogram_obj and histogram_obj.InheritsFrom("TH1F"):
                    histogram_obj.SetDirectory(0)  # Make ROOT retain ownership of the object 













scale_factor = 0.5  # replace with your scale factor
append_title = " (per second)"  # replace with the string you want to append
list_of_systems =["SiECALBarrel", "ScECalEndcap"]

for system in list_of_systems:
    system_directory = str(dir) + "/rates/" + system
    if not os.path.exists(system_directory):
        os.makedirs(system_directory) 
    
    file = ROOT.TFile.Open('data/v5_small/mu-/histograms6/{}.root'.format(system), 'READ')  # replace with your ROOT file name
    list_of_keys = file.GetListOfKeys()

    for key in list_of_keys:
        obj = key.ReadObj()
        if isinstance(obj, ROOT.TH1):
            obj.Scale(scale_factor)

            # Get the current y-axis title and append the new string
            old_title = obj.GetYaxis().GetTitle()
            new_title = old_title + append_title
            obj.GetYaxis().SetTitle(new_title)

            canvas = ROOT.TCanvas("canvas", "canvas", 800, 600)
            obj.Draw("HIST")
            canvas.SaveAs(system_directory + "/" + obj.GetName() + "_rate" + ".pdf")

    file.Close()