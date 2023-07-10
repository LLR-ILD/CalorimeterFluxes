import ROOT
import sys
import os

dir = sys.argv[1]

list_of_systems =["SiECALBarrel"]
histogram_dict = {}
system_dict = {}
for system in list_of_systems:
    root_file = ROOT.TFile.Open('data/v5_small/mu-/histograms3/{}.root'.format(system), 'READ')
    histograms_list = []
    keys = root_file.GetListOfKeys()
    # Loop over the keys
    for key in keys:
        # Get the histogram and add it to the list
        hist = key.ReadObj()
        if hist and hist.InheritsFrom("TH1F"):
            hist.SetDirectory(0)  # Make ROOT retain ownership of the object
            histograms_list.append(hist)
    histogram_dict[system] = histograms_list

    system_dict[system] = {"S":[], "M":[], "T":[], "L":[]}
    for hist in histograms_list[1::4]:
        # Split the name by underscore and use the first part as key
        key = hist.GetName().split("_")
        for selection in key[1:]:
            if selection[1:] not in system_dict[system][selection[0]]:
                system_dict[system][selection[0]].append(selection[1:])

    for key in system_dict[system].keys():
        if len(system_dict[system][key]) == 0:
            system_dict[system][key].append("*")

    

canvas = ROOT.TCanvas("canvas", "Canvas", 1000, 600)
selected_histogram_list_energy_lower_scale = {}
for system in list_of_systems:
    selected_histogram_list_energy_lower_scale[system] = histogram_dict[system][1::4]
    # Specify the directory path
    two_D_directory = str(dir) + "/2D_histograms/" + system
    fitted_directory = str(dir) + "/fitted_histograms/" + system
    # Create the directory if it doesn't exist
    if not os.path.exists(two_D_directory):
        os.makedirs(two_D_directory)
    if not os.path.exists(fitted_directory):
        os.makedirs(fitted_directory)


for system in list_of_systems: 
    for i, subhist in enumerate(selected_histogram_list_energy_lower_scale[system]):
        fit_result = subhist.Fit("landau", "SQL")
        f1 = subhist.GetFunction("landau")
        f1.SetLineColor(ROOT.kRed)
        f1.SetLineWidth(2)
        # subhist.SetStats(0)
        # subhist.SetTitle(system + " Module " + str(i) + " layers " + system_dict[system]["L"][i])
        subhist.GetYaxis().SetTitle("Number of Events")
        subhist.Draw()
        f1.Draw("SAME")
        canvas.SaveAs(fitted_directory + "/" + subhist.GetName() + "_M" + str(i) + "_fitted.pdf")