from __future__ import absolute_import
from __future__ import print_function  # python3 style printing in python2.
import logging
import os
import sys
import tarfile

from pyLCIO.io import LcioReader
from pyLCIO import EVENT, IMPL, UTIL
import ROOT

# logging.DEBUG for debugging. Else logging.INFO.
format = "%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
logging.basicConfig(format=format, level=logging.DEBUG)

help_string = """The script must be called with 2 or 4 arguments as:
$ python pylcio_powered_2ascii.py slcio_file ascii_out_dir ev_start ev_stop
- slcio_file: File with the reconstructed information in LCIO format.
- ascii_out_dir: Folder to write the ASCII output to.
    Its parent must exist. The folder itself can exist, but must be empty then.
- ev_start ev_stop: Integers. Specify both or neither of them. Will process
    (ev_stop - ev_start) events. Use ev_stop=-1 to exhaust the file.
"""

#Creating ROOT canvas to save the histograms
canvas = ROOT.TCanvas('canvas', 'Histogram', 800, 600)

system_limits = {"ECALBarrel" : (8, 5, 5, 30) , "EndCaps" : (4, "0-6", 5, 30)}
#selection format "S:M:T:L" conditions => "*:*:2:0-4,5-10" means no selection on M, S, 1 histo per 2 tower , 1 for layer 0 to 5, and one for layers in 5 to 10.
#The keys of the dictionary are the system names. Each key has a value composed of 4 lists. 
# The first list has the collections' names. 
# The second one has the selections we impose on the histograms made in the order given above. 
# The third list has 4 lists each with 2 arguments. Each list has the bin number (the first argument) and the maximum of the range of the histogram (the second argument). The 4 lists are in this order: time, lower-scale energy, upper-scale energy, and number of hits above a specific threshold.
# The fourth list has the energy threshold that we use in the Nhits histogram. 
dictionary_of_system = {
        "SiECalEndcap": (["ECalEndcapSiHitsEven", "ECalEndcapSiHitsOdd"], [["*"],["0","6"],["*"],["0:9","10:19","20:29"]], [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0002]]),
        "SiECALBarrel": (["ECalBarrelSiHitsEven", "ECalBarrelSiHitsOdd"], [["*"],["1","2","3","4","5"],["*"],["0:9","10:19","20:29"]], [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0002]]), 
        "SiECalRing": (["EcalEndcapRingCollection"], [["*"],["*"],["*"],["*"]], [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0002]]), 
        "ScECalEndcap": (["ECalEndcapScHitsEven", "ECalEndcapScHitsOdd"], [["*"],["0","6"],["*"],["0:9","10:19","20:29"]], [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0002]]),
        "ScECALBarrel": (["ECalBarrelScHitsEven", "ECalBarrelScHitsOdd"], [["*"],["1","2","3","4","5"],["*"],["0:9","10:19","20:29"]], [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0002]]), 
        "RPCHCalEndcap": (["HCalEndcapRPCHits"], [["*"],["0","6"],["*"],["0:19","20:39","40:59"]], [[100, 20], [100, 2e-6], [100, 3e-5], [100, 35]], [[0.0002]]),
        "RPCHCalBarrel": (["HCalBarrelRPCHits"], [["*"],["1","2","3","4","5"],["*"],["0:19","20:39","40:59"]], [[100, 20], [100, 2e-6], [100, 3e-5], [100, 35]], [[0.0002]]), 
        "RPCHCalECRing": (["EcalEndcapRingCollection"], [["*"],["*"],["*"],["*"]], [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0002]]),         
        "ScHCalEndcap": (["HcalEndcapsCollection"], [["*"],["0","6"],["*"],["0:19","20:39","40:59"]], [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0002]]),
        "ScHcalBarrel": (["HcalBarrelRegCollection"], [["*"],["1","2","3","4","5"],["*"],["0:19","20:39","40:59"]], [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0002]]), 
        "ScHCalECRing": (["EcalEndcapRingCollection"], [["*"],["*"],["*"],["*"]], [[100, 20], [100, 0.001], [100, 0.03], [100, 35]], [[0.0002]])                 
        }

def histograms_for_systems(system):
    histograms_args = dictionary_of_system[system][2]
    time_args = histograms_args[0]
    lower_scale_args = histograms_args[1]
    upper_scale_args = histograms_args[2]
    Nhits_args = histograms_args[3]
    selection = dictionary_of_system[system][1] 
    staves = selection[0]
    modules = selection[1]
    towers = selection[2]
    layers = selection[3]
    system_dictionary_list = []
    system_histograms_lower_Scale = []
    system_histograms_upper_Scale = []
    system_histograms_Nhits = []
    system_histograms_time = []
    for stave in staves:
            for module in modules:
                for tower in towers:
                    for layer in layers:
                        my_dict = {'staves': stave, 'modules': module, 'towers': tower, 'layers': layer}
                        my_dict = {key: value for key, value in my_dict.items() if value != "*"}
                        system_dictionary_list.append(my_dict)
                        histogram_name = "{system}{stave}{module}{tower}{layer}".format(system=system, 
                                                                                        stave="_S" + stave if stave != "*" else "",
                                                                                        module="_M" + module if module != "*" else "", 
                                                                                        tower="_T" + tower if tower != "*" else "", 
                                                                                        layer="_L" + layer if layer != "*" else "")
                        hist_time = ROOT.TH1F(histogram_name + '_time', 'Time histogram - {}'.format(histogram_name), time_args[0], 6, time_args[1])
                        hist_time.GetXaxis().SetTitle("Weighted Time of Subhits [ns]")
                        hist_time.GetYaxis().SetTitle("Number of Events times Energy [GeV]")
                        # hist_time.SetCanExtend(ROOT.TH1.kAllAxes)
                        hist_lower_scale = ROOT.TH1F(histogram_name, 'Energy histogram - {}'.format(histogram_name), lower_scale_args[0], 0, lower_scale_args[1])
                        hist_lower_scale.GetXaxis().SetTitle("Energy [GeV]")
                        hist_lower_scale.GetYaxis().SetTitle("Number of Events")
                        hist_upper_scale = ROOT.TH1F(histogram_name + '_upper_scale', 'Upper-Scale Energy histogram - {}'.format(histogram_name), upper_scale_args[0], lower_scale_args[1], upper_scale_args[1])
                        hist_upper_scale.GetXaxis().SetTitle("Energy [GeV]")
                        hist_upper_scale.GetYaxis().SetTitle("Number of Events")
                        hist_upper_scale.SetCanExtend(ROOT.TH1.kAllAxes)
                        hist_Nhits = ROOT.TH1F(histogram_name + '_#hits', 'Number-of-hits histogram - {}'.format(histogram_name), Nhits_args[0], 0, Nhits_args[1])
                        hist_Nhits.GetXaxis().SetTitle("Number of hits above " + str(dictionary_of_system[system][3][0]) + " GeV")
                        hist_Nhits.GetYaxis().SetTitle("Number of Events")
                        hist_Nhits.SetCanExtend(ROOT.TH1.kAllAxes)
                        system_histograms_time.append(hist_time)
                        system_histograms_lower_Scale.append(hist_lower_scale)
                        system_histograms_upper_Scale.append(hist_upper_scale)
                        system_histograms_Nhits.append(hist_Nhits)
    return system_dictionary_list, system_histograms_time, system_histograms_lower_Scale, system_histograms_upper_Scale, system_histograms_Nhits

def name_histograms():
    system_dictionary = {}
    all_time_histograms = {}
    all_histograms_lower_Scale = {}
    all_histograms_upper_Scale = {}
    all_Nhits_histograms = {}
    for system in dictionary_of_system.keys():
        system_dictionary[system] = histograms_for_systems(system)[0]
        all_time_histograms[system] = histograms_for_systems(system)[1]
        all_histograms_lower_Scale[system] = histograms_for_systems(system)[2]
        all_histograms_upper_Scale[system] = histograms_for_systems(system)[3]
        all_Nhits_histograms[system] = histograms_for_systems(system)[4]
    return system_dictionary, all_time_histograms, all_histograms_lower_Scale, all_histograms_upper_Scale, all_Nhits_histograms

systems_dictionary, time_histograms, histograms_lower_scale, histograms_upper_Scale, Nhits_histograms,  = name_histograms()

def decoding(event, collection_name, hit, is_ecal_endcap_ring=False):
    cell_id_info = ["system", "stave", "module", "cellX", "cellY", "tower", "layer", "wafer", "slice"]
    endcap_replacements = dict(cellX="x", cellY="y")
    # Combine 32bits CellIDo and CellId1 in a 64 bits stream
    calo_hits = event.getCollection(collection_name)
    is_endcap = (collection_name in ["EcalEndcapRingCollection"])
    cell_id_encoding = calo_hits.getParameters().getStringVal(EVENT.LCIO.CellIDEncoding)
    id_decoder = UTIL.BitField64(cell_id_encoding)
    cell_id = (hit.getCellID0() & 0xffffffff) | (hit.getCellID1() << 32)
    id_decoder.setValue(cell_id)
    hit_info = {}
    for cell_id_key in cell_id_info:
        encoded_key = cell_id_key
        if is_ecal_endcap_ring:
            if cell_id_key in endcap_replacements:
                encoded_key = endcap_replacements[cell_id_key]
            elif cell_id_key in ["wafer", "slice"]:
                # Endcaps have no wafer information.
                continue
        try:
            hit_info[encoded_key + 's'] = int(id_decoder[encoded_key].value())
        except Exception as e:  # replace with the correct type of exception
            pass
    return hit_info

def subhit_decoding(hit):
    hit_subhits = []
    for i_subhit in range(hit.getNMCContributions()):
            subhit_info = {}
            subhit_info["primary_pdg"] =  hit.getParticleCont(i_subhit).getPDG()
            subhit_info["energy"] =  hit.getEnergyCont(i_subhit)
            subhit_info["time"] =  hit.getTimeCont(i_subhit)
            subhit_info["length"] =  hit.getTimeCont(i_subhit)
            subhit_info["length"] = hit.getLengthCont(i_subhit)
            subhit_info["secondary_pdg"] = hit.getPDGCont(i_subhit)
            subhit_info["pos_x"] = hit.getStepPosition(i_subhit)[0]
            subhit_info["pos_y"] = hit.getStepPosition(i_subhit)[1]
            subhit_info["pos_z"] = hit.getStepPosition(i_subhit)[2]
            hit_subhits.append(subhit_info)
    return hit_subhits

def fill_histogram(slcio_file, ev_start, ev_stop):
    reader = LcioReader.LcioReader(slcio_file)
    if ev_stop < 0:
        ev_stop = reader.getNumberOfEvents() + ev_stop + 1
    for i, event in enumerate(reader):
        # time.sleep(0.1)
        # Print out a progress update
        if i % 10 == 0:  # Adjust this condition to control how often updates are printed
            print('Processed {} out of {} items'.format(i, reader.getNumberOfEvents()))
        if i < ev_start:
            continue
        if i >= ev_stop:
            break
        for system in ["SiECALBarrel", "ScECalEndcap"]:
            for hist, hist_upper_Scale, hist_time, hist_Nhits, system_dictionary in zip(histograms_lower_scale[system], histograms_upper_Scale[system], time_histograms[system], Nhits_histograms[system], systems_dictionary[system]):
                Nhits = 0
                for collection_name in dictionary_of_system[system][0]:          
                    calo_hits = event.getCollection(collection_name)
                    for j, hit in enumerate(calo_hits, start=1):
                        energy = hit.getEnergy()
                        decoded_hit = decoding(event,collection_name, hit)
                        values_same = True
                        for key in system_dictionary.keys():
                            split = system_dictionary[key].split(':')
                            integer_decoded_hit = decoded_hit[key]
                            if len(split) != 1:
                                if int(split[0]) > integer_decoded_hit or integer_decoded_hit > int(split[1]):
                                    values_same = False
                                    break 
                            elif int(system_dictionary[key]) != integer_decoded_hit:
                                values_same = False
                                break
                        if values_same:
                            #Number-of-cells-with-energy-above-threshold-per-cell histogram 
                            if energy > dictionary_of_system[system][3][0][0]:
                                Nhits += 1
                            #Lower and upper scale histograms
                            if 0 <= energy < dictionary_of_system[system][2][1][1]:
                                hist.Fill(energy)
                            else:
                                hist_upper_Scale.Fill(energy)
                            #time histogram
                            subhit_information = subhit_decoding(hit)
                            for subhit in subhit_information:
                                hist_time.Fill(subhit["time"], subhit["energy"])
                hist_Nhits.Fill(Nhits)
                
def write_histogram(histo_dir):
    # myfile = ROOT.TFile( str(histo_dir) + '/all.root', 'RECREATE' )
    for system in ["SiECALBarrel", "ScECalEndcap"]:
        
        # Specify the directory path
        directory = str(histo_dir) + "/" + system
        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        myfile = ROOT.TFile( str(histo_dir) + "/" + system + '.root', 'RECREATE' )
        for hist, hist_upper_Scale, hist_time, Nhits_hist in zip(histograms_lower_scale[system], histograms_upper_Scale[system], time_histograms[system], Nhits_histograms[system]):
            hist_time.Draw("HIST")
            canvas.SaveAs(directory + "/Time_histogram_{}".format(hist.GetName()) + ".pdf")
            hist_time.Write()

            hist.Draw()
            canvas.SaveAs(directory + "/energy_histogram_lower_scale{}".format(hist.GetName()) + ".pdf")
            hist.Write()

            ROOT.gPad.SetLogy()
            
            
            hist_upper_Scale.Draw()
            canvas.SaveAs(directory + "/{}_energy_histogram_{}".format("upper_scale", hist.GetName()) + ".pdf")
            hist_upper_Scale.Write()

            ROOT.gPad.SetLogy(False)

            Nhits_hist.Draw()
            canvas.SaveAs(directory + "/Nhits_histogram_{}".format(hist.GetName()) + ".pdf")
            Nhits_hist.Write()     
        myfile.Close()
    # myfile.Close()               

def validate_command_line_args():
    """This just validates and returns the command line inputs."""
    if len(sys.argv) not in [3, 5]: raise Exception(help_string)

    slcio_file = sys.argv[1]
    if not os.path.isfile(slcio_file): raise Exception(help_string)
    histo_dir = os.path.abspath(sys.argv[2])
    hist_out_parent = os.path.dirname(histo_dir)
    if not os.path.isdir(hist_out_parent): raise Exception(help_string)
    if not os.path.exists(histo_dir):
        os.mkdir(histo_dir)
    #elif len(os.listdir(ascii_out_dir)) != 0: raise Exception(help_string)

    if len(sys.argv) == 3:
        ev_start = 0
        ev_stop = -1
    else:
        try:
            ev_start = int(sys.argv[3])
            ev_stop = int(sys.argv[4])
            ev_start = int(sys.argv[3])
            ev_stop = int(sys.argv[4])
        except (IndexError, ValueError): raise Exception(help_string)
    return slcio_file, histo_dir, ev_start, ev_stop

if __name__ == "__main__":
    slcio_file, histo_dir, ev_start, ev_stop = validate_command_line_args()
    fill_histogram(slcio_file, ev_start, ev_stop)
    write_histogram(histo_dir)
    print('sad')