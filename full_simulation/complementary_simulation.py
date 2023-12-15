import os
import sys
from pyLCIO.io import LcioReader

path = sys.argv[1]
process = sys.argv[2]
total_events = int(sys.argv[3])
skipped_events = int(sys.argv[4])
number_processes = int(sys.argv[5])
input_path = sys.argv[6]

def run_ddsim(input_file, skip_events, num_events, file_number):
    ilcsoft_version = "v02-02-02"
    stdhep_path = os.path.join(input_path, process)
    output_path = os.path.join(path, process)
    output_file = "complementary_{}_fullSim_{}_{}+{}.slcio".format(file_number, process, skipped_events, total_events)
    geom_xml = "parameters/ILD_l5_v02.xml"
    steering = "parameters/ddsim_steer.py"

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
    slcio_files_path = os.path.join(path, process)
    for i in range(number_processes):
        slcio_file = os.path.join(slcio_files_path, "partial_{}_fullSim_{}_{}+{}.slcio".format(i, process, skipped_events, total_events)) #replace with the names of the slcio files. 
        reader = LcioReader.LcioReader(slcio_file)
        events_number = reader.getNumberOfEvents()

        if events_number < events_per_process:
            start_event = events_number + 1 + events_per_process*i
            remaining_events = events_per_process - events_number

            run_ddsim(input_file="{}.stdhep".format(process), skip_events=start_event, num_events=remaining_events, file_number=i)

if __name__ == "__main__":
    main()
