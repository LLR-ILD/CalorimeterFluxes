import ROOT
from oneD_histograms.histograms_library import decoding, subhit_decoding
from pyLCIO import EVENT, UTIL
from pyLCIO.io import LcioReader
import os
from itertools import islice
from array import array

ring_collections = ["EcalEndcapRingCollection",
                        "HCalBarrelRPCHits",
                        "HCalECRingRPCHits",
                        "HCalEndcapRPCHits",
                        "HcalBarrelRegCollection",
                        "HcalEndcapRingCollection",
                        "HcalEndcapsCollection"]

def plotting(slcio_files, ev_start_list, ev_stop_list, events_per_file, system, collections, output_dir):
    total_no_events = sum(events_per_file)
    ntuple = ROOT.TNtuple("hits", "hits", "x:y:M")
    for ev_start, ev_stop, total_events, (k, slcio_file) in zip(ev_start_list, ev_stop_list, events_per_file, enumerate(slcio_files)):
        reader = LcioReader.LcioReader(slcio_file)
        # ntuple_subhits = ROOT.TNtuple("subhits", "subhits", "z_sub:r_sub:t_sub")
        for i, event in enumerate(islice(reader, ev_start, ev_stop)):
            # Print out a progress update
            total_processed_events = sum(events_per_file[:k])
            if i % 2000 == 0:  # Adjust this condition to control how often updates are printed
                print('processed {} out of {} items in file {} \n processed {} out of {} total events'.format(i, total_events, k, i+total_processed_events, total_no_events))
            for collection_name in collections:
                is_endcap = (collection_name in ring_collections)
                try:
                    calo_hits = event.getCollection(collection_name)
                except:
                    continue
                # is_endcap = (collection_name in ring_collections)
                # calo_hits = event.getCollection(collection_name)
                cell_id_encoding = calo_hits.getParameters().getStringVal(EVENT.LCIO.CellIDEncoding)
                id_decoder = UTIL.BitField64(cell_id_encoding)
                for hit in calo_hits:
                    decoded_hit = decoding(id_decoder, hit, is_endcap)
                    # subhit_information = subhit_decoding(hit)
                    
                    if decoded_hit["systems"] == system:
                        # print(decoded_hit["staves"], decoded_hit["modules"], decoded_hit["towers"])
                        x, y, z, M = decoded_hit["pos_x"], decoded_hit["pos_y"], decoded_hit["pos_z"], decoded_hit["towers"]
                        # r = (x**2 + y**2)**(0.5)
                        # MJ = 2*J*(M-1.5) + 38
                        ntuple.Fill(array('f', [z, x, M]))
                        # for subhit in subhit_information:
                        #     x_sub, y_sub, z_sub, t_sub = subhit.pos_x, subhit.pos_y, subhit.pos_z, subhit.time
                        #     r_sub = (x_sub**2 + y_sub**2)**(0.5)
                        #     if 6 < t_sub < 12: ntuple_subhits.Fill(array('f', [z_sub, r_sub, t_sub]))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Drawing the ntuple
    ntuple.SetMarkerSize(0.5)
    ntuple.SetMarkerStyle(8)
    ntuple.Draw("x:y:M", "", "colz")
    
    # Get the frame of the pad
    hist = ROOT.gPad.GetPrimitive("htemp")  # This gets the last histogram drawn
    hist.SetTitle("Towers Geometry (system=ScHCALBarrel, stave=5, module=1);X;Z")  # Set your title and axis labels here
    pad = ROOT.gPad
    pad.Modified()
    pad.Update()
    
    # Access the color palette
    palette = pad.GetPrimitive("palette")
    if palette:
        x2, y2 = palette.GetX2NDC(), palette.GetY2NDC()

        # Create a TLatex object for the title
        latex = ROOT.TLatex()
        latex.SetTextSize(0.03)
        latex.SetTextAlign(33)  # Horizontal center and vertical top
        latex.SetTextFont(42)

        # Position the title above or to the right of the color palette
        title_x = x2 + 0.01 # Adjust as needed
        title_y = y2 + 0.05  # Centered vertically on the palette
        latex.DrawLatexNDC(title_x, title_y, "Towers")
    
    ROOT.gPad.SaveAs(os.path.join(output_dir, "towers_system_ScHCALBarrel.pdf"))

    # ntuple_subhits.Draw("z_sub:r_sub:t_sub", "", "colz")
    # ROOT.gPad.SaveAs(os.path.join(output_dir, "system_time.pdf"))

out_dir = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/geometry"
number_of_files = 2                 
files = ["/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/slcio_data/GeV90/mu-_90/partial_{}_fullSim_mu.slcio".format(i) for i in range(number_of_files)]
ev_start_all = [0 for _ in range(number_of_files)]
ev_stop_all = [-1 for _ in range(number_of_files)]
ev_stop_list_edited = [LcioReader.LcioReader(slico_file).getNumberOfEvents() + ev_stop + 1 if ev_stop < 0 else ev_stop for slico_file, ev_stop in zip(files, ev_stop_all)]
total_events_per_file = [a - b for a, b in zip(ev_stop_list_edited, ev_start_all)]
systemo = 22
system_collections = ["HcalBarrelRegCollection"]

c = ROOT.TCanvas("c", "3D Geometry Color Plot", 1200, 800)
# ROOT.gStyle.SetPalette(ROOT.kRainBow)
plotting(files, ev_start_all, ev_stop_list_edited, total_events_per_file, systemo, system_collections, out_dir)
