from pyLCIO.io import LcioReader
import sys
import os
# process = sys.argv[1]
def main():
    path = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/Machine/beamstrahlung_FCCee@91GeV/ILD_l5_v11gamma/"
    for i in range(100):
        slcio_file = os.path.join(path, "pairs-{}_ZatIP_tpcTimeKeepMC_keep_microcurlers_10MeV_30mrad_ILD_l5_v11gamma.slcio".format(i))
        
        print(slcio_file)
        if os.path.isfile(slcio_file):
            reader = LcioReader.LcioReader(slcio_file)
            events_number = reader.getNumberOfEvents()

            print("pairs-{}_ZatIP_tpcTimeKeepMC_keep_microcurlers_10MeV_30mrad_ILD_l5_v11gamma.slcio".format(i), events_number)
if __name__ == "__main__":
    main()

