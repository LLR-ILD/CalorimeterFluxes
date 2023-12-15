from pyLCIO.io import LcioReader
import sys
import os

path = sys.argv[1]
process = sys.argv[2]
skip_events = sys.argv[3]
total_events = sys.argv[4]
number_processes = sys.argv[5]

def main():
    slcio_file_path = os.path.join(path, process)
    for i in range(number_processes):
        slcio_file = os.path.join(slcio_file_path, "partial_{}_fullSim_{}_{}+{}.slcio".format(i, process, skip_events, total_events))
        if os.path.isfile(slcio_file):
            reader = LcioReader.LcioReader(slcio_file)
            events_number = reader.getNumberOfEvents()

            print("partial_{}_fullSim_{}_{}+{}.slcio".format(i, process, skip_events, total_events), events_number)
if __name__ == "__main__":
    main()