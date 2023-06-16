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

system_limits = {"ECALBarrel" : (8, 5, 5, 30) , "EndCaps" : (4, "4-6", 5, 30)}
#selection format "S:M:T:L" conditions => "*:*:2:0-4,5-10" means no selection on M, S, 1 histo per 2 tower , 1 for layer 0 to 5, and one for layers in 5 to 10.
dictionary_of_system = {"ECalEndcap": (["ECalEndcapSiHitsEven", "ECalEndcapSiHitsOdd"], [["*"],["*"],["*"],["*"]]),
                        "ECALBarrel": (["ECalBarrelSiHitsEven", "ECalBarrelSiHitsOdd"], [["*"],["*"],["*"],["*"]]), 
                        "ECalRing": (["EcalEndcapRingCollection"], [["*"],["*"],["*"],["*"]])}


#Function to create the histograms and name them
def name_histograms():
    all_histograms = {}
    all_histograms_upper_Scale = {}
    all_time_histograms = {}
    system_dictionary = {}
    for system in dictionary_of_system.keys():
        system_dictionary[system] = []
        all_histograms[system] = []
        all_histograms_upper_Scale[system] = []
        all_time_histograms[system] = []
        selection = dictionary_of_system[system][1] 
        staves = selection[0]
        modules = selection[1]
        towers = selection[2]
        layers = selection[3]
        for module in modules:
            for stave in staves:
                for tower in towers:
                    for layer in layers:
                        my_dict = {'modules': module, 'staves': stave, 'towers': tower, 'layers': layer}
                        my_dict = {key: value for key, value in my_dict.items() if value != "*"}
                        system_dictionary[system].append(my_dict)
                        histogram_name = "{system}{module}{stave}{tower}{layer}".format(system=system, 
                                                                                        module="_M" + module if module != "*" else "", 
                                                                                        stave="_S" + stave if stave != "*" else "", 
                                                                                        tower="_T" + tower if tower != "*" else "", 
                                                                                        layer="_L" + layer if layer != "*" else "")
                        hist = ROOT.TH1F(histogram_name, 'Energy histogram - {}'.format(histogram_name), 100, 0, 0.001)
                        hist_upper_scale = ROOT.TH1F(histogram_name + '_upper_scale', 'Upper-Scale Energy histogram - {}'.format(histogram_name), 10, 0.001, 0.03)
                        hist_upper_scale.SetCanExtend(ROOT.TH1.kAllAxes)
                        hist_time = ROOT.TH1F(histogram_name + '_time', 'Time histogram - {}'.format(histogram_name), 100, 0, 10)
                        all_histograms[system].append(hist)
                        all_histograms_upper_Scale[system].append(hist_upper_scale)
                        all_time_histograms[system].append(hist_time)
    return all_histograms, all_histograms_upper_Scale, all_time_histograms, system_dictionary

histograms, histograms_upper_Scale, time_histograms, systems_dictionary = name_histograms()

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
        hit_info[encoded_key + 's'] = int(id_decoder[encoded_key].value())
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

def create_histogram(slcio_file, ascii_out_dir, ev_start, ev_stop):
    
    for system in dictionary_of_system.keys():
        for hist, hist_upper_Scale, hist_time, system_dictionary in zip(histograms[system], histograms_upper_Scale[system], time_histograms[system], systems_dictionary[system]):
            reader = LcioReader.LcioReader(slcio_file)
            max_energy = 0
            if ev_stop < 0:
                ev_stop = reader.getNumberOfEvents() + ev_stop + 1
            for i, event in enumerate(reader):
                if i < ev_start:
                    continue
                if i >= ev_stop:
                    break
                for collection_name in dictionary_of_system[system][0]:          
                    calo_hits = event.getCollection(collection_name)
                    for j, hit in enumerate(calo_hits, start=1):
                        energy = hit.getEnergy()
                        if energy > max_energy:
                            max_energy = energy
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
                            if 0 <= energy < 0.001:
                                hist.Fill(energy)
                            else:
                                hist_upper_Scale.Fill(energy)

                            #time histogram
                            subhit_information = subhit_decoding(hit)
                            for subhit in subhit_information:
                                hist_time.Fill(subhit["time"], subhit["energy"])



           
            hist_time.Draw("HIST")
            canvas.SaveAs("created_histograms/Time_histogram_{}{}".format(hist.GetName(), ".pdf"))

            hist_name = 'energy_histogram_{}.'.format(hist.GetName())
            hist.Draw()
            canvas.SaveAs("created_histograms/{}{}".format(hist_name, "pdf"))

            canvas.Clear()

            ROOT.gPad.SetLogy()
            # hist_upper_Scale.SetAxisRange(0.001, max_energy)
            
            hist_upper_Scale.Draw()
            canvas.SaveAs("created_histograms/{}{}{}".format("upper_scale_", hist_name, "pdf"))
            ROOT.gPad.SetLogy(False)                       
            # canvas.SaveAs("created_histograms/{}{}".format(hist_name, "root"))


def validate_command_line_args():
    """This just validates and returns the command line inputs."""
    if len(sys.argv) not in [3, 5]: raise Exception(help_string)

    slcio_file = sys.argv[1]
    if not os.path.isfile(slcio_file): raise Exception(help_string)
    ascii_out_dir = os.path.abspath(sys.argv[2])
    ascii_out_parent = os.path.dirname(ascii_out_dir)
    if not os.path.isdir(ascii_out_parent): raise Exception(help_string)
    if not os.path.exists(ascii_out_dir):
        os.mkdir(ascii_out_dir)
    #elif len(os.listdir(ascii_out_dir)) != 0: raise Exception(help_string)

    if len(sys.argv) == 3:
        ev_start = 0
        ev_stop = -1
    else:
        try:
            ev_start = int(sys.argv[3])
            ev_stop = int(sys.argv[4])
        except (IndexError, ValueError): raise Exception(help_string)
    return slcio_file, ascii_out_dir, ev_start, ev_stop

if __name__ == "__main__":
    slcio_file, ascii_out_dir, ev_start, ev_stop = validate_command_line_args()
    create_histogram(slcio_file, ascii_out_dir, ev_start, ev_stop)