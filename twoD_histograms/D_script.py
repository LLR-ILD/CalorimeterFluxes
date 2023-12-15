from D_histograms_library import get_histograms, get_x_titles, get_y_titles, histograms_selections, all_histograms, write_histograms
import sys
import ROOT

file = ROOT.TFile.Open("/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/energy_histograms/GeV90/merged_log/all.root")
histogram_dictionary = get_histograms(file)
system_functions = {}
systems = histogram_dictionary.keys()
for system in systems:
    functions = histogram_dictionary[system].keys()
    system_functions[system] = functions

histograms_x_titles = get_x_titles(histogram_dictionary, systems)
histograms_y_titles = get_y_titles(histogram_dictionary, systems)

histogram_selection_dictionary, Bin_labels = histograms_selections(histogram_dictionary, systems, system_functions)

twoD_histograms = all_histograms(histogram_dictionary, histograms_x_titles, histogram_selection_dictionary, Bin_labels, systems, system_functions)

canvas = ROOT.TCanvas("canvas", "Canvas", 2000, 1000)
dir = sys.argv[1]
write_histograms(twoD_histograms, histogram_selection_dictionary, histograms_y_titles, dir, canvas, True)