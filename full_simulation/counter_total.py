from pyLCIO.io import LcioReader
import sys
import os

path = sys.argv[1]
process = sys.argv[2]
total_events = sys.argv[3]
skip_events = sys.argv[4]
number_processes = sys.argv[5]

events_number_per_process = int(total_events) / int(number_processes)

def main():
    events_numbers = []
    slcio_files_path = os.path.join(path, process)
    for i in range(int(number_processes)):
        slcio_file = os.path.join(slcio_files_path, "partial_{}_fullSim_{}_{}+{}.slcio".format(i, process, skip_events, total_events))
        if os.path.isfile(slcio_file):
            reader = LcioReader.LcioReader(slcio_file)
            events_number = reader.getNumberOfEvents()
            if events_number < events_number_per_process:
                complementary_slcio_file = os.path.join(slcio_files_path, "complementary_{}_fullSim_{}_0+10000.slcio".format(i, process, skip_events, total_events))
                if os.path.isfile(complementary_slcio_file):
                    complementary_reader = LcioReader.LcioReader(complementary_slcio_file)
                    complementary_event_number = complementary_reader.getNumberOfEvents()
                    all_events = events_number + complementary_event_number
                    events_numbers.append(all_events)
                else:
                    events_numbers.append(events_number)
            else:
                events_numbers.append(events_number)

    print(events_numbers)
if __name__ == "__main__":
    main()

