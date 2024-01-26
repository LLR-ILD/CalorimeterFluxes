import ROOT
from oneD_histograms.histograms_library import decoding, subhit_decoding
from pyLCIO import EVENT, UTIL
from pyLCIO.io import LcioReader
import os
from array import array

ring_collections = ["EcalEndcapRingCollection",
                        "HCalBarrelRPCHits",
                        "HCalECRingRPCHits",
                        "HCalEndcapRPCHits",
                        "HcalBarrelRegCollection",
                        "HcalEndcapRingCollection",
                        "HcalEndcapsCollection"]

def plotting(slcio_file, ev_start, ev_stop, system, module, collections, output_dir):
    reader = LcioReader.LcioReader(slcio_file)
    No_events = reader.getNumberOfEvents()
    if ev_stop < 0:
        ev_stop = No_events + ev_stop + 1

    ntuple = ROOT.TNtuple("hits", "hits", "y:x:ypos")
    # ntuple_subhits = ROOT.TNtuple("subhits", "subhits", "z_sub:r_sub:t_sub")
    for i, event in enumerate(reader):
        # Print out a progress update
        if i % 2000 == 0:  # Adjust this condition to control how often updates are printed
            print('processed {} out of {} items'.format(i, No_events))
        if i < ev_start:
            continue
        if i >= ev_stop:
            break 
        for collection_name in collections:
            is_endcap = (collection_name in ring_collections)
            calo_hits = event.getCollection(collection_name)
            cell_id_encoding = calo_hits.getParameters().getStringVal(EVENT.LCIO.CellIDEncoding)
            id_decoder = UTIL.BitField64(cell_id_encoding)
            for hit in calo_hits:
                decoded_hit = decoding(id_decoder, hit, is_endcap)
                # subhit_information = subhit_decoding(hit)
                
                if decoded_hit["systems"] == system and decoded_hit["staves"] == 1 and decoded_hit["modules"] == 1 and decoded_hit["towers"] == 31 and decoded_hit["layers"] == 1:
                    # print(decoded_hit["staves"], decoded_hit["modules"], decoded_hit["towers"])
                    x, y, z, l = decoded_hit["pos_x"], decoded_hit["pos_y"], decoded_hit["pos_z"], decoded_hit["xs"]
                    # r = (x**2 + y**2)**(0.5)
                    # print(r,z)
                    ntuple.Fill(array('f', [y, x, l]))
                    # for subhit in subhit_information:
                    #     x_sub, y_sub, z_sub, t_sub = subhit.pos_x, subhit.pos_y, subhit.pos_z, subhit.time
                    #     r_sub = (x_sub**2 + y_sub**2)**(0.5)
                    #     if 6 < t_sub < 12: ntuple_subhits.Fill(array('f', [z_sub, r_sub, t_sub]))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Drawing the ntuple
    ntuple.SetMarkerSize(0.5)
    ntuple.SetMarkerStyle(8)
    ntuple.Draw("y:x:ypos", "", "colz")
    
    # Get the frame of the pad
    hist = ROOT.gPad.GetPrimitive("htemp")  # This gets the last histogram drawn
    hist.SetTitle("I Geometry (system=ScHcalBarrel, stave=1, module=1, tower=31);X;Y")  # Set your title and axis labels here

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
        latex.DrawLatexNDC(title_x, title_y, "I")
    
    ROOT.gPad.SaveAs(os.path.join(output_dir, "system_ScHcalBarrel_CellYs8.pdf"))

    # ntuple_subhits.Draw("z_sub:r_sub:t_sub", "", "colz")
    # ROOT.gPad.SaveAs(os.path.join(output_dir, "system_time.pdf"))

out_dir = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/geometry"                 
file = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/slcio_data/GeV90/mu-_90/partial_0_fullSim_mu.slcio"
systemo = 22
modulo = 3
system_collections = ["HcalBarrelRegCollection"]

c = ROOT.TCanvas("c", "3D Geometry Color Plot", 1200, 800)
# ROOT.gStyle.SetPalette(ROOT.kRainBow)
plotting(file, 0, 1000, systemo, modulo, system_collections, out_dir)
