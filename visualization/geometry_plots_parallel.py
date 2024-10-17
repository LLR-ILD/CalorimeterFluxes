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
                # print(decoded_hit["systems"])
                if decoded_hit["systems"] == system:
                    x, y, z, M = decoded_hit["pos_x"], decoded_hit["pos_y"], decoded_hit["pos_z"], decoded_hit["staves"]
                    # q = 2*J*(M-1.5) + 38
                    # r = ((x**2)+(y**2))**(0.5)
                    ntuple.Fill(array('f', [x, y, M]))
    
    temp_file.Write()
    temp_file.Close()
    return temp_filename

def hadd_and_plot(temp_files, output_dir, title, xaxis_title, yaxis_title, colorbar_title, plot_name, temp_dir,
                  canvas_margins, canvas_width, canvas_height, axes_sizes, to_scale=False):
    # Use hadd to merge the temporary ntuple files
    output_filename = os.path.join(temp_dir, "final_ntuple.root")
    hadd_command = "hadd -f {} {}".format(output_filename, " ".join(temp_files))
    os.system(hadd_command)
    
    # Open the merged file and get the ntuple
    merged_file = ROOT.TFile(output_filename, "READ")
    ntuple = merged_file.Get("hits")
    
    canvas = ROOT.TCanvas("c", "3D Geometry Color Plot", canvas_width, canvas_height)
    canvas.SetLeftMargin(canvas_margins["LeftMargin"])
    canvas.SetRightMargin(canvas_margins["RighttMargin"])
    canvas.SetBottomMargin(canvas_margins["BottomMargin"])
    canvas.SetTopMargin(canvas_margins["TopMargin"])
    canvas.cd()
    
    ntuple.SetMarkerSize(1.0)
    ntuple.SetMarkerStyle(8)
    ntuple.Draw("y:x:M", "", "colz")
    
    hist = canvas.GetPrimitive("htemp")
    plotting_titles = "{};{};{}".format(title, xaxis_title, yaxis_title)
    hist.SetTitle(plotting_titles)
    hist.SetZTitle("")
    hist.GetXaxis().SetLabelSize(axes_sizes["x_axis_label_size"])
    hist.GetYaxis().SetLabelSize(axes_sizes["y_axis_label_size"])
    hist.GetXaxis().SetTitleSize(axes_sizes["x_axis_title_size"])
    hist.GetYaxis().SetTitleSize(axes_sizes["y_axis_title_size"])
    
    if to_scale:
    # Retrieve the axis limits
        x_min = hist.GetXaxis().GetXmin()
        x_max = hist.GetXaxis().GetXmax()
        y_min = hist.GetYaxis().GetXmin()
        y_max = hist.GetYaxis().GetXmax()
        aspect_ratio = (y_max - y_min) / (x_max - x_min) # Compute the aspect ratio based on the axis ranges
        
        # Adjust the canvas size dynamically based on the aspect ratio
        canvas_height = int(canvas_width * aspect_ratio)
        canvas.SetCanvasSize(canvas_width, canvas_height)
    canvas.Update()
    
    palette = canvas.GetPrimitive("palette")
    if palette:
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
    
    # Close the ROOT file before removing the temporary files
    merged_file.Close()
    
    # Ensure all temporary files are closed and then remove them
    for temp_file in temp_files:
        os.remove(temp_file)
    os.remove(output_filename)
    
    # Force garbage collection
    gc.collect()


def plotting(slcio_files, ev_start_list, ev_stop_list, system, collections, output_dir, title, xaxis_title, yaxis_title, colorbar_title, plot_name, temp_dir_name,
             canvas_margins, canvas_width, canvas_height, axes_sizes, to_scale=False):
    temp_dir = os.path.join(output_dir, temp_dir_name)
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for ev_start, ev_stop, (k, slcio_file) in zip(ev_start_list, ev_stop_list, enumerate(slcio_files)):
            futures.append(executor.submit(process_file, slcio_file, ev_start, ev_stop, k, system, collections, temp_dir))
        
        temp_files = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    hadd_and_plot(temp_files, output_dir, title, xaxis_title, yaxis_title, colorbar_title, plot_name, temp_dir,
                  canvas_margins, canvas_width, canvas_height, axes_sizes, to_scale=False)

if __name__ == "__main__":  
    out_dir = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/geometry_test"
    number_of_files = 2                 
    files = ["/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/slcio_data/GeV90/mu-_90/partial_{}_fullSim_mu.slcio".format(i) for i in range(number_of_files)]
    ev_start_all = [0 for _ in range(number_of_files)]
    ev_stop_all = [100 for _ in range(number_of_files)]
    ev_stop_list_edited = [LcioReader.LcioReader(slico_file).getNumberOfEvents() + ev_stop + 1 if ev_stop < 0 else ev_stop for slico_file, ev_stop in zip(files, ev_stop_all)]
    total_events_per_file = [a - b for a, b in zip(ev_stop_list_edited, ev_start_all)]
    systemo = 22
    system_collections = ["HcalBarrelRegCollection"]
    
    #Titles and names
    plot_title = "Staves' Geometry (system=ScHcalBarrel)"
    x_axis_title = "X (mm)"
    y_axis_title = "Y (mm)"
    color_bar_title = "Staves"
    plot_name = "staves1_HCAL.jpg"
    temp_dir_name = "Staves2"
    
    #Canvas properties
    canvas_width, canvas_height = 1600, 1600
    to_scale = False
    canvas_margins = {"LeftMargin":0.15, "RighttMargin":0.15, "BottomMargin":0.15, "TopMargin":0.15}
    axes_sizes = {"x_axis_label_size":0.02, "y_axis_label_size":0.02, "x_axis_title_size":0.05, "y_axis_title_size":0.05}
    
    profiler = Profile()
    profiler.enable()
    plotting(files, ev_start_all, ev_stop_list_edited, systemo, system_collections, out_dir, plot_title, x_axis_title, y_axis_title, color_bar_title, plot_name, temp_dir_name,
             canvas_margins, canvas_width, canvas_height, axes_sizes, to_scale)
    
    # Delay the removal slightly to avoid the file busy error
    time.sleep(2)  # wait for 2 seconds
    shutil.rmtree(os.path.join(out_dir, temp_dir_name))
    profiler.disable()
    profiler.print_stats(sort='cumtime')
