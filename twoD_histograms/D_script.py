from D_histograms_library import get_histograms, get_x_titles, get_y_titles, histograms_selections, all_histograms, write_histograms
import sys
import ROOT

def str_to_bool(s):
    """Convert a string to a boolean value."""
    if s.lower() in ['true', 't', 'yes', 'y', '1']:
        return True
    elif s.lower() in ['false', 'f', 'no', 'n', '0']:
        return False
    else:
        raise ValueError("Cannot convert {} to a boolean.".format(s))

root_file = sys.argv[1]
dir = sys.argv[2]
logarithmic = str_to_bool(sys.argv[3])
bins_stats = str_to_bool(sys.argv[4])

file = ROOT.TFile.Open(root_file)
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

units = {"time":"ns", "lower_scale_energy":"GeV", "upper_scale_energy":"GeV", "all_scale_energy":"GeV", "scaled_upper_scale_energy":"MIP", "scaled_all_scale_energy":"MIP", "low_#Nhits":"#hits", "high_#Nhits":"#hits", "all_#Nhits":"#hits"}
entries = {"time":"hits*energy [GeV]", "lower_scale_energy":"hits", "upper_scale_energy":"hits", "all_scale_energy":"hits", "scaled_upper_scale_energy":"hits", "scaled_all_scale_energy":"hits", "low_#Nhits":"events", "high_#Nhits":"events", "all_#Nhits":"events"}
merged = False
if merged:
    types = entries.keys()
    for typee in types:
        entries[typee] = entries[typee] + "/second"

canvas = ROOT.TCanvas("canvas", "Canvas", 2000, 1000)
canvas.SetBottomMargin(0.25)  # Increase the bottom margin

write_histograms(twoD_histograms, histogram_selection_dictionary, histograms_y_titles, dir, canvas, entries, units, logarithmic, bins_stats)