import os
import sys
from pyLCIO.io import LcioReader

number_processes = int(sys.argv[1])
total_events = int(sys.argv[2])
process = sys.argv[3]

def run_ddsim(input_file, skip_events, num_events, file_number):
    ilcsoft_version = "v02-02-02"
    stdhep_path = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/stdhep/{}/".format(process) #replace with the path to the stdhep file.
    output_path = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/{}/".format(process) #replace with the path to the output file. 
    output_file = "complementary_{}_fullSim_{}_0+10000.slcio".format(file_number, process)
    geom_xml = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/full_simulation/parameters/ILD_l5_v02.xml"
    steering = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/full_simulation/parameters/ddsim_steer.py"

    cmd = """
    source /cvmfs/ilc.desy.de/sw/x86_64_gcc82_centos7/{}/init_ilcsoft.sh

    ddsim --inputFiles {}{} --outputFile {}{} \
        --compactFile {} \
        --numberOfEvents {} \
        --skipNEvents {} \
        --steeringFile {} > {}{}.log 2>&1 &
    """.format(ilcsoft_version, stdhep_path, input_file, output_path, output_file, geom_xml, num_events, skip_events, steering, output_path, output_file)

    os.system(cmd)

def main():
    events_per_process = total_events/number_processes
    path = "/home/llr/ilc/hassouna/script2/CalorimeterFluxes/data/ILD/FullSim/{}".format(process) #replace with the path to the directory of the existing slcio files.
    for i in range(number_processes):
        slcio_file = os.path.join(path, "partial_{}_fullSim_{}_0+10000.slcio".format(i, process)) #replace with the names of the slcio files. 
        reader = LcioReader.LcioReader(slcio_file)
        events_number = reader.getNumberOfEvents()

        if events_number < events_per_process and i == 24:
            start_event = events_number + 1 + events_per_process*i
            remaining_events = events_per_process - events_number

            run_ddsim(input_file="{}.stdhep".format(process), skip_events=start_event, num_events=remaining_events, file_number=i)

if __name__ == "__main__":
    main()
