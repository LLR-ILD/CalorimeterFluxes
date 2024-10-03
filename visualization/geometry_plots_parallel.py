import ROOT
import concurrent.futures
from oneD_histograms.histograms_library import decoding, subhit_decoding
from pyLCIO import EVENT, UTIL
from pyLCIO.io import LcioReader
import os
from itertools import islice
from array import array
from cProfile import Profile
import shutil
import time
import gc

def process_file(slcio_file, ev_start, ev_stop, k, system, collections, temp_dir):
    ring_collections = ["EcalEndcapRingCollection",
                        "HCalBarrelRPCHits",
                        "HCalECRingRPCHits",
                        "HCalEndcapRPCHits",
                        "HcalBarrelRegCollection",
                        "HcalEndcapRingCollection",
                        "HcalEndcapsCollection"]
    temp_filename = os.path.join(temp_dir, "temp_ntuple_{}.root".format(k))
    temp_file = ROOT.TFile(temp_filename, "RECREATE")
    ntuple = ROOT.TNtuple("hits", "hits", "x:y:M")
    reader = LcioReader.LcioReader(slcio_file)
    
    for i, event in enumerate(islice(reader, ev_start, ev_stop)):
        total_processed_events = ev_stop - ev_start
        if i % 2000 == 0:
            print('processed {} events out of {} total events in file {}'.format(i, total_processed_events, k))
        
        for collection_name in collections:
            is_endcap = (collection_name in ring_collections)
            try:
                calo_hits = event.getCollection(collection_name)
            except:
                continue
            cell_id_encoding = calo_hits.getParameters().getStringVal(EVENT.LCIO.CellIDEncoding)
            id_decoder = UTIL.BitField64(cell_id_encoding)
            
            for hit in calo_hits:
                decoded_hit = decoding(id_decoder, hit, is_endcap)
                if decoded_hit["systems"] == system and decoded_hit["staves"] == 1 and decoded_hit["modules"] == 0:
                    x, y, z, M = decoded_hit["pos_x"], decoded_hit["pos_y"], decoded_hit["pos_z"], decoded_hit["towers"]
                    # q = 2*J*(M-1.5) + 38
                    # r = ((x**2)+(y**2))**(0.5)
                    ntuple.Fill(array('f', [x, y, M]))
    
    temp_file.Write()
    temp_file.Close()
    return temp_filename

def hadd_and_plot(temp_files, output_dir, canvas, title, xaxis_title, yaxis_title, colorbar_title, plot_name, temp_dir):
    # Use hadd to merge the temporary ntuple files
    output_filename = os.path.join(temp_dir, "final_ntuple.root")
    hadd_command = "hadd -f {} {}".format(output_filename, " ".join(temp_files))
    os.system(hadd_command)
    
    # Open the merged file and get the ntuple
    merged_file = ROOT.TFile(output_filename, "READ")
    ntuple = merged_file.Get("hits")
    
    # Draw the ntuple
    canvas.cd()
    ntuple.SetMarkerSize(1.0)
    ntuple.SetMarkerStyle(8)
    ntuple.Draw("y:x:M", "", "colz")
    
    hist = canvas.GetPrimitive("htemp")
    plotting_titles = "{};{};{}".format(title, xaxis_title, yaxis_title)
    hist.SetTitle(plotting_titles)
    canvas.Update()
    
    palette = canvas.GetPrimitive("palette")
    if (palette):
        x2, y2 = palette.GetX2NDC(), palette.GetY2NDC()
        latex = ROOT.TLatex()
        latex.SetTextSize(0.03)
        latex.SetTextAlign(33)
        latex.SetTextFont(42)
        title_x = x2 + 0.01
        title_y = y2 + 0.05
        latex.DrawLatexNDC(title_x, title_y, colorbar_title)
    
    canvas.Modified()
    canvas.Update()
    canvas.SaveAs(os.path.join(output_dir, plot_name))
    
    # Ensure all temporary files are closed and then remove them
    for temp_file in temp_files:
        os.remove(temp_file)
    os.remove(output_filename)
    
    # Force garbage collection
    gc.collect()

def plotting(slcio_files, ev_start_list, ev_stop_list, system, collections, output_dir, canvas, title, xaxis_title, yaxis_title, colorbar_title, plot_name, temp_dir_name):
    temp_dir = os.path.join(output_dir, temp_dir_name)
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for ev_start, ev_stop, (k, slcio_file) in zip(ev_start_list, ev_stop_list, enumerate(slcio_files)):
            futures.append(executor.submit(process_file, slcio_file, ev_start, ev_stop, k, system, collections, temp_dir))
        
        temp_files = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    hadd_and_plot(temp_files, output_dir, canvas, title, xaxis_title, yaxis_title, colorbar_title, plot_name, temp_dir)

if __name__ == "__main__":  
    out_dir = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/geometry_test"
    number_of_files = 10                 
    files = ["/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/slcio_data/GeV90/mu-_90/partial_{}_fullSim_mu.slcio".format(i) for i in range(number_of_files)]
    ev_start_all = [0 for _ in range(number_of_files)]
    ev_stop_all = [100 for _ in range(number_of_files)]
    ev_stop_list_edited = [LcioReader.LcioReader(slico_file).getNumberOfEvents() + ev_stop + 1 if ev_stop < 0 else ev_stop for slico_file, ev_stop in zip(files, ev_stop_all)]
    total_events_per_file = [a - b for a, b in zip(ev_stop_list_edited, ev_start_all)]
    systemo = 30
    system_collections = ["HcalEndcapsCollection"]
    
    plot_title = "Implicit Selection (Q=2J(M-1.5)+38) Geometry (system=ScHcalBarrel)"
    x_axis_title = "R (mm)"
    y_axis_title = "Z (mm)"
    color_bar_title = "Q=2J(M-1.5)+38"
    plot_name = "test.jpg"
    temp_dir_name = "implicit"
    
    canv = ROOT.TCanvas("c", "3D Geometry Color Plot", 1400, 800)
    profiler = Profile()
    profiler.enable()
    plotting(files, ev_start_all, ev_stop_list_edited, systemo, system_collections, out_dir, canv, plot_title, x_axis_title, y_axis_title, color_bar_title, plot_name, temp_dir_name)
    shutil.rmtree(os.path.join(out_dir, temp_dir_name))
    profiler.disable()
    profiler.print_stats(sort='cumtime')
