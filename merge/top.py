import ROOT
import os
import sys

sys.path.append('/home/llr/ilc/hassouna/script2')
from CalorimeterFluxes.twoD_histograms.D_histograms_library import get_histograms
from CalorimeterFluxes.oneD_histograms.energy_histos import systems, system_functions, histograms_to_select


processes = ["qq90", "ll90", "030ee90", "above30ee90"]

root_file_list = ["/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/energy_histograms/GeV90/{}/all.root".format(process) for process in processes]
type_names = ["time", "lower_scale_energy", "upper_scale_energy", "scaled_upper_scale_energy", "#Nhits", "high_#Nhits"]


histograms_dict = {}
for i, process in enumerate(processes):
    process_file = ROOT.TFile.Open(root_file_list[i])
    histograms_dict[process] = get_histograms(process_file)

def prepare_combined_histograms(histograms, styles, weights):
    """
    Prepare a list of histograms with their respective styles and weights for combined plotting.

    Parameters:
    histograms (list): List of ROOT histograms.
    styles (list): List of style dictionaries for each histogram.
    weights (list): List of weights (scaling factors) for each histogram.

    Returns:
    list: A list of histograms, each set to its style and scaled to its weight.
    """

    combined_histograms = []

    for hist, style, weight in zip(histograms, styles, weights):
        hist.Scale(weight)  # Scale the histogram by the given weight
        hist.SetLineColor(style.get('color', 1))
        hist.SetLineStyle(style.get('lineStyle', 1))
        hist.SetLineWidth(style.get('lineWidth', 2))
        # Additional style attributes can be set here

        y_title = hist.GetYaxis().GetTitle()
        hist.GetYaxis().SetTitle(y_title + " per second")

        combined_histograms.append(hist)

    return combined_histograms

styles = [
    {'color': ROOT.kRed, 'lineStyle': 1, 'lineWidth': 2},
    {'color': ROOT.kBlue, 'lineStyle': 1, 'lineWidth': 2},
    {'color': ROOT.kGreen, 'lineStyle': 1, 'lineWidth': 2},
    {'color': ROOT.kBlack, 'lineStyle': 1, 'lineWidth': 2}
]

weights = [4.82, 0.484, 0.0141, 0.809]  # Example weights for each histogram

histo_dir = sys.argv[1]

"""The systems and functions and histogram types are all the same. Thus, I read them from just one dictionary of histograms."""
for j, histogram_type in enumerate(type_names):
    for system in systems:
        functions = system_functions[system]
        for function in functions:
            number_histograms = len(histograms_dict[processes[0]][system][function][histogram_type])
            
            directory_type_name_dir = str(histo_dir) + "/" + system + "/" + function + "/" + histogram_type
            if not os.path.exists(directory_type_name_dir): os.makedirs(directory_type_name_dir)    
            
            for i in range(number_histograms):
                histograms_to_merge = []
                for process in processes:
                    histograms_to_merge.append(histograms_dict[process][system][function][histogram_type][i])
                
                combined_histograms = combined_histograms = prepare_combined_histograms(histograms_to_merge, styles, weights)
                c = ROOT.TCanvas()
                c.SetLogy(1)
                legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)  # Adjust these coordinates as needed

                for idx, hist in enumerate(combined_histograms):
                    hist.SetStats(False)  # Remove the stats box
                    draw_option = 'HIST same' if idx > 0 else 'HIST'
                    hist.Draw(draw_option)
                    legend.AddEntry(hist, processes[idx], "l")  # "l" for line
                
                legend.Draw()  # Draw the legend
                c.Update()
                name = combined_histograms[0].GetName()
                c.SaveAs(directory_type_name_dir + "/" + name + ".pdf")  # Save the plot