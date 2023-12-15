import ROOT
import os
import sys
from twoD_histograms.D_histograms_library import get_histograms
from oneD_histograms.energy_histos import systems, system_functions, histograms_to_select

processes = ["qq90", "ll90", "030ee90", "above30ee90", "machine"]
type_names = ["time", "lower_scale_energy", "upper_scale_energy", "scaled_upper_scale_energy", "#Nhits", "high_#Nhits"]
weights = [4.82, 0.484, 0.0141, 0.809, 4e+5] 
colors = [ROOT.kRed, ROOT.kBlue, ROOT.kBlack, ROOT.kGreen, ROOT.kYellow]
root_file_list = ["/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/energy_histograms/GeV90/{}/all.root".format(process) for process in processes]

histo_dir = sys.argv[1]

histograms_dict = {}
for i, process in enumerate(processes):
    process_file = ROOT.TFile.Open(root_file_list[i])
    histograms_dict[process] = get_histograms(process_file)

# def prepare_combined_histograms(histograms, colours, weights):
#     """
#     Prepare a list of histograms with their respective styles and weights for combined plotting.

#     Parameters:
#     histograms (list): List of ROOT histograms.
#     styles (list): List of style dictionaries for each histogram.
#     weights (list): List of weights (scaling factors) for each histogram.

#     Returns:
#     list: A list of histograms, each set to its style and scaled to its weight.
#     """

#     combined_histograms = []

#     for hist, colour, weight in zip(histograms, colours, weights):
#         hist.Scale(weight)
#         hist.SetFillColor(colour)
#         hist.SetMarkerColor(colour)
#         hist.SetLineColor(colour)  # Set line color to match fill color
#         hist.SetMarkerStyle(21)
#         hist.SetLineStyle(1)
#         hist.SetLineWidth(1)
#         # Additional style attributes can be set here

#         y_title = hist.GetYaxis().GetTitle()
#         hist.GetYaxis().SetTitle(y_title + " per second")

#         combined_histograms.append(hist)

#     return combined_histograms


def stack_histograms(histograms, colours, weights):
    """
    Stack a list of histograms.

    Parameters:
    histograms (list): List of ROOT histograms.
    colours (list): List of colors for each histogram.
    weights (list): List of weights (scaling factors) for each histogram.

    Returns:
    THStack: A THStack object containing the stacked histograms.
    """

    # Create a new THStack
    stack = ROOT.THStack("stack", "Stacked Histograms")

    # Apply styles and weights, and add histograms to the stack
    for hist, colour, weight in zip(histograms, colours, weights):
        hist.Scale(weight)
        hist.SetFillColor(colour)
        hist.SetLineColor(colour)
        hist.SetMarkerColor(colour)
        hist.SetMarkerStyle(21)
        hist.SetLineStyle(1)
        hist.SetLineWidth(1)

        stack.Add(hist)

    return stack


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
                
                combined_histograms = stack_histograms(histograms_to_merge, colors, weights)
                
                c = ROOT.TCanvas()
                combined_histograms.Draw()  # 'nostack' draws them superimposed, not actually stacked
                c.SetLogy(1)
                
                legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)  # Adjust these coordinates as needed
                for idx, hist in enumerate(histograms_to_merge):
                    legend.AddEntry(hist, processes[idx], "l")  # "l" for line
                legend.Draw()  # Draw the legend

              
                # Find the maximum value across all histograms
                # max_value = max(hist.GetMaximum() for hist in combined_histograms)

                # # Set the Y-axis range for the first histogram, add some extra space
                # combined_histograms[0].SetMaximum(max_value * 1.2)  # Adjust 1.2 as needed

                c.Update()
                name = histograms_to_merge[0].GetName()
                c.SaveAs(directory_type_name_dir + "/" + name + ".pdf")  # Save the plot