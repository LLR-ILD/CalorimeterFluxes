import ROOT
import os
import sys
from twoD_histograms.D_histograms_library import get_histograms

root_file_path = sys.argv[1]
histo_dir = sys.argv[2]

def find_mpv(histogram, min, max):

    max_value = -float('inf')
    for bin in range(histogram.FindBin(min), histogram.FindBin(max) + 1):
        if histogram.GetBinContent(bin) > max_value:
            max_value = histogram.GetBinContent(bin)
            max_bin = bin
    mpv = histogram.GetXaxis().GetBinCenter(max_bin)
    return mpv

def fit(histogram, lower_bound, upper_bound, used_canvas):
    maximum = histogram.GetMaximum()

    # Drawing vertical lines at the lower and upper bounds
    lower_bound_line = ROOT.TLine(lower_bound, 0, lower_bound, maximum)
    upper_bound_line = ROOT.TLine(upper_bound, 0, upper_bound, maximum)

    lower_bound_line.SetLineColor(ROOT.kRed)
    upper_bound_line.SetLineColor(ROOT.kRed)

    histogram.Draw("HIST")
    lower_bound_line.Draw("SAME")
    upper_bound_line.Draw("SAME")

    used_canvas.SaveAs(directory + "/{}".format(histogram.GetName()) + "_fitted" + ".pdf")
    used_canvas.Write()
    used_canvas.Update()

file = ROOT.TFile.Open(root_file_path)
histograms = get_histograms(file)

system_bounds = {"RPCHCalBarrel":[0.2e-6,1.2e-6], "RPCHCalEndcap":[0.2e-6,1.2e-6], "RPCHCalECRing":[0.2e-6, 1.2e-6], "ScECALBarrel":[0.0002,0.0005], "ScECalEndcap":[0.0001,0.0005], "ScHcalBarrel":[0.0004, 0.0009],
                  "ScHCalEndcap":[0.0004, 0.0009], "ScHCalECRing":[0.0004, 0.0009], "SiECALBarrel":[0.0001, 0.0004], "SiECalEndcap":[0.0001, 0.0004], "SiECalRing":[0.0001, 0.0004]}

myfile = ROOT.TFile(histo_dir + '/all.root', 'UPDATE')
canvas = ROOT.TCanvas("canvas", "canvas", 900, 600)
mpv = {}
suffix = '_lower_scale'

systems = system_bounds.keys()
# systems = ["RPCHCalECRing"]
for system in systems:
    sys_dir = myfile.mkdir(system)
    functions = histograms[system].keys()
    for function in functions:
        func_dir = sys_dir.mkdir(function)
        func_dir.cd()
        directory = histo_dir + "/" + system + "/" + function
        if not os.path.exists(directory): os.makedirs(directory)
        energy_histograms = histograms[system][function]["lower_scale_energy"]
        for histogram in energy_histograms:
            minimum, maximum = system_bounds[system][0], system_bounds[system][1]
            hist_name = histogram.GetName()
            if hist_name.endswith(suffix):
                hist_name = hist_name[:-len(suffix)]
            mpv[hist_name] = find_mpv(histogram, minimum, maximum)
            fit(histogram, minimum, maximum, canvas)

print(mpv)
