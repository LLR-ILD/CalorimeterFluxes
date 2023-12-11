from pyLCIO.io import LcioReader
import sys
import os
# process = sys.argv[1]

def main():
    path = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/wzp6_ee_qq_ecm365/"
    events_numbers = []
    for i in range(25):
        slcio_file = os.path.join(path, "partial_{}_fullSim_wzp6_ee_qq_ecm365_0+10000.slcio".format(i))
        
        if os.path.isfile(slcio_file):
            reader = LcioReader.LcioReader(slcio_file)
            events_number = reader.getNumberOfEvents()
            print(events_number)
            # if events_number < 400:
            #     complementary_slcio_file = os.path.join(path, "complementary_{}_fullSim_wzp6_ee_tt_ecm365_0+10000.slcio".format(i))
            #     if os.path.isfile(complementary_slcio_file):
            #         complementary_reader = LcioReader.LcioReader(complementary_slcio_file)
            #         complementary_event_number = complementary_reader.getNumberOfEvents()
            #         total_events = events_number + complementary_event_number
            #         events_numbers.append(total_events)
            #     else:
            #         events_numbers.append(events_number)
            # else:
            #     events_numbers.append(events_number)

    # print(events_numbers)
if __name__ == "__main__":
    main()

