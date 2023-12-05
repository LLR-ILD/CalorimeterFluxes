import ROOT
from histograms_library import decoding, subhit_decoding
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

def plotting(slcio_file, ev_start, ev_stop, system, collections, output_dir):
    reader = LcioReader.LcioReader(slcio_file)
    No_events = reader.getNumberOfEvents()
    if ev_stop < 0:
        ev_stop = No_events + ev_stop + 1

    ntuple = ROOT.TNtuple("hits", "hits", "r:z:m")
    ntuple_subhits = ROOT.TNtuple("subhits", "subhits", "r_sub:z_sub:t_sub")
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
                subhit_information = subhit_decoding(hit)
                
                if decoded_hit["systems"] == system:
                    x, y, z, m = decoded_hit["pos_x"], decoded_hit["pos_y"], decoded_hit["pos_z"], decoded_hit["modules"]
                    r = (x**2 + y**2)**(0.5)
                    # print(x,y,r)
                    ntuple.Fill(array('f', [r, z, m]))
                    for subhit in subhit_information:
                        x_sub, y_sub, z_sub, t_sub = subhit.pos_x, subhit.pos_y, subhit.pos_z, subhit.time
                        r_sub = (x_sub**2 + y_sub**2)**(0.5)
                        if 6 < t_sub < 12: ntuple_subhits.Fill(array('f', [r_sub, z_sub, t_sub]))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    ntuple.Draw("r:z:m", "", "colz")
    ROOT.gPad.SaveAs(os.path.join(output_dir, "system_modules.pdf"))

    ntuple_subhits.Draw("r_sub:z_sub:t_sub", "", "colz")
    ROOT.gPad.SaveAs(os.path.join(output_dir, "system_time.pdf"))

out_dir = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/geometry"                 
file = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/mu-_90/partial_0_fullSim_mu.slcio"
systemo = 20
system_collections = ["ECalBarrelSiHitsEven", "ECalBarrelSiHitsOdd"]

c = ROOT.TCanvas("c", "3D Geometry Color Plot", 800, 600)
# ROOT.gStyle.SetPalette(ROOT.kRainBow)
plotting(file, 0, 20000, systemo, system_collections, out_dir)


# and decoded_hit["modules"] == 0