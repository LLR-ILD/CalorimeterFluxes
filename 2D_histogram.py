import ROOT
import sys
import os

dir = sys.argv[1]

list_of_systems =["SiECALBarrel"]
histogram_dict = {}
system_dict = {}
for system in list_of_systems:
    root_file = ROOT.TFile.Open('data/ILD/FullSim/histograms6/{}.root'.format(system), 'READ')
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

def two_D_hist(system):
    histograms = []
    n = len(system_dict[system]["L"])
    # print(n)
    selected_histogram_list_time = histogram_dict[system][::4]
    hist_2d_time = [None] * n
    for j in range(n):
        selected_histogram_list_time_per_layer = selected_histogram_list_time[j::n]
        # print(selected_histogram_list_time_per_layer)
        min_bin_value = min([hist.GetXaxis().GetXmin() for hist in selected_histogram_list_time_per_layer])
        max_bin_value = max([hist.GetXaxis().GetXmax() for hist in selected_histogram_list_time_per_layer])
        max_bins_time = max([hist.GetNbinsX() for hist in selected_histogram_list_time_per_layer])
        hist_2d_time[j] = ROOT.TH2F("hist_2d_time_" + system + "_" + system_dict[system]["L"][j], "2D time Histogram " + system + " layers " + system_dict[system]["L"][j], len(selected_histogram_list_time_per_layer), 0, len(selected_histogram_list_time_per_layer), max_bins_time, min_bin_value, max_bin_value)
        hist_2d_time[j].GetXaxis().SetTitle("Modules")
        hist_2d_time[j].GetYaxis().SetTitle("Weighted Time")
        for i, hist in enumerate(selected_histogram_list_time_per_layer):
            # hist.GetXaxis().SetBinLabel(i+1, "module {}".format(str(i+1)))
            for bin in range(1, hist.GetNbinsX() + 1):
                # Fill the bin in 2D histogram with bin content from 1D histogram
                hist_2d_time[j].Fill(i, hist.GetBinCenter(bin), hist.GetBinContent(bin))

    selected_histogram_list_energy_lower_scale = histogram_dict[system][1::4]
    hist_2d_energy_lower_scale = [None] * n
    for j in range(n):
        selected_histogram_list_energy_lower_scale_per_layer = selected_histogram_list_energy_lower_scale[j::n]
        min_bin_value = min([hist.GetXaxis().GetXmin() for hist in selected_histogram_list_energy_lower_scale_per_layer])
        max_bin_value = max([hist.GetXaxis().GetXmax() for hist in selected_histogram_list_energy_lower_scale_per_layer])
        max_bins_energy_lower_scale = max([hist.GetNbinsX() for hist in selected_histogram_list_energy_lower_scale_per_layer])
        hist_2d_energy_lower_scale[j] = ROOT.TH2F("hist_2d_energy_lower_scale_" + system + "_" + system_dict[system]["L"][j], "2D energy Histogram " + system + " layers " + system_dict[system]["L"][j], len(selected_histogram_list_energy_lower_scale_per_layer), 0, len(selected_histogram_list_energy_lower_scale_per_layer), max_bins_energy_lower_scale, min_bin_value, max_bin_value)
        hist_2d_energy_lower_scale[j].GetXaxis().SetTitle("Modules")
        hist_2d_energy_lower_scale[j].GetYaxis().SetTitle("Energy [GeV]")
        for i, hist in enumerate(selected_histogram_list_energy_lower_scale_per_layer):
            # hist.GetXaxis().SetBinLabel(i, "module {}".format(str(i+1)))
            for bin in range(1, hist.GetNbinsX() + 1):
                # Fill the bin in 2D histogram with bin content from 1D histogram
                hist_2d_energy_lower_scale[j].Fill(i, hist.GetBinCenter(bin), hist.GetBinContent(bin))

    selected_histogram_List_energy_upper_scale = histogram_dict[system][2::4]
    hist_2d_energy_upper_scale = [None] * n
    for j in range(n):
        selected_histogram_List_energy_upper_scale_per_layer = selected_histogram_List_energy_upper_scale[j::n]
        min_bin_value = min([hist.GetXaxis().GetXmin() for hist in selected_histogram_List_energy_upper_scale_per_layer])
        max_bin_value = max([hist.GetXaxis().GetXmax() for hist in selected_histogram_List_energy_upper_scale_per_layer])
        max_bins_energy_upper_scale = max([hist.GetNbinsX() for hist in selected_histogram_List_energy_upper_scale_per_layer])
        hist_2d_energy_upper_scale[j] = ROOT.TH2F("hist_2d_energy_upper_scale_" + system + "_" + system_dict[system]["L"][j], "2D upper-energy Histogram from 1D Histograms " + system + " layers " + system_dict[system]["L"][j], len(selected_histogram_List_energy_upper_scale_per_layer), 0, len(selected_histogram_List_energy_upper_scale_per_layer), max_bins_energy_upper_scale, min_bin_value, max_bin_value)
        hist_2d_energy_upper_scale[j].GetXaxis().SetTitle("Modules")
        hist_2d_energy_upper_scale[j].GetYaxis().SetTitle("Energy [GeV]")
        for i, hist in enumerate(selected_histogram_List_energy_upper_scale_per_layer):
            # hist.GetXaxis().SetBinLabel(i, "module {}".format(str(i+1)))
            for bin in range(1, hist.GetNbinsX() + 1):
                # Fill the bin in 2D histogram with bin content from 1D histogram
                hist_2d_energy_upper_scale[j].Fill(i, hist.GetBinCenter(bin), hist.GetBinContent(bin))
    
    selected_histogram_List_Nhits = histogram_dict[system][3::4]
    hist_2d_Nhits = [None] * n
    for j in range(n):
        selected_histogram_List_Nhits_per_layer = selected_histogram_List_Nhits[j::n]
        min_bin_value = min([hist.GetXaxis().GetXmin() for hist in selected_histogram_List_Nhits_per_layer])
        max_bin_value = max([hist.GetXaxis().GetXmax() for hist in selected_histogram_List_Nhits_per_layer])
        max_bins_Nhits = max([hist.GetNbinsX() for hist in selected_histogram_List_Nhits_per_layer])
        hist_2d_Nhits[j] = ROOT.TH2F("hist_2d_Nhits_" + "_" + system_dict[system]["L"][j], "2D #hits Histogram " + system + " layers " + system_dict[system]["L"][j], len(selected_histogram_List_Nhits_per_layer), 0, len(selected_histogram_List_Nhits_per_layer), max_bins_Nhits, min_bin_value, max_bin_value)
        hist_2d_Nhits[j].GetXaxis().SetTitle("Modules")
        hist_2d_Nhits[j].GetYaxis().SetTitle("Hits above Energy Threshold")
        for i, hist in enumerate(selected_histogram_List_Nhits_per_layer):
            # hist.GetXaxis().SetBinLabel(i, "module {}".format(str(i+1)))
            for bin in range(1, hist.GetNbinsX() + 1):
                # Fill the bin in 2D histogram with bin content from 1D histogram
                hist_2d_Nhits[j].Fill(i, hist.GetBinCenter(bin), hist.GetBinContent(bin))

    histograms.append(hist_2d_time)
    histograms.append(hist_2d_energy_lower_scale)
    histograms.append(hist_2d_energy_upper_scale)
    histograms.append(hist_2d_Nhits)

    return histograms 

two_D_histogram_dict = {}

canvas = ROOT.TCanvas("canvas", "Canvas", 1000, 600)

for system in list_of_systems:
    two_D_histogram_dict[system] = two_D_hist(system)
    # Specify the directory path
    two_D_directory = str(dir) + "/2D_histograms/" + system
    fitted_directory = str(dir) + "/fitted_histograms/" + system
    # Create the directory if it doesn't exist
    if not os.path.exists(two_D_directory):
        os.makedirs(two_D_directory)
    if not os.path.exists(fitted_directory):
        os.makedirs(fitted_directory)

    for hist_collection in two_D_histogram_dict[system]:
        for subhist in hist_collection:
            subhist.Draw("COLZ")
            subhist.SetStats(0)
            canvas.SaveAs(two_D_directory + "/" + subhist.GetName() + ".pdf")

    for i, subhist in enumerate(two_D_histogram_dict[system][1]):
        for binx in range(1, subhist.GetNbinsX()+1):
            h1 = subhist.ProjectionY("_py", binx, binx)
            # for bin in range(1, h1.GetNbinsX()+1):
            #     h1.SetBinError(bin, 0)
            # fit_result = h1.Fit("landau", "SQL", "", 0.0001, 0.0004)
            # f1 = h1.GetFunction("landau")
            # f1.SetLineColor(ROOT.kRed)
            # f1.SetLineWidth(2)
            # h1.SetStats(0)
            h1.SetTitle(system + " Module " + str(binx) + " layers " + system_dict[system]["L"][i])
            h1.GetYaxis().SetTitle("Number of Events")
            h1.Draw()
            # f1.Draw("SAME")
            canvas.SaveAs(fitted_directory + "/" + subhist.GetName() + "_M" + str(binx) + "_fitted.pdf")